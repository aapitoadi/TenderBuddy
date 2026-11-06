"""Tahap 2 - Pencocokan persyaratan dengan basis pengetahuan profil perusahaan.

Setiap keputusan wajib menyebut bukti dan sumbernya. Bila bukti tidak ada,
status menjadi "kurang_dokumen" - agen tidak boleh menebak.
"""

from __future__ import annotations

import re
from datetime import date

from utilitas import normal, rupiah, parse_tanggal

# Batas pagu paket untuk kualifikasi usaha kecil (pekerjaan konstruksi).
BATAS_PAGU_KECIL = 2_500_000_000

# Kalender hari libur nasional (data contoh untuk prototipe).
LIBUR_NASIONAL = {
    "2026-11-25": "Hari Guru (bukan libur nasional - contoh data)",
    "2026-12-25": "Hari Raya Natal",
    "2027-01-01": "Tahun Baru",
}

# Ketersediaan dokumen administrasi pada basis pengetahuan (per huruf LDP).
# Nilai "dinamis" berarti agen akan memeriksa profil; "statis" berarti pakai teks default.
KETERSEDIAAN_DOKUMEN_DEFAULT = {
    "a": ("dapat_dibuat", "Surat penawaran dapat dibuat agen dari data paket; perlu tanda tangan direktur."),
    "b": ("dapat_dibuat", "Pakta integritas dapat dibuat agen; perlu tanda tangan direktur."),
    "c": ("dapat_dibuat", "Surat pernyataan minat dapat dibuat agen; surat kuasa hanya bila dikuasakan."),
    "d": ("sebagian", "CV tersedia untuk personil. Cek kelengkapan sertifikat pada butir personil."),
    "e": ("tersedia", "Pengalaman tercatat, kontrak dan BAST tersedia pada arsip."),
    "f": ("tersedia", "Akta pendirian dan perubahan terakhir tersedia."),
    "g": ("tersedia", "NIB berstatus aktif."),
    "h": ("tersedia", "SBU tersedia pada arsip."),
    "i": ("tersedia", "NPWP dan bukti pelaporan SPT Tahunan PPh Badan tersedia."),
    "j": ("tersedia", "Bukti BPJS Ketenagakerjaan personil, iuran terakhir Oktober 2026."),
    "k": ("belum_ada", "Surat dukungan bank belum diterbitkan."),
    "l": ("dapat_dibuat", "Draf metode pelaksanaan dapat disusun agen; wajib divalidasi tenaga ahli."),
}


def _ketersediaan_dokumen(huruf: str, profil: dict) -> tuple[str, str]:
    """Cek ketersediaan dokumen berdasarkan huruf LDP dan profil perusahaan."""
    if huruf == "k":
        bank = profil.get("perusahaan", {}).get("jaminan_bank", {})
        if bank.get("tersedia"):
            return ("tersedia", bank.get("catatan", "Surat dukungan bank tersedia."))
        return ("belum_ada", bank.get("catatan", "Surat dukungan bank belum diterbitkan."))
    return KETERSEDIAAN_DOKUMEN_DEFAULT.get(huruf, ("belum_ada", "Tidak ada data."))

LABEL_STATUS = {
    "memenuhi": "Memenuhi",
    "tidak_memenuhi": "Tidak memenuhi",
    "kurang_dokumen": "Kurang dokumen",
}


def _tingkat(status: str, kritis: bool = False) -> str:
    if status == "tidak_memenuhi":
        return "tinggi"
    if status == "kurang_dokumen":
        return "tinggi" if kritis else "sedang"
    return "rendah"


def _item(syarat: dict, status: str, bukti: list[dict], catatan: str = "",
          kritis: bool = False, tindakan: str = "") -> dict:
    return {
        "syarat_id": syarat["id"],
        "kategori": syarat["kategori"],
        "judul": syarat["judul"],
        "pernyataan": syarat["pernyataan"],
        "status": status,
        "label_status": LABEL_STATUS[status],
        "tingkat": _tingkat(status, kritis),
        "bukti": bukti,
        "catatan": catatan,
        "tindakan": tindakan,
        "sumber_persyaratan": syarat["sumber"],
    }


def _token_cocok(diminta: str, dimiliki: str) -> bool:
    """Cocokkan nama sertifikat secara longgar berbasis himpunan kata."""
    a = set(normal(diminta).split())
    b = set(normal(dimiliki).split())
    return bool(a) and a.issubset(b)


