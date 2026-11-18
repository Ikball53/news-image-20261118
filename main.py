#!/usr/bin/env python3
"""The World in One Picture - Wednesday 18 November 2026.

Pure-standard-library front-page generator. Reads pre-rendered text,
icon and flag PNGs plus illustrations from assets/, draws the page from
scratch on an RGB canvas, and writes /output/entry.png.

Deterministic: no network, no clock, no randomness, no dict-order
dependence; all pixel work uses integer / fixed-point math.
"""
import os
import struct
import sys
import zlib
from pathlib import Path

BASE = Path(__file__).resolve().parent
ASSETS = BASE / "assets"
OUT = Path("/output/entry.png")

W = 834
H = 985
M = 20
CW = 794

BG = (246, 241, 231)
WHITE = (255, 255, 255)
BORDER = (227, 220, 203)
NAVY = (27, 42, 74)
RED = (192, 57, 43)
GREY = (110, 106, 96)
TINT = (243, 237, 224)
PINK = (232, 175, 168)

TOP_Y = 119
TOP_H = 259
SECOND_Y = 391
SECOND_H = 249
ALSO_Y = 652
ALSO_H = 290

# (file, x, y) for every pre-rendered text line image.
TEXT = [
    ("assets/text/t001.png", 20, 23),
    ("assets/text/t002.png", 619, 23),
    ("assets/text/t003.png", 20, 46),
    ("assets/text/t004.png", 233, 164),
    ("assets/text/t005.png", 233, 195),
    ("assets/text/t006.png", 233, 231),
    ("assets/text/t007.png", 233, 249),
    ("assets/text/t008.png", 233, 267),
    ("assets/text/t009.png", 264, 134),
    ("assets/text/t010.png", 544, 130),
    ("assets/text/t011.png", 735, 131),
    ("assets/text/t012.png", 31, 527),
    ("assets/text/t013.png", 31, 549),
    ("assets/text/t014.png", 31, 574),
    ("assets/text/t015.png", 31, 590),
    ("assets/text/t016.png", 31, 606),
    ("assets/text/t017.png", 57, 501),
    ("assets/text/t018.png", 300, 527),
    ("assets/text/t019.png", 300, 549),
    ("assets/text/t020.png", 300, 574),
    ("assets/text/t021.png", 300, 590),
    ("assets/text/t022.png", 300, 606),
    ("assets/text/t023.png", 326, 501),
    ("assets/text/t024.png", 569, 527),
    ("assets/text/t025.png", 569, 548),
    ("assets/text/t026.png", 569, 572),
    ("assets/text/t027.png", 569, 588),
    ("assets/text/t028.png", 569, 604),
    ("assets/text/t029.png", 569, 620),
    ("assets/text/t030.png", 595, 501),
    ("assets/text/t031.png", 32, 661),
    ("assets/text/t032.png", 88, 686),
    ("assets/text/t033.png", 349, 686),
    ("assets/text/t034.png", 349, 701),
    ("assets/text/t035.png", 610, 686),
    ("assets/text/t036.png", 88, 748),
    ("assets/text/t037.png", 349, 748),
    ("assets/text/t038.png", 349, 763),
    ("assets/text/t039.png", 610, 748),
    ("assets/text/t040.png", 610, 763),
    ("assets/text/t041.png", 88, 810),
    ("assets/text/t042.png", 88, 823),
    ("assets/text/t043.png", 349, 810),
    ("assets/text/t044.png", 349, 825),
    ("assets/text/t045.png", 610, 810),
    ("assets/text/t046.png", 88, 872),
    ("assets/text/t047.png", 88, 887),
    ("assets/text/t048.png", 349, 872),
    ("assets/text/t049.png", 349, 887),
    ("assets/text/t050.png", 610, 872),
    ("assets/text/t051.png", 610, 887),
    ("assets/text/t052.png", 21, 954),
]

