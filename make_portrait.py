"""Turn a photo into an ASCII portrait (portrait.txt) for the banner.

usage: python make_portrait.py [photo] [--preview]
"""
import sys
from PIL import Image, ImageOps, ImageFilter, ImageChops, ImageDraw, ImageFont

args = [a for a in sys.argv[1:] if not a.startswith("--")]
SRC = args[0] if args else "portrait-source.jpeg"
OUT = "portrait.txt"
COLS, ROWS = 76, 44
CROP = (160, 20, 400, 340)  # left, top, right, bottom: the face
RAMP = " .:-=+*#%@"

img = Image.open(SRC).convert("L").crop(CROP)
img = ImageOps.autocontrast(img, cutoff=1)
# tone: photo luminance blended with local contrast so eyes, brows, beard and
# hair separate from skin; a soft vignette fades the background to nothing
wide = img.filter(ImageFilter.GaussianBlur(14))
local = ImageChops.subtract(ImageChops.add(img, Image.new("L", img.size, 128)), wide)
base = ImageOps.autocontrast(img.filter(ImageFilter.GaussianBlur(0.8)), cutoff=1)
mix = ImageChops.add(base.point(lambda p: p * 45 // 100), local.point(lambda p: p * 55 // 100))
mix = ImageOps.autocontrast(mix, cutoff=1).point(lambda p: int(255 * (p / 255) ** 1.35))
w, h = mix.size
mask = Image.new("L", (w, h), 0)
ImageDraw.Draw(mask).ellipse((w * 0.02, h * 0.02, w * 1.0, h * 1.02), fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(26))
tone = ImageChops.multiply(mix, mask).resize((COLS, ROWS), Image.LANCZOS)

lines = []
for y in range(ROWS):
    row = "".join(RAMP[min(tone.getpixel((x, y)) * len(RAMP) // 256, len(RAMP) - 1)] for x in range(COLS))
    lines.append(row.rstrip())
open(OUT, "w", encoding="utf-8").write("\n".join(lines))

if "--preview" in sys.argv:
    font = ImageFont.truetype("consola.ttf", 12)
    im = Image.new("RGB", (COLS * 8 + 20, ROWS * 12 + 20), "#0a0f1e")
    d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        d.text((10, 10 + i * 12), l, font=font, fill="#7aa2ff")
    im.save("portrait-preview.png")
print(f"wrote {OUT}: {COLS}x{ROWS}")
