# AI Market Intelligence Terminal

每日 AI 股票分析報告展示網站，架設於 GitHub Pages。  
支援每日雙版本：**版本一（盤後）** 與 **版本二（早晨修訂）**。

---

## 📁 目錄結構

```
/docs
├── index.html                    ← 導覽首頁（勿修改）
├── journal.html                  ← 交易日誌（勿修改）
├── manifest.json                 ← 日期清單（腳本自動更新）
├── update_manifest.py            ← 本機執行腳本
│
├── 20260514_1_claude.html        ← 5/14 版本一（盤後，晚上上傳）
├── 20260514_2_claude.html        ← 5/14 版本二（早晨修訂，次日早上上傳）
├── 20260513_1_claude.html
├── 20260513_2_claude.html
└── ...
```

---

## 🗂 檔案命名規則

| 版本 | 命名格式 | 上傳時機 | 說明 |
|------|----------|----------|------|
| 版本一 | `YYYYMMDD_1_claude.html` | 當日盤後（晚上 7~8 點） | 台股收盤後的初版分析 |
| 版本二 | `YYYYMMDD_2_claude.html` | 次日早上 | 隔日重新分析的修訂版 |

> **關鍵原則：日期永遠對應「分析的那一天」**
>
> 範例：5/14 盤後出的報告 → `20260514_1_claude.html`  
> 5/15 早上出的修訂版（分析的還是 5/14）→ `20260514_2_claude.html`  
> 5/15 盤後出的新報告 → `20260515_1_claude.html`

---

## 📋 每日操作步驟

### 情況一：每日盤後（晚上 7~8 點）

```
1. 將 AI 報告存為  20260514_1_claude.html
   （日期換成當天）

2. 複製到 /docs 資料夾

3. 執行腳本（在 /docs 目錄下開 PowerShell）：
   python update_manifest.py

4. 輸入今日 Regime：
   1 = Risk-On  /  2 = 中性  /  3 = Risk-Off

5. Git 提交：
   git add .
   git commit -m "Add 20260514 v1 [Risk-On]"
   git push
```

### 情況二：次日早上上傳修訂版

```
1. 將修訂版存為  20260514_2_claude.html
   （日期仍為昨天 20260514，不是今天 20260515）

2. 複製到 /docs 資料夾

3. 執行腳本：
   python update_manifest.py
   （Regime 通常直接按 Enter 保留即可）

4. Git 提交：
   git add .
   git commit -m "Add 20260514 v2"
   git push
```

---

## 🖥 網站功能說明

| 功能 | 說明 |
|------|------|
| 日期下拉選單 | 顯示所有日期、Regime 狀態、已有版本標記 |
| 版本一 / 版本二 切換 | 綠點 = 已有此版本；灰色 = 尚未上傳 |
| 自動載入 | 開啟網站優先顯示最新日期的版本二（若已上傳），否則版本一 |
| Regime 徽章 | 綠色 = Risk-On、紅色 = Risk-Off、黃色 = 中性 |

---

## 🌐 GitHub Pages 設定（第一次）

1. 進入 GitHub repo → 點選 **Settings**

2. 左側選單 → **Pages**

3. **Source** 設定：
   - Branch: `main`
   - Folder: `/docs`

4. 點 **Save**，等 1~3 分鐘後網址出現：
   ```
   https://你的帳號.github.io/你的repo名稱/
   ```

---

## 📋 manifest.json 格式

```json
{
  "latest": "20260514",
  "dates": [
    {
      "date": "20260514",
      "display": "2026/05/14",
      "regime": "中性",
      "versions": ["1", "2"]
    },
    {
      "date": "20260513",
      "display": "2026/05/13",
      "regime": "Risk-On",
      "versions": ["1"]
    }
  ]
}
```

- `versions`：包含 `"1"` 和/或 `"2"`，腳本自動掃描填入
- `regime`：執行腳本時手動選擇

---

## ⚙️ 向下相容

資料夾內若有**舊格式**檔案（`YYYYMMDD_claude.html`），腳本會自動視為版本一，**無需重新命名**。

---

## ❓ 常見問題

**Q：Regime 填錯怎麼辦？**  
直接編輯 `manifest.json` 中的 `regime` 欄位，git push 即可。

**Q：想刪除某天的報告？**  
刪除 /docs 內的 HTML 檔，重新執行腳本，該日自動從清單移除。

**Q：網站更新沒反應？**  
GitHub Pages 有快取，等 1~3 分鐘，或按 `Ctrl+Shift+R` 強制重整。

**Q：腳本顏色亂碼？**  
改用 **PowerShell** 或 **Windows Terminal** 執行。
