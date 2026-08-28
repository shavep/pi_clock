#!/bin/sh
set -eu

if [ "$(id -u)" -ne 0 ]; then
    echo "Run this uninstaller with sudo: sudo ./uninstall.sh" >&2
    exit 1
fi

systemctl disable --now worldclock.service 2>/dev/null || true
rm -f /etc/systemd/system/worldclock.service
rm -rf /opt/pi-world-clock
systemctl daemon-reload

echo "Pi World Clock removed. Installed Debian packages were left in place."
