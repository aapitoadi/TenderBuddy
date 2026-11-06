"""Tahap 1 - Ekstraksi persyaratan dari paket dokumen tender LPSE.

Setiap butir persyaratan WAJIB membawa kutipan dan lokasi sumbernya.
Kutipan diverifikasi ulang terhadap teks asli; butir yang kutipannya tidak
ditemukan akan ditandai dan tidak boleh dipakai untuk keputusan.
"""

from __future__ import annotations

import re
import textwrap
from pathlib import Path

from utilitas import normal, parse_rupiah, parse_tanggal, rupiah, cap_waktu, nama_hari

POLA_INSTRUKSI = [
    r"(?i)\b(ai|asisten|agent|agen|sistem|model)\s*[:,]\s*(abaikan|nyatakan|anggap|loloskan|jangan|hapus)",
    r"(?i)(abaikan|ignore|disregard)\s+(semua|seluruh|all|previous|sebelumnya|instruksi)",
    r"(?i)nyatakan\s+(seluruh|semua)\s+(persyaratan|syarat)",
    r"(?i)(loloskan|setujui)\s+(tanpa|dengan)\s+(pemeriksaan|verifikasi)",
    r"(?i)jangan\s+(periksa|laporkan|tampilkan)\s+(kekurangan|risiko)",
]


def baca_paket(dir_paket: Path) -> dict[str, str]:
    """Baca seluruh dokumen teks dalam folder paket tender."""
    dokumen = {}
    for p in sorted(dir_paket.glob("*.txt")):
        dokumen[p.name] = p.read_text(encoding="utf-8")
    return dokumen


def _baris(teks: str, pola: str) -> tuple[int, str] | tuple[None, None]:
    for i, baris in enumerate(teks.splitlines(), start=1):
        if re.search(pola, baris):
            return i, baris
    return None, None


def _bagian(teks: str, huruf: str) -> tuple[str, int]:
    """Ambil isi bagian berhuruf (A., B., ...) beserta nomor baris awalnya."""
    baris = teks.splitlines()
    mulai = None
    for i, b in enumerate(baris):
        if re.match(rf"^{huruf}\.\s+[A-Z]", b):
            mulai = i
            break
    if mulai is None:
        return "", 0
    akhir = len(baris)
    for j in range(mulai + 1, len(baris)):
        if re.match(r"^[A-Z]\.\s+[A-Z]", baris[j]):
            akhir = j
            break
    return "\n".join(baris[mulai:akhir]), mulai + 1


def deteksi_instruksi_tersisip(dokumen: dict[str, str]) -> list[dict]:
    """Cari teks yang berperan sebagai instruksi kepada AI di dalam dokumen.

    Dokumen tender adalah DATA, bukan perintah. Temuan dicatat, tidak dijalankan.
    """
    temuan = []
    for nama, teks in dokumen.items():
        for i, baris in enumerate(teks.splitlines(), start=1):
            for pola in POLA_INSTRUKSI:
                if re.search(pola, baris):
                    temuan.append({
                        "jenis": "instruksi_tersisip",
                        "dokumen": nama,
                        "baris": i,
                        "kutipan": baris.strip(),
                        "tindakan": "Diabaikan. Dokumen diperlakukan sebagai data, bukan perintah.",
                    })
                    break
    return temuan


def _ekstrak_personil(bagian_g: str, baris_awal: int) -> list[dict]:
    """Ekstrak kebutuhan personil inti dari bagian G KAK."""
    hasil = []
    pola_butir = re.compile(r"(?m)^\s*(\d)\.\s+(.+?)(?=^\s*\d\.\s|\Z)", re.S)
    for m in pola_butir.finditer(bagian_g):
        isi = re.sub(r"\s+", " ", m.group(2)).strip()
        # Paragraf penutup bagian G bukan bagian dari butir personil.
        isi = re.split(r"Seluruh personil inti wajib", isi)[0].strip()
        if ":" not in isi:
            continue
        jabatan, sisa = isi.split(":", 1)
        if "orang" not in sisa:
            continue

        jumlah = 1
        mj = re.search(r"(\d+)\s*\(", sisa)
        if mj:
            jumlah = int(mj.group(1))

        pendidikan = None
        mp = re.search(r"minimal\s+(S1|S2|D3|D4)\s+([A-Za-z ]+?)(?:,|$)", sisa)
        if mp:
            pendidikan = f"{mp.group(1)} {mp.group(2).strip()}"

        pengalaman = None
        mg = re.search(r"pengalaman\s+minimal\s+(\d+)", sisa)
        if mg:
            pengalaman = int(mg.group(1))

        sertifikat = []
        for pola in (
            r"SKK Konstruksi [A-Za-z0-9 ]+?(?=,|\sdan\s|$)",
            r"SKA [A-Za-z ]+?(?=,|\sdan\s|\syang\s|$)",
            r"Sertifikat Ahli K3 Umum",
        ):
            for s in re.findall(pola, sisa):
                s = re.sub(r"\s+", " ", s).strip(" ,")
                if s and s not in sertifikat:
                    sertifikat.append(s)

        hasil.append({
            "jabatan": jabatan.strip(),
            "jumlah": jumlah,
            "pendidikan": pendidikan,
            "pengalaman_min_tahun": pengalaman,
            "sertifikat_diminta": sertifikat,
            "kutipan": isi,
            "baris": baris_awal + bagian_g[: m.start()].count("\n"),
        })
    return hasil


