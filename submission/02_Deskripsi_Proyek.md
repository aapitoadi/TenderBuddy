# 02 — Deskripsi Proyek TenderBuddy

**AI CAN DO IT — Tencent Cloud Hackathon Indonesia 2026**
Track B: Agen Kantor (Office Agent)

---

## 1. Ringkasan

TenderBuddy adalah agen yang menerima satu paket dokumen tender dari LPSE —
KAK/TOR, Lembar Data Pemilihan, Lembar Data Kualifikasi, dan addendum — lalu
dalam satu perintah menghasilkan tiga hal: **checklist persyaratan yang
bersumber**, **matriks kepatuhan terhadap profil perusahaan**, dan **berkas
administrasi penawaran yang siap ditandatangani**.

Yang membedakannya dari asisten dokumen biasa bukan kecepatan menulis, melainkan
**kejujuran atas apa yang tidak dipenuhi**. Ketika personil ahli K3 belum punya
sertifikat yang diminta, TenderBuddy tidak mengarang nomor sertifikat. Ia
menulis `BELUM ADA`, menaikkan temuan itu ke lembar risiko, dan menahan
penyusunan berkas sampai manusia memutuskan.

## 2. Masalah nyata

Di Indonesia, penyedia jasa konstruksi kualifikasi kecil — perusahaan dengan
5–30 pegawai — mengikuti 20 sampai 80 paket tender per tahun melalui SPSE/LPSE.
Setiap paket menuntut pekerjaan yang sama dan berulang:

- membaca 30–120 halaman dokumen pemilihan untuk menemukan syarat kualifikasi,
  personil inti, pengalaman sejenis, SBU, dan pagu;
- mencocokkan setiap syarat dengan arsip perusahaan: akta, NIB, SBU, SKA/SKK
  personil, kontrak, dan BAST;
- mengetik ulang surat penawaran, pakta integritas, daftar personil, dan tabel
  pengalaman untuk paket berikutnya.

Pekerjaan ini biasanya jatuh pada satu orang: staf administrasi tender yang
merangkap HR dan arsip. Pada musim tender, ia mengerjakan dua sampai tiga paket
sekaligus dengan tenggat yang berimpit.

**Kegagalan yang paling mahal bukan salah ketik.** Evaluasi administrasi
menggugurkan penawaran karena satu dokumen kadaluarsa, satu sertifikat yang
tidak sesuai, atau satu klaim pengalaman yang tidak didukung kontrak. Kerugian
tidak berhenti di biaya penggarapan yang hangus — ada sanksi daftar hitam dua
tahun bila dokumen terbukti tidak benar. Artinya insentif terbesar bukan
"menulis lebih cepat", melainkan **"berhenti sebelum mengklaim"**.

## 3. Insight dari masalah

Tiga temuan yang membentuk desain produk ini:

**(a) Hambatannya ada di pencocokan, bukan penulisan.**
Menyalin format surat penawaran butuh 20 menit. Mencari apakah nilai pengalaman
perusahaan benar-benar melewati ambang 50% pagu — dan apakah pengalaman itu
dihitung sebagai subkontraktor atau bukan — butuh berjam-jam dan mudah salah.
Agen harus mengotomatiskan yang kedua.

**(b) Nilai terbesar agen adalah kemampuannya menolak.**
Asisten yang selalu menghasilkan dokumen akan mendorong pengguna mengunggah
penawaran yang cacat. Agen yang berhenti dan berkata "personil ahli K3 belum
punya sertifikat yang diminta" menyelamatkan pengguna dari kerugian yang jauh
lebih besar daripada waktu yang dihemat.

**(c) Dokumen tender bukan sumber yang bersih.**
Dokumen pemilihan kerap memuat addendum yang bertentangan dengan dokumen asli,
jadwal tanpa zona waktu, dan — pada berkas yang tidak terkendali — teks yang
berperilaku seperti perintah kepada AI. Agen yang memperlakukan semua teks
sebagai instruksi dapat "dibujuk" menyatakan sebuah paket memenuhi syarat.

