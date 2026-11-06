# TenderBuddy

Agen yang membaca paket dokumen tender LPSE dan menyiapkan berkas penawaran
administrasinya — dengan sumber yang dapat dilacak dan persetujuan manusia di
setiap langkah yang mengikat.

Dibuat untuk **AI CAN DO IT — Tencent Cloud Hackathon Indonesia 2026**,
Track B (Agen Kantor).

## Masalah

Penyedia jasa konstruksi kecil menghabiskan 1–2 hari kerja hanya untuk
menerjemahkan satu paket dokumen tender (KAK/TOR, LDP, LDK, addendum) menjadi
daftar persyaratan, mencocokkannya dengan arsip perusahaan, lalu mengetik ulang
surat penawaran, pakta integritas, daftar personil, dan tabel pengalaman.
Kesalahan yang paling mahal bukan salah ketik, melainkan **mengklaim memenuhi
syarat yang sebenarnya tidak terpenuhi** — dan itu berujung gugur atau sanksi
daftar hitam.

## Alur sekali perintah

```
input/paket_tender/  ──┐
                       ├─► ekstraksi bersumber ─► pencocokan profil ─► keputusan
input/profil_perusahaan┘                                                   │
                                                                           ▼
                                              rencana tindakan ──► PERSETUJUAN MANUSIA
                                                                           │
                                                                           ▼
                                   output/kasus_N/03_berkas_penawaran/*.docx + ringkasan risiko
```

## Cara menjalankan

Ada dua cara: **versi web user-friendly** (untuk demo dan awam) dan **versi CLI** (untuk pengembangan).

### Cara 1 — Web UI (cukup klik)

```bash
python src/server_web.py
```

Server berjalan di `http://localhost:8080` dan browser terbuka otomatis. Pengguna tinggal:
1. Pilih paket tender (Kasus 1 atau Kasus 2).
2. Klik tombol **Jalankan Agen**.
3. Lihat keputusan, metrik, klarifikasi, dan risiko.
4. Jika LOLOS, klik **Setujui & Buat Berkas** untuk mengunduh file `.docx`.
5. Jika TIDAK LOLOS, agen menolak membuat berkas — pengguna dapat membaca alasan.

### Cara 2 — CLI

```bash
# 1. Baca paket, nilai, dan ajukan rencana (belum menulis berkas apa pun)
python src/pipeline.py rencana

# Untuk kasus 2 (rehabilitasi jalan Samarinda)
python src/pipeline.py rencana \
  --paket kasus_2/paket_tender \
  --profil kasus_2/profil_perusahaan/profil_perusahaan.json

# 2. Setelah memeriksa rencana, setujui
python src/pipeline.py setujui --id USL-20261030-093646

# atau tolak dengan alasan
python src/pipeline.py tolak --id USL-20261030-093646 --alasan "Harga belum disetujui direktur"

# 3. Jalankan 20 test case akuntabilitas
cd src && python uji.py

# 4. Bangun dashboard demo (satu berkas HTML)
python src/buat_dashboard.py
```

## Struktur folder

```
TenderBuddy/
├── AGENTS.md                  aturan perilaku agen
├── input/
│   ├── paket_tender/          KAK/TOR + dokumen pengadaan (data sintetis)
│   └── profil_perusahaan/     basis pengetahuan: akta, NIB, SBU, CV, pengalaman
├── src/
│   ├── ekstraksi.py           tahap 1: persyaratan + kutipan terverifikasi
│   ├── pencocokan.py          tahap 2: cocokkan dengan profil, periksa jadwal
│   ├── draf_dokumen.py        tahap 4: surat penawaran, pakta integritas, tabel
│   ├── pipeline.py            orkestrator + gerbang persetujuan + log audit
│   ├── uji.py                 harness 20 test case
│   └── buat_dashboard.py      dashboard HTML untuk demo
├── output/
│   ├── kasus_1/               hasil untuk Kasus 1 (Gedung Balikpapan)
│   │   ├── 00_pertanyaan_klarifikasi.md
│   │   ├── 01_checklist_persyaratan.json
│   │   ├── 02_matriks_kepatuhan.md
│   │   ├── 03_berkas_penawaran/   5 dokumen .docx
│   │   ├── 04_ringkasan_risiko.md
│   │   ├── 05_log_audit.jsonl
│   │   ├── dashboard.html
│   │   └── usulan/            rencana yang menunggu persetujuan
│   └── kasus_2/               hasil untuk Kasus 2 (Jalan Samarinda)
│       └── ... (struktur sama; berkas .docx hanya muncul setelah persetujuan)
├── tests/                     hasil_uji.json + hasil_uji.md
└── submission/                paket submission hackathon
```

## Hasil pengujian

18 dari 20 test case lulus. Dua kegagalan dilaporkan terbuka:

- **TC-19** — nilai kontrak berformat singkat (`Rp1,2 M`) membuat agen berhenti
  dengan galat, belum ada penanganan.
- **TC-20** — addendum yang mengubah jadwal belum diprioritaskan terhadap
  dokumen asli.

Rincian: `tests/hasil_uji.md`.

## Catatan data

Seluruh dokumen dan nomor identitas pada folder `input/` adalah **data sintetis**
untuk demonstrasi. Tidak ada data perusahaan nyata, dan tidak ada koneksi ke
LPSE sungguhan.
