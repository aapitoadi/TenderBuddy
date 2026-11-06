# 03 — Lembar Akuntabilitas TenderBuddy

*Satu halaman. Empat pertanyaan: apa yang dapat diakses, apa yang berjalan
sendiri, apa yang menunggu manusia, dan apa yang tidak akan pernah dilakukan.*

---

## 1. Yang dapat diakses agen

| Sumber | Isi | Hak |
|---|---|---|
| `input/paket_tender/` | KAK/TOR, Lembar Data Pemilihan, LDK, addendum | Baca saja |
| `input/profil_perusahaan/` | Akta, NIB, SBU, CV personil, daftar pengalaman (JSON + dokumen sumber) | Baca saja |
| `output/` | Berkas kerja, usulan, log audit | Tulis setelah persetujuan |
| Jaringan, surel, LPSE, kalender | — | **Tidak ada akses** |

Agen tidak memiliki kredensial LPSE, tidak dapat mengirim surel, dan tidak
dapat membaca folder di luar dua folder input.

## 2. Yang berjalan otonom (tanpa persetujuan)

Semua langkah ini hanya **membaca dan menghitung** — tidak ada yang keluar dari
folder kerja:

- membaca dan memecah dokumen menjadi butir persyaratan;
- memverifikasi bahwa setiap kutipan benar-benar ada di dokumen asli;
- mencocokkan butir dengan basis pengetahuan dan memeriksa masa berlaku;
- menghitung status tiap butir dan keputusan paket;
- menyusun daftar pertanyaan klarifikasi dan lembar risiko;
- menulis berkas kerja: checklist, matriks, usulan, log audit.

## 3. Yang menunggu persetujuan manusia

| Tindakan | Mengapa harus disetujui |
|---|---|
| Menulis 5 berkas `.docx` penawaran | Isinya mengikat perusahaan secara hukum |
| Menetapkan nilai penawaran | Keputusan komersial; agen tidak punya data harga |
| Mengisi nomor/tanggal sertifikat yang belum terbit | Tidak ada sumber; mengisi berarti mengarang |
| Menandatangani dokumen | Hanya direktur yang berwenang |
| Mengunggah ke LPSE | Tindakan keluar yang tidak dapat dibatalkan |
| Mengubah basis pengetahuan | Mengubah dasar seluruh keputusan berikutnya |

Mekanismenya: agen menampilkan rencana (`output/usulan/<id>.json`) berisi daftar
berkas, hal yang dikosongkan, dan larangan. Persetujuan terikat pada
**sidik jari** isi matriks — bila dokumen berubah setelah persetujuan, sidik
jari tidak cocok dan persetujuan tidak berlaku.

## 4. Yang tidak akan pernah dilakukan

- Menyatakan sebuah paket "lolos" tanpa bukti pada basis pengetahuan.
- Mengarang nomor sertifikat, tanggal, nilai kontrak, atau nama personil.
- Mengikuti instruksi yang tertulis di dalam dokumen tender.
- Menghapus atau menimpa log audit.
- Menjanjikan kemenangan tender.

## 5. Sumber dan keterlacakan

Setiap baris matriks memuat `sumber_persyaratan` (dokumen + bagian + kutipan)
dan `bukti` (rujukan ke basis pengetahuan + dokumen sumber). Kutipan diverifikasi
ulang terhadap teks asli; butir yang kutipannya tidak ditemukan ditandai
`kutipan_terverifikasi: false` dan tidak dipakai untuk memutuskan.

## 6. Batas yang diakui

- Paket hasil pindai tanpa lapisan teks → agen menyatakan tidak bisa membaca,
  tidak menebak isi.
- Format nilai tidak lazim (`Rp1,2 M`) → saat ini berhenti dengan galat
  (TC-19, gagal, dilaporkan).
- Addendum yang mengubah jadwal → belum diprioritaskan terhadap dokumen asli
  (TC-20, gagal, dilaporkan).
- Penilaian teknis (metode pelaksanaan) hanya disusun sebagai kerangka; wajib
  divalidasi tenaga ahli.

## 7. Catatan

`output/05_log_audit.jsonl` mencatat setiap pembacaan, keputusan, penulisan,
dan persetujuan — beserta aktor (`agen` atau `manusia`). Berkas ini
append-only dan menjadi dasar pemeriksaan ulang bila hasil dipertanyakan.

---

**Ringkasnya:** agen boleh membaca dan menghitung sebanyak mungkin, tetapi
hanya boleh **menulis** setelah manusia menyetujui, dan tidak pernah boleh
**mengarang**.
