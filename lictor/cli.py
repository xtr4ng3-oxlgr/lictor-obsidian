from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import (
    APP_NAME,
    APP_VERSION,
    Store,
    analyze_email,
    analyze_file,
    analyze_text,
    analyze_url,
    make_result,
)


def app_root() -> Path:
    return Path(__file__).resolve().parents[1]


def print_human(result: dict) -> None:
    print(f"{APP_NAME} {APP_VERSION}")
    print("-" * 72)
    print(f"Type:  {result.get('type')}")
    print(f"Level: {result.get('level')} ({result.get('score')}/100)")
    print(f"Input: {result.get('input')}")
    print()
    print("Recommendation:")
    print(" ", result.get("recommendation", "Review before acting."))
    print()
    print("Signals:")
    for sig in result.get("signals", []):
        print(f" - [{sig.get('weight', 0):>2}] {sig.get('code')}: {sig.get('detail')}")


def emit(result: dict, args: argparse.Namespace, store: Store) -> int:
    if getattr(args, "save", False):
        store.save(result)

    if getattr(args, "html", None):
        store.export_html(result, args.html)

    if getattr(args, "out", None):
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    if getattr(args, "json", False):
        print(json.dumps(result, ensure_ascii=False, indent=2 if getattr(args, "pretty", False) else None))
    else:
        print_human(result)

    return 0


def add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", action="store_true", help="Print JSON result.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON.")
    parser.add_argument("--out", help="Write JSON result to file.")
    parser.add_argument("--save", action="store_true", help="Save result to local SQLite history.")
    parser.add_argument("--html", help="Write HTML report to file.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lictor",
        description="LICTOR - Local Indicator and Case Triage Operator",
    )
    parser.add_argument("--version", action="version", version=f"{APP_NAME} {APP_VERSION}")

    sub = parser.add_subparsers(dest="command")

    p_init = sub.add_parser("init", help="Initialize local data directory and database.")
    add_common(p_init)

    p_gui = sub.add_parser("gui", help="Open GUI.")

    p_url = sub.add_parser("url", help="Analyze URL or domain.")
    p_url.add_argument("value")
    add_common(p_url)

    p_domain = sub.add_parser("domain", help="Analyze domain.")
    p_domain.add_argument("value")
    add_common(p_domain)

    p_email = sub.add_parser("email", help="Analyze email sender/content.")
    p_email.add_argument("--sender", default="")
    p_email.add_argument("--subject", default="")
    p_email.add_argument("--body", default="")
    p_email.add_argument("--body-file")
    p_email.add_argument("--claimed", default="")
    add_common(p_email)

    p_text = sub.add_parser("text", help="Analyze text.")
    p_text.add_argument("value", nargs="?", default="")
    p_text.add_argument("--file")
    add_common(p_text)

    p_file = sub.add_parser("file", help="Analyze local file and calculate hashes.")
    p_file.add_argument("path")
    add_common(p_file)

    p_history = sub.add_parser("history", help="Show saved history.")
    p_history.add_argument("--json", action="store_true")
    p_history.add_argument("--limit", type=int, default=20)
    p_history.add_argument("--csv")

    return parser


def main(argv: list[str] | None = None) -> int:
    store = Store(app_root())
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        try:
            from .gui import run_gui
            return run_gui(app_root())
        except Exception as exc:
            print(f"GUI could not be started: {exc}", file=sys.stderr)
            parser.print_help()
            return 2

    if args.command == "gui":
        from .gui import run_gui
        return run_gui(app_root())

    if args.command == "init":
        store.init()
        result = make_result(
            "init",
            str(store.data_dir),
            0,
            [{"code": "initialized", "weight": 0, "detail": "LICTOR data directory and database initialized."}],
            {"data_dir": str(store.data_dir), "database": str(store.db_path)},
        )
        return emit(result, args, store)

    if args.command == "url":
        return emit(analyze_url(args.value), args, store)

    if args.command == "domain":
        return emit(analyze_url(args.value), args, store)

    if args.command == "email":
        body = args.body
        if args.body_file:
            body = Path(args.body_file).read_text(encoding="utf-8", errors="replace")
        return emit(analyze_email(args.sender, args.subject, body, args.claimed), args, store)

    if args.command == "text":
        value = args.value
        if args.file:
            value = Path(args.file).read_text(encoding="utf-8", errors="replace")
        return emit(analyze_text(value), args, store)

    if args.command == "file":
        return emit(analyze_file(args.path), args, store)

    if args.command == "history":
        if args.csv:
            print(store.export_csv(args.csv))
            return 0
        rows = store.latest(args.limit)
        if args.json:
            print(json.dumps(rows, ensure_ascii=False, indent=2))
        else:
            for row in rows:
                print(f"{row.get('created_at')} | {row.get('type')} | {row.get('level')} {row.get('score')}/100 | {str(row.get('input'))[:100]}")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
