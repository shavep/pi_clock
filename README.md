# Pi World Clock

A lightweight, full-screen world clock designed for a Raspberry Pi Zero W and a 1920×720 ultra-wide display. It renders directly to the Linux framebuffer, avoiding a desktop environment or web browser.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi-c51a4a)

## Display

- Large Central Time clock and date
- Pacific, Eastern, UK, Serbia, India, and UTC clocks
- Automatic daylight-saving handling through the system time-zone database
- Local date and relative-day indicator for every secondary location
- Slow six-hour color cycle to reduce static-color image retention
- Once-per-minute rendering to remain lightweight on a Pi Zero W
- Automatic startup through systemd

## Hardware and OS

This version targets:

- Raspberry Pi Zero W
- Raspberry Pi OS / Raspbian
- 1920×720 display
- 16-bit RGB565 framebuffer at `/dev/fb0`

It can be adapted to other resolutions by changing `WIDTH`, `HEIGHT`, and the layout constants in `worldclock.py`.

## Install

Clone the repository on the Pi, then run:

```bash
sudo sh ./install.sh
```

The installer adds the required Debian packages, installs the application under `/opt/pi-world-clock`, creates a systemd service for the invoking user, and starts the display.

Run the installer again after pulling updates. It restarts the clock and checks for immediate startup failures. Console controls are sent to the display terminal while application logs remain in the journal. Between minute updates, the clock sleeps for up to five seconds and recalculates its wait to handle system-clock corrections.

Check its status with:

```bash
systemctl status worldclock.service
```

Follow logs with:

```bash
journalctl -u worldclock.service -f
```

## Controls and customization

The clock is intended to run unattended. Stop or restart it with:

```bash
sudo systemctl stop worldclock.service
sudo systemctl restart worldclock.service
```

Time zones use standard IANA identifiers in `CLOCKS`. Change `FOCUS` to promote a different zone to the large upper clock.

## Uninstall

```bash
sudo sh ./uninstall.sh
```
