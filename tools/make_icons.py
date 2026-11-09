"""Make the home-screen icons for the AB Dashboard. Run from the repo root."""
from PIL import Image, ImageDraw, ImageFont

NAVY = (27, 35, 51)
BRASS = (214, 166, 74)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def icon(size, path, pad=0.0):
    img = Image.new("RGB", (size, size), NAVY)
    d = ImageDraw.Draw(img)
    inner = size * (1 - 2 * pad)
    # thin brass ring
    m = size * pad + inner * 0.08
    d.rounded_rectangle([m, m, size - m, size - m], radius=inner * 0.16, outline=BRASS, width=max(2, int(size * 0.025)))
    f = ImageFont.truetype(FONT, int(inner * 0.40))
    t = "AB"
    b = d.textbbox((0, 0), t, font=f)
    w, h = b[2] - b[0], b[3] - b[1]
    d.text(((size - w) / 2 - b[0], (size - h) / 2 - b[1]), t, font=f, fill=BRASS)
    img.save(path)


icon(192, "icon-192.png")
icon(512, "icon-512.png")
icon(512, "icon-maskable-512.png", pad=0.1)
icon(180, "apple-touch-icon.png")
print("icons written")