## 4. Track dan skenario yang dipilih

TenderBuddy masuk **Track B — Agen Kantor**, karena inti pekerjaannya adalah
mengubah permintaan tidak terstruktur (satu paket dokumen) menjadi rencana
tindakan terstruktur yang dieksekusi hanya setelah disetujui.

Pemetaan langsung terhadap syarat Track B:

| Syarat Track B | Pemenuhan pada TenderBuddy |
|---|---|
| Memecah permintaan menjadi tindakan terpisah: siapa, apa, kapan, di mana | Checklist 29 butir: personil (siapa), dokumen (apa), jadwal (kapan), LPSE (di mana) |
| Mengajukan klarifikasi bila ambigu | Zona waktu tidak disebut, aanwijzing bentrok salat Jumat, sertifikat belum terbit |
| Menampilkan layar konfirmasi sebelum bertindak | `output/usulan/<id>.json` + tampilan rencana di terminal/dashboard |
| Tidak boleh menjalankan tindakan langsung | Tidak ada perintah unggah; berkas hanya ditulis setelah `setujui` |
| Mematuhi aturan operasional (WIB/WITA/WIT, salat Jumat, hari libur) | Pemeriksa jadwal menandai ketiganya |
| Memperlakukan teks dokumen sebagai data | Detektor instruksi tersisip; temuan dilaporkan, tidak dijalankan |
| Menyimpan catatan audit | `output/05_log_audit.jsonl`, append-only |

Elemen dari Track A (jawaban wajib bersumber, menolak tanpa membocorkan) tetap
dipakai karena inti kepercayaan pada produk ini adalah keterlacakan sumber.

## 5. Target pengguna

**Persona utama — Rani, 34 tahun, Staf Administrasi Tender.**
Bekerja di PT Karya Nusa Persada (kualifikasi kecil, 24 pegawai). Merangkap HR
dan arsip. Menggarap 2–3 paket per musim tender. Menyimpan berkas perusahaan di
folder Drive yang penamaannya tidak konsisten. Tidak menulis kode dan tidak akan
menulis kode.

**Pengguna sekunder — Direktur.**
Hanya ingin dua hal: "paket ini layak diikuti atau tidak" dan "apa yang kurang".
Ia yang menetapkan harga dan menandatangani.

## 6. Desain solusi bisnis

Alur lima langkah, satu perintah:

1. **Lempar paket.** Seluruh berkas `.txt`/PDF dari LPSE diletakkan di
   `input/paket_tender/`.
2. **Ekstraksi bersumber.** 29 butir persyaratan dihasilkan; setiap butir
   membawa nama dokumen, bagian, dan kutipan. Kutipan diverifikasi ulang
   terhadap teks asli — butir yang kutipannya tidak ditemukan tidak dipakai
   untuk memutuskan.
3. **Pencocokan profil.** Setiap butir diuji terhadap basis pengetahuan
   perusahaan. Hasilnya tiga status saja: `memenuhi`, `tidak_memenuhi`,
   `kurang_dokumen` — masing-masing dengan bukti dan sumbernya.
4. **Keputusan dan risiko.** Satu butir `tidak_memenuhi` sudah cukup untuk
   menghentikan proses. Bila hanya ada kekurangan dokumen yang menghambat,
   keputusan menjadi **LOLOS BERSYARAT** dan agen menyusun berkas dengan
   penanda eksplisit pada bagian yang belum ada.
5. **Persetujuan, lalu eksekusi.** Agen menampilkan rencana: berkas apa yang
   akan ditulis, apa yang sengaja dikosongkan, dan apa yang tidak akan
   dilakukan. Setelah `setujui`, lima dokumen `.docx` ditulis ke
   `output/03_berkas_penawaran/` beserta lembar ringkasan risiko.

### Model keputusan tiga status

