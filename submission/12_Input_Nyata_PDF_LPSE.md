# 12 — Input Nyata: Dari PDF LPSE ke Agen

## Penjelasan (1 paragraf)

Dalam produksi, pengguna tidak perlu mengetik ulang dokumen tender. Alur yang
dirancang: pengguna mengunduh paket tender dari SPSE/LPSE dalam format PDF
(KAK/TOR, Lembar Data Pemilihan, Lembar Data Kualifikasi, dan addendum jika
ada), lalu meletakkannya di folder `input/paket_tender/`. Sebuah lapisan
konversi — menggunakan OCR (Tesseract atau layanan sejenis) untuk PDF hasil
pindai dan pdfplumber untuk PDF dengan lapisan teks — akan mengubah setiap
berkas menjadi `.txt` yang dapat dibaca agen. Demikian pula dokumen
perusahaan (akta, NIB, SBU, sertifikat personil, daftar pengalaman, bukti
kontrak) yang saat ini tersimpan sebagai PDF/JPG di arsip perusahaan akan
diekstrak menjadi `profil_perusahaan.json` terstruktur oleh modul parsing
yang sama. Setelah konversi selesai, agen menjalankan pipeline yang sama
seperti prototype ini: ekstraksi bersumber, pencocokan deterministik,
keputusan, dan gerbang persetujuan. Dengan demikian, satu-satunya perbedaan
antara prototype dan produksi adalah lapisan konversi PDF→teks di hulu —
mesin agen, aturan di `AGENTS.md`, dan format keluaran `.docx` tidak berubah.

## Diagram alur produksi

```
LPSE/SPSE (PDF)                         Arsip Perusahaan (PDF/JPG)
     │                                          │
     ▼                                          ▼
  Unduh paket                              Pindai/unggah
     │                                          │
     ▼                                          ▼
┌─────────────┐                       ┌─────────────────┐
│ Konversi    │                       │ Konversi        │
│ PDF → .txt  │                       │ PDF/JPG → JSON  │
│ (OCR +      │                       │ (OCR + parser   │
│  pdfplumber)│                       │  dokumen)       │
└──────┬──────┘                       └────────┬────────┘
       │                                       │
       ▼                                       ▼
  input/paket_tender/              input/profil_perusahaan/
  01_KAK_TOR.txt                   profil_perusahaan.json
  02_Dokumen_Pengadaan.txt
       │                                       │
       └──────────────┬────────────────────────┘
                      ▼
          ┌──────────────────────┐
          │  Agen TenderBuddy    │
          │  (pipeline.py)       │
          │  Tidak berubah       │
          └──────────────────────┘
                      │
                      ▼
              output/kasus_N/
              berkas .docx siap tanda tangan
```

## Catatan

- Prototype ini menggunakan data sintetis (`.txt` dummy) karena fokus lomba
  adalah desain agen dan alur kerja, bukan integrasi LPSE.
- Lapisan konversi PDF→teks adalah pekerjaan rekayasa standar (OCR + parser)
  dan tidak mengubah logika agen.
- Agen tetap tidak terhubung ke internet, LPSE, atau surel. Konversi dilakukan
  di luar agen; agen hanya membaca teks yang sudah jadi di folder input.
