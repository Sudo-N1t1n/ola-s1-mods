#!/usr/bin/env bash
# ==============================================================================
# S1Mods Quick Setup Tool for macOS and Linux
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================================================"
echo "          Ola S1 Quick Mod & Navigation Installer (macOS & Linux)       "
echo "========================================================================"
echo ""

OS_TYPE="$(uname -s)"

# 1. Check Python 3
PYTHON_BIN=""
if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    VER=$(python --version 2>&1 | awk '{print $2}')
    if [[ "$VER" =~ ^3\. ]]; then
        PYTHON_BIN="python"
    fi
fi

if [ -z "$PYTHON_BIN" ]; then
    echo "[ERROR] Python 3 was not found on your system!"
    if [ "$OS_TYPE" = "Darwin" ]; then
        echo "  Install via Homebrew:  brew install python3"
        echo "  Or download from:      https://www.python.org/downloads/"
    else
        echo "  On Debian/Ubuntu:      sudo apt update && sudo apt install -y python3 python3-pip python3-venv"
        echo "  On Fedora/RHEL:        sudo dnf install -y python3 python3-pip"
        echo "  On Arch Linux:         sudo pacman -S python python-pip"
    fi
    echo ""
    exit 1
fi
echo "[+] Using Python: $($PYTHON_BIN --version) ($PYTHON_BIN)"

# 2. Check ADB
ADB_BIN=""
if command -v adb >/dev/null 2>&1; then
    ADB_BIN="$(command -v adb)"
else
    # Common fallback paths
    CANDIDATES=(
        "/opt/homebrew/bin/adb"
        "/usr/local/bin/adb"
        "$HOME/Library/Android/sdk/platform-tools/adb"
        "$HOME/Library/Android/SDK/platform-tools/adb"
        "$HOME/Android/Sdk/platform-tools/adb"
        "$HOME/.local/share/android-sdk/platform-tools/adb"
        "/usr/bin/adb"
    )
    for c in "${CANDIDATES[@]}"; do
        if [ -x "$c" ]; then
            ADB_BIN="$c"
            export PATH="$(dirname "$c"):$PATH"
            break
        fi
    done
fi

if [ -z "$ADB_BIN" ]; then
    echo "[!] 'adb' command was not found in your PATH."
    if [ "$OS_TYPE" = "Darwin" ]; then
        echo "  To install on macOS:   brew install --cask android-platform-tools"
    else
        echo "  To install on Ubuntu:  sudo apt update && sudo apt install -y adb"
        echo "  To install on Fedora:  sudo dnf install -y android-tools"
        echo "  To install on Arch:    sudo pacman -S android-tools"
    fi
    echo "  Or download from:      https://developer.android.com/tools/releases/platform-tools"
    echo ""
    read -p "Continue anyway if you plan to provide manual ADB or if ADB is elsewhere? (y/N): " choice
    if [[ ! "$choice" =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "[+] Using ADB: $ADB_BIN"
fi

# 3. Environment & Dependencies (handle PEP 668 safely)
echo "[*] Checking Python dependencies..."
NEED_VENV=0

# Test if grpcio is already installed
if ! "$PYTHON_BIN" -c "import grpc" >/dev/null 2>&1; then
    # Try importing or installing
    if [ -z "$VIRTUAL_ENV" ]; then
        # We are not in an active virtualenv. Test pip install dry-run
        if "$PYTHON_BIN" -m pip install --dry-run grpcio >/dev/null 2>&1; then
            "$PYTHON_BIN" -m pip install -q -r requirements.txt || NEED_VENV=1
        else
            NEED_VENV=1
        fi
    else
        "$PYTHON_BIN" -m pip install -q -r requirements.txt
    fi
fi

if [ "$NEED_VENV" -eq 1 ] && ! "$PYTHON_BIN" -c "import grpc" >/dev/null 2>&1; then
    echo "[*] Creating virtual environment (.venv) for dependencies..."
    if [ ! -d ".venv" ]; then
        "$PYTHON_BIN" -m venv .venv || {
            echo "[ERROR] Could not create virtual environment. Please install python3-venv:"
            echo "  sudo apt install python3-venv  (on Ubuntu/Debian)"
            exit 1
        }
    fi
    source .venv/bin/activate
    PYTHON_BIN="python3"
    echo "[*] Installing requirements in virtualenv..."
    "$PYTHON_BIN" -m pip install -q -r requirements.txt
fi

# 4. Launch Setup Engine
echo "[*] Starting Ola S1 setup engine..."
echo ""
exec "$PYTHON_BIN" -u setup.py "$@"

