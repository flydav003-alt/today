#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
update_manifest.py
==================
自動掃描 /docs 資料夾，更新 manifest.json 的日期清單。
執行環境：Windows（Python 3.8+）

使用方式：
  python update_manifest.py

功能：
  - 掃描所有符合 YYYYMMDD_claude.html 格式的檔案
  - 詢問使用者輸入當天（最新日期）的 Regime
  - 更新 manifest.json，依日期降冪排序
  - 輸出確認訊息
"""

import os
import re
import json
import sys
from datetime import datetime
from pathlib import Path

# ── 設定 ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent          # 腳本所在資料夾（即 /docs）
MANIFEST_PATH = SCRIPT_DIR / "manifest.json"
HTML_PATTERN = re.compile(r"^(\d{8})_claude\.html$", re.IGNORECASE)

VALID_REGIMES = ["Risk-On", "中性", "Risk-Off"]

# ── 顏色輸出（Windows CMD / PowerShell 支援 ANSI 轉義碼）────────────────────
def c(text, code): return f"\033[{code}m{text}\033[0m"
GREEN  = lambda t: c(t, "92")
YELLOW = lambda t: c(t, "93")
RED    = lambda t: c(t, "91")
CYAN   = lambda t: c(t, "96")
BOLD   = lambda t: c(t, "1")
DIM    = lambda t: c(t, "2")

def enable_ansi_windows():
    """在 Windows 上啟用 ANSI 色彩支援"""
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass

def header():
    print()
    print(CYAN("╔══════════════════════════════════════════╗"))
    print(CYAN("║") + BOLD("   AI INTEL TERMINAL — Manifest Updater  ") + CYAN("║"))
    print(CYAN("╚══════════════════════════════════════════╝"))
    print()

def scan_html_files(docs_dir: Path) -> list[str]:
    """掃描資料夾，回傳所有符合格式的日期字串（降冪排序）"""
    dates_found = []
    for filename in os.listdir(docs_dir):
        m = HTML_PATTERN.match(filename)
        if m:
            date_str = m.group(1)
            # 驗證日期格式是否合法
            try:
                datetime.strptime(date_str, "%Y%m%d")
                dates_found.append(date_str)
            except ValueError:
                print(YELLOW(f"  ⚠  跳過格式不合法的日期：{filename}"))
    # 降冪排序（最新在前）
    dates_found.sort(reverse=True)
    return dates_found

def load_existing_manifest(path: Path) -> dict:
    """載入現有的 manifest.json，若不存在則回傳空結構"""
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(YELLOW(f"  ⚠  現有 manifest.json 讀取失敗（{e}），將重新建立"))
    return {"latest": "", "dates": []}

def format_display(date_str: str) -> str:
    """將 20260513 → 2026/05/13"""
    return f"{date_str[:4]}/{date_str[4:6]}/{date_str[6:8]}"

def ask_regime(date_str: str) -> str:
    """詢問使用者輸入最新日期的 Regime"""
    display = format_display(date_str)
    print(f"\n  📅 最新日期：{BOLD(display)}")
    print(f"  請選擇 Regime：")
    for i, r in enumerate(VALID_REGIMES, 1):
        print(f"    {CYAN(str(i))}. {r}")
    print()

    while True:
        raw = input("  輸入編號或名稱（1/2/3 或 Risk-On/中性/Risk-Off）：").strip()
        # 數字輸入
        if raw in ("1", "2", "3"):
            return VALID_REGIMES[int(raw) - 1]
        # 文字輸入（不分大小寫比對）
        for v in VALID_REGIMES:
            if raw.lower() == v.lower() or raw == v:
                return v
        print(RED("  ✕ 無效輸入，請輸入 1、2、3 或對應名稱"))

def main():
    enable_ansi_windows()
    header()

    docs_dir = SCRIPT_DIR
    print(f"  📂 掃描目錄：{DIM(str(docs_dir))}")

    # 1. 掃描 HTML 檔案
    found_dates = scan_html_files(docs_dir)

    if not found_dates:
        print(RED("\n  ✕ 找不到任何符合格式的 HTML 檔案（YYYYMMDD_claude.html）"))
        print(DIM("    請確認 /docs 資料夾內有正確命名的報告檔案"))
        input("\n  按 Enter 結束...")
        return

    print(f"\n  ✔ 找到 {GREEN(str(len(found_dates)))} 份報告：")
    for d in found_dates:
        print(f"      {DIM('•')} {format_display(d)}")

    # 2. 載入現有 manifest
    existing = load_existing_manifest(MANIFEST_PATH)
    existing_map = {entry["date"]: entry for entry in existing.get("dates", [])}

    # 3. 詢問最新日期的 Regime
    latest_date = found_dates[0]
    latest_display = format_display(latest_date)

    existing_latest = existing_map.get(latest_date, {})
    current_regime = existing_latest.get("regime", "")

    if current_regime:
        print(f"\n  📋 最新日期 {BOLD(latest_display)} 現有 Regime：{YELLOW(current_regime)}")
        answer = input("  是否更新 Regime？（直接按 Enter 保留 / 輸入新值）：").strip()
        if answer:
            # 嘗試解析新輸入
            if answer in ("1", "2", "3"):
                regime_for_latest = VALID_REGIMES[int(answer) - 1]
            else:
                matched = next((v for v in VALID_REGIMES if v.lower() == answer.lower()), None)
                if matched:
                    regime_for_latest = matched
                else:
                    print(YELLOW(f"  ⚠  未能辨識「{answer}」，保留原有 Regime：{current_regime}"))
                    regime_for_latest = current_regime
        else:
            regime_for_latest = current_regime
    else:
        regime_for_latest = ask_regime(latest_date)

    # 4. 組建新的 dates 清單
    new_dates = []
    for date_str in found_dates:
        display = format_display(date_str)
        if date_str == latest_date:
            regime = regime_for_latest
        elif date_str in existing_map:
            regime = existing_map[date_str].get("regime", "中性")
        else:
            # 新發現的舊日期，設預設值
            regime = "中性"
            print(YELLOW(f"  ⚠  {display} 為新增項目，Regime 預設為「中性」，請手動編輯 manifest.json 修改"))
        new_dates.append({"date": date_str, "display": display, "regime": regime})

    # 5. 計算差異
    old_count = len(existing.get("dates", []))
    new_count = len(new_dates)
    added   = new_count - old_count if new_count > old_count else 0
    removed = old_count - new_count if old_count > new_count else 0

    # 6. 寫入 manifest.json
    new_manifest = {
        "latest": latest_date,
        "dates": new_dates
    }
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(new_manifest, f, ensure_ascii=False, indent=2)

    # 7. 確認輸出
    print()
    print(GREEN("  ✔ manifest.json 更新完成！"))
    print()
    print(f"  {'─'*40}")
    print(f"  最新日期     ：{BOLD(latest_display)}")
    print(f"  最新 Regime  ：{YELLOW(regime_for_latest)}")
    print(f"  總筆數       ：{new_count} 筆")
    if added:
        print(f"  新增         ：{GREEN(f'+{added}')} 筆")
    if removed:
        print(f"  移除         ：{RED(f'-{removed}')} 筆")
    print(f"  {'─'*40}")
    print()
    print(DIM(f"  輸出路徑：{MANIFEST_PATH}"))
    print()
    print("  ✅ 完成！現在可以 git add / commit / push 更新網站")
    print()
    input("  按 Enter 結束...")

if __name__ == "__main__":
    main()
