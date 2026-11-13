"""Download one of Apple's Product Bezel disk images (developer.apple.com/design/resources) and pull out its PNGs.
Usage: get_bezels.py Bezel-iPhone-Duo /tmp/out   -> /tmp/out/000.png ... (names are not kept; pick by eye).
A small pure-Python UDIF reader (zlib/bz2/lzma blocks), then PNG carving, so no hdiutil or 7z is needed."""
import bz2, lzma, mmap, os, plistlib, re, struct, sys, urllib.request, zlib
from PIL import Image

name, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
dmg, raw = f"{out}/_.dmg", f"{out}/_.raw"
urllib.request.urlretrieve(f"https://devimages-cdn.apple.com/design/resources/download/{name}.dmg", dmg)
with open(dmg, "rb") as f, open(raw, "wb") as r:
    f.seek(-512, 2); koly = f.read(512); assert koly[:4] == b"koly"
    xoff, xlen = struct.unpack(">QQ", koly[216:232])
    f.seek(xoff)
    for blk in plistlib.loads(f.read(xlen))["resource-fork"]["blkx"]:
        d = blk["Data"]; first, = struct.unpack(">Q", d[8:16]); n, = struct.unpack(">I", d[200:204])
        for i in range(n):
            kind, _, sec, cnt, off, ln = struct.unpack(">IIQQQQ", d[204 + 40 * i:244 + 40 * i])
            unpack = {1: bytes, 0x80000005: zlib.decompress, 0x80000006: bz2.decompress, 0x80000008: lzma.decompress}.get(kind)
            if unpack:
                f.seek(off); r.seek((first + sec) * 512); r.write(unpack(f.read(ln)))
os.remove(dmg)
with open(raw, "rb") as f:
    data = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ); k = 0
    for m in re.finditer(b"\x89PNG\r\n\x1a\n", data):
        end = data.find(b"IEND\xaeB`\x82", m.start())
        if end < 0 or end - m.start() > 80_000_000: continue
        p = f"{out}/{k:03d}.png"
        with open(p, "wb") as o: o.write(data[m.start():end + 8])
        try: im = Image.open(p); im.load(); print(p, im.size); k += 1
        except Exception: os.remove(p)
os.remove(raw)
