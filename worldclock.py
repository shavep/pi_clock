#!/usr/bin/env python3
import mmap
import colorsys
import signal
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import numpy as np
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1920, 720
FOCUS = ZoneInfo("America/Chicago")
CLOCKS = [
    ("PACIFIC", "LOS ANGELES", ZoneInfo("America/Los_Angeles")),
    ("EASTERN", "NEW YORK", ZoneInfo("America/New_York")),
    ("UK", "LONDON", ZoneInfo("Europe/London")),
    ("SERBIA", "BELGRADE", ZoneInfo("Europe/Belgrade")),
    ("INDIA", "NEW DELHI", ZoneInfo("Asia/Kolkata")),
]

WHITE = (238, 244, 250)
REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else REGULAR, size)


F_ZONE = font(30, True)
F_PACIFIC = font(250, True)
F_DATE = font(42)
F_CITY = font(22, True)
F_TIME = font(59, True)
F_SMALL = font(20)


def centered(draw, xy, text, face, fill):
    box = draw.textbbox((0, 0), text, font=face)
    x = xy[0] - (box[2] - box[0]) / 2
    y = xy[1] - (box[3] - box[1]) / 2 - box[1]
    draw.text((x, y), text, font=face, fill=fill)


def day_marker(local, focus):
    difference = (local.date() - focus.date()).days
    return {0: "TODAY", 1: "+1 DAY", -1: "−1 DAY"}.get(difference, f"{difference:+d} DAYS")


def color(hue, saturation, value):
    return tuple(round(channel * 255) for channel in colorsys.hsv_to_rgb(hue, saturation, value))


def palette(now_utc):
    # One complete, gentle hue cycle every six hours. The background follows
    # the accent at very low brightness so the display stays calm and legible.
    minutes = now_utc.timestamp() / 60
    hue = (minutes % 360) / 360
    return {
        "bg": color(hue, 0.44, 0.075),
        "panel": color(hue, 0.34, 0.145),
        "line": color(hue, 0.28, 0.30),
        "muted": color(hue, 0.22, 0.72),
        "accent": color(hue, 0.72, 1.0),
    }


def render(now_utc):
    colors = palette(now_utc)
    image = Image.new("RGB", (WIDTH, HEIGHT), colors["bg"])
    draw = ImageDraw.Draw(image)
    focus = now_utc.astimezone(FOCUS)
    hero_h = 450

    draw.rectangle((0, 0, WIDTH, hero_h), fill=colors["panel"])
    draw.rectangle((0, 0, WIDTH, 7), fill=colors["accent"])
    centered(draw, (WIDTH // 2, 59), "CENTRAL TIME", F_ZONE, colors["accent"])
    centered(draw, (WIDTH // 2, 238), focus.strftime("%-I:%M %p"), F_PACIFIC, WHITE)
    centered(draw, (WIDTH // 2, 398), focus.strftime("%A, %B %-d, %Y").upper(), F_DATE, colors["muted"])

    card_w = WIDTH / len(CLOCKS)
    for index, (label, city, zone) in enumerate(CLOCKS):
        local = now_utc.astimezone(zone)
        left, right = round(index * card_w), round((index + 1) * card_w)
        if index:
            draw.line((left, hero_h + 24, left, HEIGHT - 24), fill=colors["line"], width=2)
        cx = (left + right) // 2
        centered(draw, (cx, hero_h + 47), label, F_CITY, colors["accent"])
        centered(draw, (cx, hero_h + 121), local.strftime("%-I:%M %p"), F_TIME, WHITE)
        centered(draw, (cx, hero_h + 190), f"{city}  ·  {day_marker(local, focus)}", F_SMALL, colors["muted"])
        centered(draw, (cx, hero_h + 229), local.strftime("%a, %b %-d").upper(), F_SMALL, colors["muted"])
    return image


def rgb565_bytes(image):
    pixels = np.asarray(image, dtype=np.uint16)
    packed = ((pixels[:, :, 0] >> 3) << 11) | ((pixels[:, :, 1] >> 2) << 5) | (pixels[:, :, 2] >> 3)
    return packed.astype("<u2", copy=False).tobytes()


def run():
    running = True

    def stop(*_):
        nonlocal running
        running = False

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    with open("/dev/fb0", "r+b", buffering=0) as framebuffer:
        with mmap.mmap(framebuffer.fileno(), WIDTH * HEIGHT * 2, access=mmap.ACCESS_WRITE) as display:
            last_minute = None
            while running:
                now = datetime.now(ZoneInfo("UTC"))
                minute = (now.year, now.month, now.day, now.hour, now.minute)
                if minute != last_minute:
                    display[:] = rgb565_bytes(render(now))
                    last_minute = minute
                time.sleep(0.05)
    return 0


if __name__ == "__main__":
    sys.exit(run())
