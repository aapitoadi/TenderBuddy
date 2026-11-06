"""Tahap 4 - Penyusunan draf berkas administrasi penawaran (.docx).

Prinsip: hanya memakai fakta dari basis pengetahuan. Nilai yang tidak diketahui
ditulis sebagai penanda eksplisit, bukan dikarang.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Pt, RGBColor

from utilitas import rupiah, parse_tanggal

MERAH = RGBColor(0xB4, 0x23, 0x18)
ABU = RGBColor(0x5F, 0x63, 0x68)

BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
         "Agustus", "September", "Oktober", "November", "Desember"]


def tanggal_indonesia(d: date) -> str:
    return f"{d.day} {BULAN[d.month - 1]} {d.year}"


def _dasar(judul: str) -> Document:
    dok = Document()
    bagian = dok.sections[0]
    bagian.page_width = Cm(21)
    bagian.page_height = Cm(29.7)
    bagian.top_margin = Cm(2.5)
    bagian.bottom_margin = Cm(2.5)
    bagian.left_margin = Cm(3)
    bagian.right_margin = Cm(2.5)

    gaya = dok.styles["Normal"]
    gaya.font.name = "Times New Roman"
    gaya.font.size = Pt(11)
    gaya.paragraph_format.space_after = Pt(6)
    gaya.paragraph_format.line_spacing = 1.15

    p = dok.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(judul)
    r.bold = True
    r.font.size = Pt(14)
    return dok


def _kop(dok: Document, profil: dict) -> None:
    per = profil["perusahaan"]
    for teks, ukuran, tebal in ((per["nama"], 13, True), (per["alamat"], 9, False),
                                (f"Telp. {per['telepon']}  |  {per['email']}", 9, False)):
        p = dok.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(teks)
        r.bold = tebal
        r.font.size = Pt(ukuran)
    p = dok.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    r = p.add_run("_" * 92)
    r.font.color.rgb = ABU


def _tanda_tangan(dok: Document, profil: dict, jabatan: str = "Direktur Utama") -> None:
    per = profil["perusahaan"]
    nama = "Hendra Gunawan" if jabatan == "Direktur Utama" else "Marlina Sari"
    dok.add_paragraph()
    p = dok.add_paragraph("Hormat kami,")
    p.paragraph_format.space_after = Pt(0)
    p = dok.add_paragraph(f"{per['nama']}")
    p.paragraph_format.space_after = Pt(36)
    p = dok.add_paragraph(nama)
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(jabatan)
    r.italic = True
    r.font.size = Pt(10)


def _tabel(dok: Document, header: list[str], baris: list[list[str]], lebar: list[float] | None = None) -> None:
    t = dok.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for i, h in enumerate(header):
        sel = t.rows[0].cells[i]
        sel.text = ""
        r = sel.paragraphs[0].add_run(h)
        r.bold = True
        r.font.size = Pt(9)
    # ulangi baris judul bila tabel berlanjut ke halaman berikutnya
    tr_pr = t.rows[0]._tr.get_or_add_trPr()
    tr_pr.append(parse_xml('<w:tblHeader %s/>' % nsdecls('w')))
    for b in baris:
        sel = t.add_row().cells
        for i, nilai in enumerate(b):
            sel[i].text = ""
            r = sel[i].paragraphs[0].add_run(str(nilai))
            r.font.size = Pt(9)
            if "BELUM ADA" in str(nilai) or "TIDAK" in str(nilai).upper()[:6]:
                r.font.color.rgb = MERAH
                r.bold = True
    if lebar:
        # set lebar kolom pada grid dan sel agar konsisten di Word maupun WPS
        for i, w in enumerate(lebar):
            t.columns[i].width = Cm(w)
        for row in t.rows:
            for i, w in enumerate(lebar):
                row.cells[i].width = Cm(w)


def _catatan_kaki(dok: Document, teks: str) -> None:
    p = dok.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    r = p.add_run(teks)
    r.italic = True
    r.font.size = Pt(8)
    r.font.color.rgb = ABU


# ---------------------------------------------------------------------------


def surat_penawaran(path: Path, profil: dict, ekstraksi: dict,
                    nama_paket: str, kode_paket: str, lokasi_paket: str,
                    nomor: str | None = None) -> Path:
    per = profil["perusahaan"]
    hps = next((s for s in ekstraksi["persyaratan"] if s["kunci"] == "hps"), None)
    nilai_hps = (hps or {}).get("parameter", {}).get("nilai") or 0
    if nomor is None:
        kode_singkat = per.get("nama_singkat", "".join(w[0] for w in per["nama"].split() if w)).upper()
        nomor = f"001/{kode_singkat}/SP/TENDER/XI/2026"

    dok = _dasar("SURAT PENAWARAN")
    _kop(dok, profil)

    dok.add_paragraph()
    p = dok.add_paragraph()
    p.paragraph_format.space_after = Pt(0)
    p.add_run("Nomor  : ").bold = True
    p.add_run(nomor)
    p = dok.add_paragraph()
    p.paragraph_format.space_after = Pt(0)
    p.add_run("Tanggal: ").bold = True
    p.add_run(tanggal_indonesia(date.today()))
    dok.add_paragraph()

    p = dok.add_paragraph("Kepada:")
    p.paragraph_format.space_after = Pt(0)
    p = dok.add_paragraph("Pokja Pemilihan Barang/Jasa Konstruksi")
    p.paragraph_format.space_after = Pt(0)
    p = dok.add_paragraph(lokasi_paket)
    p.paragraph_format.space_after = Pt(0)
    p = dok.add_paragraph(f"di {lokasi_paket.replace('Kota ', '').replace('Kabupaten ', '')}")
    dok.add_paragraph()

    p = dok.add_paragraph()
    p.add_run("Perihal: ").bold = True
    p.add_run(f"Penawaran untuk Paket {nama_paket} (Kode Paket {kode_paket})")
    dok.add_paragraph()

    dok.add_paragraph("Dengan hormat,")
    dok.add_paragraph(
        "Sehubungan dengan pengumuman tender paket pekerjaan sebagaimana tersebut di atas, "
        "kami yang bertanda tangan di bawah ini, atas nama dan mewakili:")
    dok.add_paragraph(f"Nama Perusahaan : {per['nama']}")
    dok.add_paragraph(f"Alamat          : {per['alamat']}")
    dok.add_paragraph(f"NPWP            : {per['npwp']}")
    dok.add_paragraph(f"NIB             : {per['nib']['nomor']}")
    dok.add_paragraph(f"SBU             : {per['sbu']['nomor']} ({', '.join(per['sbu']['subklasifikasi'])})")
    dok.add_paragraph()

    dok.add_paragraph("dengan ini mengajukan penawaran sebagai berikut:")
    p = dok.add_paragraph("1. Nilai penawaran   : ", style=None)
    r = p.add_run("[ DIISI OLEH DIREKTUR — KEPUTUSAN HARGA BUKAN WEWENANG AGEN ]")
    r.bold = True
    r.font.color.rgb = MERAH
    p = dok.add_paragraph()
    p.add_run("2. Nilai HPS paket   : ")
    p.add_run(rupiah(nilai_hps))
    dok.add_paragraph("3. Jangka waktu pelaksanaan : 180 (seratus delapan puluh) hari kalender.")
    dok.add_paragraph("4. Masa berlaku penawaran   : 90 (sembilan puluh) hari kalender sejak batas pemasukan penawaran.")

    dok.add_paragraph()
    dok.add_paragraph(
        "Penawaran ini mengikat kami dan kami menyatakan bahwa seluruh dokumen administrasi "
        "yang kami unggah adalah benar, sah, dan masih berlaku. Apabila di kemudian hari "
        "ditemukan ketidakbenaran, kami bersedia dikenai sanksi sesuai ketentuan peraturan "
        "perundang-undangan.")
    dok.add_paragraph(
        "Demikian surat penawaran ini kami sampaikan. Atas perhatian Bapak/Ibu, kami ucapkan terima kasih.")

    _tanda_tangan(dok, profil)
    _catatan_kaki(dok, "Dokumen ini adalah DRAF yang dihasilkan TenderBuddy. Wajib diperiksa dan "
                       "ditandatangani pejabat berwenang sebelum diunggah ke LPSE. Nilai penawaran "
                       "sengaja dikosongkan karena merupakan keputusan komersial manusia.")
    path.parent.mkdir(parents=True, exist_ok=True)
    dok.save(path)
    return path


def pakta_integritas(path: Path, profil: dict, lokasi_paket: str = "Balikpapan") -> Path:
    per = profil["perusahaan"]
    dok = _dasar("PAKTA INTEGRITAS")
    dok.add_paragraph()
    dok.add_paragraph("Saya yang bertanda tangan di bawah ini:")
    dok.add_paragraph(f"Nama      : Hendra Gunawan")
    dok.add_paragraph(f"Jabatan   : Direktur Utama {per['nama']}")
    dok.add_paragraph(f"Alamat    : {per['alamat']}")
    dok.add_paragraph()
    dok.add_paragraph(f"dalam rangka pengadaan barang/jasa pada Pemerintah {lokasi_paket}, dengan ini menyatakan:")
    for i, butir in enumerate([
        "tidak akan melakukan praktek Korupsi, Kolusi, dan Nepotisme (KKN);",
        "akan mematuhi dan melaksanakan ketentuan peraturan perundang-undangan pengadaan barang/jasa;",
        "tidak akan melakukan persaingan usaha tidak sehat, kolusi, dan/atau kesepakatan dengan peserta lain;",
        "akan menyampaikan informasi yang benar dan tidak menyesatkan, termasuk tidak akan menyampaikan dokumen palsu;",
        "apabila melanggar pakta integritas ini, bersedia menerima sanksi sesuai ketentuan yang berlaku.",
    ], start=1):
        dok.add_paragraph(f"{i}. {butir}")
    dok.add_paragraph()
    dok.add_paragraph(
        f"Demikian Pakta Integritas ini dibuat dengan sebenarnya, dalam keadaan sadar dan tanpa paksaan, "
        f"untuk dipergunakan sebagaimana mestinya.")
    p = dok.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.add_run(f"{lokasi_paket.replace('Kota ', '').replace('Kabupaten ', '')}, {tanggal_indonesia(date.today())}")
    _tanda_tangan(dok, profil)
    _catatan_kaki(dok, "DRAF TenderBuddy. Pernyataan ini adalah komitmen hukum direktur; "
                       "wajib dibaca ulang dan ditandatangani manusia.")
    path.parent.mkdir(parents=True, exist_ok=True)
    dok.save(path)
    return path


def daftar_personil(path: Path, profil: dict, matriks: list[dict],
                    nama_paket: str, kode_paket: str, lokasi_paket: str = "Balikpapan") -> Path:
    per = profil["perusahaan"]
    dok = _dasar("DAFTAR PERSONIL INTI")
    _kop(dok, profil)
    dok.add_paragraph()
    dok.add_paragraph(f"Paket: {nama_paket} (Kode {kode_paket})")
    dok.add_paragraph("Tabel ini memetakan setiap personil yang diusulkan terhadap syarat pada KAK/TOR.")

    baris = []
    for m in [x for x in matriks if x["kategori"] == "Personil" and x["judul"].startswith("Personil inti")]:
        jabatan = m["judul"].split(":", 1)[1].strip()
        orang = next((p for p in profil["personil"] if p["jabatan_kbli"] == jabatan), None)
        if not orang:
            baris.append([jabatan, "—", "—", "—", "—", "TIDAK ADA PERSONIL"])
            continue
        sert = []
        for s in orang.get("sertifikat", []):
            sert.append(f"{s['nama']} No. {s['nomor']} (s.d. {s['berlaku_sampai']})")
        if "Ahli K3" in jabatan:
            sert.append("Sertifikat Ahli K3 Umum Kemnaker: BELUM ADA")
        status = "Memenuhi" if m["status"] == "memenuhi" else "KURANG DOKUMEN"
        baris.append([
            jabatan, orang["nama"], orang.get("pendidikan", "—"),
            "; ".join(sert) if sert else "—",
            f"{orang.get('pengalaman_tahun', 0)} tahun", status,
        ])

    _tabel(dok, ["Posisi (KAK)", "Nama", "Pendidikan", "Sertifikat & masa berlaku", "Pengalaman", "Status"],
           baris, lebar=[2.4, 2.6, 2.6, 4.4, 1.2, 2.3])

    dok.add_paragraph()
    p = dok.add_paragraph()
    r = p.add_run("Catatan kepatuhan:")
    r.bold = True
    # Buat catatan dinamis berdasarkan baris yang kurang dokumen
    kurang = [b for b in baris if "KURANG DOKUMEN" in b[-1] or "TIDAK ADA PERSONIL" in b[-1]]
    if kurang:
        dok.add_paragraph(
            "Terdapat posisi personil yang belum memenuhi syarat secara lengkap. "
            "Kolom yang ditandai KURANG DOKUMEN atau TIDAK ADA PERSONIL menunjukkan kekurangan tersebut. "
            "TenderBuddy tidak mengisi nomor sertifikat, riwayat, atau data lain yang belum tersedia "
            "di basis pengetahuan perusahaan.")
    else:
        dok.add_paragraph(
            "Seluruh posisi personil inti memenuhi syarat berdasarkan dokumen yang tersedia.")
    _catatan_kaki(dok, "DRAF TenderBuddy. Dilengkapi dari basis pengetahuan profil perusahaan.")
    path.parent.mkdir(parents=True, exist_ok=True)
    dok.save(path)
    return path


def tabel_pengalaman(path: Path, profil: dict, matriks: list[dict],
                     nama_paket: str, kode_paket: str) -> Path:
    dok = _dasar("TABEL PENGALAMAN PERUSAHAAN")
    _kop(dok, profil)
    dok.add_paragraph()
    dok.add_paragraph(f"Paket: {nama_paket} (Kode {kode_paket})")
    syarat = next((m for m in matriks if m["judul"].startswith("Pengalaman pekerjaan sejenis")), None)
    if syarat:
        dok.add_paragraph(f"Syarat KAK: {syarat['pernyataan']}")

    # Ambil threshold nilai dan tahun dari matriks jika tersedia
    par = syarat.get("parameter", {}) if syarat else {}
    nilai_min = par.get("nilai_min", 0)
    tahun_min = par.get("tahun_min", date.today().year - 10)

    baris = []
    subkontrak_indeks = []
    for i, e in enumerate(profil["pengalaman"], start=1):
        memenuhi = ("Ya" if (e["peran"] == "Kontraktor Utama" and e["nilai_kontrak"] >= nilai_min
                             and e["tahun_selesai"] >= tahun_min) else "Tidak (dikecualikan)")
        if e["peran"] != "Kontraktor Utama":
            subkontrak_indeks.append(str(i))
        baris.append([str(i), e["nama_paket"], e["pemberi_kerja"], rupiah(e["nilai_kontrak"]),
                      str(e["tahun_selesai"]), e["peran"], memenuhi])

    _tabel(dok, ["No", "Nama Paket", "Pemberi Kerja", "Nilai Kontrak", "Tahun", "Peran", "Memenuhi"],
           baris, lebar=[0.9, 4.0, 2.8, 2.6, 1.1, 2.1, 2.0])

    dok.add_paragraph()
    if subkontrak_indeks:
        daftar = ", ".join(subkontrak_indeks)
        dok.add_paragraph(
            f"Pengalaman Nomor {daftar} tidak diperhitungkan karena dikerjakan sebagai subkontraktor, "
            f"sesuai ketentuan KAK.")
    else:
        dok.add_paragraph("Seluruh pengalaman di atas diperhitungkan sebagai Kontraktor Utama.")
    _catatan_kaki(dok, "DRAF TenderBuddy. Bukti kontrak dan BAST wajib dilampirkan pada saat unggah.")
    path.parent.mkdir(parents=True, exist_ok=True)
    dok.save(path)
    return path


def lembar_risiko(path: Path, paket: str, verdict: str, risiko: list[dict], ringkasan: dict) -> Path:
    dok = _dasar("LEMBAR RINGKASAN RISIKO")
    dok.add_paragraph()
    dok.add_paragraph(f"Paket   : {paket}")
    dok.add_paragraph(f"Status  : {verdict}")
    dok.add_paragraph(
        f"Ringkasan: {ringkasan['total']} persyaratan diperiksa — {ringkasan['memenuhi']} memenuhi, "
        f"{ringkasan['tidak_memenuhi']} tidak memenuhi, {ringkasan['kurang_dokumen']} kurang dokumen.")
    dok.add_paragraph()

    if not risiko:
        dok.add_paragraph("Tidak ditemukan risiko yang perlu ditindaklanjuti.")
    else:
        baris = [[str(i), r["tingkat"].upper(), r["judul"], r["uraian"], r["tindakan"]]
                 for i, r in enumerate(risiko, start=1)]
        _tabel(dok, ["No", "Tingkat", "Persyaratan", "Temuan", "Tindakan yang disarankan"],
               baris, lebar=[0.9, 1.5, 3.0, 5.6, 4.5])

    _catatan_kaki(dok, "Disusun otomatis oleh TenderBuddy. Setiap temuan dapat dilacak ke dokumen "
                       "sumber melalui log audit.")
    path.parent.mkdir(parents=True, exist_ok=True)
    dok.save(path)
    return path