# ALSO items: (icon file, [flag files]) in reading order.
ALSO = [
    ("assets/icons/screen.png", ["assets/flags/uk_30.png"]),
    ("assets/icons/columns.png", ["assets/flags/us_30.png"]),
    ("assets/icons/bars.png", ["assets/flags/uk_30.png"]),
    ("assets/icons/euro.png", ["assets/flags/eu_30.png"]),
    ("assets/icons/soccer.png", ["assets/flags/england_30.png"]),
    ("assets/icons/mic.png", ["assets/flags/uk_30.png"]),
    ("assets/icons/candle.png", ["assets/flags/latvia_30.png"]),
    ("assets/icons/globe.png", ["assets/flags/turkey_30.png"]),
    ("assets/icons/tennis.png", ["assets/flags/spain_14.png", "assets/flags/ru_14.png"]),
    ("assets/icons/trophy.png", ["assets/flags/spain_30.png"]),
    ("assets/icons/church.png", ["assets/flags/ireland_30.png"]),
    ("assets/icons/senate.png", ["assets/flags/fr_30.png"]),
]

# Map: (lon, lat, rx, ry) pink ellipses and (lon, lat) red dots.
# Longitudes/latitudes are stored as milli-degrees (integers).
ELLIPSES = [
    (-100000, 40000, 40, 26),
    (-100, 51500, 9, 6),
    (2350, 48850, 11, 8),
    (32850, 39930, 15, 12),
]
DOTS = [
    (121000, 14600),
    (114100, 22500),
    (50600, 26200),
    (80300, 13500),
    (-100, 51500),
    (-77000, 38900),
    (4350, 50850),
    (-2240, 53480),
    (24100, 56950),
    (32850, 39930),
    (7690, 45070),
    (-5980, 37390),
    (12450, 41900),
    (2350, 48850),
    (-1150, 60150),
]
MAP_BOX = (544, 155, 259, 205)


# ---------------------------------------------------------------- PNG I/O

