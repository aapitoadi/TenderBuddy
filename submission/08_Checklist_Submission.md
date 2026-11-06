# 08 — Checklist Submission

**Hackathon:** AI CAN DO IT — Tencent Cloud Hackathon Indonesia 2026
**Track:** B — Agen Kantor (Office Agent)
**Batas pengumpulan karya:** **7 November 2026** (tanggal terbaru menurut sesi
29 Oktober 2026; panduan peserta versi cetak masih mencantumkan 1 November)

---

## 1. Status per item wajib

| # | Item | Status | Berkas / tindakan |
|---|---|---|---|
| 1 | Judul proyek | ✅ Siap | `01_Judul_dan_Blurb.md` → **TenderBuddy** |
| 2 | Blurb singkat (maks 10 kata) | ✅ Siap | "Dari paket tender LPSE ke berkas penawaran siap tanda tangan." (10 kata) |
| 3 | Deskripsi proyek | ✅ Siap | `02_Deskripsi_Proyek.md` |
| 4 | Lembar akuntabilitas (1 halaman) | ✅ Siap | `03_Lembar_Akuntabilitas.md` |
| 5 | Hasil pengujian + screenshot | ✅ Siap | `05_Hasil_Pengujian.md` + `tangkapan_layar/` (8 gambar) + `tests/hasil_uji.json` |
| 6 | Diagram arsitektur | ✅ Siap | `04_Diagram_Arsitektur.md` + `gambar/arsitektur.png` / `.svg` |
| 7 | Video demo 5–8 menit | ⚠️ **Perlu direkam** | Skrip lengkap di `06_Skrip_Video_Demo.md` (6:50) |
| 8 | Berbagi produk WorkBuddy | ✅ Siap | `07_Berbagi_Produk_WorkBuddy.md` |
| 9 | Source code / workflow ekspor | ⚠️ **Perlu dipublikasikan** | Folder proyek sudah lengkap; lihat bagian 3 |
| 10 | Gambar sampul 16:9 (opsional) | ✅ Siap | `gambar/sampul.png` (380×216) dan `gambar/sampul_besar.png` (1520×864) |
| 11 | Tautan proyek (bonus) | ⭕ Opsional | Dashboard dapat dipublikasikan; lihat bagian 4 |

## 2. Yang masih harus dikerjakan manusia

### a. Rekam video demo (wajib)

Ikuti `06_Skrip_Video_Demo.md`. Tiga momen yang **tidak boleh** terlewat:

1. agen **meminta klarifikasi** (aanwijzing bentrok salat Jumat, atau sertifikat
   K3 belum terbit);
2. agen **menolak** — jalankan `setujui` pada paket ber-SBU kadaluarsa;
3. agen **menunggu persetujuan** sebelum menulis berkas.

Rekam 1920×1080, narasi direkam terpisah, unggah sebagai tautan tidak terdaftar.

### b. Publikasikan source code

Opsi A — repositori publik:

```bash
cd "TenderBuddy"
git init
git add .
git commit -m "TenderBuddy - agen berkas penawaran LPSE (AI CAN DO IT 2026)"
git branch -M main
git remote add origin https://github.com/<akun>/tenderbuddy.git
git push -u origin main
```

Opsi B — ekspor workflow WorkBuddy beserta bukti penggunaan (folder proyek ini
sudah memenuhi bentuk "folder kerja": `AGENTS.md`, `input/`, `output/`,
`tests/`). Sertakan tangkapan layar sesi WorkBuddy saat agen dijalankan.

Sebelum publikasi, pastikan tidak ada data pribadi nyata. Seluruh data pada
`input/` adalah sintetis.

### c. Daftar portal Tencent

Pendaftaran portal adalah proses terpisah dari pengumpulan karya:

- Pendaftaran: https://qdrl.qq.com/fc97Jrkr
- Pengumpulan: https://forms.gle/y1aHBH4BsrytXDxdA

## 3. Isi folder proyek yang diserahkan

```
TenderBuddy/
├── README.md                 ringkasan, cara menjalankan, hasil uji
├── AGENTS.md                 aturan perilaku agen (7 prinsip)
├── input/
│   ├── paket_tender/         2 dokumen sintetis (KAK/TOR + dokumen pengadaan)
│   └── profil_perusahaan/    profil.json + 5 dokumen sumber
├── src/                      6 modul Python (ekstraksi, pencocokan, draf,
│                             pipeline, uji, dashboard)
├── output/
│   ├── 00_pertanyaan_klarifikasi.md
│   ├── 01_checklist_persyaratan.json     29 butir bersumber
│   ├── 02_matriks_kepatuhan.md           29 baris kepatuhan
│   ├── 03_berkas_penawaran/              5 dokumen .docx
│   ├── 04_ringkasan_risiko.md
│   ├── 05_log_audit.jsonl                jejak audit append-only
│   ├── dashboard.html                    panel kepatuhan satu berkas
│   └── usulan/                           rencana yang menunggu persetujuan
├── tests/
│   ├── hasil_uji.json                    20 test case, hasil mentah
│   └── hasil_uji.md                      narasi per kasus
└── submission/               paket submission (folder ini)
```

## 4. Tautan proyek (bonus)

`output/dashboard.html` adalah satu berkas mandiri tanpa dependensi eksternal.
Untuk mendapat poin bonus tautan:

1. Publikasikan lewat fitur "Publish" di WorkBuddy, atau
2. Unggah `dashboard.html` ke GitHub Pages / Netlify Drop, atau
3. Lampirkan sebagai berkas dan cantumkan bahwa demo dapat dibuka lokal.

## 5. Perkiraan waktu yang dibutuhkan

| Kegiatan | Perkiraan |
|---|---|
| Rekam + sunting video | 2–3 jam |
| Publikasi repositori | 20 menit |
| Isi formulir submission | 30 menit |
| Daftar portal Tencent | 20 menit |

Sisakan satu hari sebelum 7 November untuk cadangan.

## 6. Sebelum menekan kirim — periksa ulang

- [ ] Blurb benar-benar ≤ 10 kata
- [ ] Lembar akuntabilitas muat satu halaman
- [ ] Hasil pengujian menyertakan test case yang **gagal** (TC-19, TC-20)
- [ ] Video menyebut track yang dipilih (Track B) dan menampilkan satu penolakan
- [ ] Tautan repositori dapat dibuka tanpa login
- [ ] Tautan video dapat dibuka tanpa login
- [ ] Tidak ada data pribadi atau nomor dokumen nyata
- [ ] Nama tim dan anggota sesuai pendaftaran
