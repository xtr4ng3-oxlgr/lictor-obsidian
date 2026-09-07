from __future__ import annotations

"""
LICTOR
Local Indicator and Case Triage Operator

Developed solely by xtr4ng3.

A local-first defensive triage engine for suspicious URLs, domains, emails,
text indicators and local files.

No network calls.
No hidden sending.
No credential collection.
No covert upload.
"""

import csv
import hashlib
import html
import ipaddress
import json
import re
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


APP_NAME = "LICTOR"
APP_VERSION = "1.0.0"
AUTHOR = "xtr4ng3"


FREE_EMAIL_DOMAINS = {
    "gmail.com", "hotmail.com", "outlook.com", "live.com", "yahoo.com", "icloud.com",
    "msn.com", "aol.com", "proton.me", "protonmail.com", "mail.com"
}

SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd",
    "cutt.ly", "shorturl.at", "rebrand.ly", "buff.ly", "lnkd.in"
}

KNOWN_BRANDS = [
    "microsoft", "outlook", "hotmail", "google", "gmail", "facebook", "instagram",
    "whatsapp", "mercadopago", "mercadolibre", "paypal", "netflix", "amazon",
    "santander", "galicia", "macro", "anses", "arca", "afip", "correoargentino",
    "visa", "mastercard", "uala", "personal", "flow", "telecom"
]

RISK_WORDS = [
    "login", "verify", "secure", "wallet", "gift", "free", "update", "support",
    "account", "confirm", "validation", "premio", "ganaste", "bloqueo", "seguridad",
    "pago", "transferencia", "reembolso", "banco", "bank", "token", "clave", "password",
    "contraseña", "otp", "urgente", "suspendida", "bloqueada", "deuda", "multa",
    "paquete", "aduana", "liberar", "cbu", "cvu"
]

TEXT_RULES = [
    ("asks_code", r"(?i)\b(c[oó]digo|token|otp|pin|clave|contraseñ?a|password)\b", 30, "Pide o menciona códigos, token, PIN, clave o contraseña."),
    ("urgent_pressure", r"(?i)\b(urgente|ahora|ya|24 horas|72 horas|último aviso|ultimo aviso|inmediato)\b", 20, "Usa presión temporal o urgencia."),
    ("money_transfer", r"(?i)\b(transferencia|alias|cbu|cvu|plata|dinero|deposito|dep[oó]sito|pago)\b", 25, "Menciona dinero, pago, alias, CBU o CVU."),
    ("secrecy", r"(?i)\b(no le digas|no cuentes|secreto|entre nosotros|no avises|no digas nada)\b", 28, "Pide secreto o aislamiento."),
    ("remote_access", r"(?i)\b(anydesk|teamviewer|control remoto|acceso remoto|instal[aá]|descarg[aá])\b", 35, "Menciona instalación, descarga o acceso remoto."),
    ("account_threat", r"(?i)\b(cerrar|baja|bloquear|suspender|perder|eliminar).{0,40}\b(cuenta|hotmail|outlook|banco|servicio|perfil)\b", 30, "Amenaza cierre, baja, bloqueo o pérdida de cuenta/perfil."),
]


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def level_from_score(score: int) -> tuple[str, str]:
    score = max(0, min(100, int(score)))
    if score >= 85:
        return "CRITICAL", "#8b0000"
    if score >= 70:
        return "HIGH", "#b3261e"
    if score >= 43:
        return "MEDIUM", "#b26a00"
    if score >= 20:
        return "LOW", "#735c00"
    return "INFO", "#1b5e20"


def recommendation_from_score(score: int) -> str:
    score = max(0, min(100, int(score)))
    if score >= 85:
        return "Critical risk. Do not open, pay, install, answer or share codes. Verify through an official channel."
    if score >= 70:
        return "High risk. Stop the interaction and verify with a trusted person or official channel."
    if score >= 43:
        return "Suspicious. Review before clicking, answering or sharing information."
    if score >= 20:
        return "Low risk signals. Keep caution and avoid sharing sensitive data."
    return "No strong local risk signals detected. Still verify before sharing sensitive data."


def add_signal(signals: list[dict[str, Any]], code: str, weight: int, detail: str) -> int:
    signals.append({"code": code, "weight": int(weight), "detail": detail})
    return int(weight)


def clamp(score: int) -> int:
    return max(0, min(100, int(score)))