def _ekstrak_jadwal(bagian_i: str, baris_awal: int) -> list[dict]:
    jadwal = []
    for i, baris in enumerate(bagian_i.splitlines()):
        if ":" not in baris:
            continue
        label, nilai = baris.split(":", 1)
        label = re.sub(r"^\s*\d+\.\s*", "", label).strip()
        if not label or not nilai.strip():
            continue
        tanggal = parse_tanggal(nilai)
        jam = re.findall(r"(\d{2})\.(\d{2})", nilai)
        zona = None
        for z in ("WIB", "WITA", "WIT"):
            if re.search(rf"\b{z}\b", nilai):
                zona = z
                break
        jadwal.append({
            "label": label,
            "nilai": nilai.strip(),
            "tanggal": tanggal.isoformat() if tanggal else None,
            "hari": nama_hari(tanggal) if tanggal else None,
            "jam": f"{jam[0][0]}.{jam[0][1]}" if jam else None,
            "jam_akhir": f"{jam[-1][0]}.{jam[-1][1]}" if len(jam) > 1 else None,
            "zona_waktu": zona,
            "rentang": bool(re.search(r"\d\s*-\s*\d", nilai)),
            "baris": baris_awal + i,
        })
    return jadwal


def _ekstrak_dokumen_admin(teks: str) -> list[dict]:
    blok = ""
    m = re.search(r"DOKUMEN PENAWARAN ADMINISTRASI YANG WAJIB DIUNGGAH(.*?)(?=^\s*7\.\s*KUALIFIKASI)", teks, re.S | re.M)
    if m:
        blok = m.group(1)
    hasil = []
    for mm in re.finditer(r"(?m)^\s{2,}([a-l])\.\s+(.+?)(?=^\s{2,}[a-l]\.\s|\Z)", blok, re.S):
        isi = re.sub(r"\s+", " ", mm.group(2)).strip().rstrip(".")
        hasil.append({"huruf": mm.group(1), "uraian": isi})
    return hasil


