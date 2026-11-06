"""Server web lokal TenderBuddy — antarmuka user-friendly untuk menjalankan agen.

Memungkinkan pengguna awam memilih paket tender, menjalankan agen dengan
satu klik, melihat hasil, dan menyetujui/menolak usulan — semua dari browser.

Cara menjalankan:
    python src/server_web.py

Lalu buka http://localhost:8080 di browser.
"""

from __future__ import annotations

import json
import sys
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

AKAR = Path(__file__).resolve().parent.parent
KELUARAN = AKAR / "output"


def keluaran_kasus(kasus_id: str) -> Path:
    """Folder output untuk satu kasus, agar antar-kasus tidak saling timpa."""
    return KELUARAN / kasus_id


# Daftar kasus yang tersedia
KASUS = [
    {
        "id": "kasus_1",
        "nama": "Kasus 1 — Gedung Serbaguna Balikpapan",
        "deskripsi": "Pembangunan gedung serbaguna, PT Karya Nusa Persada. Hasil diharapkan: LOLOS BERSYARAT.",
        "paket": str(AKAR / "input" / "paket_tender"),
        "profil": str(AKAR / "input" / "profil_perusahaan" / "profil_perusahaan.json"),
    },
    {
        "id": "kasus_2",
        "nama": "Kasus 2 — Rehabilitasi Jalan Samarinda",
        "deskripsi": "Rehabilitasi jalan, PT Sinar Karya Mandiri. SBU & sertifikat kadaluarsa. Hasil diharapkan: TIDAK LOLOS.",
        "paket": str(AKAR / "kasus_2" / "paket_tender"),
        "profil": str(AKAR / "kasus_2" / "profil_perusahaan" / "profil_perusahaan.json"),
    },
]

# Import pipeline functions
sys.path.insert(0, str(AKAR / "src"))
import pipeline as pl


