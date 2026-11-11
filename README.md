# IDM Cleaner & Resetter

A simple Python tool to fully clean all **Internet Download Manager (IDM)** traces from your Windows PC — including registry keys, cached files, and temporary data.

---

## 📁 Files

| File | Description |
|------|-------------|
| `idm_cleaner.py` | Main Python script that performs all cleanup tasks |
| `Run_IDM_Cleaner.bat` | Double-click launcher — auto-elevates to Admin and runs the script |

---

## 🧹 What It Cleans

- **Processes** — Force-kills `IDMan.exe`, `IDMGrHlp.exe`, `IDMIntegrator.exe`
- **Registry Keys** — Removes IDM entries from `HKCU` and `HKLM` (including WOW64 variants and COM/CLSID keys)
- **Files & Cache** — Deletes IDM folders in `%APPDATA%`, `%LOCALAPPDATA%`, and `%ProgramData%`
- **Install Leftovers** — Clears residual `.cfg`, `.log`, and `.id` files from the IDM install directory
- **Hosts File** — Removes any IDM-related domain entries (e.g., `tonec.com`) added by third-party tools

---

## ▶️ How to Run

### Option 1 — Batch File (Recommended)
Simply **double-click `Run_IDM_Cleaner.bat`**.  
It will automatically request Administrator privileges (UAC prompt) and run the cleanup.

### Option 2 — Command Line
Open **PowerShell or CMD as Administrator** and run:
```powershell
python "C:\Users\ADIRAJ\Desktop\IDM Reseter\idm_cleaner.py"
```

---

## ⚙️ Requirements

- **Windows** 7 / 8 / 10 / 11
- **Python 3.9+** — Download from [python.org](https://www.python.org/downloads/)  
  *(Make sure to check "Add Python to PATH" during installation)*
- **Administrator privileges** — Required for registry and hosts file access

---

## ⚠️ Notes

> - Always **close IDM** before running this tool, or let the script kill it automatically.
> - **Restart your PC** after running for all changes to take full effect.
> - This tool does **not** uninstall IDM — it only removes stored data, trial info, and cached files.

---

## 📄 License

Free to use and modify for personal use.
