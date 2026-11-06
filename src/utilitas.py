"""Utilitas bersama TenderBuddy: format rupiah, tanggal Indonesia, log audit."""

from __future__ import annotations

import json
import re
from datetime import date, datetime, timezone, timedelta
from pathlib import Path

ZONA = timezone(timedelta(hours=7))  # WIB

NAMA_BULAN = {
    "januari": 1, "februari": 2, "maret": 3, "april": 4, "mei": 5, "juni": 6,
    "juli": 7, "agustus": 8, "september": 9, "oktober": 10, "november": 11, "desember": 12,
}

NAMA_HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]


def rupiah(nilai: float) -> str:
    """Format angka menjadi rupiah gaya Indonesia: Rp2.450.000.000."""
    return "Rp{:,.0f}".format(nilai).replace(",", ".")


def parse_rupiah(teks: str) -> float | None:
    """Ambil angka rupiah dari teks. Mengembalikan None bila tidak terbaca.

    Hanya menerima notasi penuh (Rp1.234.567.890) atau (Rp1.234.567.890,00).
    Notasi singkat seperti 'Rp1,2 M' sengaja tidak ditebak.
    """
    m = re.search(r"Rp\s?([\d][\d\.]*(?:,\d{2})?)", teks)
    if not m:
        return None
    angka = m.group(1)
    if "," in angka:
        angka = angka.split(",")[0]
    angka = angka.replace(".", "")
    if not angka.isdigit():
        return None
    return float(angka)


def parse_tanggal(teks: str) -> date | None:
    """Parse tanggal Indonesia: '16 November 2026' atau '16-11-2026'."""
    m = re.search(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})", teks)
    if m:
        bulan = NAMA_BULAN.get(m.group(2).lower())
        if bulan:
            try:
                return date(int(m.group(3)), bulan, int(m.group(1)))
            except ValueError:
                return None
    m = re.search(r"(\d{1,2})-(\d{1,2})-(\d{4})", teks)
    if m:
        try:
            return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError:
            return None
    return None


def nama_hari(d: date) -> str:
    return NAMA_HARI[d.weekday()]


def sekarang() -> datetime:
    return datetime.now(ZONA)


def cap_waktu() -> str:
    return sekarang().strftime("%Y-%m-%d %H:%M:%S WIB")


def baca_teks(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def muat_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def tulis_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def normal(teks: str) -> str:
    """Normalisasi teks untuk pencocokan longgar."""
    teks = teks.lower()
    teks = re.sub(r"[^a-z0-9\s]", " ", teks)
    return re.sub(r"\s+", " ", teks).strip()


class LogAudit:
    """Log audit append-only dalam format JSON Lines.

    Setiap baris mencatat: waktu, aktor, aksi, objek, hasil, dan sumber.
    Log ini tidak pernah ditimpa agar dapat diperiksa ulang.
    """

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def catat(self, aktor: str, aksi: str, objek: str, hasil: str, sumber: str = "", detail: dict | None = None) -> dict:
        baris = {
            "waktu": cap_waktu(),
            "aktor": aktor,
            "aksi": aksi,
            "objek": objek,
            "hasil": hasil,
            "sumber": sumber,
            "detail": detail or {},
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(baris, ensure_ascii=False) + "\n")
        return baris