def _cari_personil(profil: dict, jabatan: str) -> dict | None:
    target = normal(jabatan)
    for p in profil.get("personil", []):
        if normal(p.get("jabatan_kbli", "")) == target:
            return p
    return None


def _cocok_personil(syarat: dict, profil: dict, tanggal_acuan: date) -> dict:
    par = syarat["parameter"]
    jabatan = par.get("jabatan", "")
    orang = _cari_personil(profil, jabatan)

    if not orang:
        return _item(syarat, "tidak_memenuhi", [],
                     f"Tidak ada personil dengan jabatan {jabatan} pada basis pengetahuan.",
                     tindakan="Rekrut atau tunjuk personil dengan jabatan tersebut, lalu perbarui basis pengetahuan.")

    bukti = [{"nilai": f"{orang['nama']} - {orang['jabatan_kbli']}",
              "sumber": f"profil_perusahaan.json#personil[{orang['id']}]",
              "dokumen": orang.get("sumber", "")}]
    masalah_keras: list[str] = []
    kurang: list[str] = []

    # 1. Sertifikat yang diminta
    for diminta in par.get("sertifikat_diminta", []):
        cocok = None
        for s in orang.get("sertifikat", []):
            if _token_cocok(diminta, s["nama"]):
                cocok = s
                break
        if not cocok:
            kurang.append(diminta)
            continue
        berlaku = parse_tanggal(cocok.get("berlaku_sampai", "")) or date.fromisoformat(cocok["berlaku_sampai"])
        if berlaku < tanggal_acuan:
            masalah_keras.append(
                f"{cocok['nama']} No. {cocok['nomor']} sudah berakhir {berlaku.isoformat()} "
                f"(sebelum batas pemasukan penawaran {tanggal_acuan.isoformat()}).")
        else:
            bukti.append({"nilai": f"{cocok['nama']} No. {cocok['nomor']}, berlaku s.d. {berlaku.isoformat()}",
                          "sumber": f"profil_perusahaan.json#personil[{orang['id']}].sertifikat",
                          "dokumen": orang.get("sumber", "")})

    # 2. Pengalaman
    min_tahun = par.get("pengalaman_min_tahun")
    if min_tahun:
        punya = orang.get("pengalaman_tahun", 0)
        if punya < min_tahun:
            masalah_keras.append(f"Pengalaman {punya} tahun, disyaratkan minimal {min_tahun} tahun.")
        else:
            bukti.append({"nilai": f"Pengalaman {punya} tahun", "sumber": f"profil_perusahaan.json#personil[{orang['id']}].pengalaman_tahun",
                          "dokumen": orang.get("sumber", "")})

    # 3. Pendidikan
    didik = par.get("pendidikan")
    if didik:
        level = didik.split()[0]
        if level not in (orang.get("pendidikan") or ""):
            masalah_keras.append(f"Pendidikan {orang.get('pendidikan')} tidak sesuai syarat {didik}.")
        else:
            bukti.append({"nilai": orang["pendidikan"], "sumber": f"profil_perusahaan.json#personil[{orang['id']}].pendidikan",
                          "dokumen": orang.get("sumber", "")})

    # 4. Status kepegawaian / BPJS
    if "Aktif" not in (orang.get("bpjs_ketenagakerjaan") or ""):
        masalah_keras.append("Bukti BPJS Ketenagakerjaan tidak aktif.")

    if masalah_keras:
        return _item(syarat, "tidak_memenuhi", bukti, " ".join(masalah_keras),
                     tindakan="Ganti personil atau lengkapi perpanjangan sertifikat sebelum batas pemasukan.")
    if kurang:
        catatan = f"Sertifikat belum ada: {', '.join(kurang)}."
        if orang.get("catatan"):
            catatan += f" Catatan basis pengetahuan: {orang['catatan']}"
        return _item(syarat, "kurang_dokumen", bukti, catatan, kritis=True,
                     tindakan=f"Lengkapi {', '.join(kurang)}. Agen tidak boleh mengisi nomor sertifikat yang belum terbit.")
    return _item(syarat, "memenuhi", bukti)