def ekstrak(dokumen: dict[str, str]) -> dict:
    """Ekstrak seluruh persyaratan terstruktur dari paket dokumen."""
    persyaratan: list[dict] = []
    peringatan: list[dict] = []
    nomor = 0

    def tambah(kategori, judul, kunci, pernyataan, sumber_dok, bagian, kutipan, parameter=None, wajib=True):
        nonlocal nomor
        nomor += 1
        persyaratan.append({
            "id": f"SYR-{nomor:03d}",
            "kategori": kategori,
            "judul": judul,
            "kunci": kunci,
            "pernyataan": pernyataan,
            "parameter": parameter or {},
            "wajib": wajib,
            "sumber": {
                "dokumen": sumber_dok,
                "bagian": bagian,
                "kutipan": kutipan.strip(),
            },
        })

    # ---------- Dokumen 1: KAK / TOR ----------
    kak_nama = next((n for n in dokumen if "KAK" in n.upper()), None)
    if not kak_nama:
        peringatan.append({"jenis": "dokumen_hilang", "pesan": "Dokumen KAK/TOR tidak ditemukan pada paket."})
        kak = ""
    else:
        kak = dokumen[kak_nama]

    # Pagu anggaran
    no, baris = _baris(kak, r"Pagu anggaran pekerjaan ini")
    if baris:
        lanjut = "\n".join(kak.splitlines()[no - 1: no + 1])
        nilai = parse_rupiah(lanjut)
        tambah("Pagu", "Nilai pagu anggaran", "pagu_anggaran",
               f"Pagu anggaran paket sebesar {rupiah(nilai) if nilai else 'tidak terbaca'} termasuk PPN.",
               kak_nama, "E", lanjut, {"nilai": nilai})

    # HPS
    no, baris = _baris(kak, r"Nilai HPS")
    if baris:
        nilai = parse_rupiah(baris)
        tambah("Pagu", "Nilai HPS (batas penawaran)", "hps",
               f"Nilai HPS sebesar {rupiah(nilai) if nilai else 'tidak terbaca'}; penawaran di atas HPS dinyatakan gugur.",
               kak_nama, "E", baris, {"nilai": nilai})

    # Kualifikasi usaha
    no, baris = _baris(kak, r"kualifikasi usaha kecil")
    if baris:
        tambah("Kualifikasi", "Kualifikasi usaha", "kualifikasi_usaha",
               "Peserta memiliki kualifikasi usaha kecil.", kak_nama, "F", baris,
               {"nilai": "Kecil"})

    # KBLI
    no, baris = _baris(kak, r"KBLI\)?\s*41011")
    if baris:
        kbli = re.findall(r"41\d{3}", baris)
        tambah("Kualifikasi", "Kesesuaian KBLI", "kbli",
               f"NIB memuat KBLI {' atau '.join(kbli)}.", kak_nama, "F", baris,
               {"nilai": kbli})

    # SBU
    no, baris = _baris(kak, r"Sertifikat Badan Usaha \(SBU\)")
    if baris:
        m = re.search(r"subklasifikasi\s+([A-Z]{2}\d{3})", baris)
        subklas = m.group(1) if m else None
        tambah("SBU", "Subklasifikasi SBU", "sbu_subklasifikasi",
               f"SBU dengan subklasifikasi {subklas} yang masih berlaku pada saat pemasukan penawaran.",
               kak_nama, "F", baris, {"nilai": subklas})

    # Personil inti
    bagian_g, baris_g = _bagian(kak, "G")
    for p in _ekstrak_personil(bagian_g, baris_g):
        tambah("Personil", f"Personil inti: {p['jabatan']}", f"personil:{p['jabatan']}",
               f"{p['jumlah']} orang {p['jabatan']}"
               + (f", pendidikan minimal {p['pendidikan']}" if p["pendidikan"] else "")
               + (f", pengalaman minimal {p['pengalaman_min_tahun']} tahun" if p["pengalaman_min_tahun"] else "")
               + (f", sertifikat: {', '.join(p['sertifikat_diminta'])}" if p["sertifikat_diminta"] else ""),
               kak_nama, "G", p["kutipan"], p)

    # BPJS personil
    no, baris = _baris(kak, r"BPJS Ketenagakerjaan minimal")
    if baris:
        tambah("Personil", "Bukti BPJS Ketenagakerjaan personil", "bpjs_personil",
               "Seluruh personil inti merupakan tenaga kerja tetap, dibuktikan BPJS Ketenagakerjaan minimal 3 bulan terakhir.",
               kak_nama, "G", baris)

    # Pengalaman
    bagian_h, baris_h = _bagian(kak, "H")
    teks_h = re.sub(r"\s+", " ", bagian_h)
    mp = re.search(r"paling sedikit\s+(\d+).*?nilai kontrak\s+minimal\s+Rp([\d\.]+)", teks_h)
    if mp:
        # Ambil jenis pekerjaan dari teks (mis. "konstruksi jalan", "konstruksi bangunan gedung")
        mj = re.search(r"pekerjaan\s+(konstruksi\s+[\w\s]+?)(?:\s+dalam|\s+dengan)", teks_h)
        jenis_pekerjaan = mj.group(1).strip() if mj else "konstruksi"
        tambah("Pengalaman", "Pengalaman pekerjaan sejenis", "pengalaman",
               f"Minimal {mp.group(1)} pekerjaan {jenis_pekerjaan} dengan nilai kontrak minimal {rupiah(parse_rupiah('Rp' + mp.group(2)))}.",
               kak_nama, "H", mp.group(0),
               {"jumlah_min": int(mp.group(1)), "nilai_min": parse_rupiah("Rp" + mp.group(2)),
                "jenis": jenis_pekerjaan})
    mt = re.search(r"dalam\s+(\d+)\s+\(.*?\)\s+tahun terakhir", re.sub(r"\s+", " ", bagian_h))
    if mt:
        tambah("Pengalaman", "Batas waktu pengalaman", "pengalaman_periode",
               f"Pengalaman dihitung dalam {mt.group(1)} tahun terakhir.", kak_nama, "H", mt.group(0),
               {"tahun": int(mt.group(1))})
    if re.search(r"subkontraktor tidak diperhitungkan", bagian_h):
        tambah("Pengalaman", "Pengecualian pengalaman subkontraktor", "pengalaman_subkon",
               "Pengalaman sebagai subkontraktor tidak diperhitungkan.", kak_nama, "H",
               "Pengalaman sebagai subkontraktor tidak diperhitungkan.", {})

    # ---------- Dokumen 2: Dokumen Pengadaan ----------
    dp_nama = next((n for n in dokumen if "Pengadaan" in n), None)
    dp = dokumen.get(dp_nama, "") if dp_nama else ""

    if dp:
        for d in _ekstrak_dokumen_admin(dp):
            tambah("Dokumen Administrasi", textwrap.shorten(d["uraian"], 72, placeholder="..."),
                   f"dokumen_admin:{d['huruf']}",
                   d["uraian"], dp_nama, f"LDP butir 6.{d['huruf']}", d["uraian"],
                   {"huruf": d["huruf"]})

        no, baris = _baris(dp, r"Kekayaan bersih perusahaan paling sedikit")
        if baris:
            nilai = parse_rupiah(baris)
            tambah("Kualifikasi", "Kekayaan bersih minimum", "kekayaan_bersih",
                   f"Kekayaan bersih paling sedikit {rupiah(nilai)}.", dp_nama, "LDK B.1", baris,
                   {"nilai": nilai})

        no, baris = _baris(dp, r"tenaga ahli tetap paling sedikit")
        if baris:
            m = re.search(r"paling sedikit\s+(\d+)", baris)
            tambah("Personil", "Jumlah tenaga ahli tetap", "tenaga_ahli_tetap",
                   f"Memiliki tenaga ahli tetap paling sedikit {m.group(1) if m else '?'} orang.",
                   dp_nama, "LDK B.2", baris, {"nilai": int(m.group(1)) if m else None})

        no, baris = _baris(dp, r"tidak boleh melebihi nilai HPS")
        if baris:
            nilai = parse_rupiah(baris)
            tambah("Pagu", "Batas penawaran terhadap HPS", "batas_hps",
                   "Nilai penawaran tidak boleh melebihi HPS.", dp_nama, "LDP 8.1", baris, {"nilai": nilai})

        no, baris = _baris(dp, r"ditutup pada")
        if baris:
            tgl = parse_tanggal(baris)
            m = re.search(r"pukul\s+(\d{2})\.(\d{2})", baris)
            zona = next((z for z in ("WIB", "WITA", "WIT") if re.search(rf"\b{z}\b", baris)), None)
            tambah("Jadwal", "Batas akhir pemasukan penawaran", "batas_penawaran",
                   f"Pemasukan penawaran ditutup {baris.split('pada', 1)[1].strip()}.",
                   dp_nama, "LDP 9.1", baris,
                   {"tanggal": tgl.isoformat() if tgl else None,
                    "jam": f"{m.group(1)}.{m.group(2)}" if m else None,
                    "zona_waktu": zona})

    # ---------- Jadwal ----------
    bagian_i, baris_i = _bagian(kak, "I") if kak else ("", 0)
    jadwal = _ekstrak_jadwal(bagian_i, baris_i) if bagian_i else []

    # ---------- Verifikasi kutipan (anti-halusinasi) ----------
    for nama, teks in dokumen.items():
        if len(teks.strip()) < 200:
            peringatan.append({
                "jenis": "dokumen_tidak_terbaca",
                "dokumen": nama,
                "pesan": f"Dokumen {nama} hanya memuat {len(teks.strip())} karakter. "
                         f"Kemungkinan hasil pindai tanpa lapisan teks. Agen tidak menebak isinya.",
            })

    semua_teks = normal(" ".join(dokumen.values()))
    for s in persyaratan:
        kutipan = normal(s["sumber"]["kutipan"])
        s["kutipan_terverifikasi"] = bool(kutipan) and kutipan in semua_teks

    peringatan.extend(deteksi_instruksi_tersisip(dokumen))

    batas = next((s for s in persyaratan if s["kunci"] == "batas_penawaran"), None)
    pagu = next((s for s in persyaratan if s["kunci"] == "pagu_anggaran"), None)

    return {
        "meta": {
            "diekstrak_pada": cap_waktu(),
            "dokumen_dibaca": list(dokumen.keys()),
            "jumlah_persyaratan": len(persyaratan),
            "jumlah_persyaratan_terverifikasi": sum(1 for s in persyaratan if s["kutipan_terverifikasi"]),
            "pagu_anggaran": (pagu or {}).get("parameter", {}).get("nilai"),
            "batas_penawaran": (batas or {}).get("parameter", {}).get("tanggal"),
        },
        "persyaratan": persyaratan,
        "jadwal": jadwal,
        "peringatan": peringatan,
    }
