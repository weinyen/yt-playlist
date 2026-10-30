#!/usr/bin/env python3
"""playlist.tsv から playlist.json を作り直す (Windows / Mac / Linux 共通).

使い方:
    1. このファイル (tsv_to_json.py) と playlist.tsv を同じフォルダに置く
    2. そのフォルダで下記のどちらかを実行する
           py tsv_to_json.py        (Windows)
           python tsv_to_json.py    (Windows / その他)
    3. 同じフォルダに playlist.json が作られる (既存なら上書き)

入力形式:
    1行 = タイトル<TAB>URL
    文字コードは UTF-16 (Excel の「Unicode テキスト」), UTF-8,
    Shift_JIS (CP932) のいずれでもよい。自動で判定する。

出力形式 (同梱されていた playlist.json の形式に合わせている):
    [{"title": ..., "url": ...}, ...] を indent=2, ensure_ascii=False で保存
    ※ タイトルが "NA" の行もそのまま "NA" とする (null にはしない)
    ※ id フィールドは付けない
"""
import codecs
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_TSV_NAME = "playlist.tsv"


def find_tsv(base_dir):
    """入力 TSV を探す。playlist.tsv 優先、なければフォルダ内の唯一の .tsv。"""
    preferred = base_dir / DEFAULT_TSV_NAME
    if preferred.is_file():
        return preferred
    candidates = sorted(base_dir.glob("*.tsv"))
    if len(candidates) == 1:
        return candidates[0]
    return None


def decode_tsv(data):
    """バイト列を文字コード自動判定で文字列にする。"""
    # BOM があればそれが確実
    if data.startswith((codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)):
        return data.decode("utf-16")
    if data.startswith(codecs.BOM_UTF8):
        return data.decode("utf-8-sig")
    # BOM なし UTF-16 は NUL バイトが混ざるので先に疑う
    if b"\x00" in data[:1024]:
        for encoding in ("utf-16-le", "utf-16-be"):
            try:
                return data.decode(encoding)
            except UnicodeDecodeError:
                continue
    # 通常は UTF-8、ダメなら日本語 Windows の既定 (CP932 / Shift_JIS)
    for encoding in ("utf-8", "cp932"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError(
        "tsv", data, 0, 1,
        "文字コードを判定できませんでした (UTF-16 / UTF-8 / CP932 のいずれでも読めません)",
    )


def parse_tsv(text):
    """TSV テキストを [{"title": ..., "url": ...}, ...] に変換する。"""
    items = []
    skipped = 0
    for line in text.splitlines():
        if not line.strip():
            continue
        # URL は最後の列でタブを含まない。タイトル側にタブがあっても壊れないよう右から割る
        title, sep, url = line.rpartition("\t")
        if not sep:
            skipped += 1
            print(f"warning: タブ区切りでない行をスキップしました: {line[:50]!r}",
                  file=sys.stderr)
            continue
        items.append({"title": title, "url": url.strip()})
    return items, skipped


def main():
    tsv_path = find_tsv(BASE_DIR)
    if tsv_path is None:
        print(f"error: {DEFAULT_TSV_NAME} がこのファイルと同じフォルダにありません。",
              file=sys.stderr)
        print(f"       置き場所: {BASE_DIR}", file=sys.stderr)
        print("       tsv_to_json.py と同じフォルダに playlist.tsv を置いてください。",
              file=sys.stderr)
        return 1

    json_path = tsv_path.with_suffix(".json")

    try:
        text = decode_tsv(tsv_path.read_bytes())
    except (OSError, UnicodeDecodeError) as e:
        print(f"error: {tsv_path.name} を読み込めませんでした: {e}", file=sys.stderr)
        return 1

    items, skipped = parse_tsv(text)

    try:
        # 同梱されていた playlist.json は改行が CRLF だったため、それに合わせて固定する
        # (指定しないと OS によって LF / CRLF が変わり、全行差分になってしまう)
        with json_path.open("w", encoding="utf-8", newline="\r\n") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"error: {json_path.name} を書き込めませんでした: {e}", file=sys.stderr)
        return 1

    print(f"wrote {len(items)} items to {json_path}")
    if skipped:
        print(f"({skipped} lines skipped)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
