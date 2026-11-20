#!/usr/bin/env python3
"""Self-checks for ola.py and setup.py cross-platform helpers.

Run (from the repo root):  python3 test_ola.py
These tests verify hand-rolled protobuf, address decoding/escaping,
cross-platform scope handling, ADB device string formatting, and APK resolution.
"""
import os
import ola
import setup

def _resp(status: int, message: str) -> bytes:
    """Build a wire response the way the daemon does: field1=status, field2=msg."""
    raw = message.encode()
    return (ola._vi((1 << 3) | 0) + ola._vi(status)
            + ola._vi((2 << 3) | 2) + ola._vi(len(raw)) + raw)


def test_varint_roundtrip():
    for n in (0, 1, 127, 128, 300, 16384, 1 << 31):
        value, nxt = ola._read_varint(ola._vi(n), 0)
        assert value == n, f"varint {n} -> {value}"
        assert nxt == len(ola._vi(n))


def test_varint_truncated_does_not_crash():
    # high bit set means "more bytes follow", but there are none
    value, nxt = ola._read_varint(b"\x80", 0)
    assert nxt == 1  # returned instead of IndexError


def test_decode_response_roundtrip():
    for status, msg in ((0, ""), (1, "ok"), (255, "line1\nline2"), (1, "spaced path /a b")):
        got_status, got_msg = ola._decode_response(_resp(status, msg))
        assert got_status == status, f"{status} -> {got_status}"
        assert got_msg == msg, f"{msg!r} -> {got_msg!r}"


def test_build_target():
    assert ola.build_target("192.168.43.50", 50005, None) == "192.168.43.50:50005"
    assert ola.build_target("2001:db8::1", 50005, None) == "ipv6:[2001:db8::1]:50005"
    # link-local gets its scope, and % is escaped to %25 for gRPC
    assert ola.build_target("fe80::1", 50005, 6) == "ipv6:[fe80::1%256]:50005"
    # String scopes (macOS/Linux interface names like en0, wlan0)
    assert ola.build_target("fe80::1", 50005, "en0") == "ipv6:[fe80::1%25en0]:50005"
    assert ola.build_target("fe80::1%wlan0", 50005, None) == "ipv6:[fe80::1%25wlan0]:50005"
    # ipv6: prefix and [brackets] are stripped before rebuilding
    assert ola.build_target("ipv6:[2001:db8::2]:50005", 50005, None) == "ipv6:[2001:db8::2]:50005"


def test_build_target_linklocal_needs_scope():
    try:
        ola.build_target("fe80::1", 50005, None)
    except SystemExit:
        return
    raise AssertionError("link-local without scope should raise SystemExit")


def test_sh_wrap_is_reversible():
    import base64
    cmd = 'echo "a b" > /sdcard/My File.txt'
    wrapped = ola.sh_wrap(cmd)
    b64 = wrapped.split("echo${IFS}", 1)[1].split("|", 1)[0]
    assert base64.b64decode(b64).decode() == cmd


def test_format_adb_device():
    # Numeric scope
    assert setup.format_adb_device("fe80::1", 6) == "[fe80::1%6]:5555"
    # String scope (macOS/Linux)
    assert setup.format_adb_device("fe80::1", "en0") == "[fe80::1%en0]:5555"
    # Scope already in host, no duplication
    assert setup.format_adb_device("fe80::1%en0", "en0") == "[fe80::1%en0]:5555"
    assert setup.format_adb_device("fe80::1%wlan0", None) == "[fe80::1%wlan0]:5555"
    # IPv4 without brackets
    assert setup.format_adb_device("192.168.43.50", None) == "192.168.43.50:5555"
    # Global IPv6
    assert setup.format_adb_device("2001:db8::1", None) == "[2001:db8::1]:5555"


def test_find_apk_resolution():
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    balls_path = setup.find_apk("balls-1.1.0-lite-release.apk", repo_dir)
    assert balls_path != "", "find_apk should find balls-1.1.0-lite-release.apk"
    assert os.path.isfile(balls_path), f"Resolved APK path must exist: {balls_path}"

    music_path = setup.find_apk("musicmod-release.apk", repo_dir)
    assert music_path != "", "find_apk should find musicmod-release.apk"
    assert os.path.isfile(music_path), f"Resolved APK path must exist: {music_path}"


def test_find_adb_exists():
    adb_path = setup.find_adb()
    # If adb is present on host, it should resolve to an existing executable
    if adb_path:
        assert os.path.isfile(adb_path), f"ADB path {adb_path} does not exist"


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"ok  {t.__name__}")
    print(f"\n{len(tests)} checks passed.")
