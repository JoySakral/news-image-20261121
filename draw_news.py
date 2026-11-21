#!/usr/bin/env python3
"""Draw the 21 November 2026 world-news front page, 1024x1024 PNG.

Deterministic: fixed date string, no wall-clock time, no randomness,
no network. Run: python3 draw_news.py [output_path]  (default entry.png)
"""
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 234)
INK = (26, 26, 26)
RED = (176, 42, 32)
GREY = (110, 104, 92)
LIGHT = (238, 232, 219)
PANEL = (252, 250, 244)

FONT_DIR = "/usr/share/fonts/truetype/noto/"
SERIF_BLACK = FONT_DIR + "NotoSerif-Black.ttf"
SERIF_BOLD = FONT_DIR + "NotoSerif-Bold.ttf"
SERIF_REG = FONT_DIR + "NotoSerif-Regular.ttf"
SANS_BOLD = FONT_DIR + "NotoSans-Bold.ttf"
SANS_REG = FONT_DIR + "NotoSans-Regular.ttf"
SANS_BLACK = FONT_DIR + "NotoSans-Black.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap by measured pixel width."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, max_w, fill=INK, leading=None):
    lines = wrap(draw, text, fnt, max_w)
    lh = leading or int(fnt.size * 1.28)
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


def kicker(draw, x, y, text, color=RED):
    f = font(SANS_BLACK, 17)
    draw.text((x, y), text, font=f, fill=color)
    return y + 24


def panel(draw, x, y, w, h, kicker_text, headline, body, pictogram=None,
          head_size=25, body_size=18, head_reduce=0):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=6,
                           outline=(200, 192, 176), width=2, fill=PANEL)
    px, py = x + 16, y + 14
    py = kicker(draw, px, py, kicker_text)
    py = draw_wrapped(draw, px, py, headline, font(SERIF_BOLD, head_size),
                      w - 32 - head_reduce, leading=head_size + 5)
    py += 6
    draw_wrapped(draw, px, py, body, font(SANS_REG, body_size),
                 w - 32, leading=body_size + 5)
    if pictogram:
        pictogram(draw, x, y, w, h)


# --- pictograms (simple geometry, drawn inside panel corners) ---
def pic_chart_up(draw, x, y, w, h):
    bx, by = x + w - 88, y + 44
    draw.line([(bx, by + 26), (bx + 20, by + 16), (bx + 38, by + 22),
               (bx + 58, by + 4)], fill=(40, 120, 60), width=4)
    draw.polygon([(bx + 58, by + 4), (bx + 48, by + 4), (bx + 58, by + 14)],
                 fill=(40, 120, 60))
    draw.line([(bx + 58, by + 4), (bx + 70, by + 12)], fill=RED, width=4)


def pic_target(draw, x, y, w, h):
    cx, cy = x + w - 44, y + 62
    for r, col in ((24, (60, 60, 60)), (16, RED), (8, (60, 60, 60))):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=3)
    draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=RED)


def pic_circles(draw, x, y, w, h):
    # Lowered below the kicker line: the long UK-EU kicker ran under the
    # circles at the old cy=y+34. Headline text is wrapped narrow
    # (head_reduce=76) so the right strip stays clear for the pictogram.
    cx, cy = x + w - 52, y + 74
    for dx, col in ((-26, RED), (0, (60, 60, 60)), (26, (150, 120, 40))):
        draw.ellipse([cx + dx - 15, cy - 15, cx + dx + 15, cy + 15],
                     outline=col, width=4)


def pic_placard(draw, x, y, w, h):
    bx, by = x + w - 78, y + 30
    draw.line([(bx + 24, by + 40), (bx + 24, by + 70)], fill=(90, 90, 90),
              width=4)
    draw.rectangle([bx, by, bx + 52, by + 40], fill=(255, 255, 255),
                   outline=(60, 60, 60), width=3)
    draw.line([(bx + 8, by + 12), (bx + 44, by + 12)], fill=RED, width=3)
    draw.line([(bx + 8, by + 22), (bx + 44, by + 22)], fill=(60, 60, 60),
              width=3)
    draw.line([(bx + 8, by + 32), (bx + 32, by + 32)], fill=(60, 60, 60),
              width=3)


def pic_clock(draw, x, y, w, h):
    cx, cy = x + w - 44, y + 62
    draw.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], outline=(60, 60, 60),
                 width=4, fill=(255, 255, 255))
    draw.line([(cx, cy), (cx, cy - 15)], fill=(60, 60, 60), width=3)
    draw.line([(cx, cy), (cx + 12, cy + 6)], fill=RED, width=3)
    draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(60, 60, 60))


