"""Generate the PulseBoard cover diagram for the portfolio card.

Outputs pulseboard_cover.png next to this script. Run with `python3 _generate_pulseboard_cover.py`.
"""

from PIL import Image, ImageDraw, ImageFont

W, H = 1600, 900

BG = (9, 9, 11)
PANEL = (24, 24, 27)
PANEL_BORDER = (63, 63, 70)
TEXT = (244, 244, 245)
TEXT_DIM = (161, 161, 170)
TEXT_FAINT = (113, 113, 122)
GREEN = (16, 185, 129)
INDIGO = (99, 102, 241)

HELV = "/System/Library/Fonts/HelveticaNeue.ttc"


def font(size, weight=0):
    return ImageFont.truetype(HELV, size, index=weight)


def text_size(draw, txt, fnt):
    box = draw.textbbox((0, 0), txt, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def rounded_box(draw, xy, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def stage_box(draw, x, y, w, h, num, title, subtitle, accent):
    rounded_box(draw, (x, y, x + w, y + h), 14, PANEL, PANEL_BORDER, 2)
    badge_d = 28
    bx0, by0 = x + 14, y + 14
    draw.ellipse((bx0, by0, bx0 + badge_d, by0 + badge_d), fill=accent)
    f_badge = font(16, 1)
    tw, th = text_size(draw, str(num), f_badge)
    draw.text((bx0 + (badge_d - tw) / 2, by0 + (badge_d - th) / 2 - 2), str(num), fill=BG, font=f_badge)

    f_title = font(22, 1)
    draw.text((x + 16, y + 56), title, fill=TEXT, font=f_title)

    f_sub = font(14)
    for i, line in enumerate(subtitle):
        draw.text((x + 16, y + 86 + i * 18), line, fill=TEXT_DIM, font=f_sub)


def harrow(draw, x1, x2, y, color=GREEN, width=3, head=12):
    draw.line((x1, y, x2, y), fill=color, width=width)
    if x2 > x1:
        draw.polygon([(x2, y), (x2 - head, y - head // 2 - 2), (x2 - head, y + head // 2 + 2)], fill=color)
    else:
        draw.polygon([(x2, y), (x2 + head, y - head // 2 - 2), (x2 + head, y + head // 2 + 2)], fill=color)


def varrow(draw, x, y1, y2, color=GREEN, width=3, head=12):
    draw.line((x, y1, x, y2), fill=color, width=width)
    if y2 > y1:
        draw.polygon([(x, y2), (x - head // 2 - 2, y2 - head), (x + head // 2 + 2, y2 - head)], fill=color)
    else:
        draw.polygon([(x, y2), (x - head // 2 - 2, y2 + head), (x + head // 2 + 2, y2 + head)], fill=color)


def main():
    img = Image.new("RGB", (W, H), BG)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    odraw = ImageDraw.Draw(overlay)

    # Subtle corner glows
    for r, alpha in [(440, 16), (300, 24), (180, 30)]:
        odraw.ellipse((120 - r, 120 - r, 120 + r, 120 + r), fill=(16, 185, 129, alpha))
        odraw.ellipse((W - 120 - r, H - 120 - r, W - 120 + r, H - 120 + r), fill=(99, 102, 241, alpha))

    # Title
    f_brand = font(64, 1)
    draw.text((80, 70), "Pulse", fill=TEXT, font=f_brand)
    bw, _ = text_size(draw, "Pulse", f_brand)
    draw.text((80 + bw, 70), "Board", fill=GREEN, font=f_brand)

    f_tag = font(24)
    draw.text((80, 152), "End-to-end product-analytics pipeline  ·  six services, one stack",
              fill=TEXT_DIM, font=f_tag)

    # Top row: 6 stages
    box_w, box_h = 200, 130
    gap = 48
    total = 6 * box_w + 5 * gap
    start_x = (W - total) // 2  # 80 — matches the title margin
    top_y = 260

    stages = [
        ("1", "SDK", ["Python client", "Batches + disk buffer"], GREEN),
        ("2", "Ingestion API", ["FastAPI", "Bearer auth"], GREEN),
        ("3", "Postgres", ["Outbox table", "Idempotent writes"], INDIGO),
        ("4", "Transport", ["Relay service", "At-least-once"], INDIGO),
        ("5", "Redpanda", ["Kafka topic", "events.raw"], INDIGO),
        ("6", "Sink", ["Consumer +", "fan-out"], GREEN),
    ]

    centers_top = []
    for i, (num, title, sub, accent) in enumerate(stages):
        x = start_x + i * (box_w + gap)
        centers_top.append(x + box_w // 2)
        stage_box(draw, x, top_y, box_w, box_h, num, title, sub, accent)
        if i < 5:
            ax1 = x + box_w + 6
            ax2 = x + box_w + gap - 6
            ay = top_y + box_h // 2
            harrow(draw, ax1, ax2, ay, GREEN, 3, 12)

    sink_cx = centers_top[5]
    top_bottom = top_y + box_h

    # Bottom storage row — centered ClickHouse + Redis
    storage_w, storage_h = 240, 120
    storage_gap = 120
    storage_total = 2 * storage_w + storage_gap
    ch_x = (W - storage_total) // 2
    redis_x = ch_x + storage_w + storage_gap
    bottom_y = 500

    ch_cx = ch_x + storage_w // 2
    redis_cx = redis_x + storage_w // 2

    # Branch routing: Sink down, run left to the two storage centers, drop down to each
    elbow_y = top_bottom + 50
    draw.line((sink_cx, top_bottom, sink_cx, elbow_y), fill=GREEN, width=3)
    # Horizontal trunk from Sink center back to ClickHouse center (passes Redis center)
    draw.line((ch_cx, elbow_y, sink_cx, elbow_y), fill=GREEN, width=3)
    # Drop arrows into ClickHouse and Redis
    varrow(draw, ch_cx, elbow_y, bottom_y - 4, GREEN, 3, 12)
    varrow(draw, redis_cx, elbow_y, bottom_y - 4, INDIGO, 3, 12)

    f_t = font(24, 1)
    f_s = font(14)

    # ClickHouse box
    rounded_box(draw, (ch_x, bottom_y, ch_x + storage_w, bottom_y + storage_h), 16, PANEL, GREEN, 2)
    draw.text((ch_x + 20, bottom_y + 16), "ClickHouse", fill=TEXT, font=f_t)
    draw.text((ch_x + 20, bottom_y + 54), "Analytical store", fill=TEXT_DIM, font=f_s)
    draw.text((ch_x + 20, bottom_y + 76), "Cohorts · KPIs · top events", fill=TEXT_FAINT, font=f_s)

    # Redis box
    rounded_box(draw, (redis_x, bottom_y, redis_x + storage_w, bottom_y + storage_h), 16, PANEL, INDIGO, 2)
    draw.text((redis_x + 20, bottom_y + 16), "Redis pub/sub", fill=TEXT, font=f_t)
    draw.text((redis_x + 20, bottom_y + 54), "Realtime channel", fill=TEXT_DIM, font=f_s)
    draw.text((redis_x + 20, bottom_y + 76), "events:{app_id}", fill=TEXT_FAINT, font=f_s)

    # Dashboard at bottom, fed by both
    dash_w, dash_h = 440, 130
    dash_x = (W - dash_w) // 2
    dash_y = 720
    dash_cx = dash_x + dash_w // 2

    rounded_box(draw, (dash_x, dash_y, dash_x + dash_w, dash_y + dash_h), 18, PANEL, TEXT_DIM, 2)
    f_dt = font(28, 1)
    draw.text((dash_x + 24, dash_y + 18), "Dashboard", fill=TEXT, font=f_dt)
    draw.text((dash_x + 24, dash_y + 60), "Next.js · KPIs · cohorts · live firehose", fill=TEXT_DIM, font=f_s)
    draw.text((dash_x + 24, dash_y + 84), "HTTP query API + Server-Sent Events", fill=TEXT_FAINT, font=f_s)

    # Storage → Dashboard join: drop each storage center down to a join line, then to dashboard
    join_y = dash_y - 40
    draw.line((ch_cx, bottom_y + storage_h, ch_cx, join_y), fill=GREEN, width=3)
    draw.line((redis_cx, bottom_y + storage_h, redis_cx, join_y), fill=INDIGO, width=3)
    draw.line((ch_cx, join_y, redis_cx, join_y), fill=TEXT_FAINT, width=2)
    varrow(draw, dash_cx, join_y, dash_y - 4, TEXT_DIM, 3, 12)

    # Edge labels
    f_lbl = font(14, 1)
    draw.text((ch_cx + 10, (bottom_y + storage_h + join_y) // 2 - 8), "SELECT", fill=GREEN, font=f_lbl)
    draw.text((redis_cx + 10, (bottom_y + storage_h + join_y) // 2 - 8), "SSE", fill=INDIGO, font=f_lbl)

    # Live status pill, bottom-right
    pill_text = "Live  ·  sub-second end-to-end"
    f_pill = font(15, 1)
    tw, th = text_size(draw, pill_text, f_pill)
    pad_x, pad_y = 16, 8
    px2 = W - 80
    px1 = px2 - tw - pad_x * 2 - 24
    py1 = H - 60 - th - pad_y
    py2 = py1 + th + pad_y * 2
    rounded_box(draw, (px1, py1, px2, py2), 999, PANEL, GREEN, 2)
    dot_r = 5
    dot_cx = px1 + pad_x + dot_r
    dot_cy = (py1 + py2) // 2
    draw.ellipse((dot_cx - dot_r, dot_cy - dot_r, dot_cx + dot_r, dot_cy + dot_r), fill=GREEN)
    draw.text((dot_cx + dot_r + 8, py1 + pad_y - 2), pill_text, fill=TEXT, font=f_pill)

    out = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    out.save("/Users/udivak/Self Projects/portfolio/pulseboard_cover.png", optimize=True)
    print("wrote pulseboard_cover.png")


if __name__ == "__main__":
    main()