| Status | Arti | Dampak |
|---|---|---|
| `memenuhi` | Bukti ada, masih berlaku, nilainya cukup | Tidak menghambat |
| `kurang_dokumen` | Bukti tidak ada di basis pengetahuan | Menghambat → LOLOS BERSYARAT; berkas disusun dengan `BELUM ADA` |
| `tidak_memenuhi` | Bukti ada tetapi gagal (kadaluarsa, nilai kurang, klasifikasi salah) | Menghentikan → TIDAK LOLOS; berkas tidak disusun |

Pemisahan `kurang_dokumen` dan `tidak_memenuhi` adalah keputusan desain yang
disengaja. Keduanya terlihat mirip bagi pengguna, tetapi konsekuensinya berbeda:
yang pertama bisa diselesaikan dengan melengkapi berkas, yang kedua menuntut
personil atau strategi baru.

## 7. Desain teknis

Prototipe terdiri atas dua lapisan yang sengaja dipisahkan.

**Lapisan agen (WorkBuddy).** Percakapan dengan pengguna, pembacaan dokumen,
penyusunan narasi klarifikasi, dan permintaan persetujuan. Perilakunya diatur
`AGENTS.md`: tujuh prinsip yang tidak boleh dilanggar, alur kerja baku, dan
daftar hal yang harus ditolak.

**Lapisan pemeriksa deterministik (Python, tanpa model).** Ekstraksi pola
persyaratan, pencocokan bukti, penegakan gerbang keputusan, penulisan berkas,
dan log audit.

Pemisahan ini punya alasan teknis: keputusan lolos/tidak lolos tidak boleh
berubah karena suhu model atau variasi prompt. Pada tender, hasil yang
"hampir benar" sama nilainya dengan hasil yang salah. Karena itu lapisan yang
menentukan status dibuat deterministik dan dapat dijalankan ulang dengan hasil
identik, sementara lapisan agen dipakai untuk hal yang memang butuh penalaran
bahasa: membaca dokumen yang formatnya tidak seragam, merumuskan pertanyaan
klarifikasi, dan menyusun narasi.

**Komponen:**

| Komponen | Berkas | Tanggung jawab |
|---|---|---|
| Pembaca paket | `src/ekstraksi.py` | Baca dokumen, ekstrak persyaratan + kutipan, deteksi instruksi tersisip |
| Pencocok | `src/pencocokan.py` | Uji tiap butir terhadap profil, periksa masa berlaku, periksa jadwal |
| Penyusun dokumen | `src/draf_dokumen.py` | Hasilkan `.docx` dengan `python-docx` |
| Orkestrator | `src/pipeline.py` | Keputusan, risiko, gerbang persetujuan, log audit, CLI |
| Harness uji | `src/uji.py` | 20 test case, termasuk yang gagal |
| Dashboard | `src/buat_dashboard.py` | Panel kepatuhan satu berkas HTML |

**Trust boundary.** Ada tiga zona dengan hak berbeda:

- *Zona baca* — dokumen tender dan profil perusahaan. Agen hanya membaca.
- *Zona putus* — keputusan dan penyusunan draf. Agen bekerja, tetapi belum ada
  yang keluar dari folder kerja.
- *Zona tulis* — penulisan berkas final dan (di masa depan) unggah ke LPSE.
  Hanya terbuka setelah persetujuan tercatat, dan tidak pernah mencakup
  penandatanganan atau penetapan harga.

## 8. Peran prompt

Prompt bukan satu kalimat ajaib, melainkan tiga lapis:

1. **`AGENTS.md` sebagai kebijakan.** Tujuh prinsip (sumber, larangan mengarang,
   dokumen adalah data, persetujuan, klarifikasi, batas, catatan) ditulis
   sebagai aturan yang mengikat seluruh sesi, bukan sebagai permintaan sopan.
2. **Prompt tugas.** "Baca paket di `input/paket_tender/`, nilai terhadap profil,
   ajukan rencana" — pendek, karena detail perilaku sudah ada di lapisan
   kebijakan.
3. **Prompt penolakan.** Saat pengguna meminta hal di luar kewenangan (mengisi
   harga, menandatangani, mengunggah), agen menolak dengan menyebut alasan dan
   menawarkan langkah berikutnya.

