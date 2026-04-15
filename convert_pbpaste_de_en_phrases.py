#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
import sys


NUMBER_PREFIX_RE = re.compile(r"^\s*\d+[\.)]\s*")
SEPARATOR_RE = re.compile(r"\s*(?:\u2014|\u2013|--|-)\s*")


def read_pbpaste():
    try:
        result = subprocess.run(
            ["pbpaste"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError:
        sys.exit("pbpaste was not found. This script is intended for macOS.")
    except subprocess.CalledProcessError as exc:
        message = exc.stderr.strip() or "pbpaste failed."
        sys.exit(message)
    return result.stdout


def js_string(value):
    return json.dumps(value, ensure_ascii=False)


def convert(text):
    rows = []
    skipped = []

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = NUMBER_PREFIX_RE.sub("", raw_line.strip())
        if not line:
            continue

        parts = SEPARATOR_RE.split(line, maxsplit=1)
        if len(parts) != 2:
            skipped.append((line_number, raw_line))
            continue

        de, en = (part.strip() for part in parts)
        if not de or not en:
            skipped.append((line_number, raw_line))
            continue

        rows.append(f"  {{ en: {js_string(en)}, de: {js_string(de)} }},")

    return rows, skipped


def main():
    parser = argparse.ArgumentParser(
        description="Convert clipboard lines like '1. German - English' into EN-DE JS phrase objects."
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read from stdin instead of macOS pbpaste.",
    )
    args = parser.parse_args()

    text = sys.stdin.read() if args.stdin else read_pbpaste()
    rows, skipped = convert(text)

    if rows:
        print("\n".join(rows))

    if skipped:
        print("", file=sys.stderr)
        print("Skipped lines:", file=sys.stderr)
        for line_number, raw_line in skipped:
            print(f"{line_number}: {raw_line}", file=sys.stderr)


if __name__ == "__main__":
    main()
