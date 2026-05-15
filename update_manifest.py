#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
update_manifest.py
==================
自動掃描 /docs 資料夾，更新 manifest.json。
支援雙版本：版本一（盤後）與版本二（早晨修訂）。

檔案命名規則：
  20260514_1_claude.html  ← 版本一：台股盤後（晚上 7~8 點上傳）
  20260514_2_claude.html  ← 版本二：早晨修訂版（次日早上上傳，日期仍為分析當日）

執行環境：Windows（Python 3.8+）
使用方式：在 /docs 資料夾內執行  python update_manifest.py
"""

import os
import re
import json
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR    = Path(__file__).parent
MANIFEST_PATH = SCRIPT_DIR / "manifest.json"

# 新格式：YYYYMMDD_1_claude.html 或 YYYYMMDD_2_claude.html
HTML_PATTERN = re.compile(r"^(\d{8})_([12])_claude\.html$", re.IGNORECASE)
# 舊格式（向下相容）：YYYYMMDD_claude.html → 視為版本一
HTML_PATTERN_OLD = re.compile(r"^(\d{8})_claude\.html$", re.IGNORECASE)

VALID_REGIMES  = ["Risk-On", "中性", "Risk-Off"]
DEFAULT_REGIME = "中性"

# ── 顏色輸出 ──────────────────────────────────────────────────────────────────
def c(text, code): return f"\033[{code}m{text}\033[0m"
GREEN  = lambda t: c(t, "92")
YELLOW = lambda t: c(t, "93")
RED    = lambda t: c(t, "91")
CYAN   = lambda t: c(t, "96")
BOLD   = lambda t: c(t, "1")
DIM    = lambda t: c(t, "2")

def enable_ansi():
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.kernel32.SetConsoleMode(
                ctypes.windll.kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass

def header():
    print()
    print(CYAN("╔══════════════════════════════════════════════════╗"))
    print(CYAN("║") + BOLD("   AI INTEL TERMINAL — Manifest Updater          ") + CYAN("║"))
    print(CYAN("║") + DIM("   命名規則：YYYYMMDD_1_claude.html / _2_claude   ") + CYAN("║"))
    print(CYAN("╚══════════════════════════════════════════════════╝"))
    print()

# ── 掃描 ──────────────────────────────────────────────────────────────────────
def scan_files(docs_dir: Path) -> dict:
    """回傳 {date_str: {'1', '2', ...}} 的字典"""
    result: dict[str, set] = {}

    for filename in os.listdir(docs_dir):
        # 新格式
        m = HTML_PATTERN.match(filename)
        if m:
            date_str, ver = m.group(1), m.group(2)
            try:
                datetime.strptime(date_str, "%Y%m%d")
                result.setdefault(date_str, set()).add(ver)
            except ValueError:
                print(YELLOW(f"  ⚠  跳過日期不合法：{filename}"))
            continue

        # 舊格式（相容）
        m2 = HTML_PATTERN_OLD.match(filename)
        if m2:
            date_str = m2.group(1)
            try:
                datetime.strptime(date_str, "%Y%m%d")
                result.setdefault(date_str, set()).add("1")
                print(YELLOW(f"  ⚠  舊格式偵測：{filename} → 視為版本一"))
            except ValueError:
                print(YELLOW(f"  ⚠  跳過日期不合法：{filename}"))

    return result

def load_manifest(path: Path) -> dict:
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(YELLOW(f"  ⚠  讀取失敗（{e}），將重新建立"))
    return {"latest": "", "dates": []}

def fd(d: str) -> str:
    return f"{d[:4]}/{d[4:6]}/{d[6:8]}"

def ask_regime(date_str: str, current: str = "") -> str:
    if current:
        print(f"\n  {BOLD(fd(date_str))} 現有 Regime：{YELLOW(current)}")
        raw = input("  直接 Enter 保留，或輸入新值（1/2/3）：").strip()
        if not raw:
            return current
    else:
        print(f"\n  {BOLD(fd(date_str))} 請選擇 Regime：")
        raw = input("  1=Risk-On  2=中性  3=Risk-Off  > ").strip()

    if raw in ("1", "2", "3"):
        return VALID_REGIMES[int(raw) - 1]
    for v in VALID_REGIMES:
        if raw.lower() == v.lower():
            return v
    if raw:
        print(YELLOW(f"  ⚠  未辨識「{raw}」，保留：{current or DEFAULT_REGIME}"))
    return current or DEFAULT_REGIME

# ── 主程式 ────────────────────────────────────────────────────────────────────
def main():
    enable_ansi()
    header()

    docs_dir = SCRIPT_DIR
    print(f"  📂 掃描：{DIM(str(docs_dir))}\n")

    date_versions = scan_files(docs_dir)

    if not date_versions:
        print(RED("  ✕ 找不到任何報告檔案"))
        print(DIM("    請確認命名格式：YYYYMMDD_1_claude.html"))
        input("\n  按 Enter 結束...")
        return

    sorted_dates = sorted(date_versions.keys(), reverse=True)

    # 顯示掃描結果
    total_files = sum(len(v) for v in date_versions.values())
    print(f"  ✔ 找到 {GREEN(str(len(sorted_dates)))} 個交易日，共 {GREEN(str(total_files))} 份報告：\n")
    for d in sorted_dates:
        vers = sorted(date_versions[d])
        tags = "  ".join(
            (GREEN(f"版本{v}●") if v == "2" else YELLOW(f"版本{v}●"))
            for v in vers
        )
        print(f"      {DIM('•')} {fd(d)}  {tags}")

    # 載入現有 manifest
    existing      = load_manifest(MANIFEST_PATH)
    existing_map  = {e["date"]: e for e in existing.get("dates", [])}
    latest_date   = sorted_dates[0]

    print(f"\n  {'─'*46}")
    print(f"  ★  最新日期：{BOLD(fd(latest_date))}")
    print(f"  {'─'*46}")

    new_dates = []
    for date_str in sorted_dates:
        old_entry  = existing_map.get(date_str, {})
        old_regime = old_entry.get("regime", "")
        old_vers   = set(old_entry.get("versions", []))
        new_vers   = sorted(date_versions[date_str])

        # 詢問 Regime：最新日期 or 首次出現的日期
        is_new = date_str not in existing_map
        if date_str == latest_date or is_new:
            regime = ask_regime(date_str, old_regime)
        else:
            regime = old_regime or DEFAULT_REGIME

        new_dates.append({
            "date":     date_str,
            "display":  fd(date_str),
            "regime":   regime,
            "versions": new_vers
        })

    # 寫入
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump({"latest": latest_date, "dates": new_dates}, f,
                  ensure_ascii=False, indent=2)

    # 摘要
    added   = set(sorted_dates) - set(existing_map)
    removed = set(existing_map) - set(sorted_dates)

    print()
    print(GREEN("  ✔ manifest.json 更新完成！"))
    print()
    print(f"  {'─'*46}")
    print(f"  最新日期    ：{BOLD(fd(latest_date))}")
    print(f"  最新 Regime ：{YELLOW(new_dates[0]['regime'])}")
    print(f"  已有版本    ：{', '.join('版本'+v for v in new_dates[0]['versions'])}")
    print(f"  交易日總數  ：{len(new_dates)} 天")
    if added:
        print(f"  新增日期    ：{GREEN(', '.join(fd(d) for d in sorted(added, reverse=True)))}")
    if removed:
        print(f"  移除日期    ：{RED(', '.join(fd(d) for d in sorted(removed, reverse=True)))}")
    print(f"  {'─'*46}")
    print()
    print(DIM(f"  輸出：{MANIFEST_PATH}"))
    print()
    print("  ✅ 完成！執行 git add . → commit → push")
    print()
    input("  按 Enter 結束...")

if __name__ == "__main__":
    main()