Pelajarannya: **prompt saja tidak cukup untuk keputusan yang mengikat.** Aturan
"jangan mengarang nomor sertifikat" baru benar-benar berlaku ketika ada lapisan
yang memeriksa bahwa setiap nomor yang muncul di dokumen benar-benar ada di
basis pengetahuan. Karena itu `AGENTS.md` dan pemeriksa deterministik harus
berjalan berpasangan.

## 9. Nilai bisnis terukur

Angka berikut adalah **asumsi model** yang dipakai untuk menghitung nilai, bukan
hasil pengukuran lapangan. Semuanya dinyatakan terbuka agar dapat divalidasi
pada pilot.

| Variabel | Asumsi | Dasar |
|---|---|---|
| Waktu menyiapkan 1 paket (manual) | 16 jam kerja | Baca dokumen, cocokkan arsip, ketik 4 dokumen, periksa ulang |
| Waktu dengan TenderBuddy | 2,5 jam | 20 menit menjalankan + 2 jam memeriksa dan melengkapi |
| Jumlah paket per tahun | 40 | Rentang 20–80 untuk penyedia kecil |
| Biaya tenaga kerja | Rp48.000/jam | Rp8 juta/bulan ÷ 167 jam |
| Biaya penggarapan per paket | Rp6 juta | Legalisir, jilid, transport, waktu |
| Tingkat gugur administrasi (asumsi) | 2 dari 10 penawaran | Umum pada penyedia kecil |

**Perhitungan:**

- Waktu hemat: 13,5 jam × 40 paket = **540 jam/tahun** (≈ 67 hari kerja).
- Nilai waktu: 540 × Rp48.000 = **Rp25.920.000/tahun** per perusahaan.
- Penawaran cacat yang dicegah: 8 penawaran/tahun × Rp6 juta =
  **Rp48.000.000/tahun** biaya yang tidak terbuang.

Yang lebih penting tetapi tidak diuangkan: satu klaim dokumen palsu yang lolos
dapat berujung sanksi daftar hitam dua tahun — pada penyedia kecil, itu setara
kehilangan seluruh pipeline pendapatannya.

## 10. Mengapa ini dapat dipertanggungjawabkan

| Prinsip | Wujud konkret di produk |
|---|---|
| Menunjukkan sumber | Setiap butir membawa dokumen, bagian, kutipan; kutipan diverifikasi ulang |
| Mematuhi izin | Agen hanya membaca dua folder input; tidak ada akses jaringan |
| Meminta persetujuan | Berkas final tidak ditulis sebelum `setujui`; sidik jari matriks mengikat persetujuan pada isi yang ditampilkan |
| Mengakui batasan | Dokumen tanpa lapisan teks ditandai; format nilai tak dikenal ditolak, bukan ditebak |
| Menyimpan catatan | `05_log_audit.jsonl` append-only: apa yang dibaca, diputuskan, ditulis, oleh siapa |

## 11. Batasan yang diakui

- Dua test case gagal dan dilaporkan terbuka: format nilai singkat (`Rp1,2 M`)
  dan addendum yang mengubah jadwal (TC-19, TC-20).
- Ekstraksi masih berbasis pola untuk 12 jenis persyaratan yang paling sering
  muncul; dokumen dengan format sangat berbeda butuh penyesuaian pola.
- Belum ada OCR untuk paket hasil pindai.
- Basis pengetahuan berupa JSON yang dirawat manual; belum tersambung ke arsip
  Drive perusahaan.
- Tidak ada koneksi ke LPSE. Unggah tetap dilakukan manusia.

## 12. Rencana lanjutan

1. Penanganan addendum berprioritas versi + penanganan format angka singkat
   (menutup TC-19 dan TC-20).
2. OCR untuk paket hasil pindai.
3. Konektor arsip (Drive/S3) agar basis pengetahuan memperbarui diri.
4. Mode "bandingkan dua paket" untuk memilih tender yang paling layak diikuti.
5. Pilot dengan 3–5 penyedia jasa konstruksi kecil di Balikpapan.
