#!/usr/bin/env python3
"""Generate a PNG app icon (no third-party deps) for Add-to-Home-Screen.

Draws a simple ascending bar chart + uptrend line on a dark background.
Outputs icon-512.png. Run once; the icon is static (not part of publish.sh).
"""
import struct
import zlib

W = H = 512
BG = (11, 13, 18)        # #0B0D12
PANEL = (20, 24, 33)     # #141821
AMBER = (247, 161, 59)   # #F7A13B
BLUE = (93, 176, 255)    # #5DB0FF

# RGB framebuffer
buf = bytearray()
for _ in range(W * H):
    buf += bytes(BG)


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i:i + 3] = bytes(c)


def rect(x0, y0, x1, y1, c):
    for y in range(int(y0), int(y1)):
        for x in range(int(x0), int(x1)):
            px(x, y, c)


def rrect(x0, y0, x1, y1, r, c):
    """filled rounded rectangle"""
    for y in range(int(y0), int(y1)):
        for x in range(int(x0), int(x1)):
            dx = min(x - x0, x1 - 1 - x)
            dy = min(y - y0, y1 - 1 - y)
            if dx < r and dy < r:
                if (r - dx) ** 2 + (r - dy) ** 2 > r * r:
                    continue
            px(x, y, c)


def disc(cx, cy, rad, c):
    for y in range(int(cy - rad), int(cy + rad + 1)):
        for x in range(int(cx - rad), int(cx + rad + 1)):
            if (x - cx) ** 2 + (y - cy) ** 2 <= rad * rad:
                px(x, y, c)


def line(x0, y0, x1, y1, c, width=10):
    steps = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
    for s in range(steps + 1):
        t = s / steps
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0) * t
        disc(x, y, width / 2, c)


# Rounded dark panel inset
rrect(40, 40, 472, 472, 84, PANEL)

# Ascending bars
bar_w = 56
base = 392
xs = [108, 196, 284, 372]
heights = [110, 168, 150, 232]
for x, h in zip(xs, heights):
    rrect(x, base - h, x + bar_w, base, 16, (38, 45, 58))

# Uptrend line across the bar tops
pts = [(136, 300), (224, 250), (312, 268), (400, 176)]
for (ax, ay), (bx, by) in zip(pts, pts[1:]):
    line(ax, ay, bx, by, BLUE, width=14)
for cx, cy in pts:
    disc(cx, cy, 13, AMBER)


def write_png(path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter type 0
        raw += buf[y * W * 3:(y + 1) * W * 3]

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(png)
    print(f"wrote {path} ({len(png)} bytes)")


if __name__ == "__main__":
    write_png("icon-512.png")
