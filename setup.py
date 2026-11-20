#!/usr/bin/env python3
"""
Ola S1 Quick Mod & Setup Tool (Cross-Platform: Windows, macOS, Linux)
Automates:
  1. Finding Ola scooter IP over local Wi-Fi / Hotspot
  2. Verifying environment, MoveOS compatibility, and waking scooter
  3. Unlocking ADB access (safe, reversible RAM bind-mount)
  4. Resolving bundled local APKs (Balls Navigation, Music Mod, Android Auto)
  5. Installing APKs & granting required Android permissions
  6. Bringing dashboard speedometer back to front
"""
from __future__ import annotations

import argparse
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time

try:
    import grpc
    import ola
except ImportError:
    print("[*] Missing dependencies. Installing grpcio...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--disable-pip-version-check", "grpcio>=1.50.0"], check=True)
        import grpc
        import ola
    except Exception as exc:
        print(f"[!] Could not install grpcio automatically: {exc}")
        print("    Please run:  pip install -r requirements.txt")
        sys.exit(1)

BANNER = r"""
========================================================================
     ___  _          ____  _     ___        _      _     ____       _               
    / _ \| | __ _   / ___|/ |   / _ \ _   _(_) ___| | __/ ___|  ___| |_ _   _ _ __  
   | | | | |/ _` |  \___ \| |  | | | | | | | |/ __| |/ /\___ \ / _ \ __| | | | '_ \ 
   | |_| | | (_| |   ___) | |  | |_| | |_| | | (__|   <  ___) |  __/ |_| |_| | |_) |
    \___/|_|\__,_|  |____/|_|   \__\_\\__,_|_|\___|_|\_\|____/ \___|\__|\__,_| .__/ 
                                                                              |_|    
               Automated Floating Navigation & Music Installer
                   Cross-Platform (Windows, macOS & Linux)
========================================================================
"""

def print_step(num: int, title: str):
    print(f"\n[{num}/6] {title}")
    print("-" * 60)

def find_adb() -> str:
    """Finds adb executable path on Windows, macOS, and Linux."""
    found = shutil.which("adb")
    if found:
        return found

    system = platform.system()
    home = os.path.expanduser("~")
    candidates = []

    if system == "Windows":
        candidates = [
            os.path.expandvars(r"%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe"),
            r"C:\platform-tools\adb.exe",
            r"C:\Program Files\platform-tools\adb.exe",
            r"C:\Program Files\DroidCam\Client\data\obs-plugins\droidcam-obs\adb\adb.exe",
        ]
    elif system == "Darwin":  # macOS
        candidates = [
            "/opt/homebrew/bin/adb",
            "/usr/local/bin/adb",
            os.path.join(home, "Library/Android/sdk/platform-tools/adb"),
            os.path.join(home, "Library/Android/SDK/platform-tools/adb"),
            os.path.join(home, ".android-sdk/platform-tools/adb"),
            "/usr/bin/adb",
        ]
    else:  # Linux / BSD
        candidates = [
            "/usr/bin/adb",
            "/usr/local/bin/adb",
            os.path.join(home, "Android/Sdk/platform-tools/adb"),
            os.path.join(home, ".local/share/android-sdk/platform-tools/adb"),
            os.path.join(home, "android-sdk-linux/platform-tools/adb"),
        ]

    for c in candidates:
        if os.path.isfile(c) and os.access(c, os.X_OK if system != "Windows" else os.F_OK):
            return c
    return ""

def format_adb_device(host: str, scope: int | str | None = None) -> str:
    """Formats the host and scope into an ADB target string."""
    h = host.strip().strip("[]")
    if ":" in h:  # IPv6
        clean_ip = h.split("%")[0]
        s = scope or (h.split("%")[1] if "%" in h else None)
        return f"[{clean_ip}%{s}]:5555" if s else f"[{clean_ip}]:5555"
    else:  # IPv4
        return f"{h}:5555"