def make_result(kind: str, input_value: Any, score: int, signals: list[dict[str, Any]], extra: dict[str, Any] | None = None) -> dict[str, Any]:
    score = clamp(score)
    level, color = level_from_score(score)
    if not signals:
        signals = [{"code": "no_strong_signal", "weight": 0, "detail": "No strong local risk signal detected."}]
    result = {
        "id": str(uuid.uuid4()),
        "created_at": now_iso(),
        "tool": APP_NAME,
        "version": APP_VERSION,
        "author": AUTHOR,
        "type": kind,
        "input": input_value,
        "score": score,
        "level": level,
        "color": color,
        "recommendation": recommendation_from_score(score),
        "signals": signals,
    }
    if extra:
        result.update(extra)
    return result


def defang(value: str) -> str:
    return (value or "").replace("https://", "hxxps://").replace("http://", "hxxp://").replace(".", "[.]")


def normalize_url(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    if re.match(r"(?i)^https?://", value):
        return value
    return "https://" + value


def is_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
        return True
    except Exception:
        return False


def extract_urls(text: str) -> list[str]:
    pattern = r"(?i)\bhttps?://[^\s<>'\"\)]+|\bwww\.[^\s<>'\"\)]+"
    return sorted(set(m.group(0).strip(".,);]\"'") for m in re.finditer(pattern, text or "")))


def analyze_url(value: str) -> dict[str, Any]:
    original = (value or "").strip()
    normalized = normalize_url(original)
    parsed = urlparse(normalized)
    host = (parsed.hostname or "").lower()
    scheme = (parsed.scheme or "").lower()
    path = parsed.path or ""
    query = parsed.query or ""
    combined = f"{host} {path} {query}".lower()

    signals: list[dict[str, Any]] = []
    score = 0

    if not original:
        score += add_signal(signals, "empty_url", 10, "No URL or domain was provided.")
    if scheme == "http":
        score += add_signal(signals, "plain_http", 22, "Uses HTTP without transport encryption.")
    if host in SHORTENERS:
        score += add_signal(signals, "shortener", 35, "Uses a known URL shortener.")
    if host.startswith("xn--") or ".xn--" in host:
        score += add_signal(signals, "punycode", 35, "Uses punycode, possible visual impersonation.")
    if host and is_ip(host):
        score += add_signal(signals, "raw_ip_host", 24, "Uses a raw IP address as host.")
    if "@" in original:
        score += add_signal(signals, "at_symbol", 28, "Contains @, which can obscure the real destination.")
    if host.count("-") >= 3:
        score += add_signal(signals, "many_hyphens", 14, "Host contains many hyphens.")
    if host.count(".") >= 3:
        score += add_signal(signals, "many_subdomains", 12, "Host contains many subdomains.")
    if len(host) > 45:
        score += add_signal(signals, "long_host", 10, "Host is unusually long.")

    for word in RISK_WORDS:
        if word in combined:
            score += add_signal(signals, f"risk_word_{word}", 5, f"Contains risk word: {word}")

    compact_host = host.replace("-", "").replace("_", "").replace(".", "")
    for brand in KNOWN_BRANDS:
        if brand in compact_host:
            official_like = host.endswith(f"{brand}.com") or host.endswith(f"{brand}.com.ar")
            if not official_like:
                score += add_signal(signals, f"brand_reference_{brand}", 8, f"Mentions or resembles known brand: {brand}")

    for param in ["token", "auth", "password", "pass", "session", "code", "otp", "clave", "pin"]:
        if re.search(rf"(?i)(^|&){re.escape(param)}=", query):
            score += add_signal(signals, f"sensitive_query_{param}", 22, f"Sensitive query parameter: {param}")

    return make_result("url", original, score, signals, {
        "normalized": normalized,
        "defanged": defang(original),
        "host": host,
        "scheme": scheme,
        "path": path,
        "query_present": bool(query),
    })


def email_domain(address: str) -> str:
    m = re.search(r"(?i)([a-z0-9._%+\-]+)@([a-z0-9.\-]+\.[a-z]{2,})", address or "")
    return m.group(2).lower() if m else ""


def analyze_email(sender: str = "", subject: str = "", body: str = "", claimed: str = "") -> dict[str, Any]:
    sender = sender or ""
    subject = subject or ""
    body = body or ""
    claimed = claimed or ""
    domain = email_domain(sender)
    full_text = f"{sender}\n{subject}\n{body}\n{claimed}"
    lower = full_text.lower()

    signals: list[dict[str, Any]] = []
    score = 0

    if not domain:
        score += add_signal(signals, "invalid_sender", 25, "Could not identify a valid sender domain.")
    elif domain in FREE_EMAIL_DOMAINS and claimed:
        score += add_signal(signals, "free_mail_claiming_entity", 35, f"Free email domain {domain} claims or implies an organization.")
    elif domain in FREE_EMAIL_DOMAINS:
        score += add_signal(signals, "free_mail_sender", 10, f"Sender uses free email domain {domain}.")

    for code, pattern, weight, detail in TEXT_RULES:
        if re.search(pattern, full_text):
            score += add_signal(signals, code, weight, detail)

    if any(w in lower for w in ["microsoft 365", "office 365", "hotmail", "outlook"]) and any(w in lower for w in ["cerrar", "baja", "expira", "bloqueada", "perder", "suspendida"]):
        score += add_signal(signals, "microsoft_hotmail_closure", 35, "Message threatens Microsoft/Hotmail/Outlook closure or expiration.")

    if any(w in lower for w in ["anses", "arca", "afip", "banco", "mercado pago", "mercadopago", "correo argentino"]) and any(w in lower for w in ["clave", "token", "código", "codigo", "pago", "deuda", "datos", "tarjeta"]):
        score += add_signal(signals, "institution_sensitive_request", 38, "Institution-like message asks for sensitive action or data.")

    urls = extract_urls(full_text)
    if urls:
        score += add_signal(signals, "embedded_urls", 18, "Email/text contains links.")
        for url in urls[:5]:
            sub = analyze_url(url)
            if sub["score"] >= 43:
                score += add_signal(signals, "risky_embedded_url", min(25, sub["score"] // 3), f"Embedded URL is suspicious: {defang(url)}")

    return make_result("email", sender, score, signals, {
        "sender_domain": domain,
        "claimed_entity": claimed,
        "subject": subject,
        "body_preview": body[:500],
        "urls": [defang(u) for u in urls],
    })


def analyze_text(text: str) -> dict[str, Any]:
    text = text or ""
    lower = text.lower()
    signals: list[dict[str, Any]] = []
    score = 0

    for code, pattern, weight, detail in TEXT_RULES:
        if re.search(pattern, text):
            score += add_signal(signals, code, weight, detail)

    urls = extract_urls(text)
    if urls:
        score += add_signal(signals, "urls_present", 15, "Text contains one or more URLs.")
        for url in urls[:5]:
            sub = analyze_url(url)
            if sub["score"] >= 43:
                score += add_signal(signals, "suspicious_url_inside_text", min(25, sub["score"] // 3), f"Suspicious URL inside text: {defang(url)}")

    special = [
        ("changed_number", ["cambié de número", "cambie de numero", "nuevo número", "nuevo numero"], 25, "Mentions changed/new number."),
        ("family_urgent", ["soy tu nieto", "soy tu hijo", "soy tu mamá", "soy tu mama", "me mandé una cagada", "me mande una cagada"], 30, "Matches family-urgency scam phrasing."),
        ("do_not_tell", ["no le digas a nadie", "no avises", "esto queda entre nosotros", "no digas nada"], 30, "Requests secrecy."),
    ]
    for code, phrases, weight, detail in special:
        if any(p in lower for p in phrases):
            score += add_signal(signals, code, weight, detail)

    return make_result("text", text[:1000], score, signals, {
        "length": len(text),
        "urls": [defang(u) for u in urls],
    })


def file_hashes(path: Path) -> dict[str, str]:
    md5 = hashlib.md5()
    sha1 = hashlib.sha1()
    sha256 = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            md5.update(chunk)
            sha1.update(chunk)
            sha256.update(chunk)
    return {"md5": md5.hexdigest(), "sha1": sha1.hexdigest(), "sha256": sha256.hexdigest()}


def analyze_file(path_value: str) -> dict[str, Any]:
    path = Path(path_value)
    signals: list[dict[str, Any]] = []
    score = 0

    if not path.exists():
        score += add_signal(signals, "file_not_found", 40, "File does not exist.")
        return make_result("file", path_value, score, signals)

    if not path.is_file():
        score += add_signal(signals, "not_a_file", 20, "Path is not a file.")
        return make_result("file", path_value, score, signals)

    suffix = path.suffix.lower()
    risky = {".exe", ".scr", ".bat", ".cmd", ".ps1", ".vbs", ".js", ".jar", ".lnk", ".msi", ".hta"}
    if suffix in risky:
        score += add_signal(signals, "risky_extension", 25, f"Executable or script-like extension: {suffix}")

    size = path.stat().st_size
    if size == 0:
        score += add_signal(signals, "empty_file", 10, "File is empty.")
    if size > 100 * 1024 * 1024:
        score += add_signal(signals, "large_file", 5, "Large file. Hashes calculated; manual review may be needed.")

    return make_result("file", str(path), score, signals, {
        "file_name": path.name,
        "extension": suffix,
        "size_bytes": size,
        "hashes": file_hashes(path),
    })


class Store:
    def __init__(self, root: Path):
        self.root = root
        self.data_dir = root / "lictor_data"
        self.reports_dir = self.data_dir / "reports"
        self.exports_dir = self.data_dir / "exports"
        self.db_path = self.data_dir / "lictor.sqlite3"

    def init(self) -> None:
        self.data_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        self.exports_dir.mkdir(exist_ok=True)
        with sqlite3.connect(self.db_path) as con:
            con.execute("""
            CREATE TABLE IF NOT EXISTS scans(
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                scan_type TEXT NOT NULL,
                input_value TEXT,
                score INTEGER NOT NULL,
                level TEXT NOT NULL,
                result_json TEXT NOT NULL
            )
            """)

    def save(self, result: dict[str, Any]) -> None:
        self.init()
        with sqlite3.connect(self.db_path) as con:
            con.execute(
                "INSERT OR REPLACE INTO scans(id, created_at, scan_type, input_value, score, level, result_json) VALUES(?,?,?,?,?,?,?)",
                (
                    result["id"],
                    result["created_at"],
                    result["type"],
                    str(result.get("input", ""))[:1000],
                    int(result["score"]),
                    result["level"],
                    json.dumps(result, ensure_ascii=False, indent=2),
                ),
            )

    def latest(self, limit: int = 50) -> list[dict[str, Any]]:
        self.init()
        with sqlite3.connect(self.db_path) as con:
            con.row_factory = sqlite3.Row
            rows = con.execute("SELECT result_json FROM scans ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        out = []
        for row in rows:
            try:
                out.append(json.loads(row["result_json"]))
            except Exception:
                pass
        return out

    def export_csv(self, out: str | None = None) -> Path:
        self.init()
        path = Path(out) if out else self.exports_dir / f"lictor_scans_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        rows = self.latest(100000)
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "created_at", "type", "score", "level", "input", "recommendation"])
            writer.writeheader()
            for r in rows:
                writer.writerow({key: r.get(key, "") for key in writer.fieldnames})
        return path

    def export_html(self, result: dict[str, Any], out: str | None = None) -> Path:
        self.init()
        path = Path(out) if out else self.reports_dir / f"lictor_report_{result['id']}.html"
        path.parent.mkdir(parents=True, exist_ok=True)
        signal_items = "\n".join(
            f"<li><strong>{html.escape(str(s.get('code','')))}</strong> "
            f"(+{html.escape(str(s.get('weight','')))}): "
            f"{html.escape(str(s.get('detail','')))}</li>"
            for s in result.get("signals", [])
        )
        doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>LICTOR Report</title>
<style>
body{{font-family:Segoe UI,Arial,sans-serif;background:#f3f4f6;color:#111827;padding:28px}}
.card{{background:white;border:1px solid #d1d5db;border-radius:12px;padding:18px;margin:14px 0}}
h1,h2{{color:#111827}}
pre{{background:#eef2f7;padding:12px;border-radius:8px;white-space:pre-wrap}}
.footer{{color:#6b7280;margin-top:28px}}
</style>
</head>
<body>
<h1>LICTOR Report</h1>
<div class="card">
<b>Tool:</b> LICTOR {APP_VERSION}<br>
<b>Author:</b> {AUTHOR}<br>
<b>Created:</b> {html.escape(result.get('created_at',''))}<br>
<b>Type:</b> {html.escape(result.get('type',''))}<br>
<b>Score:</b> {html.escape(str(result.get('score','')))} / 100<br>
<b>Level:</b> {html.escape(result.get('level',''))}<br>
</div>
<div class="card"><h2>Input</h2><pre>{html.escape(str(result.get('input','')))}</pre></div>
<div class="card"><h2>Recommendation</h2><p>{html.escape(str(result.get('recommendation','')))}</p></div>
<div class="card"><h2>Signals</h2><ul>{signal_items}</ul></div>
<div class="footer">LICTOR · Local Indicator and Case Triage Operator · xtr4ng3</div>
</body>
</html>"""
        path.write_text(doc, encoding="utf-8")
        return path
