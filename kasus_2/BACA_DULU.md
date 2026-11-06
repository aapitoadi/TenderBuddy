# Kasus ke-2 — TenderBuddy Demo

## Skenario

Paket: **Rehabilitasi Jalan Merdeka - Diponegoro, Kota Samarinda**
Perusahaan: **PT Sinar Karya Mandiri** (dummy)

## Yang berbeda dari kasus ke-1

| Aspek | Kasus 1 | Kasus 2 |
|---|---|---|
| Jenis pekerjaan | Bangunan gedung | Jalan |
| Lokasi | Balikpapan | Samarinda |
| Zona waktu jadwal | WIB | WITA |
| SBU | Berlaku s.d. 2027 | **Kadaluarsa** (9 Okt 2026) |
| Site Engineer sertifikat | Berlaku | **Kadaluarsa** (31 Des 2025) |
| Ahli K3 | Sertifikat belum terbit | Berlaku penuh |
| Surat dukungan bank | Belum ada | Tersedia |
| Pagu | Rp2,45 M | Rp1,85 M |
| Hasil yang diharapkan | LOLOS BERSYARAT | **TIDAK LOLOS** |

## Cara menjalankan

```bash
cd TenderBuddy

# 1. Jalankan tahap rencana (ekstraksi + pencocokan + keputusan)
python src/pipeline.py rencana \
  --paket kasus_2/paket_tender \
  --profil kasus_2/profil_perusahaan/profil_perusahaan.json

# 2. Baca keputusan di output/
#    - output/02_matriks_kepatuhan.md  (matriks lengkap)
#    - output/04_ringkasan_risiko.md   (risiko)
#    - output/00_pertanyaan_klarifikasi.md

# 3. Bila verdict = TIDAK LOLOS, pipeline akan menolak membuat berkas:
python src/pipeline.py setujui --id <ID_USULAN>

# Output yang diharapkan: "DITOLAK: keputusan agen untuk paket ini adalah TIDAK LOLOS."
```

## Mengapa TIDAK LOLOS?

Dua butir `tidak_memenuhi` kritis:

1. **SBU kadaluarsa** — berlaku s.d. 9 Oktober 2026, batas pemasukan 19 November 2026.
2. **Sertifikat Site Engineer kadaluarsa** — SKA Ahli Teknik Jalan dan Jembatan berakhir 31 Desember 2025.

Satu `tidak_memenuhi` saja sudah cukup untuk memblokir seluruh penawaran.
Agen tidak akan menulis berkas apa pun.