def test_tcp_port6(ip: str, port: int, scope: int | str | None, timeout: float = 0.8) -> bool:
    """Tests if an IPv6 TCP port is open, resolving interface names to scope IDs."""
    try:
        s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        s.settimeout(timeout)
        scope_id = 0
        clean_ip = ip.split("%")[0].strip("[]")
        raw_scope = scope or (ip.split("%")[1] if "%" in ip else None)

        if raw_scope is not None:
            if isinstance(raw_scope, int):
                scope_id = raw_scope
            elif str(raw_scope).isdigit():
                scope_id = int(raw_scope)
            elif hasattr(socket, "if_nametoindex"):
                try:
                    scope_id = socket.if_nametoindex(str(raw_scope))
                except Exception:
                    scope_id = 0

        s.connect((clean_ip, port, 0, scope_id))
        s.close()
        return True
    except Exception:
        return False

def get_active_interfaces() -> list[tuple[str, int | str]]:
    """Retrieves active network interfaces per OS: returns (label, identifier)."""
    system = platform.system()
    interfaces: list[tuple[str, int | str]] = []

    if system == "Windows":
        ps_cmd = 'Get-NetAdapter | Where-Object { $_.Status -eq "Up" } | Select-Object -ExpandProperty InterfaceIndex'
        try:
            proc = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True)
            for x in proc.stdout.splitlines():
                line = x.strip()
                if line.isdigit():
                    idx = int(line)
                    interfaces.append((f"Interface {idx}", idx))
        except Exception:
            pass

    elif system == "Darwin":  # macOS
        try:
            for idx, name in socket.if_nameindex():
                # Filter out loopback, tunnels, and inactive Apple internal interfaces
                if name.startswith(("lo", "gif", "stf", "utun", "nan")):
                    continue
                interfaces.append((name, name))
        except Exception:
            pass
        if not interfaces:
            try:
                out = subprocess.check_output(["ifconfig", "-l"], text=True)
                for iface in out.split():
                    if not iface.startswith(("lo", "gif", "stf", "utun")):
                        interfaces.append((iface, iface))
            except Exception:
                pass

    else:  # Linux
        try:
            for idx, name in socket.if_nameindex():
                if name.startswith(("lo", "docker", "veth", "br-")):
                    continue
                interfaces.append((name, name))
        except Exception:
            pass
        if not interfaces:
            try:
                out = subprocess.check_output(["ip", "-o", "link"], text=True)
                for line in out.splitlines():
                    parts = line.split(":")
                    if len(parts) >= 2:
                        name = parts[1].strip()
                        if not name.startswith(("lo", "docker")):
                            interfaces.append((name, name))
            except Exception:
                pass

    return interfaces

