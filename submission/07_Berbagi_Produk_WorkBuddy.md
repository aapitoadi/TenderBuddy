# 07 — Berbagi Produk: Di Mana WorkBuddy Memberi Nilai Tambah

## 1. Mengapa kami membangun di WorkBuddy

Tiga hal yang membuat WorkBuddy cocok untuk kasus ini, dan bukan sekadar alat
untuk menulis kode:

**Folder kerja sebagai unit.** Panduan menyebut "folder kerja di WorkBuddy" —
dan ternyata itu keputusan desain yang kuat, bukan formalitas. Satu folder
berisi aturan (`AGENTS.md`), masukan (`input/`), keluaran (`output/`), dan bukti
(`tests/`). Siapa pun — juri, calon pengguna, atau rekan tim — dapat membuka
folder itu dan melihat apa yang dilakukan agen tanpa menjalankan apa pun. Untuk
produk yang nilai jualnya "dapat dipercaya", kemudahan diperiksa adalah fitur.

**`AGENTS.md` sebagai kebijakan, bukan prompt.** Kami menulis tujuh prinsip yang
tidak boleh dilanggar, alur kerja baku, tiga status keputusan, dan daftar hal
yang harus ditolak. Setelah itu, prompt tugas cukup satu kalimat. Perbedaan
antara "prompt yang diulang setiap percakapan" dan "aturan yang mengikat
seluruh sesi" ternyata besar: yang pertama mudah luntur saat percakapan
memanjang, yang kedua tetap berlaku.

**Batas kewenangan yang dapat dinyatakan.** Karena agen bekerja pada folder,
kami bisa menyatakan dengan tegas: agen tidak punya akses jaringan, surel, atau
LPSE. Batas itu bukan janji di dokumentasi — memang tidak ada alatnya.

## 2. Pembagian kerja: apa yang dikerjakan WorkBuddy, apa yang tidak

| Pekerjaan | Dikerjakan oleh | Alasan |
|---|---|---|
| Membaca dokumen dan menjelaskan isinya | WorkBuddy | Format dokumen tidak seragam; butuh penalaran bahasa |
| Merumuskan pertanyaan klarifikasi | WorkBuddy | Harus enak dibaca manusia, bukan sekadar kode galat |
| Menyusun narasi ringkasan risiko | WorkBuddy | Pengguna butuh kalimat, bukan tabel mentah |
| Menentukan status tiap syarat | Kode deterministik | Harus dapat dijalankan ulang dengan hasil identik |
| Memeriksa masa berlaku sertifikat | Kode deterministik | Perbandingan tanggal tidak boleh meleset |
| Menegakkan gerbang persetujuan | Kode deterministik | Tidak boleh bisa "dibujuk" lewat percakapan |
| Menulis log audit | Kode deterministik | Harus append-only dan tidak dapat dihapus agen |

Kami tidak menyerahkan keputusan yang mengikat kepada model bahasa. Bukan
karena model tidak mampu, tetapi karena keputusan tender harus dapat
dipertanggungjawabkan ulang enam bulan kemudian — dan itu menuntut hasil yang
sama setiap kali dijalankan.

## 3. Empat pembelajaran utama

**(1) Agen yang baik harus punya sesuatu yang gagal.**
Empat komponen terpenting di arsitektur kami — verifikasi kutipan, pemeriksa
masa berlaku, detektor instruksi tersisip, penjaga anti-karang — semuanya
bekerja dengan cara menggagalkan sesuatu. Tidak satu pun menghasilkan keluaran.
Di awal kami mengira nilai produk ada pada dokumen yang dihasilkan; ternyata
nilainya ada pada dokumen yang **tidak** dihasilkan.

**(2) "Kurang dokumen" dan "tidak memenuhi" harus dipisah.**
Versi pertama kami hanya punya dua status: memenuhi dan tidak. Hasilnya, agen
menyamakan dua masalah yang biayanya sangat berbeda — "lengkapi surat dukungan
bank" dan "personil Anda tidak memenuhi syarat". Pemisahan tiga status membuat
keluaran agen bisa langsung ditindaklanjuti.

**(3) Persetujuan harus mengikat pada isi, bukan pada niat.**
Kami menyimpan sidik jari (hash) matriks kepatuhan pada saat persetujuan. Bila
dokumen berubah di antara "rencana" dan "setujui", sidik jari tidak cocok dan
persetujuan batal. Ini friksi yang kami tambahkan dengan sengaja: lebih baik
pengguna menyetujui dua kali daripada menyetujui satu penilaian lalu
mengeksekusi penilaian lain.

**(4) Kejujuran lebih sulit dari kecerdasan.**
Bagian tersulit dari proyek ini bukan membuat agen menemukan syarat, melainkan
membuatnya berhenti ketika tidak menemukan bukti. Model bahasa secara alami
cenderung mengisi kekosongan. Menahan kecenderungan itu butuh aturan, penjaga,
dan keberanian menampilkan `BELUM ADA` di dokumen yang akan ditandatangani
direktur.

## 4. Catatan tentang tooling

**Yang sangat membantu:**

- Folder kerja membuat "keadaan agen" menjadi konkret dan dapat diperiksa.
- `AGENTS.md` memisahkan kebijakan dari tugas, sehingga tugas bisa pendek.
- Kredit gratis per peserta cukup untuk seluruh iterasi pengembangan dan
  pengujian 20 test case.
- Karena tidak perlu menulis kode untuk memulai, waktu habis untuk memikirkan
  perilaku agen — bukan untuk menyiapkan lingkungan.

**Yang kami hadapi:**

- Menjaga konsistensi antara `AGENTS.md` dan kode penegak aturan butuh disiplin;
  mudah terjadi aturan tertulis di dokumen tetapi tidak ditegakkan di kode.
  Kami menutupnya dengan test case yang secara khusus menguji kepatuhan
  (TC-14, TC-17, TC-18).
- Data uji harus dibuat sendiri. Untuk kasus LPSE, membuat paket tender sintetis
  yang realistis memakan waktu hampir sama dengan membangun agennya.
- Demonstrasi hasil lebih meyakinkan lewat berkas nyata (`.docx`) daripada
  tangkapan layar percakapan — sehingga kami memilih menghasilkan dokumen
  sungguhan.

## 5. Saran untuk peserta berikutnya

1. **Pilih satu pengguna dan satu alur.** Kami sempat ingin menambahkan
   penilaian harga dan penyusunan metode pelaksanaan. Keduanya kami buang, dan
   demo menjadi jauh lebih mudah dipercaya.
2. **Rancang satu kasus yang harus gagal, lalu tunjukkan.** Juri lebih percaya
   pada agen yang berhenti daripada agen yang selalu berhasil.
3. **Simpan bukti sejak awal.** Log audit, hasil uji, dan tangkapan layar yang
   dikumpulkan sambil membangun jauh lebih murah daripada direkonstruksi di
   akhir.
4. **Jangan sembunyikan kegagalan.** Dua test case kami gagal dan tetap
   ditampilkan. Menyembunyikannya justru mengundang pertanyaan yang lebih sulit
   di sesi tanya jawab.
