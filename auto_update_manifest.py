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
# 新格式：YYYYMMDD_1_claude.html 或 YYYYMMDD_2_claude.html
HTML_PATTERN = re.compile(r"^(\d{8})_([12])_claude\.html$", re.IGNORECASE)
# 舊格式（向下相容）：YYYYMMDD_claude.html → 視為版本一
HTML_PATTERN_OLD = re.compile(r"^(\d{8})_claude\.html$", re.IGNORECASE)

VALID_REGIMES = ["Risk-On", "中性", "Risk-Off"]
DEFAULT_REGIME = "中性"


def scan_html_files() -> dict:
    """回傳 {date_str: sorted list of versions}"""
    result: dict[str, set] = {}
    for filename in os.listdir(DOCS_DIR):
        # 新格式
        m = HTML_PATTERN.match(filename)
        if m:
            date_str, ver = m.group(1), m.group(2)
            try:
                datetime.strptime(date_str, "%Y%m%d")
                result.setdefault(date_str, set()).add(ver)
            except ValueError:
                print(f"[WARN] 跳過格式不合法：{filename}")
            continue
        # 舊格式（相容）
        m2 = HTML_PATTERN_OLD.match(filename)
        if m2:
            date_str = m2.group(1)
            try:
                datetime.strptime(date_str, "%Y%m%d")
                result.setdefault(date_str, set()).add("1")
                print(f"[WARN] 舊格式偵測：{filename} → 視為版本一")
            except ValueError:
                print(f"[WARN] 跳過格式不合法：{filename}")
    # 回傳 {date: sorted versions list}，日期降冪排序
    return {d: sorted(result[d]) for d in sorted(result.keys(), reverse=True)}


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
    date_versions = scan_html_files()
    if not date_versions:
        print("[ERROR] 找不到任何 YYYYMMDD_N_claude.html 檔案，結束。")
        return

    sorted_dates = list(date_versions.keys())  # 已降冪排序
    total_files = sum(len(v) for v in date_versions.values())
    print(f"[INFO] 找到 {len(sorted_dates)} 個交易日，共 {total_files} 份報告：")
    for d in sorted_dates:
        print(f"       {format_display(d)}  版本：{', '.join(date_versions[d])}")

    # 載入現有 manifest
    existing = load_existing_manifest()
    existing_map = {entry["date"]: entry for entry in existing.get("dates", [])}

    latest_date = sorted_dates[0]

    # 組建新清單
    new_dates = []
    for date_str in sorted_dates:
        display = format_display(date_str)
        versions = date_versions[date_str]

        if date_str == latest_date and detected_regime:
            regime = detected_regime
        elif date_str in existing_map:
            regime = existing_map[date_str].get("regime", DEFAULT_REGIME)
        else:
            regime = DEFAULT_REGIME
            print(f"[WARN] {display} 為新增且非最新，Regime 預設為「{DEFAULT_REGIME}」")

        new_dates.append({"date": date_str, "display": display, "regime": regime, "versions": versions})

    # 計算變動
    old_set = set(existing_map.keys())
    new_set = set(sorted_dates)
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