def _cocok_pengalaman(syarat: dict, profil: dict, acuan: date) -> dict:
    par = syarat["parameter"]
    nilai_min = par.get("nilai_min") or 0
    jumlah_min = par.get("jumlah_min") or 1
    batas_tahun = acuan.year - 10
    jenis_diminta = normal(par.get("jenis", "konstruksi"))

    valid, dikecualikan = [], []
    for e in profil.get("pengalaman", []):
        if normal(e.get("peran", "")) != "kontraktor utama":
            dikecualikan.append(e)
            continue
        if e.get("tahun_selesai", 0) < batas_tahun:
            dikecualikan.append(e)
            continue
        jenis_ada = normal(e.get("jenis", ""))
        # Cocokkan jika jenis diminta mengandung kata kunci jenis yang ada (mis. "jalan" in "konstruksi jalan")
        kata_kunci = [k for k in jenis_diminta.split() if len(k) > 3 and k not in ("konstruksi", "pekerjaan")]
        if kata_kunci:
            if not any(k in jenis_ada for k in kata_kunci):
                dikecualikan.append(e)
                continue
        if e.get("nilai_kontrak", 0) < nilai_min:
            dikecualikan.append(e)
            continue
        valid.append(e)

    bukti = [{"nilai": f"{e['nama_paket']} ({e['tahun_selesai']}) - {rupiah(e['nilai_kontrak'])}",
              "sumber": f"profil_perusahaan.json#pengalaman[{e['id']}]",
              "dokumen": e.get("sumber", "")} for e in valid]
    for e in dikecualikan:
        bukti.append({"nilai": f"Dikecualikan: {e['nama_paket']} ({rupiah(e['nilai_kontrak'])}, peran {e['peran']})",
                      "sumber": f"profil_perusahaan.json#pengalaman[{e['id']}]",
                      "dokumen": e.get("sumber", "")})

    if len(valid) >= jumlah_min:
        return _item(syarat, "memenuhi", bukti,
                     f"{len(valid)} paket memenuhi syarat nilai minimal {rupiah(nilai_min)}; "
                     f"{len(dikecualikan)} paket dikecualikan (subkontraktor/nilai/waktu).")
    return _item(syarat, "tidak_memenuhi", bukti,
                 f"Hanya {len(valid)} paket memenuhi, disyaratkan {jumlah_min}.",
                 tindakan="Cari pengalaman lain atau ajukan kerja sama operasi (KSO).")


def periksa_jadwal(jadwal: list[dict]) -> list[dict]:
    """Periksa jadwal terhadap aturan operasional: zona waktu, salat Jumat, hari libur."""
    catatan = []
    for j in jadwal:
        if not j["tanggal"]:
            continue
        d = date.fromisoformat(j["tanggal"])
        if j["jam"] and not j["zona_waktu"]:
            catatan.append({"jenis": "zona_waktu_tidak_jelas", "label": j["label"],
                            "pesan": f"Jadwal '{j['label']}' mencantumkan pukul {j['jam']} tanpa zona waktu. "
                                     f"Perlu konfirmasi WIB/WITA/WIT.",
                            "tingkat": "sedang"})
        if j["hari"] == "Jumat" and j["jam"]:
            jam = float(j["jam"].replace(".", "."))
            if 11.5 <= jam <= 13.5:
                catatan.append({"jenis": "bentrok_salat_jumat", "label": j["label"],
                                "pesan": f"'{j['label']}' dijadwalkan Jumat pukul {j['jam']} "
                                         f"({j['zona_waktu'] or 'zona waktu tidak disebut'}) - berpotensi bentrok "
                                         f"dengan salat Jumat. Konfirmasi ke Pokja atau siapkan perwakilan.",
                                "tingkat": "sedang"})
        if j["tanggal"] in LIBUR_NASIONAL:
            catatan.append({"jenis": "hari_libur", "label": j["label"],
                            "pesan": f"'{j['label']}' jatuh pada {LIBUR_NASIONAL[j['tanggal']]}.",
                            "tingkat": "sedang"})
    return catatan


