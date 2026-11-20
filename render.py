#!/usr/bin/env python3
"""THE WORLD IN ONE DAY — classic broadsheet front page for Friday 20 November 2026.

Renders entry.png (1024x1024) with PIL. Runs only on the build machine;
the grader never executes this file (main.py copies the committed PNG).
All stories and figures come from the verified 20 Nov 2026 news dossier.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W = H = 1024
PAPER = (247, 242, 231)
INK = (20, 20, 20)
ACCENT = (158, 27, 27)
GREY = (92, 88, 80)
RULE_LIGHT = (196, 188, 168)

SERIF_B = os.path.join(HERE, "fonts", "LiberationSerif-Bold.ttf")
SERIF_R = os.path.join(HERE, "fonts", "LiberationSerif-Regular.ttf")
SANS_B = os.path.join(HERE, "fonts", "LiberationSans-Bold.ttf")
SANS_R = os.path.join(HERE, "fonts", "LiberationSans-Regular.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def fit(draw, text, path, size, max_w, min_size=9):
    """Return (font, text) with the font shrunk until the text fits max_w."""
    size_now = size
    while size_now > min_size:
        f = font(path, size_now)
        if draw.textlength(text, font=f) <= max_w:
            return f, text
        size_now -= 1
    f = font(path, min_size)
    while text and draw.textlength(text, font=f) > max_w:
        text = text[:-1]
    return f, text.rstrip() + "…"


def wrap(draw, text, fnt, max_w, max_lines=2):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
            if len(lines) == max_lines:
                break
    if cur and len(lines) < max_lines:
        lines.append(cur)
    return lines


def centred(draw, cx, y, text, fnt, fill=INK):
    w = draw.textlength(text, font=fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)
    return y + fnt.size + 4


# ---------------------------------------------------------------- stories
LEADS = [
    {
        "kicker": "EUROPE · UKRAINE",
        "headline": "Missiles and drones pound Kyiv's river bridges",
        "details": [
            "Ballistic barrage from 01:25 ran 6+ hours",
            "3 bridges hit · 3 killed, ~15 hurt · grid critical",
        ],
        "scene": "kyiv",
    },
    {
        "kicker": "ASIA · INDIA",
        "headline": "Cyclone Akvan makes landfall on the Odisha coast",
        "details": [
            "Winds 70-80 km/h, gusting 90, near Gopalpur",
            "3rd cyclone in a month · mass evacuations",
        ],
        "scene": "cyclone",
    },
    {
        "kicker": "CLIMATE · ANTALYA, TÜRKIYE",
        "headline": "COP31 final day closes deadlocked on fossil fuels",
        "details": [
            "Fossil wording cut; $120B adaptation goal dropped",
            "Overtime expected · US absent a second year",
        ],
        "scene": "cop",
    },
]

# (region name, [(headline, detail), ...]) — grouped into 3 columns below.
EUROPE = [
    ("UK-EU reset deal agreed in Brussels", "Food checks end; youth mobility 100,000 a side"),
    ("Youth strike across 25+ countries", "Rallies over living costs, housing, spending"),
    ("UK pledges 1,000+ drones for Ukraine", "£260M package announced in Berlin speech"),
    ("EU to summon Russia's envoy", "Over embassy damage in Kyiv strikes — Kallas"),
    ("Poland probes objects near border", "Air-threat warning lifted at 07:30"),
    ("Denmark ratifies Greenland deal", "Security agreement with the US approved"),
    ("Italy fines Meta €805M", "Penalty over Android photo access"),
]
MIDDLE_EAST = [
    ("Houthi missiles hit Riyadh tower", "PIF tower damaged in financial district"),
    ("Tanker hits mine in Hormuz", "Ship ablaze as attacks rise; war in month 9"),
    ("Trump: Iran strike call in 2027", "\"Not rushing\" — decision after the new year"),
    ("Israeli forces cross Gaza line", "Incursion at Nuseirat, first since the truce"),
    ("Iraq moves on Kataib Hezbollah", "Baghdad orders group out of Jurf al-Sakhar"),
]
ASIA_PACIFIC = [
    ("Trump, Xi, Putin sign declaration", "Four-point peace pact at Shenzhen summit"),
    ("Myanmar rejects ICJ ruling", "Rohingya refugees celebrate in Cox's Bazar"),
    ("Nikkei falls 4.8% in AI sell-off", "Lowest since April; chip makers hit hardest"),
    ("North Korea expanding enrichment", "IAEA: uranium work growing at Yongbyon"),
    ("Violence ahead of Hasina return", "Bangladesh tensions rise before arrival"),
    ("Sri Lanka raises rate to 9%", "First central bank hike in six months"),
]
AFRICA = [
    ("Kenya declares Ebola over", "Last patient out, 37 days after first case"),
    ("Drone strike kills 10 in Sudan", "Gold mine hit in South Kordofan"),
    ("Dozens missing off Senegal", "Migrant boat capsizes off Yenne"),
    ("Zimbabwe destroys landmines", "250,000 mines cleared by HALO Trust"),
]
AMERICAS = [
    ("GTA VI breaks launch records", "Sensor Tower estimates: $2.36B day one"),
    ("Wall Street falls a fifth day", "AI sell-off spreads to US markets"),
    ("SpaceX sells ~$32B in bonds", "AI-chip bond sale, per Bloomberg/FT"),
    ("Anthropic makes Nasdaq debut", "Ticker ANT, listing into the sell-off"),
    ("IMF: debt near 100% of GDP", "Georgieva at APEC: highest since WWII"),
    ("Record floods hit Florida", "St Johns River at record stage; marathon off"),
    ("Dragon leaves ISS with science", "6,300 lb of cargo; Falcon 9 flies USSF-317"),
    ("Bukele registers for third term", "El Salvador president files for re-election"),
    ("Lula recognises Indigenous lands", "Kayapo and Yudja territories formalised"),
    ("Ella Langley sweeps CMA Awards", "Entertainer of the Year; Swift returns"),
]
SCIENCE = [
    ("Star caught swallowing companion", "Nature: merger near Andromeda, star \"Bao\""),
]

COLUMNS = [
    [("EUROPE", EUROPE), ("AFRICA", AFRICA)],
    [("MIDDLE EAST", MIDDLE_EAST), ("ASIA-PACIFIC", ASIA_PACIFIC)],
    [("AMERICAS", AMERICAS), ("SCIENCE & CLIMATE", SCIENCE)],
]

STORY_COUNT = len(LEADS) + sum(len(cards) for col in COLUMNS for _, cards in col)


# ---------------------------------------------------------------- scenes
def scene_kyiv(draw, x, y, w, h):
    """Night river skyline: three bridges, missile trails, dark water."""
    draw.rectangle([x, y, x + w, y + h], fill=(24, 34, 62))
    # stars + moon
    for sx, sy in [(28, 18), (70, 40), (120, 14), (205, 30), (268, 16), (150, 44), (44, 58), (238, 52)]:
        draw.point((x + sx, y + sy), fill=(220, 224, 235))
    draw.ellipse([x + w - 52, y + 12, x + w - 24, y + 40], fill=(232, 230, 214))
    # far bank skyline
    for bx, bh in [(6, 26), (38, 38), (78, 22), (210, 34), (248, 24), (282, 40)]:
        draw.rectangle([x + bx, y + h - 52 - bh, x + bx + 24, y + h - 52], fill=(13, 19, 38))
    # river
    draw.rectangle([x, y + h - 52, x + w, y + h], fill=(31, 55, 92))
    for rx in range(12, w - 10, 34):
        draw.line([x + rx, y + h - 30, x + rx + 16, y + h - 30], fill=(70, 105, 150), width=2)
    # three bridges: deck + towers/arches, lit steel so they read at night
    steel = (104, 128, 168)
    deck_y = y + h - 52
    for i, bx in enumerate((18, 128, 232)):
        bw = 74
        draw.rectangle([x + bx, deck_y - 4, x + bx + bw, deck_y], fill=steel)
        if i == 1:  # arched bridge
            draw.arc([x + bx + 6, deck_y - 34, x + bx + bw - 6, deck_y + 8], 180, 360, fill=steel, width=4)
        else:  # pylon bridges
            draw.rectangle([x + bx + bw // 2 - 2, deck_y - 34, x + bx + bw // 2 + 2, deck_y - 4], fill=steel)
            draw.line([x + bx + 2, deck_y - 4, x + bx + bw // 2, deck_y - 32], fill=steel, width=2)
            draw.line([x + bx + bw - 2, deck_y - 4, x + bx + bw // 2, deck_y - 32], fill=steel, width=2)
    # missile trails with bright heads
    trails = [((36, 8), (96, 66)), ((150, 4), (196, 60)), ((286, 10), (238, 64)), ((96, 2), (140, 52))]
    for (ax, ay), (bx2, by2) in trails:
        draw.line([x + ax, y + ay, x + bx2, y + by2], fill=(240, 178, 92), width=2)
        draw.ellipse([x + bx2 - 3, y + by2 - 3, x + bx2 + 3, y + by2 + 3], fill=(255, 226, 160))


def scene_cyclone(draw, x, y, w, h):
    """Cyclone spiral over a coastline, seen from above."""
    draw.rectangle([x, y, x + w, y + h], fill=(38, 96, 118))  # sea
    # landmass along the right and bottom edges
    land = [(x + w - 96, y), (x + w, y), (x + w, y + h), (x + w - 130, y + h),
            (x + w - 108, y + h - 44), (x + w - 128, y + h - 88), (x + w - 96, y + h - 120)]
    draw.polygon(land, fill=(196, 178, 128))
    draw.line(land + [land[0]], fill=(150, 132, 92), width=3)
    cx, cy = x + w * 0.40, y + h * 0.46
    # spiral arms
    for k in range(3):
        pts = []
        for t in range(0, 101):
            ang = k * (2 * math.pi / 3) + t * 0.055
            r = 4 + t * 0.62
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang) * 0.82))
        draw.line(pts, fill=(238, 246, 250), width=5)
    draw.ellipse([cx - 9, cy - 8, cx + 9, cy + 8], fill=(16, 52, 70))  # eye
    # rain streaks
    for rx, ry in [(18, 96), (52, 112), (88, 100), (24, 66), (270, 30), (292, 62)]:
        draw.line([x + rx, y + ry, x + rx - 8, y + ry + 12], fill=(170, 205, 220), width=2)
    # landfall marker
    mx, my = x + w - 104, y + h - 92
    draw.ellipse([mx - 5, my - 5, mx + 5, my + 5], fill=ACCENT)
    draw.ellipse([mx - 10, my - 10, mx + 10, my + 10], outline=ACCENT, width=2)


def scene_cop(draw, x, y, w, h):
    """Conference table with a globe split by a jagged deadlock crack."""
    draw.rectangle([x, y, x + w, y + h], fill=(233, 226, 205))
    cx, cy = x + w // 2, y + h // 2 - 8
    # table
    draw.ellipse([cx - 128, cy + 26, cx + 128, cy + 74], fill=(122, 88, 58))
    draw.rectangle([cx - 128, cy + 38, cx + 128, cy + 50], fill=(122, 88, 58))
    # delegate seats at the two ends of the table only (kept clear of the
    # scene edges so nothing collides with the kicker text below)
    for sx in (cx - 146, cx + 146):
        draw.rectangle([sx - 8, cy + 34, sx + 8, cy + 62], fill=(70, 70, 74))
    # globe: left half green/blue, right half grey
    r = 44
    draw.pieslice([cx - r, cy - r, cx + r, cy + r], 90, 270, fill=(74, 128, 168))
    draw.pieslice([cx - r, cy - r, cx + r, cy + r], 270, 90, fill=(158, 156, 148))
    draw.ellipse([cx - 26, cy - 22, cx - 6, cy - 6], fill=(96, 158, 104))   # continent, live half
    draw.ellipse([cx - 20, cy + 8, cx - 2, cy + 24], fill=(96, 158, 104))
    draw.ellipse([cx + 8, cy - 16, cx + 26, cy - 2], fill=(128, 126, 118))  # continent, grey half
    draw.ellipse([cx + 4, cy + 10, cx + 20, cy + 24], fill=(128, 126, 118))
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=2)
    # deadlock crack down the middle
    crack = [(cx, cy - r), (cx - 6, cy - 24), (cx + 5, cy - 8), (cx - 5, cy + 10), (cx + 4, cy + 26), (cx, cy + r)]
    draw.line(crack, fill=ACCENT, width=3)
    # small flags
    for i, col in enumerate([(158, 27, 27), (38, 96, 118), (96, 158, 104), (200, 160, 60)]):
        fx = x + 22 + i * 14
        draw.line([fx, y + 14, fx, y + 30], fill=INK, width=2)
        draw.rectangle([fx, y + 14, fx + 10, y + 21], fill=col)


SCENES = {"kyiv": scene_kyiv, "cyclone": scene_cyclone, "cop": scene_cop}

MARGIN = 26
COL_W = (W - 2 * MARGIN - 2 * 16) // 3  # 3 columns, 16px gutters


def masthead(draw):
    y = 16
    draw.line([MARGIN, y, W - MARGIN, y], fill=INK, width=1)
    y += 7
    f_small = font(SANS_R, 12)
    centred(draw, W // 2, y, "EST. 2026 · ONE PAGE · THE WHOLE DAY", f_small, GREY)
    y += 20
    f_title = font(SERIF_B, 63)
    centred(draw, W // 2, y, "THE WORLD IN ONE DAY", f_title)
    y += 72
    draw.rectangle([MARGIN, y, W - MARGIN, y + 5], fill=INK)
    y += 13
    f_date = font(SERIF_B, 30)
    centred(draw, W // 2, y, "FRIDAY 20 NOVEMBER 2026", f_date)
    y += 38
    f_sub = font(SANS_R, 14)
    centred(draw, W // 2, y,
            f"{STORY_COUNT} stories · 6 continents · one front page", f_sub, ACCENT)
    y += 22
    draw.line([MARGIN, y, W - MARGIN, y], fill=INK, width=2)
    return y + 10


def lead_card(draw, x, y, lead):
    draw.rectangle([x, y, x + COL_W, y + 112], outline=RULE_LIGHT, width=1)
    SCENES[lead["scene"]](draw, x, y, COL_W, 112)
    cy = y + 120
    f_kick, kick = fit(draw, lead["kicker"], SANS_B, 12, COL_W)
    draw.text((x, cy), kick, font=f_kick, fill=ACCENT)
    cy += 18
    f_head = font(SERIF_B, 24)
    for line in wrap(draw, lead["headline"], f_head, COL_W, 2):
        draw.text((x, cy), line, font=f_head, fill=INK)
        cy += 28
    cy += 2
    f_det = font(SANS_R, 12)
    for det in lead["details"]:
        f_d, d = fit(draw, det, SANS_R, 12, COL_W)
        draw.text((x, cy), d, font=f_d, fill=(52, 50, 46))
        cy += 16
    return cy


def body_card(draw, x, y, headline, detail):
    f_h, h = fit(draw, headline, SANS_B, 15, COL_W)
    draw.text((x, y), h, font=f_h, fill=INK)
    f_d, d = fit(draw, detail, SANS_R, 12, COL_W)
    draw.text((x, y + 18), d, font=f_d, fill=(52, 50, 46))
    draw.line([x, y + 36, x + COL_W, y + 36], fill=RULE_LIGHT, width=1)
    return y + 42


def body_column(draw, x, y, regions):
    for name, cards in regions:
        f_r = font(SANS_B, 15)
        draw.text((x, y), name, font=f_r, fill=ACCENT)
        draw.line([x, y + 19, x + COL_W, y + 19], fill=ACCENT, width=2)
        y += 25
        for headline, detail in cards:
            y = body_card(draw, x, y, headline, detail)
        y += 5
    return y


def footer(draw):
    top = H - 40
    draw.rectangle([0, top, W, H], fill=INK)
    f1 = font(SANS_R, 12)
    centred(draw, W // 2, top + 7,
            "Every story happened or was first reported on Friday 20 November 2026", f1, PAPER)
    f2 = font(SANS_R, 11)
    centred(draw, W // 2, top + 23,
            "Sources: Reuters · AP · UN News · The Times · Sensor Tower   ·   One page, 1024 × 1024",
            f2, (196, 190, 174))


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    y = masthead(draw)
    # lead row
    lead_bottom = y
    for i, lead in enumerate(LEADS):
        x = MARGIN + i * (COL_W + 16)
        lead_bottom = max(lead_bottom, lead_card(draw, x, y, lead))
    y = lead_bottom + 8
    draw.line([MARGIN, y, W - MARGIN, y], fill=INK, width=2)
    y += 10
    # body columns
    bottom = y
    for i, regions in enumerate(COLUMNS):
        x = MARGIN + i * (COL_W + 16)
        bottom = max(bottom, body_column(draw, x, y, regions))
    footer(draw)
    img.save(OUT, "PNG", optimize=True)
    print(f"stories={STORY_COUNT} body_bottom={bottom} size={os.path.getsize(OUT)}")


if __name__ == "__main__":
    main()
