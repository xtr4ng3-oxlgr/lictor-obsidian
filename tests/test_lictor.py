from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / "lictor.py"


def run_cmd(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(ENTRY), *args],
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=25,
    )


def json_cmd(*args: str) -> dict:
    proc = run_cmd(*args, "--json", "--pretty")
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data["tool"] == "LICTOR"
    assert "score" in data
    assert "signals" in data
    return data


def test_init_json():
    data = json_cmd("init")
    assert data["type"] == "init"


def test_url_json():
    data = json_cmd("url", "http://bit.ly/test?token=123")
    assert data["type"] == "url"
    assert data["score"] >= 43


def test_domain_json():
    data = json_cmd("domain", "mercadopago-seguridad-login.example.com")
    assert data["type"] == "url"


def test_email_json():
    data = json_cmd(
        "email",
        "--sender", "support@hotmail.com",
        "--claimed", "Microsoft",
        "--subject", "Cuenta bloqueada",
        "--body", "Tu cuenta será cerrada. Confirma tu clave y token urgente.",
    )
    assert data["type"] == "email"
    assert data["score"] >= 43


def test_text_json():
    data = json_cmd("text", "Soy tu nieto cambié de número necesito plata urgente no le digas a nadie")
    assert data["type"] == "text"
    assert data["score"] >= 43


def test_file_json():
    sample = ROOT / "examples" / "sample_test.bat"
    sample.write_text("@echo off\necho test\n", encoding="utf-8")
    try:
        data = json_cmd("file", str(sample))
        assert data["type"] == "file"
        assert "hashes" in data
        assert data["score"] >= 20
    finally:
        sample.unlink(missing_ok=True)


def test_out_html_save_history():
    out_json = ROOT / "examples" / "out_test.json"
    out_html = ROOT / "examples" / "out_test.html"
    for p in [out_json, out_html]:
        p.unlink(missing_ok=True)

    proc = run_cmd(
        "url",
        "http://example.com/login?token=1",
        "--json",
        "--pretty",
        "--out",
        str(out_json),
        "--html",
        str(out_html),
        "--save",
    )
    assert proc.returncode == 0, proc.stderr
    assert out_json.exists()
    assert out_html.exists()

    data = json.loads(out_json.read_text(encoding="utf-8"))
    assert data["tool"] == "LICTOR"

    hist = run_cmd("history", "--json")
    assert hist.returncode == 0, hist.stderr
    rows = json.loads(hist.stdout)
    assert isinstance(rows, list)

    out_json.unlink(missing_ok=True)
    out_html.unlink(missing_ok=True)


def test_help_does_not_crash():
    proc = run_cmd("--help")
    assert proc.returncode == 0
    assert "LICTOR" in proc.stdout


if __name__ == "__main__":
    tests = [
        test_init_json,
        test_url_json,
        test_domain_json,
        test_email_json,
        test_text_json,
        test_file_json,
        test_out_html_save_history,
        test_help_does_not_crash,
    ]

    failed = 0
    for test in tests:
        try:
            test()
            print("[OK]", test.__name__)
        except Exception as exc:
            failed += 1
            print("[FAIL]", test.__name__, exc)

    raise SystemExit(1 if failed else 0)
