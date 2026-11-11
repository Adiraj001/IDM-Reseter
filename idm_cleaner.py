"""
IDM (Internet Download Manager) Cleaner & Resetter
----------------------------------------------------
Clears IDM used files, cache, download history, and registry keys.
Run as Administrator for full registry access.
"""

import os
import sys
import shutil
import winreg
import subprocess
import ctypes
from pathlib import Path


# ─── Helpers ────────────────────────────────────────────────────────────────

def is_admin() -> bool:
    """Check if the script is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def run_as_admin():
    """Re-launch the script with administrator privileges."""
    script = sys.argv[0]
    params = " ".join(sys.argv[1:])
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, f'"{script}" {params}', None, 1
    )
    sys.exit(0)


def kill_idm_processes():
    """Terminate all running IDM processes."""
    processes = ["IDMan.exe", "IDMGrHlp.exe", "IDMIntegrator.exe"]
    killed = []
    for proc in processes:
        result = subprocess.run(
            ["taskkill", "/F", "/IM", proc],
            capture_output=True, text=True
        )
        if "SUCCESS" in result.stdout or "successfully" in result.stdout.lower():
            killed.append(proc)
    if killed:
        print(f"  [✓] Killed processes: {', '.join(killed)}")
    else:
        print("  [i] No IDM processes were running.")


def delete_registry_key(hive, key_path: str):
    """Recursively delete a registry key and all its sub-keys."""
    try:
        hive_handle = winreg.OpenKey(hive, key_path, 0, winreg.KEY_ALL_ACCESS)
    except FileNotFoundError:
        print(f"  [i] Registry key not found (already clean): {key_path}")
        return
    except PermissionError:
        print(f"  [!] Permission denied for key: {key_path}")
        return

    # Delete all sub-keys first (registry requires depth-first deletion)
    try:
        while True:
            subkey_name = winreg.EnumKey(hive_handle, 0)
            delete_registry_key(hive, f"{key_path}\\{subkey_name}")
    except OSError:
        pass  # No more sub-keys

    winreg.CloseKey(hive_handle)
    try:
        winreg.DeleteKey(hive, key_path)
        print(f"  [✓] Deleted registry key: {key_path}")
    except Exception as e:
        print(f"  [✗] Failed to delete key {key_path}: {e}")


def delete_registry_value(hive, key_path: str, value_name: str):
    """Delete a single registry value."""
    try:
        with winreg.OpenKey(hive, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, value_name)
            print(f"  [✓] Deleted registry value: {key_path}\\{value_name}")
    except FileNotFoundError:
        print(f"  [i] Registry value not found (already clean): {key_path}\\{value_name}")
    except Exception as e:
        print(f"  [✗] Failed to delete value {key_path}\\{value_name}: {e}")


def delete_path(path: str):
    """Delete a file or directory (with all its contents)."""
    p = Path(path)
    if not p.exists():
        print(f"  [i] Not found (already clean): {path}")
        return
    try:
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
        print(f"  [✓] Deleted: {path}")
    except Exception as e:
        print(f"  [✗] Failed to delete {path}: {e}")


# ─── Main Sections ────────────────────────────────────────────────────────────

def clear_registry_keys():
    """Remove IDM registry keys (trial data, serial, settings)."""
    print("\n[1] Clearing IDM Registry Keys...")

    # Main IDM key under HKCU
    delete_registry_key(winreg.HKEY_CURRENT_USER, r"Software\DownloadManager")

    # IDM entries under HKLM (requires admin)
    delete_registry_key(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Internet Download Manager")
    delete_registry_key(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Internet Download Manager")

    # Uninstall entries (optional — only deletes if IDM is already uninstalled)
    for uninst_key in [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Internet Download Manager",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Internet Download Manager",
    ]:
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, uninst_key):
                pass  # Key exists — IDM still installed, skip
        except FileNotFoundError:
            # IDM uninstalled; safe to remove leftover uninstall entry
            delete_registry_key(winreg.HKEY_LOCAL_MACHINE, uninst_key)

    # Browser integration / shell extension COM keys
    clsids = [
        r"SOFTWARE\Classes\CLSID\{BD071E56-3DDF-4E78-8B4D-A7CB6B6F7B62}",
        r"SOFTWARE\Classes\CLSID\{BEEBEEF1-C6EA-4b69-88A7-73A7E3BD7B73}",
    ]
    for clsid in clsids:
        delete_registry_key(winreg.HKEY_LOCAL_MACHINE, clsid)
        delete_registry_key(winreg.HKEY_CURRENT_USER, clsid)


def clear_idm_files():
    """Remove IDM temporary files, cache, and download history databases."""
    print("\n[2] Clearing IDM Files & Cache...")

    appdata = os.getenv("APPDATA", "")
    localappdata = os.getenv("LOCALAPPDATA", "")
    programdata = os.getenv("ProgramData", "C:\\ProgramData")

    paths_to_delete = [
        # IDM AppData folders
        os.path.join(appdata, "IDM"),
        os.path.join(localappdata, "IDM"),
        # IDM temp / cache inside Internet Download Manager install folder
        os.path.join(programdata, "IDM"),
        # Common IDM download history / queue file locations
        os.path.join(appdata, "Internet Download Manager"),
        os.path.join(localappdata, "Internet Download Manager"),
        # Specific known files
        os.path.join(appdata, "IDM", "DwnlData"),
        os.path.join(os.getenv("SystemRoot", "C:\\Windows"), "system32", "IDMShellExt64.dll"),
        os.path.join(os.getenv("SystemRoot", "C:\\Windows"), "SysWOW64", "IDMShellExt.dll"),
    ]

    for path in paths_to_delete:
        delete_path(path)


def clear_idm_install_leftovers():
    """Remove leftover files from the IDM installation directory."""
    print("\n[3] Clearing IDM Installation Leftovers...")

    candidate_dirs = [
        r"C:\Program Files\Internet Download Manager",
        r"C:\Program Files (x86)\Internet Download Manager",
    ]

    for d in candidate_dirs:
        p = Path(d)
        if p.exists():
            # Only wipe residual data files, not the full install (IDM may still be installed)
            residual_files = ["IDMan.id", "IDMGrHlp.dll", "*.cfg", "*.log"]
            for pattern in residual_files:
                for f in p.glob(pattern):
                    try:
                        f.unlink()
                        print(f"  [✓] Deleted residual file: {f}")
                    except Exception as e:
                        print(f"  [✗] Could not delete {f}: {e}")
        else:
            print(f"  [i] IDM install directory not found: {d}")


def clear_hosts_entries():
    """Remove IDM-related activation-bypass entries from the hosts file (if any)."""
    print("\n[4] Checking Hosts File for IDM Entries...")

    hosts_path = Path(os.getenv("SystemRoot", "C:\\Windows")) / "System32" / "drivers" / "etc" / "hosts"
    idm_domains = ["tonec.com", "internetdownloadmanager.com", "mirror.internetdownloadmanager.com"]

    try:
        lines = hosts_path.read_text(encoding="utf-8", errors="ignore").splitlines(keepends=True)
        filtered = [
            line for line in lines
            if not any(domain in line.lower() for domain in idm_domains)
        ]
        if len(filtered) < len(lines):
            hosts_path.write_text("".join(filtered), encoding="utf-8")
            removed = len(lines) - len(filtered)
            print(f"  [✓] Removed {removed} IDM-related host(s) entry(ies).")
        else:
            print("  [i] No IDM entries found in hosts file.")
    except PermissionError:
        print("  [!] Cannot write to hosts file — run as Administrator.")
    except Exception as e:
        print(f"  [✗] Error processing hosts file: {e}")


# ─── Entry Point ─────────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("   IDM Cleaner & Resetter")
    print("=" * 55)

    if not is_admin():
        print("\n[!] Not running as Administrator.")
        choice = input("    Re-launch with admin privileges? [Y/n]: ").strip().lower()
        if choice in ("", "y", "yes"):
            run_as_admin()
        else:
            print("    Continuing without admin — some operations may fail.\n")

    print("\nStep 0: Terminating IDM processes...")
    kill_idm_processes()

    clear_registry_keys()
    clear_idm_files()
    clear_idm_install_leftovers()
    clear_hosts_entries()

    print("\n" + "=" * 55)
    print("   Done! IDM data has been cleared.")
    print("   Restart your PC for changes to take full effect.")
    print("=" * 55)
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
