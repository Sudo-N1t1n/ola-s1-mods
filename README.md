# 🛵 Ola S1 Mods (MoveOS)

1-click setup utility to enable **Floating Touch Navigation (Back, Home, Settings)** and **Ad-Free Music** on Ola S1 scooters running **MoveOS 4.0.5 and above**.

Works directly from an **Android Phone (No PC required)** or from any **Mac, Linux, or Windows PC**.

> **100% Safe & Reversible:** Zero soldering, zero flash writes, and zero system file tampering. Everything runs via a temporary in-memory RAM mount that cleanly resets whenever the vehicle restarts.

---

## 📱 Supported Scooters

| Vehicle Model | Display | MoveOS Version | Status |
| :--- | :--- | :--- | :--- |
| **Ola S1 Pro (Gen 2)** | 7" Touchscreen | MoveOS ≥ 4.0.5 | ✅ Fully Tested |
| **Ola S1 Pro (Gen 1)** | 7" Touchscreen | MoveOS ≥ 4.0.5 | ✅ Supported |
| **Ola S1 (Gen 1)** | 7" Touchscreen | MoveOS ≥ 4.0.5 | ✅ Supported |
| **Ola S1 Air** | 7" Touchscreen | MoveOS ≥ 4.0.5 | ✅ Supported |
| **Ola S1 X / S1 X+** | Segmented LCD (Non-touch) | Any | ❌ Incompatible (No Android display) |

---

## ⚡ Quick Start

### 🟢 Method 1: Android Phone (Recommended — No PC Needed)

1. Turn on **Personal Hotspot** on your phone.
2. On your scooter display, go to **Settings > Wi-Fi** and connect to your phone's hotspot.
3. Download and install [`S1Mods-v1.2.apk`](S1Mods-v1.2.apk) on your phone.
4. Open the app, tap **Auto Scan** *(allow location when prompted)*.
5. Keep the scooter **side stand UP** and the screen active.
6. Tap **1-CLICK AUTOMATED SETUP** — within seconds, navigation controls and mods are active!

---

### 💻 Method 2: Mac & Linux PC

1. Connect your computer and scooter to the **same Wi-Fi or phone hotspot**.
2. Keep the scooter **side stand UP** and the screen awake.
3. Open your terminal in this repository and run:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
4. The script will automatically check ADB, find your scooter, unlock wireless access, and install all mods.

---

### 🪟 Method 3: Windows PC

1. Connect your PC and scooter to the **same Wi-Fi or phone hotspot**.
2. Keep the scooter **side stand UP** and the screen awake.
3. Double-click **`setup.bat`** (or open Command Prompt and run `setup.bat`).

---

## 🎮 What Mods Are Installed?

* 🔘 **Balls Navigation:** Adds a floating assist ball to your screen. Tap it anytime for:
  * **Back:** Go back within any app.
  * **Home:** Return instantly to the official speedometer dashboard.
  * **Settings:** Quick shortcut to native Android settings (Wi-Fi, Bluetooth, Audio, Display).
* 🎵 **Music Mod:** Lightweight, ad-free music player for streaming and offline tracks.
* 🚗 **Android Auto (OpenHeadUnit):** Projection support for Google Maps and phone media.

---

## 🎨 Dashboard Customization Studio (In Companion App)

Tailor your scooter's 7" MoveOS touchscreen directly from your phone:
* **Display Density (DPI Scaling):** Switch between Compact (175 DPI), Balanced (195 DPI), Stock (213 DPI), and Large (240 DPI).
* **HMI Responsiveness (Animation Speed):** Set animations to `0.5x` or `0.0x` (Instant) to eliminate speedometer animation stutter and make the UI feel fast and responsive.
* **Typography Scaling:** Adjust system text size (`0.85x`, `1.0x`, `1.15x`).
* **Dark Mode Override:** Force dark themes across sideloaded apps.
* **Display Timeout:** Customize sleep timers (1m, 2m, 5m, 10m).
* **HMI Soft-Restart:** Clear frozen speedometer animations with one tap without rebooting the vehicle.

---

## 🛠️ Handy CLI Commands (`ola.py`)

You can run diagnostics and control your scooter display from any Mac, Linux, or Windows terminal:

```bash
# 🔍 Automatically find scooter on your Wi-Fi:
python3 ola.py discover

# ⚡ Fast ADB re-unlock (after vehicle restart, without reinstalling APKs):
./setup.sh --unlock-only

# 📸 Take a screenshot from the scooter dashboard:
python3 ola.py screenshot dash.png --ipv6 <scooter-ip>

# ⚙️ Launch Android Settings directly on the scooter:
python3 ola.py settings --ipv6 <scooter-ip>
python3 ola.py wifi     --ipv6 <scooter-ip>
python3 ola.py bluetooth --ipv6 <scooter-ip>

# 📋 View vehicle specs & build info:
python3 ola.py info --ipv6 <scooter-ip>
```

> **Note on Link-Local IPv6:** If your address starts with `fe80::`, specify your interface name or scope index:
> * macOS: `python3 ola.py info --ipv6 fe80::... --scope en0`
> * Linux: `python3 ola.py info --ipv6 fe80::... --scope wlan0`
> * Windows: `python3 ola.py info --ipv6 fe80::... --scope 22`

---

## ❓ Frequently Asked Questions (FAQ)

<details>
<summary><b>1. Will this void my vehicle warranty or affect riding?</b></summary>
No. S1Mods communicates only with the Android infotainment touchscreen layer (HMI). It has zero access to the motor controller (MCU), battery management (BMS), accelerator, or braking systems.
</details>

<details>
<summary><b>2. What happens when the scooter restarts?</b></summary>
Because the ADB unlock uses an in-memory RAM mount (`mount --bind`), it automatically resets upon vehicle reboot. To re-enable ADB, simply run <code>./setup.sh --unlock-only</code> or tap the setup button in the Android app. Installed apps remain installed in user storage.
</details>

<details>
<summary><b>3. Why can't the tool discover my scooter?</b></summary>
Ensure:
1. Your scooter and computer/phone are on the <b>exact same Wi-Fi or hotspot</b>.
2. Scooter display is <b>awake</b> and the <b>side stand is UP</b>.
3. If auto-scan is blocked by router isolation, check your hotspot's <i>Connected Devices</i> list, copy the scooter's IP or MAC, and enter it manually.
</details>

---

## ⚖️ License & Disclaimer

Released under the [MIT License](LICENSE). Independent, community-driven educational utility. Not affiliated with, authorized, or endorsed by Ola Electric Mobility Ltd. Use at your own discretion.