def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def read_png(path):
    """Return (width, height, RGBA bytearray). Supports 8-bit colour
    types 2 (RGB) and 6 (RGBA), non-interlaced, filters 0-4."""
    raw = open(path, "rb").read()
    if raw[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG: %s" % path)
    pos = 8
    width = height = bitdepth = colortype = None
    idat = bytearray()
    while pos < len(raw):
        size = struct.unpack(">I", raw[pos:pos + 4])[0]
        kind = raw[pos + 4:pos + 8]
        data = raw[pos + 8:pos + 8 + size]
        if kind == b"IHDR":
            width, height, bitdepth, colortype = struct.unpack(">IIBB", data[:10])
            if bitdepth != 8 or colortype not in (2, 6):
                raise ValueError("unsupported PNG %s depth=%d type=%d" % (path, bitdepth, colortype))
        elif kind == b"IDAT":
            idat += data
        elif kind == b"IEND":
            break
        pos += 12 + size
    bpp = 3 if colortype == 2 else 4
    stride = width * bpp
    inflated = zlib.decompress(bytes(idat))
    out = bytearray(width * height * 4)
    prev = bytearray(stride)
    p = 0
    for y in range(height):
        ftype = inflated[p]
        p += 1
        row = inflated[p:p + stride]
        p += stride
        cur = bytearray(stride)
        if ftype == 0:
            cur[:] = row
        elif ftype == 1:
            for i in range(stride):
                a = cur[i - bpp] if i >= bpp else 0
                cur[i] = (row[i] + a) & 0xFF
        elif ftype == 2:
            for i in range(stride):
                cur[i] = (row[i] + prev[i]) & 0xFF
        elif ftype == 3:
            for i in range(stride):
                a = cur[i - bpp] if i >= bpp else 0
                cur[i] = (row[i] + ((a + prev[i]) >> 1)) & 0xFF
        elif ftype == 4:
            for i in range(stride):
                a = cur[i - bpp] if i >= bpp else 0
                b = prev[i]
                c = prev[i - bpp] if i >= bpp else 0
                pa = abs(b - c)
                pb = abs(a - c)
                pc = abs(a + b - 2 * c)
                if pa <= pb and pa <= pc:
                    pred = a
                elif pb <= pc:
                    pred = b
                else:
                    pred = c
                cur[i] = (row[i] + pred) & 0xFF
        else:
            raise ValueError("bad filter %d" % ftype)
        if bpp == 3:
            for x in range(width):
                o = (y * width + x) * 4
                s = x * 3
                out[o] = cur[s]
                out[o + 1] = cur[s + 1]
                out[o + 2] = cur[s + 2]
                out[o + 3] = 255
        else:
            o = y * width * 4
            out[o:o + width * 4] = cur
        prev = cur
    return width, height, out


def _filter_up(row, prev):
    return bytes((a - b) & 0xFF for a, b in zip(row, prev))


def _row_cost(frow):
    total = 0
    for b in frow:
        s = b if b < 128 else b - 256
        total += s if s >= 0 else -s
    return total


def write_png(path, width, height, rgb):
    """Write an RGB bytearray as PNG. Filter 0 per row; if the result
    would exceed 1 MiB, rebuild with a per-row 0/up filter choice."""
    stride = width * 3

    def build(use_up):
        raw = bytearray()
        prev = bytes(stride)
        for y in range(height):
            row = bytes(rgb[y * stride:(y + 1) * stride])
            if use_up:
                up = _filter_up(row, prev)
                if _row_cost(up) < _row_cost(row):
                    raw.append(2)
                    raw += up
                else:
                    raw.append(0)
                    raw += row
            else:
                raw.append(0)
                raw += row
            prev = row
        return raw

    raw = build(False)
    data = zlib.compress(bytes(raw), 9)
    if 8 + 25 + 12 + len(data) + 12 > 1048576:
        raw = build(True)
        data = zlib.compress(bytes(raw), 9)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    blob = b"\x89PNG\r\n\x1a\n"
    blob += _chunk(b"IHDR", ihdr)
    blob += _chunk(b"IDAT", data)
    blob += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(blob)
    return len(blob)


# ---------------------------------------------------------------- canvas

class Canvas:
    def __init__(self, w, h, color):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, color)

    def fill_rect(self, x, y, w, h, color):
        x0 = x if x > 0 else 0
        y0 = y if y > 0 else 0
        x1 = x + w if x + w < self.w else self.w
        y1 = y + h if y + h < self.h else self.h
        if x1 <= x0 or y1 <= y0:
            return
        r, g, b = color
        row = bytes((r, g, b)) * (x1 - x0)
        stride = self.w * 3
        for yy in range(y0, y1):
            o = yy * stride + x0 * 3
            self.px[o:o + (x1 - x0) * 3] = row

    def fill_span(self, x0, x1, y, color):
        if y < 0 or y >= self.h:
            return
        if x0 < 0:
            x0 = 0
        if x1 >= self.w:
            x1 = self.w - 1
        if x1 < x0:
            return
        r, g, b = color
        o = (y * self.w + x0) * 3
        self.px[o:o + (x1 - x0 + 1) * 3] = bytes((r, g, b)) * (x1 - x0 + 1)

    def blend_span(self, x0, x1, y, color, alpha):
        """Blend a horizontal span of `color` at 0-255 alpha."""
        if y < 0 or y >= self.h or alpha <= 0:
            return
        if x0 < 0:
            x0 = 0
        if x1 >= self.w:
            x1 = self.w - 1
        if x1 < x0:
            return
        inv = 255 - alpha
        r, g, b = color
        o = (y * self.w + x0) * 3
        for i in range(x1 - x0 + 1):
            p = o + i * 3
            self.px[p] = (r * alpha + self.px[p] * inv) // 255
            self.px[p + 1] = (g * alpha + self.px[p + 1] * inv) // 255
            self.px[p + 2] = (b * alpha + self.px[p + 2] * inv) // 255

    def fill_rounded_rect(self, x, y, w, h, r, color):
        if r <= 0:
            self.fill_rect(x, y, w, h, color)
            return
        if r * 2 > w:
            r = w // 2
        if r * 2 > h:
            r = h // 2
        self.fill_rect(x + r, y, w - 2 * r, h, color)
        self.fill_rect(x, y + r, r, h - 2 * r, color)
        self.fill_rect(x + w - r, y + r, r, h - 2 * r, color)
        # corner quadrants: integer circle spans
        for k in range(r):
            ddy = r - k
            dx = _isqrt(r * r - ddy * ddy)
            self.fill_span(x + r - dx, x + r - 1, y + k, color)
            self.fill_span(x + w - r, x + w - r + dx - 1, y + k, color)
            self.fill_span(x + r - dx, x + r - 1, y + h - 1 - k, color)
            self.fill_span(x + w - r, x + w - r + dx - 1, y + h - 1 - k, color)

    def card(self, x, y, w, h, r, border_w):
        self.fill_rounded_rect(x, y, w, h, r, BORDER)
        self.fill_rounded_rect(x + border_w, y + border_w, w - 2 * border_w,
                               h - 2 * border_w, r - border_w, WHITE)

    def fill_ellipse(self, cx, cy, rx, ry, color):
        for dy in range(-ry, ry + 1):
            rem = ry * ry - dy * dy
            if rem < 0:
                continue
            dx = _isqrt(rx * rx * rem // (ry * ry))
            self.fill_span(cx - dx, cx + dx, cy + dy, color)

    def blend_ellipse(self, cx, cy, rx, ry, color, alpha):
        for dy in range(-ry, ry + 1):
            rem = ry * ry - dy * dy
            if rem < 0:
                continue
            dx = _isqrt(rx * rx * rem // (ry * ry))
            self.blend_span(cx - dx, cx + dx, cy + dy, color, alpha)


def _isqrt(n):
    """Integer square root (n >= 0)."""
    if n <= 0:
        return 0
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x


# ---------------------------------------------------------------- blitting

def blit_rgba(cv, src, sw, sh, dx, dy):
    """Paste an RGBA image at (dx, dy), alpha-compositing."""
    for sy in range(sh):
        ty = dy + sy
        if ty < 0 or ty >= cv.h:
            continue
        for sx in range(sw):
            tx = dx + sx
            if tx < 0 or tx >= cv.w:
                continue
            so = (sy * sw + sx) * 4
            a = src[so + 3]
            if a == 0:
                continue
            o = (ty * cv.w + tx) * 3
            if a == 255:
                cv.px[o] = src[so]
                cv.px[o + 1] = src[so + 1]
                cv.px[o + 2] = src[so + 2]
            else:
                inv = 255 - a
                cv.px[o] = (src[so] * a + cv.px[o] * inv) // 255
                cv.px[o + 1] = (src[so + 1] * a + cv.px[o + 1] * inv) // 255
                cv.px[o + 2] = (src[so + 2] * a + cv.px[o + 2] * inv) // 255


def _bilinear(src, sw, sh, sx_fp, sy_fp):
    """Fixed-point 16.16 bilinear sample; returns (r, g, b, a)."""
    max_x = (sw - 1) << 16
    max_y = (sh - 1) << 16
    if sx_fp < 0:
        sx_fp = 0
    if sx_fp > max_x:
        sx_fp = max_x
    if sy_fp < 0:
        sy_fp = 0
    if sy_fp > max_y:
        sy_fp = max_y
    x0 = sx_fp >> 16
    y0 = sy_fp >> 16
    fx = sx_fp & 0xFFFF
    fy = sy_fp & 0xFFFF
    x1 = x0 + 1 if x0 + 1 < sw else x0
    y1 = y0 + 1 if y0 + 1 < sh else y0
    w00 = (65536 - fx) * (65536 - fy)
    w10 = fx * (65536 - fy)
    w01 = (65536 - fx) * fy
    w11 = fx * fy
    o00 = (y0 * sw + x0) * 4
    o10 = (y0 * sw + x1) * 4
    o01 = (y1 * sw + x0) * 4
    o11 = (y1 * sw + x1) * 4
    out = []
    for c in range(4):
        v = (src[o00 + c] * w00 + src[o10 + c] * w10 +
             src[o01 + c] * w01 + src[o11 + c] * w11) >> 32
        out.append(v)
    return out[0], out[1], out[2], out[3]


def resize_rgba(src, sw, sh, dw, dh):
    """Stretch-resize an RGBA image to (dw, dh) with fixed-point bilinear."""
    out = bytearray(dw * dh * 4)
    step_x = (sw << 16) // dw
    step_y = (sh << 16) // dh
    for dy in range(dh):
        sy_fp = dy * step_y + step_y // 2
        for dx in range(dw):
            sx_fp = dx * step_x + step_x // 2
            r, g, b, a = _bilinear(src, sw, sh, sx_fp, sy_fp)
            o = (dy * dw + dx) * 4
            out[o] = r
            out[o + 1] = g
            out[o + 2] = b
            out[o + 3] = a
    return dw, dh, out


def blit_cover(cv, src, sw, sh, dx, dy, dw, dh, radius, focus):
    """Cover-crop resample of an RGB image into a rounded-rect box.
    focus is vertical focus in milli-units (0..1000)."""
    step_x = (sw << 16) // dw
    step_y = (sh << 16) // dh
    # Cover: one source pixel per output pixel is the SMALLER step
    # (min of sw/dw and sh/dh); the larger step over-zooms the image.
    step = step_x if step_x < step_y else step_y
    off_x = ((sw << 16) - dw * step) // 2
    off_y = (((sh << 16) - dh * step) * focus) // 1000
    for row in range(dh):
        ty = dy + row
        if ty < 0 or ty >= cv.h:
            continue
        x0 = dx
        x1 = dx + dw - 1
        if radius > 0:
            if row < radius:
                ddy = radius - row
                ddx = _isqrt(radius * radius - ddy * ddy)
                x0 = dx + radius - ddx
                x1 = dx + dw - radius + ddx - 1
            elif row >= dh - radius:
                ddy = radius - (dh - 1 - row)
                ddx = _isqrt(radius * radius - ddy * ddy)
                x0 = dx + radius - ddx
                x1 = dx + dw - radius + ddx - 1
        if x0 < 0:
            x0 = 0
        if x1 >= cv.w:
            x1 = cv.w - 1
        sy_fp = off_y + row * step + step // 2
        for tx in range(x0, x1 + 1):
            sx_fp = off_x + (tx - dx) * step + step // 2
            r, g, b, _a = _bilinear(src, sw, sh, sx_fp, sy_fp)
            o = (ty * cv.w + tx) * 3
            cv.px[o] = r
            cv.px[o + 1] = g
            cv.px[o + 2] = b


def blit_stretch_rgb(cv, src, sw, sh, dx, dy, dw, dh):
    """Stretch an RGB(A) image into a box, ignoring alpha (opaque)."""
    step_x = (sw << 16) // dw
    step_y = (sh << 16) // dh
    for row in range(dh):
        ty = dy + row
        if ty < 0 or ty >= cv.h:
            continue
        sy_fp = row * step_y + step_y // 2
        for col in range(dw):
            tx = dx + col
            if tx < 0 or tx >= cv.w:
                continue
            sx_fp = col * step_x + step_x // 2
            r, g, b, _a = _bilinear(src, sw, sh, sx_fp, sy_fp)
            o = (ty * cv.w + tx) * 3
            cv.px[o] = r
            cv.px[o + 1] = g
            cv.px[o + 2] = b


# ---------------------------------------------------------------- page

def badge(cv, cx, cy, diameter, number):
    r = diameter // 2
    cv.fill_ellipse(cx, cy, r, r, RED)
    size = 12 if diameter > 21 else 11
    _w, h, img = read_png(ASSETS / "text" / ("digit_%d_%s.png" % (size, number)))
    blit_rgba(cv, img, _w, h, cx - _w // 2, cy - h // 2)


def main():
    cv = Canvas(W, H, BG)

    # Header + title + rule.
    for name, x, y in TEXT[:3]:
        w, h, img = read_png(BASE / name)
        blit_rgba(cv, img, w, h, x, y)
    cv.fill_rect(M, 107, CW, 2, NAVY)

    # ---- top row ----
    cv.card(M, TOP_Y, 500, TOP_H, 11, 2)
    cv.card(533, TOP_Y, 281, TOP_H, 11, 2)
    w, h, img = read_png(ASSETS / "ill_trump.png")
    blit_cover(cv, img, w, h, 26, 125, 195, 247, 8, 620)
    badge(cv, 244, 142, 23, "1")
    for name, x, y in TEXT[3:11]:
        tw, th, timg = read_png(BASE / name)
        blit_rgba(cv, timg, tw, th, x, y)

    # ---- map card ----
    mw, mh, mimg = read_png(ASSETS / "map.png")
    mx, my, mbw, mbh = MAP_BOX
    blit_stretch_rgb(cv, mimg, mw, mh, mx, my, mbw, mbh)
    for lon, lat, rx, ry in ELLIPSES:
        px = mx + (lon + 180000) * mbw // 360000
        py = my + (83000 - lat) * mbh // 138000
        cv.blend_ellipse(px, py, rx, ry, PINK, 78)
    for lon, lat in DOTS:
        px = mx + (lon + 180000) * mbw // 360000
        py = my + (83000 - lat) * mbh // 138000
        cv.fill_ellipse(px, py, 7, 7, WHITE)
        cv.fill_ellipse(px, py, 5, 5, RED)

    # ---- second row ----
    banners = [("ill_apec.png", 2), ("ill_radar.png", 3), ("ill_cyclone.png", 4)]
    for i, (fname, num) in enumerate(banners):
        x = M + i * 269
        cv.card(x, SECOND_Y, 256, SECOND_H, 11, 2)
        w, h, img = read_png(ASSETS / fname)
        blit_cover(cv, img, w, h, x + 6, SECOND_Y + 6, 244, 91, 8, 450)
        badge(cv, x + 21, 509, 20, str(num))
    for name, x, y in TEXT[11:30]:
        tw, th, timg = read_png(BASE / name)
        blit_rgba(cv, timg, tw, th, x, y)

    # ---- ALSO section ----
    cv.card(M, ALSO_Y, 794, ALSO_H, 11, 2)
    gy = ALSO_Y + 31
    for i, (icon, flags) in enumerate(ALSO):
        col = i % 3
        row = i // 3
        cx = 32 + col * 261
        cy = gy + row * 62
        cv.fill_rounded_rect(cx, cy, 46, 46, 8, TINT)
        iw, ih, iimg = read_png(BASE / icon)
        _rw, _rh, rimg = resize_rgba(iimg, iw, ih, 31, 31)
        blit_rgba(cv, rimg, 31, 31, cx + 7, cy + 2)
        if len(flags) == 1:
            fw, fh, fimg = read_png(BASE / flags[0])
            _rw, _rh, frimg = resize_rgba(fimg, fw, fh, 23, 9)
            blit_rgba(cv, frimg, 23, 9, cx + 12, cy + 36)
        else:
            for j, flag in enumerate(flags):
                fw, fh, fimg = read_png(BASE / flag)
                _rw, _rh, frimg = resize_rgba(fimg, fw, fh, 11, 9)
                blit_rgba(cv, frimg, 11, 9, cx + 12 + j * 12, cy + 36)
    for name, x, y in TEXT[30:]:
        tw, th, timg = read_png(BASE / name)
        blit_rgba(cv, timg, tw, th, x, y)

    os.makedirs("/output", exist_ok=True)
    n = write_png(str(OUT), W, H, cv.px)
    print("wrote %s %dx%d %d bytes" % (OUT, W, H, n))


if __name__ == "__main__":
    main()