def ping_multicast(interfaces: list[tuple[str, int | str]]):
    """Pings local IPv6 multicast address (ff02::1) across interfaces."""
    system = platform.system()
    for _, iface in interfaces:
        try:
            if system == "Windows":
                subprocess.run(f"ping -6 -n 1 -w 300 ff02::1%{iface}", shell=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif system == "Darwin":
                # macOS ping6 syntax
                subprocess.run(["ping6", "-c", "1", "-t", "1", "-I", str(iface), "ff02::1"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                # Linux ping syntax
                subprocess.run(["ping", "-6", "-c", "1", "-w", "1", "-I", str(iface), "ff02::1"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
    time.sleep(0.5)

def get_neighbor_candidates() -> list[tuple[str, int | str]]:
    """Parses local IPv6 neighbor tables across Windows, macOS, and Linux."""
    system = platform.system()
    candidates: list[tuple[str, int | str]] = []

    if system == "Windows":
        try:
            out = subprocess.check_output("netsh interface ipv6 show neighbors", text=True, stderr=subprocess.DEVNULL)
        except Exception:
            out = ""

        current_idx = None
        for line in out.splitlines():
            m_if = re.match(r"Interface\s+(\d+):", line)
            if m_if:
                current_idx = int(m_if.group(1))
            elif current_idx and line.strip().startswith("fe80:"):
                parts = line.split()
                if len(parts) >= 3 and parts[2].lower() != "unreachable":
                    candidates.append((parts[0], current_idx))

    elif system == "Darwin":  # macOS ndp table
        try:
            out = subprocess.check_output(["ndp", "-an"], text=True, stderr=subprocess.DEVNULL)
        except Exception:
            out = ""

        for line in out.splitlines():
            parts = line.split()
            if len(parts) >= 3 and parts[0].lower().startswith("fe80:"):
                if parts[1] != "(incomplete)":
                    raw_ip = parts[0].split("%")[0]
                    scope = parts[2]
                    candidates.append((raw_ip, scope))

    else:  # Linux ip neighbor table
        try:
            out = subprocess.check_output(["ip", "-6", "neigh", "show"], text=True, stderr=subprocess.DEVNULL)
        except Exception:
            out = ""

        for line in out.splitlines():
            parts = line.split()
            if len(parts) >= 4 and parts[0].lower().startswith("fe80:"):
                if "FAILED" not in line and "INCOMPLETE" not in line:
                    raw_ip = parts[0].split("%")[0]
                    if "dev" in parts:
                        dev_idx = parts.index("dev")
                        if dev_idx + 1 < len(parts):
                            scope = parts[dev_idx + 1]
                            candidates.append((raw_ip, scope))

    return candidates

def scan_for_scooter() -> tuple[str, int | str] | None:
    """Pings multicast and scans IPv6 neighbors for open port 50005 across OSes."""
    print("[*] Detecting active network adapters...")
    interfaces = get_active_interfaces()
    if interfaces:
        print(f"    Found {len(interfaces)} interface(s): {', '.join([str(i[1]) for i in interfaces])}")
    else:
        print("    Scanning default interfaces...")

    print("[*] Pinging local IPv6 multicast to discover network devices...")
    ping_multicast(interfaces)

    print("[*] Scanning IPv6 neighbor table for Ola Head Unit (Port 50005)...")
    candidates = get_neighbor_candidates()
    # Deduplicate candidates
    seen = set()
    deduped = []
    for ip, scope in candidates:
        key = (ip, str(scope))
        if key not in seen:
            seen.add(key)
            deduped.append((ip, scope))

    for ip, scope in deduped:
        print(f"    Checking {ip}%{scope} ...", end="", flush=True)
        if test_tcp_port6(ip, 50005, scope):
            print(" [OPEN] -> Found Ola Scooter!")
            return ip, scope
        else:
            print(" [closed]")

    return None

def pre_setup_wake(channel):
    """Wakes screen safely without modifying persistent sleep/power states."""
    print("[*] Waking display...")
    ola.run(channel, "input keyevent 224", quiet=True)
    try:
        _, model = ola.run(channel, "getprop ro.product.model", timeout=10, quiet=True)
        _, build = ola.run(channel, "getprop ro.build.display.id", timeout=10, quiet=True)
        print(f"    Vehicle Info: {model.strip() or 'Ola Scooter'} (Build: {build.strip() or 'MoveOS'})")
    except Exception:
        pass
    print("    >> PRE-CHECK: Ensure scooter side stand is UP and screen stays awake during mods.")
    time.sleep(0.5)

def unlock_adb(channel, host: str, scope: int | str | None, adb_exe: str) -> str:
    """Safely unlocks ADB via RAM bind mount without flashing partitions."""
    print("[*] Preparing ADB key...")
    adb_key_dir = os.path.expanduser("~/.android")
    adb_pub = os.path.join(adb_key_dir, "adbkey.pub")
    if not os.path.exists(adb_pub):
        print("    Generating fresh ADB keypair on host...")
        os.makedirs(adb_key_dir, exist_ok=True)
        subprocess.run([adb_exe, "keygen", os.path.join(adb_key_dir, "adbkey")], check=True, stdout=subprocess.DEVNULL)

    print("    Uploading host public key to scooter...")
    ola.push(channel, adb_pub, "/data/local/tmp/adb_keys_mine")
    ola.run(channel, "chmod 644 /data/local/tmp/adb_keys_mine", quiet=True)

    print("    Setting scootermode=serv...")
    ola.run(channel, "setprop persist.ola.security.scootermode serv", quiet=True)

    bind_script = """#!/system/bin/sh
if [ -f /data/misc/adb/adbkeymoveos3_pub_prod ]; then
    T=/data/misc/adb/adbkeymoveos3_pub_prod
elif [ -f /data/misc/adb/adb_keys ]; then
    T=/data/misc/adb/adb_keys
else
    T=/adbkeymoveos3_pub_prod
fi
mount | grep -q " $T " && umount "$T"
mount --bind /data/local/tmp/adb_keys_mine "$T" || exit 1
echo "bound $T"
"""
    tmp_path = os.path.join(tempfile.gettempdir(), "ola_bind_key.sh")
    with open(tmp_path, "wb") as f:
        f.write(bind_script.replace("\r\n", "\n").encode("ascii"))

    ola.push(channel, tmp_path, "/data/local/tmp/bind_key.sh")
    ola.run(channel, "chmod 755 /data/local/tmp/bind_key.sh", quiet=True)
    ola.run(channel, "sh /data/local/tmp/bind_key.sh", quiet=True)
    time.sleep(1.0)

    device = format_adb_device(host, scope)
    print(f"[*] Connecting ADB to {device}...")
    subprocess.run([adb_exe, "connect", device], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.0)

    # Verify state
    res = subprocess.run([adb_exe, "-s", device, "get-state"], capture_output=True, text=True)
    if "device" not in res.stdout:
        subprocess.run([adb_exe, "connect", device], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1.0)
    print("    [+] ADB connected successfully as 'device'!")
    return device

def find_apk(filename: str, repo_dir: str, custom_dir: str | None = None) -> str:
    """Finds an APK file looking in custom dir, repo apks/, and android assets/."""
    candidates = []
    if custom_dir:
        candidates.append(os.path.join(custom_dir, filename))
    candidates.extend([
        os.path.join(repo_dir, "apks", filename),
        os.path.join(repo_dir, "android", "app", "src", "main", "assets", filename),
    ])
    for c in candidates:
        if os.path.isfile(c):
            return c
    return ""

def install_and_grant(device: str, adb_exe: str, apks: dict[str, str]):
    """Installs bundled APKs and grants necessary Android permissions."""
    def safe_install(apk_path: str, app_name: str):
        print(f"[*] Installing {app_name} ({os.path.basename(apk_path)})...")
        res = subprocess.run([adb_exe, "-s", device, "install", "-r", "-d", apk_path], capture_output=True, text=True)
        combined = (res.stdout + " " + res.stderr).strip()
        if "Success" in combined:
            print(f"    [+] {app_name} installed successfully.")
        elif "ALREADY_EXISTS" in combined or "signatures do not match" in combined:
            print(f"    [+] {app_name} is already installed / updated.")
        else:
            print(f"    [*] Install status: {combined or 'Done'}")

    for name, path in apks.items():
        if path and os.path.isfile(path):
            safe_install(path, name)

    # Balls Navigation permissions
    pkg_ball = "com.asjohn720.ball"
    svc_ball = f"{pkg_ball}/com.asjohn720.ball.core.QuickBallService"
    if "Balls Navigation" in apks and apks["Balls Navigation"] and os.path.isfile(apks["Balls Navigation"]):
        print("[*] Granting special permissions to Balls Navigation via ADB...")
        subprocess.run([adb_exe, "-s", device, "shell", "appops", "set", pkg_ball, "SYSTEM_ALERT_WINDOW", "allow"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run([adb_exe, "-s", device, "shell", "appops", "set", pkg_ball, "WRITE_SETTINGS", "allow"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run([adb_exe, "-s", device, "shell", "settings", "put", "secure", "enabled_accessibility_services", svc_ball], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run([adb_exe, "-s", device, "shell", "settings", "put", "secure", "accessibility_enabled", "1"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("    [+] Balls: SYSTEM_ALERT_WINDOW, WRITE_SETTINGS & Accessibility granted.")
        subprocess.run([adb_exe, "-s", device, "shell", "am", "start", "-n", f"{pkg_ball}/.ui.MainActivity"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1.0)

    # Android Auto permissions
    pkg_aa = "com.asjohn720.androidauto"
    if "Android Auto" in apks and apks["Android Auto"] and os.path.isfile(apks["Android Auto"]):
        print("[*] Granting permissions to Android Auto (OpenHeadUnit) via ADB...")
        subprocess.run([adb_exe, "-s", device, "shell", "appops", "set", pkg_aa, "SYSTEM_ALERT_WINDOW", "allow"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run([adb_exe, "-s", device, "shell", "appops", "set", pkg_aa, "WRITE_SETTINGS", "allow"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run([adb_exe, "-s", device, "shell", "pm", "grant", pkg_aa, "android.permission.RECORD_AUDIO"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run([adb_exe, "-s", device, "shell", "pm", "grant", pkg_aa, "android.permission.ACCESS_FINE_LOCATION"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run([adb_exe, "-s", device, "shell", "pm", "grant", pkg_aa, "android.permission.ACCESS_COARSE_LOCATION"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run([adb_exe, "-s", device, "shell", "pm", "grant", pkg_aa, "android.permission.READ_EXTERNAL_STORAGE"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run([adb_exe, "-s", device, "shell", "pm", "grant", pkg_aa, "android.permission.WRITE_EXTERNAL_STORAGE"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run([adb_exe, "-s", device, "shell", "appops", "set", pkg_aa, "MANAGE_EXTERNAL_STORAGE", "allow"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run([adb_exe, "-s", device, "shell", "pm", "grant", pkg_aa, "android.permission.NEARBY_WIFI_DEVICES"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run([adb_exe, "-s", device, "shell", "pm", "grant", pkg_aa, "android.permission.BLUETOOTH_CONNECT"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run([adb_exe, "-s", device, "shell", "pm", "grant", pkg_aa, "android.permission.BLUETOOTH_SCAN"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("    [+] Android Auto: Mic, Location, Overlay, Storage & Bluetooth granted.")

    print("[*] Bringing Dashboard Home to front...")
    subprocess.run([adb_exe, "-s", device, "shell", "am", "start", "-n", "com.olaelectric.hmiclient/.MainActivity"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run([adb_exe, "-s", device, "shell", "input", "keyevent", "3"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("    [+] Scooter returned to speedometer dashboard.")

def main():
    print(BANNER)

    parser = argparse.ArgumentParser(description="Ola S1 Quick Mod & Setup Tool (Cross-Platform)")
    parser.add_argument("--ipv6", help="Scooter IPv6/IPv4 address (e.g. fe80::1234:5678:9abc:def0)")
    parser.add_argument("--scope", help="Interface scope ID or name (e.g. 22 or en0)")
    parser.add_argument("--port", type=int, default=50005, help="Ola gRPC port (default 50005)")
    parser.add_argument("--apks-dir", help="Custom directory containing mod APKs")
    parser.add_argument("--unlock-only", action="store_true", help="Authorize ADB only (skip APK installations)")
    args = parser.parse_args()

    # Step 1: Check ADB
    print_step(1, "Verifying Tools & Environment")
    adb_exe = find_adb()
    if not adb_exe:
        print("[!] ERROR: 'adb' was not found on your system.")
        system = platform.system()
        if system == "Darwin":
            print("    Install via Homebrew: brew install --cask android-platform-tools")
        elif system == "Linux":
            print("    Install via package manager: sudo apt install adb  OR  sudo dnf install android-tools")
        else:
            print("    Download from: https://developer.android.com/tools/releases/platform-tools")
        sys.exit(1)
    print(f"[+] ADB found: {adb_exe}")
    print(f"[+] Operating System: {platform.system()} ({platform.release()})")

    # Step 2: Locate Scooter
    print_step(2, "Connecting to Ola Scooter on Wi-Fi")
    ipv6 = args.ipv6
    scope = args.scope

    # Handle user supplying address with embedded scope, e.g. fe80::1%en0
    if ipv6 and "%" in ipv6:
        clean_ip, embedded_scope = ipv6.split("%", 1)
        ipv6 = clean_ip
        if not scope:
            scope = embedded_scope

    if not ipv6:
        while True:
            found = scan_for_scooter()
            if found:
                ipv6, scope = found
                print(f"[+] Discovered scooter at: {ipv6} (Scope {scope})")
                break
            else:
                print("\n[!] Could not automatically detect scooter on Wi-Fi.")
                print("    Please ensure:")
                print("    1. Your PC/Mac and Scooter are connected to the SAME Wi-Fi or Hotspot.")
                print("    2. The scooter screen is AWAKE (press power button or tap display).")
                print("\nOptions:")
                print("  [1] Try scanning again")
                print("  [2] Enter Scooter IPv6 address manually")
                print("  [3] Exit")
                choice = input("\nEnter choice [1-3] (default 1): ").strip()
                if choice == "2":
                    raw_in = input("Enter Scooter IP (e.g. fe80::1234:5678:9abc:def0 or 192.168.43.50): ").strip()
                    if "%" in raw_in:
                        ipv6, scope = raw_in.split("%", 1)
                    else:
                        ipv6 = raw_in
                        scope_str = input("Enter Interface Scope (e.g. 22, en0, or leave empty): ").strip()
                        scope = scope_str if scope_str else None
                    break
                elif choice == "3":
                    sys.exit(0)

    target = ola.build_target(ipv6, args.port, scope)
    print(f"[*] Connecting to Ola daemon at {target} ...")
    try:
        channel = ola.connect(target, wait=6.0)
    except Exception as e:
        print(f"[!] Failed to connect to scooter at {target}: {e}")
        print("    Ensure scooter is awake and Wi-Fi is active.")
        sys.exit(1)

    # Step 3: Prevent Sleep & Wake Screen
    print_step(3, "Waking Screen & Pre-Flight Check")
    pre_setup_wake(channel)

    # Step 4: Unlock ADB
    print_step(4, "Unlocking ADB Access")
    device = unlock_adb(channel, ipv6, scope, adb_exe)

    if args.unlock_only:
        print("\n[+] --unlock-only specified: ADB is unlocked and connected.")
        print(f"    You can now use: adb -s {device} shell")
        sys.exit(0)

    # Step 5: Verify Bundled APKs
    print_step(5, "Verifying Bundled Mod APK Packages")
    repo_dir = os.path.dirname(os.path.abspath(__file__))

    balls_apk = find_apk("balls-1.1.0-lite-release.apk", repo_dir, args.apks_dir)
    music_apk = find_apk("musicmod-release.apk", repo_dir, args.apks_dir)
    aa_apk = find_apk("com.asjohn720.androidauto.apk", repo_dir, args.apks_dir)

    if not balls_apk:
        print("[!] Error: Mandatory Balls Navigation APK missing!")
        print("    Searched in:")
        print(f"      - {os.path.join(repo_dir, 'apks')}")
        print(f"      - {os.path.join(repo_dir, 'android', 'app', 'src', 'main', 'assets')}")
        sys.exit(1)

    apks_to_install = {
        "Balls Navigation": balls_apk,
        "Music Mod": music_apk,
        "Android Auto": aa_apk
    }

    for name, path in apks_to_install.items():
        if path and os.path.isfile(path):
            print(f"    [+] Found: {name} -> {os.path.basename(path)} ({os.path.getsize(path)/1024/1024:.2f} MB)")
        else:
            print(f"    [-] Optional APK not found: {name} (skipping)")

    # Step 6: Install & Configure
    print_step(6, "Installing Modded Apps & Granting Permissions")
    install_and_grant(device, adb_exe, apks_to_install)

    # Completion Banner & User Guide
    print("\n" + "=" * 72)
    print("         CONGRATULATIONS! ALL MODS INSTALLED SUCCESSFULLY!       ")
    print("=" * 72)
    print("\n[+] Scooter display is now back on your Speedometer Dashboard.")
    print("[+] Balls navigation overlay is active and ready to use!")
    print("\n>>> HOW TO USE YOUR NEW MODS:")
    print("  Tap the floating ball on your screen anytime to access:")
    print("    * Back          -> Instant Back button inside any app")
    print("    * Home          -> Instant return to Speedometer Dashboard")
    print("    * Settings      -> Direct access to Android Settings (Wi-Fi, Bluetooth, etc.)")
    print("    * Music Mod     -> Ad-free streaming & offline music playback")
    print("    * Android Auto  -> OpenHeadUnit projection")
    print("    * Via Browser   -> Lightweight web browsing")
    print("\nNo manual configuration required - everything is ready to enjoy!")
    print("=" * 72)

if __name__ == "__main__":
    main()
