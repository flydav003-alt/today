# AI 股票分析報告網站

每日 AI 市場分析報告展示平台，部署於 GitHub Pages。

---

## 📁 檔案結構

```
repo/
├── docs/
│   ├── index.html              ← 導覽首頁（不需修改）
│   ├── manifest.json           ← 日期清單（每日自動更新）
│   ├── 20260513_claude.html    ← 每日手動新增的報告
│   ├── 20260512_claude.html
│   └── 20260511_claude.html
├── update_manifest.py          ← 每日執行的更新腳本
└── README.md
```

---

## 🚀 第一次設定：開啟 GitHub Pages

### 步驟 1：建立 GitHub Repository

1. 登入 [GitHub](https://github.com)
2. 點選右上角 **＋ → New repository**
3. 填入 Repository name（例如：`ai-market-intel`）
4. 選擇 **Public**（GitHub Pages 免費版需公開）
5. 點選 **Create repository**

### 步驟 2：上傳檔案到 repo

```bash
# 在本機初始化
git init
git add .
git commit -m "init: setup AI intel terminal"
git branch -M main
git remote add origin https://github.com/你的帳號/ai-market-intel.git
git push -u origin main
```

### 步驟 3：啟用 GitHub Pages

1. 進入 repo 頁面，點選上方 **Settings**
2. 左側選單找到 **Pages**
3. 在 **Branch** 下拉選單選擇 `main`
4. 在資料夾下拉選單選擇 `/docs`
5. 點選 **Save**

> 等待約 1～3 分鐘後，網站網址會顯示在 Pages 設定頁面頂端，格式為：
> `https://你的帳號.github.io/ai-market-intel/`

---

## 📋 每日操作流程

### 步驟 1：新增當日報告 HTML

將 Claude 產生的分析報告存為 HTML 檔，命名格式：

```
YYYYMMDD_claude.html
```

範例：
```
20260514_claude.html
```

將此檔案放入 `docs/` 資料夾。

---

### 步驟 2：執行 update_manifest.py 更新日期清單

在 repo 根目錄（`update_manifest.py` 所在位置）執行：

```bash
python update_manifest.py
```

程式會：
1. 自動掃描 `docs/` 內所有 `YYYYMMDD_claude.html` 檔案
2. 詢問你輸入今日的 **Market Regime**（選 1/2/3）：
   - `1` → Risk-On
   - `2` → 中性
   - `3` → Risk-Off
3. 自動更新 `docs/manifest.json`
4. 顯示確認訊息

範例輸出：
```
╔══════════════════════════════════════════╗
║   AI INTEL TERMINAL — Manifest Updater  ║
╚══════════════════════════════════════════╝

  📂 掃描目錄：C:\Users\你\repos\ai-market-intel\docs
  ✔ 找到 4 份報告：
      • 2026/05/14
      • 2026/05/13
      • 2026/05/12
      • 2026/05/11

  📅 最新日期：2026/05/14
  請選擇 Regime：
    1. Risk-On
    2. 中性
    3. Risk-Off

  輸入編號或名稱：1

  ✔ manifest.json 更新完成！
  最新日期     ：2026/05/14
  最新 Regime  ：Risk-On
  總筆數       ：4 筆
  新增         ：+1 筆
```

---

### 步驟 3：git push 更新網站

```bash
cd docs                              # 或在 repo 根目錄
git add docs/20260514_claude.html
git add docs/manifest.json
git commit -m "report: add 20260514 analysis [Risk-On]"
git push
```

> GitHub Pages 會在約 **1 分鐘** 內自動重新部署，重新整理網站即可看到最新報告。

---

## ⚡ 每日快速指令（複製貼上用）

```bash
# 假設今日日期為 20260514，報告已放入 docs/
python update_manifest.py
git add docs/20260514_claude.html docs/manifest.json
git commit -m "report: 20260514"
git push
```

---

## 🗂 manifest.json 格式說明

```json
{
  "latest": "20260514",
  "dates": [
    {"date": "20260514", "display": "2026/05/14", "regime": "Risk-On"},
    {"date": "20260513", "display": "2026/05/13", "regime": "Risk-On"},
    {"date": "20260512", "display": "2026/05/12", "regime": "中性"},
    {"date": "20260511", "display": "2026/05/11", "regime": "Risk-Off"}
  ]
}
```

| 欄位 | 說明 |
|------|------|
| `latest` | 最新報告的日期（YYYYMMDD 格式） |
| `dates` | 所有報告清單，依日期降冪排序 |
| `date` | 日期字串，對應 HTML 檔名前綴 |
| `display` | 顯示用日期（YYYY/MM/DD 格式） |
| `regime` | 市場狀態：`Risk-On` / `中性` / `Risk-Off` |

---

## ❓ 常見問題

### Q：網站更新後看不到最新報告？
- 嘗試強制重新整理：`Ctrl + Shift + R`（Windows）或 `Cmd + Shift + R`（Mac）
- GitHub Pages 部署需要 1～3 分鐘，請稍等後再試

### Q：update_manifest.py 找不到 Python？
- 確認已安裝 Python 3.8+：`python --version`
- Windows 使用者可從 [python.org](https://www.python.org/downloads/) 下載安裝

### Q：manifest.json 的舊日期 Regime 填錯了怎麼辦？
- 直接用文字編輯器（如 VS Code）開啟 `docs/manifest.json` 手動修改對應的 `"regime"` 欄位，存檔後 git push 即可

### Q：如何手動修改已存在日期的 Regime？
- 執行 `python update_manifest.py` 時，若最新日期已有 Regime，腳本會詢問是否更新
- 或直接編輯 `manifest.json` 的 `"regime"` 欄位

---

## 🔧 技術規格

| 項目 | 說明 |
|------|------|
| 部署平台 | GitHub Pages（/docs 資料夾） |
| 前端框架 | 純 HTML/CSS/JS（無外部依賴） |
| 風格 | Bloomberg Terminal 深色系，monospace 字型 |
| 資料來源 | `manifest.json`（靜態 JSON，無需後端） |
| Python 版本 | 3.8+（update_manifest.py） |

---

*AI Intel Terminal — Powered by Claude*
