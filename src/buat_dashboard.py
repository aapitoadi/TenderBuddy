"""Membangun dashboard HTML satu berkas untuk demo dan tangkapan layar."""

from __future__ import annotations

import json
from pathlib import Path

AKAR = Path(__file__).resolve().parent.parent
KELUARAN = AKAR / "output"


def _muat(path: Path, bawaan=None):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return bawaan


def bangun() -> Path:
    checklist = _muat(KELUARAN / "01_checklist_persyaratan.json", {})
    matriks = _muat(KELUARAN / "02_matriks.json", [])
    usulan_path = sorted((KELUARAN / "usulan").glob("*.json"))
    usulan = _muat(usulan_path[-1], {}) if usulan_path else {}
    audit = []
    p_audit = KELUARAN / "05_log_audit.jsonl"
    if p_audit.exists():
        audit = [json.loads(x) for x in p_audit.read_text(encoding="utf-8").splitlines() if x.strip()]
    uji = _muat(AKAR / "tests" / "hasil_uji.json", {"ringkasan": {}, "kasus": []})

    data = {"checklist": checklist, "matriks": matriks, "usulan": usulan,
            "audit": audit, "uji": uji}
    isi = json.dumps(data, ensure_ascii=False)

    html = """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TenderBuddy - Dashboard Kepatuhan Tender</title>
<style>
  :root{
    --bg:#f5f6f8; --card:#ffffff; --line:#e3e6eb; --teks:#16181d; --redup:#5f6570;
    --biru:#1257d6; --biru-lembut:#eaf0fd; --hijau:#0d7a4f; --hijau-lembut:#e6f5ee;
    --merah:#b42318; --merah-lembut:#fdecea; --kuning:#b54708; --kuning-lembut:#fdf3e3;
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--teks);
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
    font-size:14px;line-height:1.55}
  .bungkus{max-width:1180px;margin:0 auto;padding:28px 24px 64px}
  header{display:flex;align-items:flex-start;justify-content:space-between;gap:24px;margin-bottom:22px}
  .merek{display:flex;gap:12px;align-items:center}
  .logo{width:42px;height:42px;border-radius:11px;background:var(--biru);color:#fff;display:flex;
    align-items:center;justify-content:center;font-weight:700;font-size:18px;letter-spacing:-.5px}
  h1{font-size:20px;margin:0;letter-spacing:-.3px}
  .sub{color:var(--redup);font-size:13px;margin-top:2px}
  .pil{font-size:12px;padding:4px 10px;border-radius:99px;background:var(--biru-lembut);
    color:var(--biru);font-weight:600;white-space:nowrap}
  .kartu{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px 22px}
  .grid{display:grid;gap:14px}
  .g4{grid-template-columns:repeat(4,1fr)}
  .g3{grid-template-columns:repeat(3,1fr)}
  .metrik .angka{font-size:26px;font-weight:700;letter-spacing:-.8px;line-height:1.2}
  .metrik .label{font-size:12px;color:var(--redup);text-transform:uppercase;letter-spacing:.04em}
  .metrik .ket{font-size:12px;color:var(--redup);margin-top:4px}
  .hijau{color:var(--hijau)} .merah{color:var(--merah)} .kuning{color:var(--kuning)} .biru{color:var(--biru)}
  .tabs{display:flex;gap:4px;margin:24px 0 16px;border-bottom:1px solid var(--line);flex-wrap:wrap}
  .tab{padding:9px 14px;border:0;background:none;font:inherit;font-weight:600;color:var(--redup);
    cursor:pointer;border-bottom:2px solid transparent;margin-bottom:-1px}
  .tab.aktif{color:var(--biru);border-bottom-color:var(--biru)}
  .panel{display:none;padding-top:2px} .panel.aktif{display:block}
  table{width:100%;border-collapse:collapse;font-size:13px}
  th{text-align:left;font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:var(--redup);
    padding:9px 10px;border-bottom:1px solid var(--line);font-weight:700}
  td{padding:9px 10px;border-bottom:1px solid #eef0f3;vertical-align:top}
  tr:last-child td{border-bottom:0}
  .lencana{display:inline-block;font-size:11px;font-weight:700;padding:2px 8px;border-radius:99px;white-space:nowrap}
  .b-hijau{background:var(--hijau-lembut);color:var(--hijau)}
  .b-merah{background:var(--merah-lembut);color:var(--merah)}
  .b-kuning{background:var(--kuning-lembut);color:var(--kuning)}
  .b-abu{background:#eef0f3;color:var(--redup)}
  .b-biru{background:var(--biru-lembut);color:var(--biru)}
  .alur{display:flex;gap:8px;align-items:stretch;margin-top:6px}
  .langkah{flex:1;background:#fafbfc;border:1px solid var(--line);border-radius:10px;padding:10px 12px}
  .langkah .n{font-size:11px;color:var(--redup);font-weight:700}
  .langkah .t{font-weight:600;font-size:13px;margin-top:2px}
  .langkah.selesai{background:var(--hijau-lembut);border-color:#cfe8db}
  .langkah.tunggu{background:var(--kuning-lembut);border-color:#f0dcbd}
  .kode{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12px}
  #p1 td:first-child,#p2 td:first-child,#p6 td:first-child{white-space:nowrap}
  .kecil{font-size:12px;color:var(--redup)}
  ul.rapat{margin:8px 0 0;padding-left:18px} ul.rapat li{margin:3px 0}
  .dua{display:grid;grid-template-columns:1.15fr .85fr;gap:14px}
  h2{font-size:15px;margin:0 0 12px;letter-spacing:-.2px}
  h3{font-size:13px;margin:18px 0 8px;color:var(--redup);text-transform:uppercase;letter-spacing:.05em}
  .catatan{border-left:3px solid var(--kuning);background:var(--kuning-lembut);padding:10px 14px;
    border-radius:0 8px 8px 0;font-size:13px}
  .berkas{display:flex;gap:12px;align-items:center;padding:12px 14px;border:1px solid var(--line);
    border-radius:10px;background:#fafbfc;margin-bottom:8px}
  .ikon{width:34px;height:34px;border-radius:8px;background:var(--biru-lembut);color:var(--biru);
    display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700}
  footer{margin-top:28px;font-size:12px;color:var(--redup);text-align:center}
</style>
</head>
<body>
<div class="bungkus">
  <header>
    <div class="merek">
      <div class="logo">TB</div>
      <div>
        <h1>TenderBuddy</h1>
        <div class="sub">Agen berkas penawaran LPSE &middot; Panel kepatuhan dan jejak audit</div>
      </div>
    </div>
    <div class="pil">Track B &middot; Agen Kantor</div>
  </header>

  <div id="ringkasan"></div>

  <div class="tabs" id="tabs">
    <button class="tab aktif" data-p="p1">Checklist Persyaratan</button>
    <button class="tab" data-p="p2">Matriks Kepatuhan</button>
    <button class="tab" data-p="p3">Berkas Penawaran</button>
    <button class="tab" data-p="p4">Ringkasan Risiko</button>
    <button class="tab" data-p="p5">Log Audit</button>
    <button class="tab" data-p="p6">Hasil Pengujian</button>
  </div>

  <div class="panel aktif" id="p1"></div>
  <div class="panel" id="p2"></div>
  <div class="panel" id="p3"></div>
  <div class="panel" id="p4"></div>
  <div class="panel" id="p5"></div>
  <div class="panel" id="p6"></div>

  <footer>Data sintetis untuk demonstrasi hackathon. Seluruh nomor dokumen fiktif.</footer>
</div>

<script>
const D = __DATA__;

const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const rp = n => n ? "Rp" + Math.round(n).toLocaleString("id-ID") : "—";

function lencana(status){
  const map = {memenuhi:["b-hijau","Memenuhi"], tidak_memenuhi:["b-merah","Tidak memenuhi"],
               kurang_dokumen:["b-kuning","Kurang dokumen"]};
  const [k, t] = map[status] || ["b-abu", status];
  return `<span class="lencana ${k}">${t}</span>`;
}

// ---------- ringkasan ----------
(function(){
  const u = D.usulan, r = u.ringkasan || {}, m = D.checklist.meta || {};
  const verdictWarna = u.verdict === "LOLOS" ? "hijau" : u.verdict === "TIDAK LOLOS" ? "merah" : "kuning";
  const langkah = [
    ["1","Baca paket tender","selesai"],
    ["2","Ekstraksi bersumber","selesai"],
    ["3","Cocokkan profil","selesai"],
    ["4","Keputusan & risiko","selesai"],
    ["5","Persetujuan manusia","tunggu"]
  ].map(([n,t,k]) => `<div class="langkah ${k}"><div class="n">LANGKAH ${n}</div><div class="t">${t}</div></div>`).join("");

  document.getElementById("ringkasan").innerHTML = `
    <div class="kartu" style="margin-bottom:14px">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:20px;flex-wrap:wrap">
        <div>
          <div class="kecil">Paket yang dinilai</div>
          <div style="font-size:17px;font-weight:700;margin-top:2px">${esc(u.paket?.nama || "—")}</div>
          <div class="kecil" style="margin-top:4px">Kode ${esc(u.paket?.kode || "—")} &middot; Pagu ${rp(u.paket?.pagu)} &middot; Batas penawaran ${esc(u.paket?.batas_penawaran || "—")}</div>
        </div>
        <div style="text-align:right">
          <div class="kecil">Keputusan agen</div>
          <div style="font-size:24px;font-weight:800;letter-spacing:-.6px" class="${verdictWarna}">${esc(u.verdict || "—")}</div>
          <div class="kecil">sidik jari ${esc(u.sidik_jari || "—")}</div>
        </div>
      </div>
      <div class="alur" style="margin-top:18px">${langkah}</div>
    </div>

    <div class="grid g4" style="margin-bottom:14px">
      <div class="kartu metrik"><div class="label">Persyaratan</div><div class="angka">${r.total || 0}</div>
        <div class="ket">${m.jumlah_persyaratan_terverifikasi || 0} kutipan terverifikasi</div></div>
      <div class="kartu metrik"><div class="label">Memenuhi</div><div class="angka hijau">${r.memenuhi || 0}</div>
        <div class="ket">bukti ditemukan di basis pengetahuan</div></div>
      <div class="kartu metrik"><div class="label">Kurang dokumen</div><div class="angka kuning">${r.kurang_dokumen || 0}</div>
        <div class="ket">${r.kurang_dokumen_kritis || 0} bersifat penghambat</div></div>
      <div class="kartu metrik"><div class="label">Tidak memenuhi</div><div class="angka merah">${r.tidak_memenuhi || 0}</div>
        <div class="ket">menghentikan penyusunan berkas</div></div>
    </div>

    <div class="dua">
      <div class="kartu">
        <h2>Perlu klarifikasi sebelum berkas disusun</h2>
        ${(u.klarifikasi || []).map(t => `<div class="catatan" style="margin-bottom:8px">${esc(t.pertanyaan)}</div>`).join("") || '<div class="kecil">Tidak ada.</div>'}
      </div>
      <div class="kartu">
        <h2>Agen tidak akan melakukan</h2>
        <ul class="rapat">${(u.tidak_akan_dilakukan || []).map(x => `<li>${esc(x)}</li>`).join("")}</ul>
        <div class="kecil" style="margin-top:10px">Status usulan: <b>${esc(u.status || "—")}</b>${u.disetujui_pada ? " &middot; " + esc(u.disetujui_pada) : ""}</div>
      </div>
    </div>`;
})();

// ---------- checklist ----------
(function(){
  const p = D.checklist.persyaratan || [];
  const baris = p.map(s => `<tr>
      <td class="kode">${esc(s.id)}</td>
      <td>${esc(s.kategori)}</td>
      <td><b>${esc(s.judul)}</b><div class="kecil">${esc(s.pernyataan)}</div></td>
      <td class="kecil">${esc(s.sumber.dokumen)}<br>bagian ${esc(s.sumber.bagian)}</td>
      <td class="kecil" style="max-width:320px">"${esc(s.sumber.kutipan).slice(0,150)}"</td>
      <td>${s.kutipan_terverifikasi ? '<span class="lencana b-hijau">Terverifikasi</span>' : '<span class="lencana b-merah">Tidak</span>'}</td>
    </tr>`).join("");
  document.getElementById("p1").innerHTML = `<div class="kartu">
    <h2>Checklist persyaratan hasil ekstraksi (${p.length} butir)</h2>
    <div class="kecil" style="margin-bottom:12px">Setiap butir wajib menyertakan kutipan dan lokasi. Kutipan diperiksa ulang terhadap teks asli sebelum dipakai.</div>
    <table><thead><tr><th>ID</th><th>Kategori</th><th>Persyaratan</th><th>Sumber</th><th>Kutipan</th><th>Verifikasi</th></tr></thead>
    <tbody>${baris}</tbody></table></div>`;
})();

// ---------- matriks ----------
(function(){
  const m = D.matriks || [];
  const baris = m.map(x => `<tr>
      <td class="kode">${esc(x.syarat_id)}</td>
      <td>${esc(x.judul)}</td>
      <td>${lencana(x.status)}</td>
      <td class="kecil" style="max-width:300px">${esc(x.bukti[0]?.nilai || "—")}</td>
      <td class="kecil" style="max-width:320px">${esc(x.catatan || "—")}</td>
    </tr>`).join("");
  document.getElementById("p2").innerHTML = `<div class="kartu">
    <h2>Matriks kepatuhan</h2>
    <div class="kecil" style="margin-bottom:12px">Kolom bukti menunjuk ke basis pengetahuan profil perusahaan; kolom catatan menjelaskan alasan keputusan.</div>
    <table><thead><tr><th>ID</th><th>Persyaratan</th><th>Status</th><th>Bukti</th><th>Catatan</th></tr></thead>
    <tbody>${baris}</tbody></table></div>`;
})();

// ---------- berkas ----------
(function(){
  const b = D.usulan.berkas_dihasilkan || [];
  const daftar = (b.length ? b : (D.usulan.tindakan || []).map(t => t.berkas)).map(n =>
    `<div class="berkas"><div class="ikon">DOC</div>
      <div><div style="font-weight:600">${esc(n)}</div>
      <div class="kecil">${b.length ? "dihasilkan setelah persetujuan" : "menunggu persetujuan"}</div></div></div>`).join("");
  document.getElementById("p3").innerHTML = `<div class="dua">
    <div class="kartu"><h2>Berkas administrasi</h2>${daftar || '<div class="kecil">Belum ada.</div>'}
      <div class="kecil" style="margin-top:12px">Semua berkas ditulis ke <span class="kode">output/03_berkas_penawaran/</span> hanya setelah persetujuan tercatat.</div></div>
    <div class="kartu"><h2>Yang sengaja dikosongkan</h2>
      <ul class="rapat">
        <li>Nilai penawaran &rarr; keputusan komersial direktur</li>
        <li>Sertifikat Ahli K3 Umum &rarr; belum terbit, ditandai BELUM ADA</li>
        <li>Tanda tangan &rarr; hanya manusia yang menandatangani</li>
        <li>Unggah ke LPSE &rarr; di luar kewenangan agen</li>
      </ul>
      <div class="kecil" style="margin-top:10px">Prinsip: lebih baik kosong dan jujur daripada terisi tetapi salah.</div>
    </div></div>`;
})();

// ---------- risiko ----------
(function(){
  const r = D.usulan.risiko || [];
  const baris = r.map((x,i) => `<tr>
      <td>${i+1}</td>
      <td><span class="lencana ${x.tingkat==="tinggi"?"b-merah":x.tingkat==="sedang"?"b-kuning":"b-abu"}">${esc(x.tingkat).toUpperCase()}</span></td>
      <td>${esc(x.judul)}</td>
      <td class="kecil" style="max-width:340px">${esc(x.uraian)}</td>
      <td class="kecil" style="max-width:260px">${esc(x.tindakan)}</td>
    </tr>`).join("");
  document.getElementById("p4").innerHTML = `<div class="kartu">
    <h2>Lembar ringkasan risiko</h2>
    <table><thead><tr><th>No</th><th>Tingkat</th><th>Persyaratan</th><th>Temuan</th><th>Tindakan</th></tr></thead>
    <tbody>${baris || '<tr><td colspan="5" class="kecil">Tidak ditemukan risiko.</td></tr>'}</tbody></table></div>`;
})();

// ---------- audit ----------
(function(){
  const a = D.audit || [];
  const baris = a.map(x => `<tr>
      <td class="kode">${esc(x.waktu)}</td>
      <td>${esc(x.aktor)}</td>
      <td class="kode">${esc(x.aksi)}</td>
      <td class="kecil">${esc(x.objek)}</td>
      <td class="kecil">${esc(x.hasil)}</td>
    </tr>`).join("");
  document.getElementById("p5").innerHTML = `<div class="kartu">
    <h2>Log audit (${a.length} peristiwa)</h2>
    <div class="kecil" style="margin-bottom:12px">Berkas <span class="kode">output/05_log_audit.jsonl</span> bersifat append-only: apa yang dilihat, diputuskan, dan dilakukan.</div>
    <table><thead><tr><th>Waktu</th><th>Aktor</th><th>Aksi</th><th>Objek</th><th>Hasil</th></tr></thead>
    <tbody>${baris}</tbody></table></div>`;
})();

// ---------- uji ----------
(function(){
  const u = D.uji || {}, r = u.ringkasan || {};
  const baris = (u.kasus || []).map(k => `<tr>
      <td class="kode">${esc(k.kode)}</td>
      <td>${esc(k.judul)}</td>
      <td class="kecil">${esc(k.kategori)}</td>
      <td>${k.hasil === "LULUS" ? '<span class="lencana b-hijau">LULUS</span>' : '<span class="lencana b-merah">GAGAL</span>'}</td>
      <td class="kecil" style="max-width:420px">${esc(k.bukti)}</td>
    </tr>`).join("");
  document.getElementById("p6").innerHTML = `
    <div class="grid g3" style="margin-bottom:14px">
      <div class="kartu metrik"><div class="label">Test case</div><div class="angka">${r.total || 0}</div></div>
      <div class="kartu metrik"><div class="label">Lulus</div><div class="angka hijau">${r.lulus || 0}</div></div>
      <div class="kartu metrik"><div class="label">Gagal (dilaporkan)</div><div class="angka merah">${r.gagal || 0}</div>
        <div class="ket">kegagalan diungkap, bukan disembunyikan</div></div>
    </div>
    <div class="kartu"><h2>Hasil pengujian terhadap alur agen</h2>
    <table><thead><tr><th>Kode</th><th>Test case</th><th>Kategori</th><th>Hasil</th><th>Bukti</th></tr></thead>
    <tbody>${baris}</tbody></table></div>`;
})();

// ---------- tabs ----------
document.getElementById("tabs").addEventListener("click", e => {
  const b = e.target.closest(".tab"); if (!b) return;
  document.querySelectorAll(".tab").forEach(t => t.classList.remove("aktif"));
  document.querySelectorAll(".panel").forEach(p => p.classList.remove("aktif"));
  b.classList.add("aktif");
  document.getElementById(b.dataset.p).classList.add("aktif");
});
</script>
</body>
</html>"""

    html = html.replace("__DATA__", isi)
    path = KELUARAN / "dashboard.html"
    path.write_text(html, encoding="utf-8")
    return path


if __name__ == "__main__":
    p = bangun()
    print(f"Dashboard: {p} ({p.stat().st_size/1024:.0f} KB)")
