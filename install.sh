#!/bin/sh
set -eu

if [ "$(id -u)" -ne 0 ]; then
    echo "Run this installer with sudo: sudo ./install.sh" >&2
    exit 1
fi

install_user=${SUDO_USER:-}
if [ -z "$install_user" ] || [ "$install_user" = root ]; then
    echo "Run this installer via sudo from the account that should run the clock." >&2
    exit 1
fi

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

apt-get update
apt-get install -y python3-numpy python3-pil fonts-dejavu-core

install -d -m 0755 /opt/pi-world-clock
install -m 0755 "$script_dir/worldclock.py" /opt/pi-world-clock/worldclock.py
sed "s/__USER__/$install_user/g" "$script_dir/worldclock.service.in" >/etc/systemd/system/worldclock.service

systemctl daemon-reload
systemctl enable worldclock.service
systemctl restart worldclock.service
# Catch immediate failures and restart loops, not just a successful start job.
sleep 10
if ! systemctl is-active --quiet worldclock.service ||
    [ "$(systemctl show --property=NRestarts --value worldclock.service)" != 0 ]; then
    journalctl -u worldclock.service -n 30 --no-pager >&2
    echo "Clock failed its startup check; inspect the journal above." >&2
    exit 1
fi

echo "Pi World Clock installed and started."
