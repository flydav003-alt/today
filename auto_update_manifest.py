#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auto_update_manifest.py
========================
GitHub Actions 自動化版本。
- 從環境變數 COMMIT_MSG 解析 Regime
- 自動掃描 docs/ 資料夾
- 更新 manifest.json

Regime 解析規則（commit message 包含以下關鍵字）：
  Risk-On  → Risk-On
  Risk-Off → Risk-Off
  中性 / neutral → 中性
  未偵測到  → 沿用舊值，若為新日期則預設「中性」
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path

DOCS_DIR = Path(__file__).parent / "docs"
MANIFEST_PATH = DOCS_DIR / "manifest.json"
HTML_PATTERN = re.compile(r"^(\d{8})_claude\.html$", re.IGNORECASE)

VALID_REGIMES = ["Risk-On", "中性", "Risk-Off"]
DEFAULT_REGIME = "中性"


def scan_html_files() -> list[str]:
    dates = []
    for filename in os.listdir(DOCS_DIR):
        m = HTML_PATTERN.match(filename)
        if m:
            date_str = m.group(1)
            try:
                datetime.strptime(date_str, "%Y%m%d")
                dates.append(date_str)
            except ValueError:
                print(f"[WARN] 跳過格式不合法：{filename}")
    dates.sort(reverse=True)
    return dates


def load_existing_manifest() -> dict:
    if MANIFEST_PATH.exists():
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARN] 無法讀取現有 manifest.json：{e}")
    return {"latest": "", "dates": []}


def parse_regime_from_commit(commit_msg: str) -> str | None:
    """從 commit message 解析 Regime"""
    if not commit_msg:
        return None
    msg = commit_msg.lower()
    if "risk-on" in msg or "risk on" in msg:
        return "Risk-On"
    if "risk-off" in msg or "risk off" in msg:
        return "Risk-Off"
    if "中性" in commit_msg or "neutral" in msg:
        return "中性"
    return None


def format_display(date_str: str) -> str:
    return f"{date_str[:4]}/{date_str[4:6]}/{date_str[6:8]}"


def main():
    print("=" * 50)
    print("  AI Intel Terminal — Auto Manifest Updater")
    print("=" * 50)

    # 取得 commit message
    commit_msg = os.environ.get("COMMIT_MSG", "")
    print(f"[INFO] Commit message: {commit_msg!r}")

    # 解析 Regime
    detected_regime = parse_regime_from_commit(commit_msg)
    if detected_regime:
        print(f"[INFO] 從 commit message 偵測到 Regime：{detected_regime}")
    else:
        print(f"[INFO] 未偵測到 Regime，將沿用舊值（新日期預設：{DEFAULT_REGIME}）")

    # 掃描檔案
    found_dates = scan_html_files()
    if not found_dates:
        print("[ERROR] 找不到任何 YYYYMMDD_claude.html 檔案，結束。")
        return

    print(f"[INFO] 找到 {len(found_dates)} 份報告：{', '.join(format_display(d) for d in found_dates)}")

    # 載入現有 manifest
    existing = load_existing_manifest()
    existing_map = {entry["date"]: entry for entry in existing.get("dates", [])}

    latest_date = found_dates[0]

    # 組建新清單
    new_dates = []
    for date_str in found_dates:
        display = format_display(date_str)

        if date_str == latest_date and detected_regime:
            # 最新日期 + commit message 有帶 Regime → 使用解析值
            regime = detected_regime
        elif date_str in existing_map:
            # 舊日期 → 沿用原有 Regime
            regime = existing_map[date_str].get("regime", DEFAULT_REGIME)
        else:
            # 新掃描到的舊日期（不是 latest）→ 預設中性
            regime = DEFAULT_REGIME
            print(f"[WARN] {display} 為新增且非最新，Regime 預設為「{DEFAULT_REGIME}」")

        new_dates.append({"date": date_str, "display": display, "regime": regime})

    # 計算變動
    old_set = set(existing_map.keys())
    new_set = set(found_dates)
    added = new_set - old_set
    removed = old_set - new_set

    # 寫入
    new_manifest = {"latest": latest_date, "dates": new_dates}
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(new_manifest, f, ensure_ascii=False, indent=2)

    # 輸出摘要
    print()
    print("[OK] manifest.json 更新完成")
    print(f"     最新日期  : {format_display(latest_date)}")
    print(f"     最新Regime: {new_dates[0]['regime']}")
    print(f"     總筆數    : {len(new_dates)} 筆")
    if added:
        print(f"     新增      : {', '.join(format_display(d) for d in sorted(added, reverse=True))}")
    if removed:
        print(f"     移除      : {', '.join(format_display(d) for d in sorted(removed, reverse=True))}")
    print("=" * 50)


if __name__ == "__main__":
    main()
