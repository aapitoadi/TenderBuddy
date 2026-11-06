"""TenderBuddy - orkestrator alur kerja agen.

Alur: baca paket -> ekstraksi bersumber -> cocokkan profil -> keputusan ->
usulan tindakan -> MENUNGGU PERSETUJUAN MANUSIA -> berkas administrasi.

Tidak ada berkas penawaran yang ditulis sebelum persetujuan dicatat.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date, datetime
from pathlib import Path

from utilitas import LogAudit, cap_waktu, muat_json, rupiah, tulis_json, normal
from ekstraksi import baca_paket, ekstrak
from pencocokan import cocokkan, periksa_jadwal, BATAS_PAGU_KECIL
import draf_dokumen as draf

AKAR = Path(__file__).resolve().parent.parent
PAKET = AKAR / "input" / "paket_tender"
PROFIL = AKAR / "input" / "profil_perusahaan" / "profil_perusahaan.json"
KELUARAN = AKAR / "output"
BERKAS = KELUARAN / "03_berkas_penawaran"
USULAN_DIR = KELUARAN / "usulan"
AUDIT = KELUARAN / "05_log_audit.jsonl"

NAMA_PAKET_DEFAULT = "Pembangunan Gedung Serbaguna Kelurahan Sukamaju"
KODE_PAKET_DEFAULT = "4411023"
NAMA_PAKET = NAMA_PAKET_DEFAULT
KODE_PAKET = KODE_PAKET_DEFAULT


# --------------------------------------------------------------------------- #
# Keputusan dan risiko
# --------------------------------------------------------------------------- #

def putuskan(matriks: list[dict]) -> str:
    if any(m["status"] == "tidak_memenuhi" for m in matriks):
        return "TIDAK LOLOS"
    kritis = [m for m in matriks if m["status"] == "kurang_dokumen" and m["tingkat"] == "tinggi"]
    if kritis:
        return "LOLOS BERSYARAT"
    return "LOLOS"


def susun_risiko(matriks: list[dict], catatan_jadwal: list[dict], peringatan: list[dict]) -> list[dict]:
    risiko = []
    for m in matriks:
        if m["status"] == "memenuhi":
            continue
        if m["status"] == "tidak_memenuhi":
            risiko.append({"tingkat": "tinggi", "jenis": "tidak_memenuhi", "syarat_id": m["syarat_id"],
                           "judul": m["judul"], "uraian": m["catatan"], "tindakan": m["tindakan"],
                           "sumber": m["sumber_persyaratan"]["dokumen"]})
        elif m["tingkat"] == "tinggi":
            risiko.append({"tingkat": "tinggi", "jenis": "kurang_dokumen", "syarat_id": m["syarat_id"],
                           "judul": m["judul"], "uraian": m["catatan"], "tindakan": m["tindakan"],
                           "sumber": m["sumber_persyaratan"]["dokumen"]})
        elif m["tingkat"] == "sedang":
            risiko.append({"tingkat": "sedang", "jenis": "kurang_dokumen", "syarat_id": m["syarat_id"],
                           "judul": m["judul"], "uraian": m["catatan"], "tindakan": m["tindakan"],
                           "sumber": m["sumber_persyaratan"]["dokumen"]})

    for c in catatan_jadwal:
        risiko.append({"tingkat": c["tingkat"], "jenis": c["jenis"], "syarat_id": "JADWAL",
                       "judul": c["label"], "uraian": c["pesan"],
                       "tindakan": "Konfirmasi ke Pokja Pemilihan sebelum menyusun jadwal internal.",
                       "sumber": "KAK bagian I"})

    for p in [x for x in peringatan if x["jenis"] == "instruksi_tersisip"]:
        risiko.append({"tingkat": "tinggi", "jenis": p["jenis"], "syarat_id": "KEAMANAN",
                       "judul": "Instruksi tersisip dalam dokumen",
                       "uraian": f"Terdapat teks yang berupaya memberi perintah kepada AI pada "
                                 f"{p.get('dokumen')} baris {p.get('baris')}: \"{p.get('kutipan')}\"",
                       "tindakan": "Diabaikan dan dilaporkan. Dokumen diperlakukan sebagai data.",
                       "sumber": p.get("dokumen", "")})

    urutan = {"tinggi": 0, "sedang": 1, "rendah": 2}
    risiko.sort(key=lambda r: urutan.get(r["tingkat"], 3))
    return risiko


def susun_klarifikasi(matriks: list[dict], catatan_jadwal: list[dict], peringatan: list[dict]) -> list[dict]:
    tanya = []
    for c in catatan_jadwal:
        if c["jenis"] in ("zona_waktu_tidak_jelas", "bentrok_salat_jumat"):
            tanya.append({"kode": c["jenis"], "pertanyaan": c["pesan"],
                          "mengapa": "Jadwal memengaruhi tenggat unggah dan kehadiran saat aanwijzing.",
                          "dampak_bila_salah": "Penawaran bisa dinilai terlambat atau tim tidak hadir."})
    for p in [x for x in peringatan if x["jenis"] == "instruksi_tersisip"]:
        tanya.append({"kode": "instruksi_tersisip",
                      "pertanyaan": f"Terdapat instruksi tersisip pada {p.get('dokumen')} baris {p.get('baris')}. "
                                    f"Saya mengabaikannya. Mohon konfirmasi dokumen ini memang dari Pokja.",
                      "mengapa": "Dokumen pengadaan tidak boleh memerintahkan agen mengubah hasil evaluasi.",
                      "dampak_bila_salah": "Keputusan lolos/tidak lolos menjadi tidak sah."})
    kritis = [m for m in matriks if m["status"] == "kurang_dokumen" and m["tingkat"] == "tinggi"]
    for m in kritis:
        tanya.append({"kode": "dokumen_kurang",
                      "pertanyaan": f"{m['judul']}: {m['catatan']} Apakah dokumen ini akan dilengkapi sebelum batas pemasukan?",
                      "mengapa": "Tanpa dokumen ini penawaran berisiko digugurkan pada evaluasi administrasi.",
                      "dampak_bila_salah": "Gugur di tahap evaluasi administrasi."})
    return tanya


# --------------------------------------------------------------------------- #
# Penulisan laporan
# --------------------------------------------------------------------------- #

def _md_tabel(header: list[str], baris: list[list[str]]) -> str:
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    for b in baris:
        out.append("| " + " | ".join(str(x).replace("|", "\\|") for x in b) + " |")
    return "\n".join(out)


def tulis_checklist(hasil: dict) -> Path:
    path = KELUARAN / "01_checklist_persyaratan.json"
    tulis_json(path, hasil)
    return path


def tulis_matriks(hasil: dict, hasil_cocok: dict, verdict: str, catatan_jadwal: list[dict]) -> Path:
    baris = []
    for m in hasil_cocok["matriks"]:
        bukti = m["bukti"][0]["nilai"] if m["bukti"] else "—"
        baris.append([m["syarat_id"], m["kategori"], m["judul"][:60], m["label_status"],
                      m["tingkat"], bukti[:70], m["sumber_persyaratan"]["dokumen"]])
    isi = [
        "# Matriks Kepatuhan - " + NAMA_PAKET,
        "",
        f"Kode paket: {KODE_PAKET}  ",
        f"Disusun: {cap_waktu()}  ",
        f"**Keputusan agen: {verdict}**",
        "",
        "## Ringkasan",
        "",
        _md_tabel(["Status", "Jumlah"], [
            ["Memenuhi", hasil_cocok["ringkasan"]["memenuhi"]],
            ["Tidak memenuhi", hasil_cocok["ringkasan"]["tidak_memenuhi"]],
            ["Kurang dokumen", hasil_cocok["ringkasan"]["kurang_dokumen"]],
            ["Total diperiksa", hasil_cocok["ringkasan"]["total"]],
        ]),
        "",
        "## Rincian per persyaratan",
        "",
        _md_tabel(["ID", "Kategori", "Persyaratan", "Status", "Tingkat", "Bukti utama", "Sumber"], baris),
        "",
        "## Catatan jadwal",
        "",
    ]
    if catatan_jadwal:
        isi += [f"- **{c['jenis']}** - {c['pesan']}" for c in catatan_jadwal]
    else:
        isi.append("- Tidak ada anomali jadwal.")
    isi += ["", "> Setiap baris dapat dilacak ke dokumen sumber pada kolom terakhir.", ""]
    path = KELUARAN / "02_matriks_kepatuhan.md"
    path.write_text("\n".join(isi), encoding="utf-8")
    tulis_json(KELUARAN / "02_matriks.json", hasil_cocok["matriks"])
    return path


def tulis_klarifikasi(tanya: list[dict]) -> Path:
    isi = ["# Pertanyaan Klarifikasi untuk Pengguna", "",
           "Agen berhenti dan bertanya sebelum menyusun berkas, karena butir berikut mengubah hasil.", ""]
    if not tanya:
        isi.append("Tidak ada pertanyaan. Seluruh butir dapat diputuskan dari dokumen yang tersedia.")
    for i, t in enumerate(tanya, start=1):
        isi += [f"## {i}. {t['kode'].replace('_', ' ').title()}", "",
                f"**Pertanyaan:** {t['pertanyaan']}", "",
                f"**Mengapa ditanyakan:** {t['mengapa']}", "",
                f"**Risiko bila salah:** {t['dampak_bila_salah']}", ""]
    path = KELUARAN / "00_pertanyaan_klarifikasi.md"
    path.write_text("\n".join(isi), encoding="utf-8")
    return path


def tulis_risiko_md(paket: str, verdict: str, risiko: list[dict], ringkasan: dict) -> Path:
    baris = [[i, r["tingkat"].upper(), r["judul"][:50], r["uraian"][:100], r["tindakan"][:80]]
             for i, r in enumerate(risiko, start=1)]
    isi = ["# Lembar Ringkasan Risiko", "",
           f"**Paket:** {paket}  ",
           f"**Status:** {verdict}  ",
           f"**Disusun:** {cap_waktu()}",
           "",
           f"{ringkasan['total']} persyaratan diperiksa: {ringkasan['memenuhi']} memenuhi, "
           f"{ringkasan['tidak_memenuhi']} tidak memenuhi, {ringkasan['kurang_dokumen']} kurang dokumen.",
           ""]
    if risiko:
        isi.append(_md_tabel(["No", "Tingkat", "Persyaratan", "Temuan", "Tindakan"], baris))
    else:
        isi.append("Tidak ditemukan risiko.")
    path = KELUARAN / "04_ringkasan_risiko.md"
    path.write_text("\n".join(isi), encoding="utf-8")
    return path


# --------------------------------------------------------------------------- #
# Alur utama
# --------------------------------------------------------------------------- #

def _sidik(matriks: list[dict]) -> str:
    inti = json.dumps([(m["syarat_id"], m["status"]) for m in matriks], sort_keys=True)
    return hashlib.sha256(inti.encode()).hexdigest()[:16]


def _info_paket(dokumen: dict[str, str]) -> tuple[str, str, str]:
    """Ambil nama, kode, dan lokasi paket dari teks KAK."""
    import re as _re
    teks = " ".join(dokumen.values())
    # Kode paket
    m_kode = _re.search(r"Kode Paket\s*:?\s*(\d+)", teks)
    kode = m_kode.group(1) if m_kode else KODE_PAKET_DEFAULT
    # Nama paket: baris setelah "KERANGKA ACUAN KERJA" header
    nama = NAMA_PAKET_DEFAULT
    for nama_file, isi in dokumen.items():
        baris = isi.splitlines()
        if "KERANGKA ACUAN KERJA" in baris[0].upper() if baris else False:
            if len(baris) > 1 and baris[1].strip():
                nama = baris[1].strip()
            break
    # Lokasi: cari "Kota <nama>" atau "Kabupaten <nama>" per baris dokumen
    lokasi = "Balikpapan"
    for isi in dokumen.values():
        for baris in isi.splitlines():
            baris = baris.strip()
            for z in ("Kota", "Kabupaten"):
                m = _re.search(rf"{z}\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b", baris)
                if m:
                    lokasi = f"{z} {m.group(1)}"
                    break
            if lokasi != "Balikpapan":
                break
        if lokasi != "Balikpapan":
            break
    return nama, kode, lokasi


def rencana(dir_paket: Path = PAKET, path_profil: Path = PROFIL, keluar: Path = KELUARAN) -> dict:
    global KELUARAN, BERKAS, USULAN_DIR, NAMA_PAKET, KODE_PAKET
    KELUARAN, BERKAS, USULAN_DIR = keluar, keluar / "03_berkas_penawaran", keluar / "usulan"

    audit = LogAudit(keluar / "05_log_audit.jsonl")
    audit.catat("agen", "baca_paket", dir_paket.name, "berhasil", str(dir_paket))

    dokumen = baca_paket(dir_paket)
    NAMA_PAKET, KODE_PAKET, LOKASI_PAKET = _info_paket(dokumen)
    hasil = ekstrak(dokumen)
    audit.catat("agen", "ekstraksi_persyaratan", f"{hasil['meta']['jumlah_persyaratan']} butir",
                f"{hasil['meta']['jumlah_persyaratan_terverifikasi']} kutipan terverifikasi",
                ", ".join(hasil["meta"]["dokumen_dibaca"]))

    for p in hasil["peringatan"]:
        if p["jenis"] == "instruksi_tersisip":
            audit.catat("agen", "instruksi_tersisip_diabaikan",
                        f"{p['dokumen']} baris {p.get('baris', '-')}", "diabaikan", p["kutipan"])
        elif p["jenis"] == "dokumen_tidak_terbaca":
            audit.catat("agen", "dokumen_tidak_terbaca", p.get("dokumen", "-"), "agen berhenti membaca",
                        p.get("pesan", ""))

    profil = muat_json(path_profil)
    audit.catat("agen", "muat_profil", profil["perusahaan"]["nama"], f"versi {profil['meta']['versi']}", str(path_profil))

    batas = hasil["meta"].get("batas_penawaran")
    acuan = date.fromisoformat(batas) if batas else date.today()

    hasil_cocok = cocokkan(hasil, profil, acuan)
    verdict = putuskan(hasil_cocok["matriks"])
    catatan_jadwal = periksa_jadwal(hasil["jadwal"])
    risiko = susun_risiko(hasil_cocok["matriks"], catatan_jadwal, hasil["peringatan"])
    tanya = susun_klarifikasi(hasil_cocok["matriks"], catatan_jadwal, hasil["peringatan"])

    tulis_checklist(hasil)
    tulis_matriks(hasil, hasil_cocok, verdict, catatan_jadwal)
    tulis_klarifikasi(tanya)

    id_usulan = "USL-" + datetime.now().strftime("%Y%m%d-%H%M%S")
    tindakan = []
    if verdict != "TIDAK LOLOS":
        tindakan = [
            {"aksi": "tulis", "berkas": "01_Surat_Penawaran.docx",
             "keterangan": "Nilai penawaran dikosongkan untuk keputusan direktur."},
            {"aksi": "tulis", "berkas": "02_Pakta_Integritas.docx",
             "keterangan": "Pernyataan komitmen direktur."},
            {"aksi": "tulis", "berkas": "03_Daftar_Personil_Inti.docx",
             "keterangan": "Dipetakan ke syarat KAK, termasuk kekurangan sertifikat."},
            {"aksi": "tulis", "berkas": "04_Tabel_Pengalaman_Sejenis.docx",
             "keterangan": "Pengalaman subkontraktor dikecualikan."},
            {"aksi": "tulis", "berkas": "05_Lembar_Ringkasan_Risiko.docx",
             "keterangan": "Ringkasan temuan dan tindakan."},
        ]

    usulan = {
        "id": id_usulan,
        "dibuat": cap_waktu(),
        "paket": {"nama": NAMA_PAKET, "kode": KODE_PAKET,
                  "lokasi": LOKASI_PAKET,
                  "pagu": hasil["meta"]["pagu_anggaran"],
                  "batas_penawaran": batas},
        "verdict": verdict,
        "ringkasan": hasil_cocok["ringkasan"],
        "risiko": risiko,
        "klarifikasi": tanya,
        "peringatan_dokumen": hasil["peringatan"],
        "tindakan": tindakan,
        "tidak_akan_dilakukan": [
            "Mengunggah berkas ke LPSE",
            "Menetapkan nilai penawaran",
            "Mengisi nomor sertifikat atau dokumen yang belum terbit",
            "Menandatangani dokumen atas nama direktur",
        ],
        "sidik_jari": _sidik(hasil_cocok["matriks"]),
        "status": "menunggu_persetujuan",
    }
    tulis_json(USULAN_DIR / f"{id_usulan}.json", usulan)
    audit.catat("agen", "usulan_dibuat", id_usulan,
                f"{verdict}; {len(tindakan)} tindakan menunggu persetujuan",
                detail={"sidik_jari": usulan["sidik_jari"]})
    return usulan


def setujui(id_usulan: str, keluar: Path = KELUARAN, paksa: bool = False,
            path_profil: Path = PROFIL) -> dict:
    global KELUARAN, BERKAS, USULAN_DIR, NAMA_PAKET, KODE_PAKET
    KELUARAN, BERKAS, USULAN_DIR = keluar, keluar / "03_berkas_penawaran", keluar / "usulan"
    audit = LogAudit(keluar / "05_log_audit.jsonl")

    path = USULAN_DIR / f"{id_usulan}.json"
    if not path.exists():
        raise SystemExit(f"Usulan {id_usulan} tidak ditemukan.")
    usulan = muat_json(path)

    NAMA_PAKET = usulan["paket"].get("nama", NAMA_PAKET)
    KODE_PAKET = usulan["paket"].get("kode", KODE_PAKET)
    LOKASI_PAKET = usulan["paket"].get("lokasi", "Balikpapan")

    if usulan["verdict"] == "TIDAK LOLOS" and not paksa:
        audit.catat("agen", "tolak_eksekusi", id_usulan,
                    "dibatalkan: keputusan TIDAK LOLOS", "gerbang kepatuhan")
        raise SystemExit(
            "DITOLAK: keputusan agen untuk paket ini adalah TIDAK LOLOS. "
            "Berkas penawaran tidak disusun. Perbaiki butir yang tidak memenuhi terlebih dahulu.")

    profil = muat_json(path_profil)
    hasil = muat_json(KELUARAN / "01_checklist_persyaratan.json")
    matriks = [m for m in muat_json(KELUARAN / "02_matriks.json")] if (KELUARAN / "02_matriks.json").exists() else None
    if matriks is None:
        # rekonstruksi dari checklist + profil agar tetap deterministik
        batas = hasil["meta"].get("batas_penawaran")
        acuan = date.fromisoformat(batas) if batas else date.today()
        matriks = cocokkan(hasil, profil, acuan)["matriks"]

    berkas = []
    berkas.append(draf.surat_penawaran(BERKAS / "01_Surat_Penawaran.docx", profil, hasil,
                                       NAMA_PAKET, KODE_PAKET, LOKASI_PAKET))
    berkas.append(draf.pakta_integritas(BERKAS / "02_Pakta_Integritas.docx", profil, LOKASI_PAKET))
    berkas.append(draf.daftar_personil(BERKAS / "03_Daftar_Personil_Inti.docx", profil, matriks,
                                       NAMA_PAKET, KODE_PAKET, LOKASI_PAKET))
    berkas.append(draf.tabel_pengalaman(BERKAS / "04_Tabel_Pengalaman_Sejenis.docx", profil, matriks,
                                        NAMA_PAKET, KODE_PAKET))
    berkas.append(draf.lembar_risiko(BERKAS / "05_Lembar_Ringkasan_Risiko.docx",
                                     NAMA_PAKET, usulan["verdict"], usulan["risiko"], usulan["ringkasan"]))
    tulis_risiko_md(NAMA_PAKET, usulan["verdict"], usulan["risiko"], usulan["ringkasan"])

    usulan["status"] = "disetujui"
    usulan["disetujui_pada"] = cap_waktu()
    usulan["berkas_dihasilkan"] = [b.name for b in berkas]
    tulis_json(path, usulan)

    for b in berkas:
        audit.catat("agen", "tulis_berkas", b.name, "berhasil", "persetujuan " + id_usulan)
    audit.catat("manusia", "setujui_usulan", id_usulan, "disetujui",
                detail={"sidik_jari": usulan["sidik_jari"]})
    return usulan


def tolak(id_usulan: str, alasan: str, keluar: Path = KELUARAN) -> dict:
    path = keluar / "usulan" / f"{id_usulan}.json"
    usulan = muat_json(path)
    usulan["status"] = "ditolak"
    usulan["alasan_penolakan"] = alasan
    usulan["ditolak_pada"] = cap_waktu()
    tulis_json(path, usulan)
    LogAudit(keluar / "05_log_audit.jsonl").catat("manusia", "tolak_usulan", id_usulan, alasan)
    return usulan


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def _cetak_ringkas(usulan: dict) -> None:
    print()
    print("=" * 78)
    print(f"  TenderBuddy  |  {usulan['paket']['nama']}")
    print("=" * 78)
    r = usulan["ringkasan"]
    print(f"  Keputusan        : {usulan['verdict']}")
    print(f"  Persyaratan      : {r['total']} diperiksa | {r['memenuhi']} memenuhi | "
          f"{r['tidak_memenuhi']} tidak memenuhi | {r['kurang_dokumen']} kurang dokumen")
    print(f"  Pagu paket       : {rupiah(usulan['paket']['pagu'] or 0)}")
    print(f"  Batas penawaran  : {usulan['paket']['batas_penawaran']}")
    print()

    if usulan["klarifikasi"]:
        print("  PERLU KLARIFIKASI")
        for t in usulan["klarifikasi"]:
            print(f"   - {t['pertanyaan'][:110]}")
        print()

    print("  RISIKO UTAMA")
    for r_ in usulan["risiko"][:6]:
        print(f"   [{r_['tingkat'].upper():7}] {r_['judul'][:40]:42} {r_['uraian'][:60]}")
    print()

    if usulan["tindakan"]:
        print("  RENCANA TINDAKAN (belum dijalankan, menunggu persetujuan)")
        for t in usulan["tindakan"]:
            print(f"   + {t['berkas']}")
    else:
        print("  TIDAK ADA TINDAKAN. Paket tidak memenuhi syarat, berkas tidak akan disusun.")
    print()
    print("  AGEN TIDAK AKAN: " + "; ".join(usulan["tidak_akan_dilakukan"]))
    print()
    print(f"  ID usulan: {usulan['id']}   sidik jari: {usulan['sidik_jari']}")
    print("  Setujui : python src/pipeline.py setujui --id " + usulan["id"])
    print("  Tolak   : python src/pipeline.py tolak --id " + usulan["id"] + " --alasan \"...\"")
    print("=" * 78)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="TenderBuddy - agen berkas penawaran LPSE")
    sub = p.add_subparsers(dest="perintah", required=True)

    r = sub.add_parser("rencana", help="baca paket, nilai, dan ajukan rencana tindakan")
    r.add_argument("--paket", default=str(PAKET))
    r.add_argument("--profil", default=str(PROFIL))

    s = sub.add_parser("setujui", help="jalankan rencana yang sudah disetujui")
    s.add_argument("--id", required=True)
    s.add_argument("--paksa", action="store_true")

    t = sub.add_parser("tolak", help="tolak usulan dan catat alasannya")
    t.add_argument("--id", required=True)
    t.add_argument("--alasan", required=True)

    args = p.parse_args(argv)

    if args.perintah == "rencana":
        usulan = rencana(Path(args.paket), Path(args.profil))
        _cetak_ringkas(usulan)
        return 0
    if args.perintah == "setujui":
        usulan = setujui(args.id, paksa=args.paksa)
        print(f"Disetujui. {len(usulan['berkas_dihasilkan'])} berkas ditulis ke output/03_berkas_penawaran/")
        for b in usulan["berkas_dihasilkan"]:
            print("  - " + b)
        return 0
    if args.perintah == "tolak":
        tolak(args.id, args.alasan)
        print(f"Usulan {args.id} ditolak. Tidak ada berkas yang ditulis.")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
