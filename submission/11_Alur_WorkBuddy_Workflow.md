# 11 — Alur sebagai WorkBuddy Workflow

## Ikhtisar

TenderBuddy dibangun sebagai **agen di dalam folder kerja WorkBuddy**. Seluruh
siklus hidup agen — aturan, masukan, proses, keluaran, dan bukti — berada dalam
satu folder yang dapat dibuka, diperiksa, dan dijalankan ulang oleh siapa pun.

```
┌─────────────────────────────────────────────────────────────┐
│  Folder Kerja WorkBuddy: TenderBuddy/                        │
│                                                              │
│  AGENTS.md  ← kebijakan agen (7 prinsip, 3 status, alur)     │
│      │                                                       │
│      ▼                                                       │
│  ┌──────────┐    ┌──────────────┐    ┌───────────────────┐  │
│  │ input/   │───►│ src/         │───►│ output/kasus_N/   │  │
│  │ paket    │    │ pipeline.py  │    │ berkas .docx      │  │
│  │ profil   │    │ ekstraksi.py │    │ matriks kepatuhan │  │
│  └──────────┘    │ pencocokan   │    │ log audit         │  │
│                  │ draf_dokumen │    │ dashboard.html    │  │
│                  └──────────────┘    └───────────────────┘  │
│                         │                                   │
│                    GERBANG PERSETUJUAN                      │
│                    (manusia wajib setuju)                   │
│                         │                                   │
│                         ▼                                   │
│                   5 berkas .docx ditulis                    │
│                                                              │
│  tests/    ← 20 test case akuntabilitas                     │
│  submission/ ← dokumen hackathon                            │
└─────────────────────────────────────────────────────────────┘
```

## Alur langkah demi langkah

### Langkah 1 — Siapkan folder kerja

Buka folder `TenderBuddy` di WorkBuddy. Struktur sudah siap:

- `AGENTS.md` — kontrak perilaku agen (7 prinsip, alur kerja baku, 3 status)
- `input/paket_tender/` — KAK/TOR + dokumen pengadaan (data sintetis)
- `input/profil_perusahaan/profil_perusahaan.json` — basis pengetahuan
- `src/` — mesin deterministik (Python)

### Langkah 2 — Jalankan agen

**Cara web (untuk pengguna awam):**

```bash
python src/server_web.py
```

Browser terbuka otomatis di `http://localhost:8080`. Pengguna:

1. Pilih paket tender (Kasus 1 atau Kasus 2).
2. Klik **Jalankan Agen**.
3. Lihat keputusan, metrik, klarifikasi, dan risiko.
4. Jika LOLOS, klik **Setujui & Buat Berkas**.
5. Unduh file `.docx` atau buka dashboard lengkap.

**Cara CLI (untuk pengembang):**

```bash
python src/pipeline.py rencana
python src/pipeline.py setujui --id USL-...
```

### Langkah 3 — Agen membaca dan mengekstrak (Zona Baca)

`ekstraksi.py` membaca seluruh dokumen di folder paket, menghasilkan:

- Daftar persyaratan terstruktur (kualifikasi, pengalaman, personil, SBU, pagu, jadwal)
- Setiap butir membawa: dokumen sumber, bagian, kutipan, dan status verifikasi
- Deteksi instruksi tersisip (keamanan prompt injection)

### Langkah 4 — Agen mencocokkan dan memutuskan (Zona Putus)

`pencocokan.py` membandingkan setiap persyaratan dengan profil perusahaan:

- **memenuhi** — bukti ditemukan, masih berlaku, nilainya cukup
- **kurang_dokumen** — bukti tidak ada (dapat dilengkapi)
- **tidak_memenuhi** — bukti ada tapi gagal (kadaluarsa, nilai kurang)

Keputusan paket:
- **LOLOS** — semua butir memenuhi
- **LOLOS BERSYARAT** — ada butir kurang_dokumen kritis
- **TIDAK LOLOS** — ada butir tidak_memenuhi → berkas tidak disusun

### Langkah 5 — Gerbang persetujuan manusia

Agen berhenti. Rencana tindakan disimpan ke `output/kasus_N/usulan/<id>.json`
dengan status `menunggu_persetujuan`. Tidak ada berkas final yang ditulis.

Jika keputusan **TIDAK LOLOS**, gerbang kepatuhan menolak sepenuhnya —
meskipun pengguna memaksa, sistem menolak menulis berkas.

### Langkah 6 — Penulisan berkas (Zona Tulis)

Setelah persetujuan tercatat, `draf_dokumen.py` menulis 5 berkas `.docx`:

1. `01_Surat_Penawaran.docx` — nilai penawaran dikosongkan
2. `02_Pakta_Integritas.docx` — komitmen direktur
3. `03_Daftar_Personil_Inti.docx` — pemetakan ke syarat KAK
4. `04_Tabel_Pengalaman_Sejenis.docx` — subkontraktor dikecualikan
5. `05_Lembar_Ringkasan_Risiko.docx` — temuan dan tindakan

Setiap berkas ditandai sebagai DRAF dan wajib ditandatangani manusia.

### Langkah 7 — Log audit

Setiap peristiwa dicatat ke `output/kasus_N/05_log_audit.jsonl` (append-only):
pembacaan, keputusan, penolakan, persetujuan, dan penulisan berkas.

## Pembagian peran: WorkBuddy vs kode deterministik

| Pekerjaan | Dikerjakan oleh | Alasan |
|---|---|---|
| Membaca dokumen dan menjelaskan isinya | WorkBuddy (LLM) | Format tidak seragam, butuh penalaran bahasa |
| Merumuskan pertanyaan klarifikasi | WorkBuddy (LLM) | Harus enak dibaca manusia |
| Menyusun narasi ringkasan risiko | WorkBuddy (LLM) | Pengguna butuh kalimat, bukan tabel mentah |
| Menentukan status tiap syarat | Kode deterministik | Harus dapat dijalankan ulang dengan hasil identik |
| Memeriksa masa berlaku sertifikat | Kode deterministik | Perbandingan tanggal tidak boleh meleset |
| Menegakkan gerbang persetujuan | Kode deterministik | Tidak boleh bisa "dibujuk" lewat percakapan |
| Menulis log audit | Kode deterministik | Harus append-only, tidak dapat dihapus agen |

## Dua kasus demo

| Kasus | Paket | Perusahaan | Hasil diharapkan |
|---|---|---|---|
| 1 | Gedung Serbaguna, Balikpapan | PT. Karya Karya Karya | LOLOS BERSYARAT |
| 2 | Rehabilitasi Jalan, Samarinda | PT. Sinar Sinar Sinar | TIDAK LOLOS |

Setiap kasus disimpan di folder output terpisah (`output/kasus_1/` dan
`output/kasus_2/`) sehingga tidak saling menimpa.