class TenderBuddyHandler(BaseHTTPRequestHandler):
    def _kirim_json(self, data, kode=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(kode)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _kirim_html(self, html, kode=200):
        body = html.encode("utf-8")
        self.send_response(kode)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _kirim_file(self, path: Path, mime="text/plain"):
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Content-Disposition", f'attachment; filename="{path.name}"')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            self._kirim_html(_halaman_utama())
        elif path == "/api/kasus":
            self._kirim_json([{"id": k["id"], "nama": k["nama"], "deskripsi": k["deskripsi"]} for k in KASUS])
        elif path == "/api/status":
            self._kirim_json(_status_saat_ini())
        elif path.startswith("/api/berkas/"):
            bagian = path.split("/")
            if len(bagian) >= 5:
                kasus_id = bagian[3]
                nama = bagian[4]
            else:
                kasus_id = "kasus_1"
                nama = bagian[-1]
            f = keluaran_kasus(kasus_id) / "03_berkas_penawaran" / nama
            if f.exists():
                self._kirim_file(f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            else:
                self._kirim_json({"error": "Berkas tidak ditemukan"}, 404)
        elif path.startswith("/api/dashboard/"):
            kasus_id = path.split("/")[-1]
            d = keluaran_kasus(kasus_id) / "dashboard.html"
            if d.exists():
                self._kirim_html(d.read_text(encoding="utf-8"))
            else:
                self._kirim_html("<h1>Dashboard belum dibuat.</h1><p>Jalankan agen terlebih dahulu.</p>")
        elif path == "/api/dashboard":
            # fallback: arahkan ke dashboard kasus terakhir yang ada
            usulan_semua = sorted(KELUARAN.glob("*/usulan/*.json"))
            if usulan_semua:
                kasus_id = usulan_semua[-1].parent.parent.name
                d = keluaran_kasus(kasus_id) / "dashboard.html"
                if d.exists():
                    self._kirim_html(d.read_text(encoding="utf-8"))
                    return
            self._kirim_html("<h1>Dashboard belum dibuat.</h1><p>Jalankan agen terlebih dahulu.</p>")
        else:
            self._kirim_json({"error": "Tidak ditemukan"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/jalankan":
            body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
            data = json.loads(body)
            kasus_id = data.get("kasus_id", "kasus_1")
            kasus = next((k for k in KASUS if k["id"] == kasus_id), KASUS[0])

            try:
                # Reset output folder untuk kasus ini saja, jangan hapus kasus lain
                import shutil
                out = keluaran_kasus(kasus_id)
                if out.exists():
                    shutil.rmtree(out)
                out.mkdir(parents=True)

                # Run pipeline
                usulan = pl.rencana(
                    dir_paket=Path(kasus["paket"]),
                    path_profil=Path(kasus["profil"]),
                    keluar=out,
                )

                # Build dashboard untuk kasus ini
                sys.path.insert(0, str(AKAR / "src"))
                import buat_dashboard as bd
                bd.KELUARAN = out
                bd.bangun()

                self._kirim_json({
                    "status": "ok",
                    "kasus_id": kasus_id,
                    "verdict": usulan["verdict"],
                    "id_usulan": usulan["id"],
                    "ringkasan": usulan["ringkasan"],
                    "paket": usulan["paket"],
                    "berkas_dihasilkan": usulan.get("berkas_dihasilkan", []),
                    "tindakan": usulan.get("tindakan", []),
                    "klarifikasi": usulan.get("klarifikasi", []),
                    "risiko": usulan.get("risiko", []),
                    "tidak_akan_dilakukan": usulan.get("tidak_akan_dilakukan", []),
                    "dashboard_url": f"/api/dashboard/{kasus_id}",
                })
            except Exception as e:
                import traceback
                self._kirim_json({"status": "error", "pesan": str(e), "trace": traceback.format_exc()[:500]}, 500)

        elif path == "/api/setujui":
            body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
            data = json.loads(body)
            id_usulan = data.get("id_usulan", "")
            kasus_id = data.get("kasus_id", "kasus_1")

            try:
                kasus_setujui = next((k for k in KASUS if k["id"] == kasus_id), KASUS[0])
                out = keluaran_kasus(kasus_id)
                usulan = pl.setujui(id_usulan, keluar=out, path_profil=Path(kasus_setujui["profil"]))
                # Rebuild dashboard untuk kasus ini
                import buat_dashboard as bd
                bd.KELUARAN = out
                bd.bangun()

                self._kirim_json({
                    "status": "ok",
                    "kasus_id": kasus_id,
                    "berkas_dihasilkan": usulan.get("berkas_dihasilkan", []),
                    "pesan": f"{len(usulan.get('berkas_dihasilkan', []))} berkas berhasil ditulis.",
                })
            except SystemExit as e:
                self._kirim_json({"status": "ditolak", "pesan": str(e)}, 200)
            except Exception as e:
                self._kirim_json({"status": "error", "pesan": str(e)}, 500)

        elif path == "/api/tolak":
            body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
            data = json.loads(body)
            id_usulan = data.get("id_usulan", "")
            alasan = data.get("alasan", "")
            kasus_id = data.get("kasus_id", "kasus_1")

            try:
                out = keluaran_kasus(kasus_id)
                usulan = pl.tolak(id_usulan, alasan, keluar=out)
                import buat_dashboard as bd
                bd.KELUARAN = out
                bd.bangun()
                self._kirim_json({"status": "ok", "pesan": "Usulan ditolak. Tidak ada berkas yang ditulis."})
            except Exception as e:
                self._kirim_json({"status": "error", "pesan": str(e)}, 500)

        else:
            self._kirim_json({"error": "Tidak ditemukan"}, 404)

    def log_message(self, format, *args):
        # Suppress default logging
        pass


def _status_saat_ini() -> dict:
    """Cek output untuk setiap kasus yang sudah pernah dijalankan."""
    kasus_aktif = []
    for kasus_id in [k["id"] for k in KASUS]:
        usulan_dir = keluaran_kasus(kasus_id) / "usulan"
        usulan_path = sorted(usulan_dir.glob("*.json")) if usulan_dir.exists() else []
        if not usulan_path:
            continue
        usulan = json.loads(usulan_path[-1].read_text(encoding="utf-8"))
        berkas_dir = keluaran_kasus(kasus_id) / "03_berkas_penawaran"
        berkas_list = [f.name for f in berkas_dir.glob("*.docx")] if berkas_dir.exists() else []
        kasus_aktif.append({
            "kasus_id": kasus_id,
            "verdict": usulan.get("verdict"),
            "status": usulan.get("status"),
            "id_usulan": usulan.get("id"),
            "paket": usulan.get("paket", {}).get("nama"),
            "berkas_dihasilkan": berkas_list,
        })
    return {"ada_output": bool(kasus_aktif), "kasus": kasus_aktif}


def _halaman_utama() -> str:
    return """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TenderBuddy - Agen Berkas Penawaran LPSE</title>
<style>
  :root{
    --bg:#f5f6f8; --card:#ffffff; --line:#e3e6eb; --teks:#16181d; --redup:#5f6570;
    --biru:#1257d6; --biru-lembut:#eaf0fd; --hijau:#0d7a4f; --hijau-lembut:#e6f5ee;
    --merah:#b42318; --merah-lembut:#fdecea; --kuning:#b54708; --kuning-lembut:#fdf3e3;
  }
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:var(--bg);color:var(--teks);
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
    font-size:15px;line-height:1.6}
  .bungkus{max-width:820px;margin:0 auto;padding:32px 24px 80px}
  header{display:flex;align-items:center;gap:14px;margin-bottom:32px}
  .logo{width:48px;height:48px;border-radius:13px;background:var(--biru);color:#fff;
    display:flex;align-items:center;justify-content:center;font-weight:800;font-size:20px;letter-spacing:-.5px}
  h1{font-size:22px;letter-spacing:-.3px}
  .sub{color:var(--redup);font-size:14px;margin-top:2px}
  .kartu{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:24px;margin-bottom:16px}
  h2{font-size:17px;margin-bottom:12px;letter-spacing:-.2px}
  .kecil{font-size:13px;color:var(--redup)}
  .pilih-kasus{display:grid;gap:12px;margin-bottom:20px}
  .opsi{border:2px solid var(--line);border-radius:14px;padding:18px;cursor:pointer;
    transition:all .15s;background:var(--card)}
  .opsi:hover{border-color:var(--biru);background:var(--biru-lembut)}
  .opsi.terpilih{border-color:var(--biru);background:var(--biru-lembut)}
  .opsi h3{font-size:15px;margin-bottom:4px}
  .opsi .meta{font-size:12px;color:var(--redup);margin-top:6px}
  .tombol{display:inline-block;padding:12px 28px;border:0;border-radius:12px;
    font:inherit;font-size:15px;font-weight:700;cursor:pointer;transition:all .15s}
  .tombol-biru{background:var(--biru);color:#fff}
  .tombol-biru:hover{background:#0e47b0}
  .tombol-biru:disabled{background:#a0b4d8;cursor:not-allowed}
  .tombol-hijau{background:var(--hijau);color:#fff}
  .tombol-hijau:hover{background:#0a5e3d}
  .tombol-merah{background:transparent;color:var(--merah);border:2px solid var(--merah)}
  .tombol-merah:hover{background:var(--merah-lembut)}
  .tombol-kuning{background:var(--kuning);color:#fff}
  .tombol-kuning:hover{background:#923906}
  .baris-tombol{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
  .lencana{display:inline-block;font-size:12px;font-weight:700;padding:3px 10px;
    border-radius:99px;white-space:nowrap}
  .b-hijau{background:var(--hijau-lembut);color:var(--hijau)}
  .b-merah{background:var(--merah-lembut);color:var(--merah)}
  .b-kuning{background:var(--kuning-lembut);color:var(--kuning)}
  .b-biru{background:var(--biru-lembut);color:var(--biru)}
  .hasil{display:none}
  .hasil.tampil{display:block}
  .metrik{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:16px 0}
  .metrik .kartu{padding:16px;text-align:center}
  .metrik .angka{font-size:28px;font-weight:800;letter-spacing:-.8px;line-height:1.2}
  .metrik .label{font-size:11px;color:var(--redup);text-transform:uppercase;letter-spacing:.04em;margin-top:4px}
  .hijau{color:var(--hijau)} .merah{color:var(--merah)} .kuning{color:var(--kuning)}
  .catatan{border-left:3px solid var(--kuning);background:var(--kuning-lembut);padding:12px 16px;
    border-radius:0 8px 8px 0;font-size:14px;margin-bottom:8px}
  .berkas-item{display:flex;align-items:center;gap:12px;padding:12px;border:1px solid var(--line);
    border-radius:10px;background:#fafbfc;margin-bottom:8px}
  .ikon-dok{width:38px;height:38px;border-radius:9px;background:var(--biru-lembut);color:var(--biru);
    display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700}
  .loading{display:none;text-align:center;padding:40px}
  .loading.tampil{display:block}
  .spinner{width:40px;height:40px;border:4px solid var(--biru-lembut);border-top-color:var(--biru);
    border-radius:50%;animation:putar 1s linear infinite;margin:0 auto 12px}
  @keyframes putar{to{transform:rotate(360deg)}}
  .alur{display:flex;gap:6px;margin:12px 0}
  .langkah{flex:1;background:#fafbfc;border:1px solid var(--line);border-radius:10px;padding:8px 10px;text-align:center}
  .langkah .n{font-size:10px;color:var(--redup);font-weight:700}
  .langkah .t{font-weight:600;font-size:12px;margin-top:2px}
  .langkah.selesai{background:var(--hijau-lembut);border-color:#cfe8db}
  .langkah.tunggu{background:var(--kuning-lembut);border-color:#f0dcbd}
  .langkah.blokir{background:var(--merah-lembut);border-color:#f0ccc8}
  a{color:var(--biru);text-decoration:none;font-weight:600}
  a:hover{text-decoration:underline}
  .divider{height:1px;background:var(--line);margin:20px 0}
  .peringatan{border-left:3px solid var(--merah);background:var(--merah-lembut);padding:12px 16px;
    border-radius:0 8px 8px 0;font-size:14px;margin-bottom:8px}
</style>
</head>
<body>
<div class="bungkus">
  <header>
    <div class="logo">TB</div>
    <div>
      <h1>TenderBuddy</h1>
      <div class="sub">Agen berkas penawaran LPSE &middot; Baca dokumen tender, cek kepatuhan, buat berkas</div>
    </div>
  </header>

  <!-- LANGKAH 1: Pilih kasus -->
  <div class="kartu" id="langkah-pilih">
    <h2>1. Pilih paket tender</h2>
    <p class="kecil" style="margin-bottom:16px">Pilih salah satu paket di bawah. Agen akan membaca dokumen KAK, dokumen pengadaan, dan profil perusahaan.</p>
    <div class="pilih-kasus" id="daftar-kasus"></div>
  </div>

  <!-- LANGKAH 2: Jalankan agen -->
  <div class="kartu" id="langkah-jalankan">
    <h2>2. Jalankan agen</h2>
    <p class="kecil" style="margin-bottom:16px">Agen akan membaca paket, mengekstrak persyaratan, mencocokkan dengan profil perusahaan, dan mengeluarkan keputusan.</p>
    <button class="tombol tombol-biru" id="tombol-jalankan" onclick="jalankanAgen()">
      &rarr; Jalankan Agen
    </button>
  </div>

  <!-- LOADING -->
  <div class="loading" id="loading">
    <div class="spinner"></div>
    <p>Sedang membaca dokumen, mengekstrak persyaratan, dan mencocokkan profil...</p>
  </div>

  <!-- HASIL -->
  <div class="hasil" id="hasil">

    <!-- Ringkasan keputusan -->
    <div class="kartu">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:20px;flex-wrap:wrap">
        <div>
          <div class="kecil">Paket yang dinilai</div>
          <div style="font-size:18px;font-weight:700;margin-top:2px" id="hasil-paket">—</div>
          <div class="kecil" style="margin-top:4px" id="hasil-meta">—</div>
        </div>
        <div style="text-align:right">
          <div class="kecil">Keputusan agen</div>
          <div style="font-size:26px;font-weight:800" id="hasil-verdict">—</div>
        </div>
      </div>
      <div class="alur" id="hasil-alur"></div>
    </div>

    <!-- Metrik -->
    <div class="metrik" id="hasil-metrik"></div>

    <!-- Klarifikasi -->
    <div class="kartu" id="hasil-klarifikasi-box" style="display:none">
      <h2>Perlu klarifikasi</h2>
      <div id="hasil-klarifikasi"></div>
    </div>

    <!-- Risiko -->
    <div class="kartu" id="hasil-risiko-box" style="display:none">
      <h2>Risiko utama</h2>
      <div id="hasil-risiko"></div>
    </div>

    <!-- Agen tidak akan -->
    <div class="kartu">
      <h2>Agen tidak akan melakukan</h2>
      <div id="hasil-tidak-akan" class="kecil"></div>
    </div>

    <!-- LANGKAH 3: Persetujuan -->
    <div class="kartu" id="langkah-persetujuan">
      <h2>3. Persetujuan manusia</h2>
      <p class="kecil" style="margin-bottom:16px" id="teks-persetujuan">
        Agen sudah menyiapkan rencana. Tinjau hasil di atas, lalu putuskan:
      </p>
      <div class="baris-tombol" id="tombol-persetujuan">
        <button class="tombol tombol-hijau" id="tombol-setujui" onclick="setujuiUsulan()">
          &checkmark; Setujui &amp; Buat Berkas
        </button>
        <button class="tombol tombol-merah" id="tombol-tolak" onclick="tolakUsulan()">
          &times; Tolak
        </button>
        <a href="/api/dashboard" id="link-dashboard" target="_blank" class="tombol" style="background:var(--biru-lembut);color:var(--biru);border:2px solid var(--biru)">
          &nearr; Lihat Dashboard Lengkap
        </a>
      </div>
    </div>

    <!-- Hasil persetujuan -->
    <div class="kartu" id="hasil-persetujuan-box" style="display:none">
      <h2 id="hasil-persetujuan-judul">—</h2>
      <div id="hasil-persetujuan-isi"></div>
    </div>

  </div>

  <div style="margin-top:24px;text-align:center;font-size:12px;color:var(--redup)">
    Data sintetis untuk demo hackathon. Seluruh nomor dokumen fiktif.<br>
    TenderBuddy &copy; 2026 &middot; Track B - Agen Kantor
  </div>
</div>

<script>
let kasusTerpilih = null;
let usulanSaatIni = null;
let kasusSaatIni = null;

// Muat daftar kasus
fetch("/api/kasus").then(r => r.json()).then(kasus => {
  const div = document.getElementById("daftar-kasus");
  kasus.forEach((k, i) => {
    const el = document.createElement("div");
    el.className = "opsi" + (i === 0 ? " terpilih" : "");
    el.onclick = () => pilihKasus(k.id, el);
    el.innerHTML = `<h3>${k.nama}</h3><div class="kecil">${k.deskripsi}</div>`;
    div.appendChild(el);
  });
  if (kasus.length > 0) kasusTerpilih = kasus[0].id;
});

function pilihKasus(id, el) {
  kasusTerpilih = id;
  document.querySelectorAll(".opsi").forEach(o => o.classList.remove("terpilih"));
  el.classList.add("terpilih");
}

async function jalankanAgen() {
  document.getElementById("loading").classList.add("tampil");
  document.getElementById("hasil").classList.remove("tampil");
  document.getElementById("tombol-jalankan").disabled = true;

  try {
    const res = await fetch("/api/jalankan", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({kasus_id: kasusTerpilih})
    });
    const data = await res.json();

    document.getElementById("loading").classList.remove("tampil");
    document.getElementById("tombol-jalankan").disabled = false;

    if (data.status === "error") {
      alert("Error: " + data.pesan);
      return;
    }

    usulanSaatIni = data;
    kasusSaatIni = data.kasus_id || kasusTerpilih;
    tampilkanHasil(data);
  } catch (e) {
    document.getElementById("loading").classList.remove("tampil");
    document.getElementById("tombol-jalankan").disabled = false;
    alert("Gagal menjalankan agen: " + e.message);
  }
}

function tampilkanHasil(data) {
  const r = data.ringkasan || {};
  const verdictWarna = data.verdict === "LOLOS" ? "hijau" :
    data.verdict === "TIDAK LOLOS" ? "merah" : "kuning";
  const verdictLencana = data.verdict === "LOLOS" ? "b-hijau" :
    data.verdict === "TIDAK LOLOS" ? "b-merah" : "b-kuning";

  document.getElementById("hasil-paket").textContent = data.paket?.nama || "—";
  document.getElementById("hasil-meta").textContent =
    `Kode ${data.paket?.kode || "—"} · Pagu Rp${(data.paket?.pagu || 0).toLocaleString("id-ID")} · Batas ${data.paket?.batas_penawaran || "—"}`;

  // Dashboard link mengikuti kasus yang sedang aktif
  const dashLink = document.getElementById("link-dashboard");
  if (dashLink) {
    dashLink.href = `/api/dashboard/${kasusSaatIni || data.kasus_id || "kasus_1"}`;
  }

  const v = document.getElementById("hasil-verdict");
  v.textContent = data.verdict || "—";
  v.className = verdictWarna;

  // Alur langkah
  const langkahHtml = [
    ["1", "Baca paket", "selesai"],
    ["2", "Ekstraksi", "selesai"],
    ["3", "Cocokkan profil", "selesai"],
    ["4", "Keputusan", data.verdict === "TIDAK LOLOS" ? "blokir" : "selesai"],
    ["5", "Persetujuan", data.verdict === "TIDAK LOLOS" ? "blokir" : "tunggu"]
  ].map(([n,t,k]) =>
    `<div class="langkah ${k}"><div class="n">LANGKAH ${n}</div><div class="t">${t}</div></div>`
  ).join("");
  document.getElementById("hasil-alur").innerHTML = langkahHtml;

  // Metrik
  document.getElementById("hasil-metrik").innerHTML = `
    <div class="kartu"><div class="angka">${r.total || 0}</div><div class="label">Persyaratan</div></div>
    <div class="kartu"><div class="angka hijau">${r.memenuhi || 0}</div><div class="label">Memenuhi</div></div>
    <div class="kartu"><div class="angka kuning">${r.kurang_dokumen || 0}</div><div class="label">Kurang</div></div>
    <div class="kartu"><div class="angka merah">${r.tidak_memenuhi || 0}</div><div class="label">Tidak</div></div>
  `;

  // Klarifikasi
  const klarBox = document.getElementById("hasil-klarifikasi-box");
  if (data.klarifikasi && data.klarifikasi.length > 0) {
    klarBox.style.display = "block";
    document.getElementById("hasil-klarifikasi").innerHTML =
      data.klarifikasi.map(k => `<div class="catatan">${k.pertanyaan}</div>`).join("");
  } else {
    klarBox.style.display = "none";
  }

  // Risiko
  const risBox = document.getElementById("hasil-risiko-box");
  if (data.risiko && data.risiko.length > 0) {
    risBox.style.display = "block";
    document.getElementById("hasil-risiko").innerHTML =
      data.risiko.map(r => `<div class="${r.tingkat === "tinggi" ? "peringatan" : "catatan"}">
        <b>[${r.tingkat.toUpperCase()}]</b> ${r.judul}: ${r.uraian}<br>
        <span class="kecil">Tindakan: ${r.tindakan}</span>
      </div>`).join("");
  } else {
    risBox.style.display = "none";
  }

  // Agen tidak akan
  document.getElementById("hasil-tidak-akan").innerHTML =
    (data.tidak_akan_dilakukan || []).map(x => `&bull; ${x}`).join("<br>");

  // Persetujuan
  const persetujuanBox = document.getElementById("langkah-persetujuan");
  const tombolSetujui = document.getElementById("tombol-setujui");
  const tombolTolak = document.getElementById("tombol-tolak");
  const teksPersetujuan = document.getElementById("teks-persetujuan");

  if (data.verdict === "TIDAK LOLOS") {
    persetujuanBox.style.display = "block";
    tombolSetujui.style.display = "none";
    tombolTolak.style.display = "inline-block";
    teksPersetujuan.innerHTML = "<b style='color:var(--merah)'>Agen memutuskan TIDAK LOLOS.</b> Berkas tidak akan disusun. Anda dapat menolak untuk mencatat alasan, atau perbaiki data perusahaan lalu jalankan ulang.";
  } else if (data.berkas_dihasilkan && data.berkas_dihasilkan.length > 0) {
    persetujuanBox.style.display = "none";
  } else {
    persetujuanBox.style.display = "block";
    tombolSetujui.style.display = "inline-block";
    tombolTolak.style.display = "inline-block";
    teksPersetujuan.textContent = "Agen sudah menyiapkan rencana berkas. Tinjau hasil di atas, lalu putuskan:";
  }

  document.getElementById("hasil").classList.add("tampil");
  document.getElementById("hasil-persetujuan-box").style.display = "none";
}

async function setujuiUsulan() {
  if (!usulanSaatIni) return;
  document.getElementById("tombol-setujui").disabled = true;
  document.getElementById("tombol-setujui").textContent = "Memproses...";

  try {
    const res = await fetch("/api/setujui", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({id_usulan: usulanSaatIni.id_usulan, kasus_id: kasusSaatIni || "kasus_1"})
    });
    const data = await res.json();

    const box = document.getElementById("hasil-persetujuan-box");
    const judul = document.getElementById("hasil-persetujuan-judul");
    const isi = document.getElementById("hasil-persetujuan-isi");
    const kId = data.kasus_id || kasusSaatIni || "kasus_1";

    if (data.status === "ok") {
      judul.textContent = "Berkas berhasil dibuat";
      judul.className = "hijau";
      isi.innerHTML = `
        <p>${data.pesan}</p>
        <div style="margin-top:12px">
          ${data.berkas_dihasilkan.map(b => `
            <div class="berkas-item">
              <div class="ikon-dok">DOCX</div>
              <div><div style="font-weight:600">${b}</div>
              <a href="/api/berkas/${kId}/${b}">Unduh berkas</a></div>
            </div>
          `).join("")}
        </div>
        <a href="/api/dashboard/${kId}" target="_blank" class="tombol" style="display:inline-block;margin-top:12px;background:var(--biru-lembut);color:var(--biru);border:2px solid var(--biru);padding:8px 20px;border-radius:10px;text-decoration:none;font-weight:600">
          &nearr; Lihat Dashboard Lengkap
        </a>
      `;
    } else if (data.status === "ditolak") {
      judul.textContent = "Agen menolak membuat berkas";
      judul.className = "merah";
      isi.innerHTML = `<div class="peringatan">${data.pesan}</div>`;
    }

    box.style.display = "block";
    box.scrollIntoView({behavior: "smooth"});
  } catch (e) {
    alert("Gagal: " + e.message);
  }
  document.getElementById("tombol-setujui").disabled = false;
  document.getElementById("tombol-setujui").textContent = "\u2713 Setujui & Buat Berkas";
}

async function tolakUsulan() {
  if (!usulanSaatIni) return;
  const alasan = prompt("Alasan penolakan (opsional):", "");
  if (alasan === null) return;

  try {
    const res = await fetch("/api/tolak", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({id_usulan: usulanSaatIni.id_usulan, alasan: alasan || "Tanpa alasan", kasus_id: kasusSaatIni || "kasus_1"})
    });
    const data = await res.json();

    const box = document.getElementById("hasil-persetujuan-box");
    document.getElementById("hasil-persetujuan-judul").textContent = "Usulan ditolak";
    document.getElementById("hasil-persetujuan-judul").className = "merah";
    document.getElementById("hasil-persetujuan-isi").innerHTML =
      `<div class="peringatan">${data.pesan}</div>`;
    box.style.display = "block";
  } catch (e) {
    alert("Gagal: " + e.message);
  }
}

// Cek status saat ini (kasus mana saja yang sudah pernah dijalankan)
fetch("/api/status").then(r => r.json()).then(s => {
  if (s.ada_output && s.kasus && s.kasus.length > 0) {
    const div = document.createElement("div");
    div.className = "kartu";
    div.innerHTML = `<h2>Kasus yang sudah dijalankan</h2>
      <div class="kecil" style="margin-bottom:8px">Setiap kasus tersimpan di folder tersendiri sehingga tidak saling menimpa.</div>
      ${s.kasus.map(k => `
        <div class="berkas-item">
          <div class="ikon-dok">${k.kasus_id.replace("kasus_", "K")}</div>
          <div>
            <div style="font-weight:600">${k.paket || k.kasus_id}</div>
            <div class="kecil">${k.verdict} · ${k.status}${k.berkas_dihasilkan.length ? " · " + k.berkas_dihasilkan.length + " berkas" : ""}</div>
            ${k.berkas_dihasilkan.length ? `<a href="/api/dashboard/${k.kasus_id}" target="_blank">Dashboard</a>` : ""}
          </div>
        </div>
      `).join("")}`;
    document.querySelector(".bungkus").insertBefore(div, document.getElementById("langkah-pilih"));
  }
});
</script>
</body>
</html>"""


def jalankan_server(port=8080):
    server = HTTPServer(("127.0.0.1", port), TenderBuddyHandler)
    url = f"http://localhost:{port}"
    print(f"TenderBuddy berjalan di {url}")
    print("Buka browser ke alamat tersebut, atau tekan Ctrl+C untuk berhenti.")
    print()
    # Buka browser otomatis
    threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer dihentikan.")
        server.shutdown()


if __name__ == "__main__":
    jalankan_server()
