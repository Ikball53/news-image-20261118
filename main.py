#!/usr/bin/env python3
"""The World in One Picture -- Wednesday 18 November 2026.

A pure-standard-library front-page renderer. It composites pre-rendered
RGBA PNG assets (text lines, icons, number badges, dotted world map) onto
a cream newspaper page and writes entry.png to the output directory named
by MAKEFUN_OUTPUT_DIR (default /output/entry.png, the path the contest
reads), plus a copy next to this file when that directory is writable.

No network, no clock, no randomness: the same assets always produce the
same bytes, so the output is deterministic.
"""
import os
import struct
import zlib

# ------------------------------------------------------------------ palette
CREAM = (244, 240, 228)
PAGE_LINE = (222, 216, 198)
INK = (25, 25, 25)
NAVY = (24, 37, 46)
RED = (168, 52, 44)
GRAY = (107, 102, 88)
CARD_LINE = (226, 220, 204)
WHITE = (255, 255, 255)

PAGE_W, PAGE_H = 850, 1024
MARGIN = 26
CONTENT_RIGHT = 824  # MARGIN + 798

# ------------------------------------------------------------------ png io
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def _paeth(a, b, c):
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def read_png(path):
    """Decode an 8-bit non-interlaced RGB/RGBA PNG to (w, h, rgba bytes)."""
    with open(path, "rb") as fh:
        raw = fh.read()
    if raw[:8] != PNG_MAGIC:
        raise ValueError("not a PNG: " + path)
    pos, idat = 8, b""
    width = height = depth = ctype = interlace = None
    while pos < len(raw):
        (ln,) = struct.unpack(">I", raw[pos:pos + 4])
        kind = raw[pos + 4:pos + 8]
        data = raw[pos + 8:pos + 8 + ln]
        if kind == b"IHDR":
            (width, height, depth, ctype, _c, _f,
             interlace) = struct.unpack(">IIBBBBB", data)
        elif kind == b"IDAT":
            idat += data
        elif kind == b"IEND":
            break
        pos += 12 + ln
    if depth != 8 or interlace != 0 or ctype not in (2, 6):
        raise ValueError("unsupported PNG (need 8-bit RGB/RGBA): " + path)
    channels = 4 if ctype == 6 else 3
    stride = width * channels
    blob = zlib.decompress(idat)
    out = bytearray(width * height * 4)
    prev = bytearray(stride)
    p = 0
    for y in range(height):
        f = blob[p]
        p += 1
        line = bytearray(blob[p:p + stride])
        p += stride
        if f == 1:
            for i in range(channels, stride):
                line[i] = (line[i] + line[i - channels]) & 255
        elif f == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 255
        elif f == 3:
            for i in range(stride):
                left = line[i - channels] if i >= channels else 0
                line[i] = (line[i] + ((left + prev[i]) >> 1)) & 255
        elif f == 4:
            for i in range(stride):
                a = line[i - channels] if i >= channels else 0
                b = prev[i]
                c = prev[i - channels] if i >= channels else 0
                line[i] = (line[i] + _paeth(a, b, c)) & 255
        for x in range(width):
            o = (y * width + x) * 4
            s = x * channels
            if channels == 4:
                out[o:o + 4] = line[s:s + 4]
            else:
                out[o:o + 3] = line[s:s + 3]
                out[o + 3] = 255
        prev = line
    return width, height, bytes(out)


def _chunk(kind, data):
    block = struct.pack(">I", len(data)) + kind + data
    return block + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def write_png(width, height, rgb):
    """Encode RGB bytes as a PNG, picking the smallest filter per row."""
    stride = width * 3
    raw = bytearray()
    prev = bytes(stride)
    for y in range(height):
        row = rgb[y * stride:(y + 1) * stride]
        variants = []
        variants.append((0, row))
        sub = bytearray(row)
        for i in range(3, stride):
            sub[i] = (row[i] - row[i - 3]) & 255
        variants.append((1, bytes(sub)))
        variants.append((2, bytes((row[i] - prev[i]) & 255
                                 for i in range(stride))))
        avg = bytearray(stride)
        for i in range(stride):
            left = row[i - 3] if i >= 3 else 0
            avg[i] = (row[i] - ((left + prev[i]) >> 1)) & 255
        variants.append((3, bytes(avg)))
        pae = bytearray(stride)
        for i in range(stride):
            a = row[i - 3] if i >= 3 else 0
            b = prev[i]
            c = prev[i - 3] if i >= 3 else 0
            pae[i] = (row[i] - _paeth(a, b, c)) & 255
        variants.append((4, bytes(pae)))

        def _cost(buf):
            return sum(v if v < 128 else 256 - v for v in buf)

        fnum, fdata = min(variants, key=lambda item: _cost(item[1]))
        raw.append(fnum)
        raw += fdata
        prev = row
    png = bytearray(PNG_MAGIC)
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2,
                                       0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    return bytes(png)


