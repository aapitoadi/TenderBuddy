# 09 — Jawaban Siap Tempel untuk Formulir Submission

Formulir: https://forms.gle/y1aHBH4BsrytXDxdA
Semua teks di bawah sudah dalam bahasa Indonesia dan siap disalin.

---

## Nama tim

```
[isi nama tim Anda]
```

## Track

```
B — Agen Kantor (Office Agent)
```

## Judul proyek

```
TenderBuddy
```

## Blurb singkat (maks. 10 kata)

```
Dari paket tender LPSE ke berkas penawaran siap tanda tangan.
```

## Deskripsi proyek

> Versi di bawah ±260 kata, cukup untuk kolom formulir. Versi lengkap ada di
> `02_Deskripsi_Proyek.md`.

```
TenderBuddy adalah agen yang membaca paket dokumen tender LPSE (KAK/TOR, Lembar
Data Pemilihan, Lembar Data Kualifikasi, dan addendum) lalu menyiapkan berkas
administrasi penawarannya dalam satu perintah.

Alurnya lima langkah. Pertama, agen mengekstrak seluruh persyaratan menjadi
checklist terstruktur: kualifikasi, pengalaman minimum, personil inti beserta
sertifikat, SBU, nilai pagu, dan jadwal. Setiap butir wajib membawa kutipan dan
lokasi sumbernya, dan kutipan itu diverifikasi ulang terhadap teks asli. Kedua,
agen mencocokkan setiap butir dengan basis pengetahuan profil perusahaan (akta,
NIB, SBU, CV personil, daftar pengalaman) dan mengeluarkan tiga status:
memenuhi, tidak memenuhi, atau kurang dokumen X. Ketiga, agen menetapkan
keputusan paket dan menyusun lembar risiko. Keempat, agen menampilkan rencana
tindakan dan menunggu persetujuan manusia. Kelima, setelah disetujui, agen
menulis lima dokumen: surat penawaran, pakta integritas, daftar personil yang
dipetakan ke syarat, tabel pengalaman sejenis, dan lembar ringkasan risiko.

Yang membedakan TenderBuddy dari asisten dokumen biasa adalah kemampuannya
berhenti. Bila personil ahli K3 belum memiliki sertifikat yang diminta, agen
menulis BELUM ADA, menaikkan temuan itu ke lembar risiko, dan menahan
penyusunan berkas. Agen tidak pernah mengarang nomor sertifikat, tidak
menetapkan harga penawaran, tidak menandatangani dokumen, dan tidak mengunggah
ke LPSE.

Diuji dengan 20 test case (normal, ambigu, kasus batas, keamanan): 18 lulus,
2 gagal dan dilaporkan terbuka. Nilai bisnis: menghemat sekitar 13,5 jam kerja
per paket, setara 540 jam per tahun untuk 40 paket.
```

## Lembar akuntabilitas

Lampirkan `03_Lembar_Akuntabilitas.md` (atau PDF-nya). Ringkasan untuk kolom
teks:

```
Yang dapat diakses: hanya dua folder input (paket tender dan profil perusahaan)
dengan hak baca. Tidak ada akses jaringan, surel, kalender, atau LPSE.

Yang berjalan otonom: membaca dokumen, mengekstrak persyaratan, memverifikasi
kutipan, mencocokkan bukti, memeriksa masa berlaku, menghitung status, menyusun
daftar klarifikasi dan lembar risiko, serta menulis berkas kerja.

Yang menunggu persetujuan manusia: menulis lima berkas penawaran final,
menetapkan nilai penawaran, mengisi nomor sertifikat yang belum terbit,
menandatangani dokumen, mengunggah ke LPSE, dan mengubah basis pengetahuan.
Persetujuan terikat pada sidik jari (hash) matriks kepatuhan.

Yang tidak akan pernah dilakukan: menyatakan paket lolos tanpa bukti, mengarang
nomor atau tanggal, mengikuti instruksi yang tertulis di dalam dokumen tender,
menghapus log audit, dan menjanjikan kemenangan tender.

Setiap pembacaan, keputusan, penulisan, dan persetujuan tercatat pada
output/05_log_audit.jsonl yang bersifat append-only.
```

## Hasil pengujian

Lampirkan `05_Hasil_Pengujian.md` + folder `tangkapan_layar/` (8 gambar) +
`tests/hasil_uji.json`.