def pic_lead_chart(draw, x, y, w, h):
    # Falling market line on a pale blue panel, right side of the lead.
    bx, by = x, y
    draw.rectangle([bx, by, bx + w, by + h], fill=(214, 226, 233))
    draw.rectangle([bx, by + h - 34, bx + w, by + h], fill=(120, 160, 190))
    # grid lines
    for gy in (by + 34, by + 66, by + 98):
        draw.line([(bx + 10, gy), (bx + w - 10, gy)], fill=(180, 198, 208),
                  width=2)
    # falling red line with dots
    pts = [(bx + 14, by + 30), (bx + 62, by + 44), (bx + 110, by + 40),
           (bx + 158, by + 62), (bx + 206, by + 78), (bx + 258, by + 104)]
    draw.line(pts, fill=RED, width=5, joint="curve")
    for px, py in pts:
        draw.ellipse([px - 5, py - 5, px + 5, py + 5], fill=RED)
    draw.text((bx + 10, by + h - 28), "WALL STREET  ·  FRIDAY",
              font=font(SANS_BOLD, 15), fill=(60, 60, 60))


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 36  # margin
    CW = W - 2 * M  # content width

    # Masthead
    d.text((W // 2, 34), "THE WORLD IN ONE IMAGE",
           font=font(SERIF_BLACK, 58), fill=INK, anchor="ma")
    d.line([(M, 112), (W - M, 112)], fill=RED, width=4)
    d.text((W // 2, 124), "S A T U R D A Y   2 1   N O V E M B E R   2 0 2 6",
           font=font(SANS_BOLD, 20), fill=RED, anchor="ma")

    # Lead story
    ly, lh = 162, 244
    d.rounded_rectangle([M, ly, W - M, ly + lh], radius=6,
                        outline=(200, 192, 176), width=2, fill=PANEL)
    lx, lw = M + 18, 600
    py = kicker(d, lx, ly + 14, "LEAD STORY")
    py = draw_wrapped(d, lx, py, "AI SELL-OFF DRAGS MARKETS INTO CORRECTION",
                      font(SERIF_BLACK, 40), lw, leading=46)
    py += 8
    draw_wrapped(d, lx, py,
                 "US stocks fall 3.7% as the AI and chip rout deepens; the "
                 "S&P 500 and the Dow both slide into correction territory.",
                 font(SANS_REG, 19), lw, leading=26)
    pic_lead_chart(d, W - M - 18 - 284, ly + 40, 284, 146)

    # Row 2: two panels
    y2, h2 = 422, 194
    pw2 = (CW - 16) // 2
    panel(d, M, y2, pw2, h2, "ANTHROPIC'S $2 TRILLION DEBUT",
          "Anthropic's $2tn Wall Street debut",
          "Anthropic opens trading on Wall Street as one of the world's "
          "most valuable public companies, days after the biggest IPO on "
          "record.",
          pic_chart_up, head_size=24, body_size=17, head_reduce=76)
    panel(d, M + pw2 + 16, y2, pw2, h2, "TRUMP WEIGHS NEW IRAN STRIKES",
          "Trump weighs new strikes on Iran",
          "President Trump weighs another round of extensive strikes on "
          "Iran as Israel presses for fast, aggressive action, officials "
          "say.",
          pic_target, head_size=24, body_size=17, head_reduce=76)

    # Row 3: three panels
    y3, h3 = 632, 224
    pw3 = (CW - 32) // 3
    panel(d, M, y3, pw3, h3, "UK-EU SIGN POST-BREXIT DEALS",
          "Biggest post-Brexit deal signed",
          "Britain and the EU sign their biggest post-Brexit agreements "
          "in Brussels: food exports, carbon markets and youth mobility.",
          pic_circles, head_size=24, body_size=17, head_reduce=76)
    panel(d, M + pw3 + 16, y3, pw3, h3, "GEN Z PROTESTS SPREAD",
          "Protests in 25 countries",
          "Gen Z protests spread across 25 European countries.",
          pic_placard, head_size=24, body_size=17, head_reduce=76)
    panel(d, M + 2 * (pw3 + 16), y3, pw3, h3, "COP31 RUNS PAST DEADLINE",
          "Climate talks in overtime",
          "Climate talks in Antalya run into overtime as nearly 200 "
          "nations fail to agree on fossil fuels.",
          pic_clock, head_size=24, body_size=17, head_reduce=76)

    # ALSO strip
    ay, ah = 872, 88
    d.rounded_rectangle([M, ay, W - M, ay + ah], radius=6, fill=LIGHT,
                        outline=(200, 192, 176), width=2)
    d.text((M + 16, ay + 12), "ALSO:", font=font(SANS_BLACK, 19), fill=RED)
    draw_wrapped(d, M + 16, ay + 38,
                 "Pancreatic cancer pill makes tumours undetectable in 1 in "
                 "12 patients · FBI criminal database reportedly hacked · "
                 "Denmark ratifies Greenland security deal 109-0",
                 font(SANS_REG, 19), CW - 32, leading=26)

    # Footer
    d.line([(M, 974), (W - M, 974)], fill=(200, 192, 176), width=2)
    d.text((W // 2, 984), "Summarised from multiple news reports · 21 November 2026",
           font=font(SERIF_REG, 17), fill=GREY, anchor="ma")

    img.save(out, "PNG", optimize=True)
    print("wrote", out)


if __name__ == "__main__":
    main()