# ------------------------------------------------------------------ canvas
class Sheet:
    """An RGB pixel sheet with rectangle and RGBA-blit drawing."""

    def __init__(self, width, height, bg):
        self.w = width
        self.h = height
        self.px = bytearray(bytes(bg) * (width * height))

    def _set(self, x, y, color):
        o = (y * self.w + x) * 3
        self.px[o:o + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            base = (yy * self.w + x) * 3
            self.px[base:base + w * 3] = bytes(color) * w

    def rounded(self, x, y, w, h, r, color):
        """Fill a rounded rectangle: flat bands plus tested corners."""
        self.rect(x, y + r, w, h - 2 * r, color)
        self.rect(x + r, y, w - 2 * r, r, color)
        self.rect(x + r, y + h - r, w - 2 * r, r, color)
        corners = ((x + r, y + r), (x + w - r - 1, y + r),
                   (x + r, y + h - r - 1), (x + w - r - 1, y + h - r - 1))
        for cx, cy in corners:
            for yy in range(cy - r, cy + r + 1):
                for xx in range(cx - r, cx + r + 1):
                    if (xx - cx) ** 2 + (yy - cy) ** 2 > r * r:
                        continue
                    if x <= xx < x + w and y <= yy < y + h:
                        self._set(xx, yy, color)

    def blit(self, img, dx, dy):
        """Source-over composite of an (w, h, rgba) asset onto the sheet."""
        w, h, px = img
        for y in range(h):
            yy = dy + y
            if yy < 0 or yy >= self.h:
                continue
            for x in range(w):
                xx = dx + x
                if xx < 0 or xx >= self.w:
                    continue
                s = (y * w + x) * 4
                a = px[s + 3]
                if a == 0:
                    continue
                o = (yy * self.w + xx) * 3
                if a == 255:
                    self.px[o:o + 3] = px[s:s + 3]
                else:
                    inv = 255 - a
                    self.px[o] = (px[s] * a + self.px[o] * inv) // 255
                    self.px[o + 1] = (px[s + 1] * a +
                                      self.px[o + 1] * inv) // 255
                    self.px[o + 2] = (px[s + 2] * a +
                                      self.px[o + 2] * inv) // 255

    def blit_centred(self, img, cx, y):
        w, h, _px = img
        self.blit(img, cx - w // 2, y)


# ------------------------------------------------------------------ layout
# Region tag asset per story card (cards 2..16 in reading order).
CARD_TAGS = ["asia", "middle_east", "asia", "europe", "united_states",
             "europe", "europe", "sport", "europe", "europe", "climate",
             "sport", "sport", "europe", "europe"]
GRID_X = (26, 295, 564)
GRID_Y = (306, 437, 568, 699, 830)
CARD_W, CARD_H = 259, 122


def build(base):
    """Compose the whole front page; returns raw RGB bytes."""
    sheet = Sheet(PAGE_W, PAGE_H, CREAM)
    sheet.rounded(0, 0, PAGE_W, PAGE_H, 18, PAGE_LINE)
    sheet.rounded(2, 2, PAGE_W - 4, PAGE_H - 4, 16, CREAM)

    def asset(rel):
        return read_png(os.path.join(base, "assets", rel))

    # Masthead: red kicker left, story count right, navy date title.
    sheet.blit(asset("text/kicker.png"), MARGIN, 20)
    meta = asset("text/meta.png")
    sheet.blit(meta, CONTENT_RIGHT - meta[0], 22)
    title = asset("text/title.png")
    if title[0] > CONTENT_RIGHT - MARGIN:
        raise ValueError("title asset too wide: %d" % title[0])
    sheet.blit(title, MARGIN, 44)
    sheet.rect(MARGIN, 100, CONTENT_RIGHT - MARGIN, 4, RED)

    # Lead story #1 on the left, dotted world map on the right.
    sheet.blit(asset("badges/b01.png"), MARGIN, 116)
    sheet.blit(asset("text/tag_asia.png"), 64, 125)
    sheet.blit(asset("text/lead_head.png"), MARGIN, 152)
    sheet.blit(asset("text/lead_sum.png"), MARGIN, 228)
    sheet.blit(asset("map/map.png"), 520, 116)
    sheet.blit(asset("text/where.png"), 606, 272)

    # Numbered cards 2..16 in a 3-column grid, five rows.
    for i, num in enumerate(range(2, 17)):
        x = GRID_X[i % 3]
        y = GRID_Y[i // 3]
        sheet.rounded(x, y, CARD_W, CARD_H, 9, CARD_LINE)
        sheet.rounded(x + 1, y + 1, CARD_W - 2, CARD_H - 2, 8, WHITE)
        sheet.blit(asset("badges/b%02d.png" % num), x + 10, y + 9)
        sheet.blit(asset("text/tag_%s.png" % CARD_TAGS[i]), x + 44, y + 15)
        sheet.blit(asset("icons/ic%02d.png" % num), x + 225, y + 9)
        # A text asset wider or taller than its slot would clip or
        # overlap the card edge, so fail loudly instead of rendering it.
        head = asset("text/c%02d_head.png" % num)
        summ = asset("text/c%02d_sum.png" % num)
        if head[0] > CARD_W - 20 or head[1] > 36:
            raise ValueError("card %d headline asset too big: %dx%d"
                             % (num, head[0], head[1]))
        if summ[0] > CARD_W - 20 or summ[1] > 39:
            raise ValueError("card %d summary asset too big: %dx%d"
                             % (num, summ[0], summ[1]))
        sheet.blit(head, x + 10, y + 40)
        sheet.blit(summ, x + 10, y + 79)

    # Footer: offbeat closer, then the sources line.
    sheet.blit_centred(asset("text/finally.png"), PAGE_W // 2, 964)
    sheet.blit_centred(asset("text/sources.png"), PAGE_W // 2, 990)
    return bytes(sheet.px)


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    data = write_png(PAGE_W, PAGE_H, build(base))
    # The contest reads /output/entry.png (or $MAKEFUN_OUTPUT_DIR when the
    # harness sets it); the repository itself is mounted read-only, so the
    # graded copy must go to the output directory, not beside the script.
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(outdir, exist_ok=True)
    outpath = os.path.join(outdir, "entry.png")
    with open(outpath, "wb") as fh:
        fh.write(data)
    print("wrote", outpath)
    # A plain local run also leaves a copy beside the script for a human
    # to look at; never let that optional copy fail the graded run.
    try:
        with open(os.path.join(base, "entry.png"), "wb") as fh:
            fh.write(data)
    except OSError:
        pass


if __name__ == "__main__":
    main()