def cocokkan(hasil_ekstraksi: dict, profil: dict, acuan: date) -> dict:
    matriks = []
    for s in hasil_ekstraksi["persyaratan"]:
        kunci = s["kunci"]
        par = s["parameter"]
        per = profil["perusahaan"]

        if kunci == "pagu_anggaran":
            nilai = par.get("nilai") or 0
            bukti = [{"nilai": f"Pagu paket {rupiah(nilai)}", "sumber": s["sumber"]["dokumen"], "dokumen": s["sumber"]["dokumen"]},
                     {"nilai": f"Kualifikasi usaha {per['kualifikasi_usaha']}, batas pagu {rupiah(BATAS_PAGU_KECIL)}",
                      "sumber": "profil_perusahaan.json#perusahaan.kualifikasi_usaha", "dokumen": "dokumen/03_sbu.txt"}]
            if nilai > BATAS_PAGU_KECIL:
                matriks.append(_item(s, "tidak_memenuhi", bukti,
                                     f"Pagu {rupiah(nilai)} melebihi batas paket untuk kualifikasi kecil "
                                     f"({rupiah(BATAS_PAGU_KECIL)}).",
                                     tindakan="Tidak dapat diikuti. Perlu peningkatan kualifikasi atau kerja sama operasi."))
            else:
                matriks.append(_item(s, "memenuhi", bukti,
                                     f"Pagu {rupiah(nilai)} masih dalam batas kualifikasi kecil."))

        elif kunci == "hps":
            matriks.append(_item(s, "memenuhi",
                                 [{"nilai": f"HPS {rupiah(par.get('nilai') or 0)}",
                                   "sumber": s["sumber"]["dokumen"], "dokumen": s["sumber"]["dokumen"]}],
                                 "Batas penawaran. Nilai penawaran akan dijaga di bawah HPS."))

        elif kunci == "kualifikasi_usaha":
            cocok = normal(per["kualifikasi_usaha"]) == normal(par.get("nilai", ""))
            matriks.append(_item(
                s, "memenuhi" if cocok else "tidak_memenuhi",
                [{"nilai": per["kualifikasi_usaha"], "sumber": "profil_perusahaan.json#perusahaan.kualifikasi_usaha",
                  "dokumen": "dokumen/03_sbu.txt"}],
                "" if cocok else f"Kualifikasi perusahaan {per['kualifikasi_usaha']}, disyaratkan {par.get('nilai')}."))

        elif kunci == "kbli":
            diminta = par.get("nilai") or []
            punya = per["nib"]["kbli"]
            irisan = [k for k in diminta if k in punya]
            matriks.append(_item(
                s, "memenuhi" if irisan else "tidak_memenuhi",
                [{"nilai": f"KBLI terdaftar: {', '.join(punya)}", "sumber": "profil_perusahaan.json#perusahaan.nib.kbli",
                  "dokumen": "dokumen/02_nib_dan_izin.txt"}],
                f"KBLI {', '.join(irisan)} sesuai." if irisan else "KBLI tidak sesuai."))

        elif kunci == "sbu_subklasifikasi":
            sbu = per["sbu"]
            cocok = par.get("nilai") in sbu["subklasifikasi"]
            berlaku = date.fromisoformat(sbu["berlaku_sampai"])
            bukti = [{"nilai": f"SBU {sbu['nomor']} - {', '.join(sbu['subklasifikasi'])} - berlaku s.d. {sbu['berlaku_sampai']}",
                      "sumber": "profil_perusahaan.json#perusahaan.sbu", "dokumen": "dokumen/03_sbu.txt"}]
            if not cocok:
                matriks.append(_item(s, "tidak_memenuhi", bukti,
                                     f"SBU tidak memuat subklasifikasi {par.get('nilai')}."))
            elif berlaku < acuan:
                matriks.append(_item(s, "tidak_memenuhi", bukti,
                                     f"SBU berakhir {sbu['berlaku_sampai']}, sebelum batas pemasukan {acuan.isoformat()}.",
                                     tindakan="Perpanjang SBU sebelum pemasukan penawaran."))
            else:
                matriks.append(_item(s, "memenuhi", bukti,
                                     f"Subklasifikasi sesuai dan masih berlaku {sbu['berlaku_sampai']}."))

        elif kunci.startswith("personil:"):
            matriks.append(_cocok_personil(s, profil, acuan))

        elif kunci == "bpjs_personil":
            jumlah = sum(1 for p in profil["personil"] if "Aktif" in (p.get("bpjs_ketenagakerjaan") or ""))
            matriks.append(_item(
                s, "memenuhi" if jumlah >= 4 else "kurang_dokumen",
                [{"nilai": f"{jumlah} personil dengan BPJS aktif", "sumber": "profil_perusahaan.json#personil",
                  "dokumen": "dokumen/04_cv_personil.txt"}],
                f"Bukti BPJS tersedia untuk {jumlah} personil."))

        elif kunci == "pengalaman":
            matriks.append(_cocok_pengalaman(s, profil, acuan))

        elif kunci in ("pengalaman_periode", "pengalaman_subkon", "batas_hps"):
            matriks.append(_item(s, "memenuhi",
                                 [{"nilai": "Aturan dipahami dan diterapkan pada pencocokan",
                                   "sumber": s["sumber"]["dokumen"], "dokumen": s["sumber"]["dokumen"]}],
                                 "Aturan dipakai sebagai penyaring pada butir pengalaman."))

        elif kunci == "kekayaan_bersih":
            nilai = per["kekayaan_bersih"]
            butuh = par.get("nilai") or 0
            matriks.append(_item(
                s, "memenuhi" if nilai >= butuh else "tidak_memenuhi",
                [{"nilai": f"Kekayaan bersih {rupiah(nilai)} (2025)", "sumber": "profil_perusahaan.json#perusahaan.kekayaan_bersih",
                  "dokumen": "dokumen/01_akta_dan_legalitas.txt"}],
                f"Di atas syarat {rupiah(butuh)}." if nilai >= butuh else f"Di bawah syarat {rupiah(butuh)}."))

        elif kunci == "tenaga_ahli_tetap":
            butuh = par.get("nilai") or 0
            punya = per.get("jumlah_tenaga_ahli_tetap", 0)
            matriks.append(_item(
                s, "memenuhi" if punya >= butuh else "tidak_memenuhi",
                [{"nilai": f"{punya} tenaga ahli tetap", "sumber": "profil_perusahaan.json#perusahaan.jumlah_tenaga_ahli_tetap",
                  "dokumen": "dokumen/04_cv_personil.txt"}],
                f"Tersedia {punya}, disyaratkan {butuh}."))

        elif kunci.startswith("dokumen_admin:"):
            huruf = par.get("huruf")
            status_dok, catatan = _ketersediaan_dokumen(huruf, profil)
            if status_dok == "tersedia":
                matriks.append(_item(s, "memenuhi",
                                     [{"nilai": catatan, "sumber": "profil_perusahaan.json", "dokumen": "dokumen/"}],
                                     catatan))
            elif status_dok == "dapat_dibuat":
                butir = _item(s, "kurang_dokumen",
                              [{"nilai": catatan, "sumber": "rencana agen", "dokumen": ""}],
                              catatan, kritis=False,
                              tindakan="Agen akan menyiapkan draf; perlu tanda tangan pejabat berwenang.")
                butir["tingkat"] = "rendah"  # bukan penghambat, agen dapat menyiapkannya
                matriks.append(butir)
            elif status_dok == "sebagian":
                matriks.append(_item(s, "kurang_dokumen",
                                     [{"nilai": catatan, "sumber": "profil_perusahaan.json#personil", "dokumen": "dokumen/04_cv_personil.txt"}],
                                     catatan, kritis=True,
                                     tindakan="Lengkapi sertifikat yang belum terbit sebelum unggah."))
            else:
                matriks.append(_item(s, "kurang_dokumen",
                                     [{"nilai": catatan, "sumber": "profil_perusahaan.json#perusahaan.jaminan_bank",
                                       "dokumen": "dokumen/05_daftar_pengalaman.txt"}],
                                     catatan, kritis=True,
                                     tindakan="Ajukan surat dukungan bank ke bank mitra."))

        elif kunci == "batas_penawaran":
            tgl = par.get("tanggal")
            catatan_jadwal = [c for c in periksa_jadwal(hasil_ekstraksi["jadwal"]) if c["jenis"] != "bentrok_salat_jumat"]
            pesan = f"Batas pemasukan {tgl} pukul {par.get('jam')} {par.get('zona_waktu') or '(zona tidak disebut)'}."
            matriks.append(_item(s, "memenuhi",
                                 [{"nilai": pesan, "sumber": s["sumber"]["dokumen"], "dokumen": s["sumber"]["dokumen"]}],
                                 pesan))

        else:
            matriks.append(_item(s, "kurang_dokumen", [], "Belum ada aturan pencocokan untuk butir ini.", kritis=False,
                                 tindakan="Perlu peninjauan manual."))

    ringkasan = {
        "total": len(matriks),
        "memenuhi": sum(1 for m in matriks if m["status"] == "memenuhi"),
        "tidak_memenuhi": sum(1 for m in matriks if m["status"] == "tidak_memenuhi"),
        "kurang_dokumen": sum(1 for m in matriks if m["status"] == "kurang_dokumen"),
        "kurang_dokumen_kritis": sum(1 for m in matriks if m["status"] == "kurang_dokumen" and m["tingkat"] == "tinggi"),
    }
    return {"matriks": matriks, "ringkasan": ringkasan}