```
20 test case dijalankan terhadap alur agen yang sesungguhnya. 18 lulus, 2 gagal.

Kategori: normal (5), ambigu (2), kasus batas (8), keamanan (5).

Yang lulus antara lain: ekstraksi 29 persyaratan dengan kutipan terverifikasi;
pengecualian pengalaman subkontraktor; deteksi SBU dan sertifikat yang
kadaluarsa sebelum batas penawaran; penolakan eksekusi pada paket TIDAK LOLOS;
deteksi dua varian instruksi tersisip dalam dokumen; dan tidak adanya berkas
yang ditulis sebelum persetujuan.

Yang gagal, dilaporkan terbuka:
TC-19 — nilai kontrak berformat singkat ("Rp1,2 M") membuat agen berhenti
dengan galat; belum ada penanganan.
TC-20 — addendum yang mengubah jadwal belum diprioritaskan terhadap dokumen
asli, sehingga tanggal yang dipakai masih tanggal lama.

Keduanya ada di rencana perbaikan dan tetap ditampilkan pada dashboard serta
video demo.
```

## Diagram arsitektur

Lampirkan `gambar/arsitektur.png`.

```
Tiga zona dengan hak berbeda. Zona baca (paket tender + profil perusahaan,
hanya baca). Zona putus (orkestrator: ekstraksi, pencocokan, keputusan, draf;
bekerja tetapi belum ada keluaran). Zona tulis (berkas .docx, ringkasan risiko,
log audit; hanya terbuka setelah persetujuan).

Antar zona dijaga empat komponen yang tugasnya menggagalkan sesuatu: verifikasi
kutipan, pemeriksa masa berlaku, detektor instruksi tersisip, dan penjaga
anti-karang.

Trade-off utama: keputusan lolos/tidak lolos dibuat deterministik agar dapat
dijalankan ulang dengan hasil identik, sedangkan lapisan bahasa dipakai untuk
membaca format dokumen yang tidak seragam dan merumuskan pertanyaan klarifikasi.
Konsekuensinya cakupan ekstraksi dibatasi pola yang dikenal, tetapi setiap
keputusan dapat dipertanggungjawabkan dan diuji ulang.
```

## Video demo

```
[tempel tautan video — YouTube tidak terdaftar / Google Drive]
```

Durasi 6 menit 50 detik. Menampilkan: masalah dan pengguna, solusi dan track,
arsitektur dan trust boundary, alur kerja lengkap, satu momen agen menolak, satu
momen agen meminta klarifikasi, satu momen agen menunggu persetujuan, serta dua
test case yang gagal.

## Berbagi produk WorkBuddy

```
WorkBuddy memberi nilai pada tiga hal.

Pertama, folder kerja sebagai unit. Satu folder berisi aturan (AGENTS.md),
masukan, keluaran, dan bukti uji. Siapa pun dapat membukanya dan memeriksa apa
yang dilakukan agen tanpa menjalankan apa pun. Untuk produk yang nilai jualnya
"dapat dipercaya", kemudahan diperiksa adalah fitur.

Kedua, AGENTS.md sebagai kebijakan, bukan prompt. Tujuh prinsip yang mengikat
seluruh sesi membuat prompt tugas cukup satu kalimat. Aturan yang tertulis di
AGENTS.md tidak luntur saat percakapan memanjang.

Ketiga, batas kewenangan yang dapat dinyatakan. Karena agen bekerja pada folder,
kami bisa menyatakan dengan tegas bahwa agen tidak punya akses jaringan, surel,
atau LPSE — bukan sebagai janji di dokumentasi, tetapi karena alatnya memang
tidak ada.

Pembelajaran utama: prompt saja tidak cukup untuk keputusan yang mengikat.
Aturan "jangan mengarang nomor sertifikat" baru benar-benar berlaku ketika ada
lapisan yang memeriksa bahwa setiap nomor di dokumen memang ada di basis
pengetahuan. Karena itu kami memisahkan lapisan agen (bahasa) dari lapisan
pemeriksa (deterministik), dan menjalankan keduanya berpasangan.
```

## Source code

```
[tempel tautan repositori publik]
```

Alternatif: lampirkan folder proyek (bentuk folder kerja WorkBuddy: `AGENTS.md`,
`input/`, `output/`, `tests/`) beserta tangkapan layar sesi WorkBuddy.

## Gambar sampul

Lampirkan `gambar/sampul.png` (380×216). Versi besar: `gambar/sampul_besar.png`.

## Tautan proyek (bonus)

```
[tempel tautan dashboard bila dipublikasikan]
```

---

## Catatan pengisian

1. Isi formulir dalam satu sesi agar tidak kehilangan tautan.
2. Unggah berkas dengan nama yang jelas, misalnya
   `TenderBuddy_Lembar_Akuntabilitas.pdf`.
3. Pastikan tautan video dan repositori dapat dibuka tanpa login (mode
   penyamaran).
4. Simpan salinan formulir yang sudah diisi (tangkapan layar halaman konfirmasi).
