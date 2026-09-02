from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "05_architecture" / "diagrams" / "ai_new_product_agent_runtime_architecture.png"

COLORS = {
    "bg": "#F7F9FC",
    "paper": "#FFFFFF",
    "ink": "#1F2329",
    "muted": "#646A73",
    "subtle": "#8F959E",
    "line": "#DEE4EB",
    "line_dark": "#B7C3D0",
    "blue": "#3370FF",
    "blue_dark": "#245BDB",
    "blue_soft": "#E8F1FF",
    "blue_pale": "#F4F8FF",
    "green": "#2EA66B",
    "green_soft": "#EAF8F1",
    "amber": "#C47F17",
    "amber_soft": "#FFF6E5",
}


def font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size, index=1 if bold else 0)
        except Exception:
            continue
    return ImageFont.load_default()


def text_size(draw, text, fnt):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def wrap_text(draw, text, fnt, max_width):
    lines = []
    for raw_line in text.split("\n"):
        current = ""
        for char in raw_line:
            trial = current + char
            if text_size(draw, trial, fnt)[0] <= max_width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = char
        if current:
            lines.append(current)
        elif raw_line == "":
            lines.append("")
    return lines


def draw_wrapped(draw, box, text, fnt, fill, align="center", valign="center", gap=7):
    x1, y1, x2, y2 = box
    lines = wrap_text(draw, text, fnt, x2 - x1)
    sizes = [text_size(draw, line, fnt) for line in lines]
    total_h = sum(h for _, h in sizes) + gap * max(0, len(lines) - 1)
    y = y1 if valign == "top" else y1 + max(0, (y2 - y1 - total_h) / 2)
    for line, (w, h) in zip(lines, sizes):
        if align == "left":
            x = x1
        elif align == "right":
            x = x2 - w
        else:
            x = x1 + (x2 - x1 - w) / 2
        draw.text((x, y), font=fnt, text=line, fill=fill)
        y += h + gap


def rounded(draw, box, fill, outline, radius=18, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def arrow_head(draw, point, direction, color):
    x, y = point
    if direction == "right":
        pts = [(x, y), (x - 18, y - 10), (x - 18, y + 10)]
    elif direction == "left":
        pts = [(x, y), (x + 18, y - 10), (x + 18, y + 10)]
    elif direction == "down":
        pts = [(x, y), (x - 10, y - 18), (x + 10, y - 18)]
    else:
        pts = [(x, y), (x - 10, y + 18), (x + 10, y + 18)]
    draw.polygon(pts, fill=color)


def arrow(draw, start, end, color=None, width=4):
    color = color or COLORS["subtle"]
    draw.line((start[0], start[1], end[0], end[1]), fill=color, width=width)
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    if abs(dx) >= abs(dy):
        arrow_head(draw, end, "right" if dx >= 0 else "left", color)
    else:
        arrow_head(draw, end, "down" if dy >= 0 else "up", color)


def elbow_arrow(draw, points, color=None, width=4, direction="right"):
    color = color or COLORS["subtle"]
    for start, end in zip(points, points[1:]):
        draw.line((start[0], start[1], end[0], end[1]), fill=color, width=width)
    arrow_head(draw, points[-1], direction, color)


def dashed(draw, points, color, width=4, dash=16, gap=12):
    for start, end in zip(points, points[1:]):
        x1, y1 = start
        x2, y2 = end
        length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        if not length:
            continue
        ux = (x2 - x1) / length
        uy = (y2 - y1) / length
        pos = 0
        while pos < length:
            seg_end = min(pos + dash, length)
            draw.line(
                (x1 + ux * pos, y1 + uy * pos, x1 + ux * seg_end, y1 + uy * seg_end),
                fill=color,
                width=width,
            )
            pos += dash + gap


def pill(draw, box, text, fill, color, outline=None, size=18):
    rounded(draw, box, fill, outline or fill, radius=20, width=1)
    draw_wrapped(draw, (box[0] + 18, box[1], box[2] - 18, box[3]), text, font(size, True), color)


def section_header(draw, x, y, label, title, subtitle, color=COLORS["blue"]):
    pill(draw, (x, y, x + 74, y + 36), label, COLORS["blue_soft"], color, size=17)
    draw_wrapped(draw, (x + 92, y - 2, x + 760, y + 34), title, font(25, True), COLORS["ink"], align="left")
    draw_wrapped(draw, (x + 92, y + 34, x + 1080, y + 62), subtitle, font(17), COLORS["muted"], align="left")


def card(draw, box, title, body, accent=COLORS["blue"], fill=COLORS["paper"], title_size=23, body_size=18):
    x1, y1, x2, y2 = box
    rounded(draw, box, fill, COLORS["line"], radius=16, width=2)
    draw.rounded_rectangle((x1, y1, x2, y1 + 6), radius=4, fill=accent)
    draw_wrapped(draw, (x1 + 24, y1 + 24, x2 - 24, y1 + 62), title, font(title_size, True), COLORS["ink"], align="left")
    draw_wrapped(draw, (x1 + 24, y1 + 78, x2 - 24, y2 - 24), body, font(body_size), COLORS["muted"], align="left", gap=7)


def large_card(draw, box, title, body, bullets, accent=COLORS["blue"]):
    x1, y1, x2, y2 = box
    rounded(draw, box, COLORS["blue_pale"], accent, radius=18, width=3)
    draw_wrapped(draw, (x1 + 30, y1 + 26, x2 - 30, y1 + 66), title, font(28, True), COLORS["ink"], align="left")
    draw_wrapped(draw, (x1 + 30, y1 + 74, x2 - 30, y1 + 112), body, font(18), COLORS["muted"], align="left")
    bx, by = x1 + 30, y1 + 136
    for idx, item in enumerate(bullets):
        col = idx % 2
        row = idx // 2
        px = bx + col * 355
        py = by + row * 54
        rounded(draw, (px, py, px + 320, py + 38), COLORS["paper"], COLORS["line"], radius=10, width=1)
        draw_wrapped(draw, (px + 16, py, px + 304, py + 38), item, font(16, True), accent, align="left")


def list_card(draw, box, title, items, accent=COLORS["blue"], item_size=17, item_gap=38):
    x1, y1, x2, y2 = box
    rounded(draw, box, COLORS["blue_pale"], COLORS["line"], radius=16, width=2)
    draw_wrapped(draw, (x1 + 24, y1 + 18, x2 - 24, y1 + 54), title, font(22, True), COLORS["ink"], align="left")
    y = y1 + 72
    for item in items:
        draw.ellipse((x1 + 26, y + 7, x1 + 36, y + 17), fill=accent)
        draw_wrapped(draw, (x1 + 52, y, x2 - 28, y + 28), item, font(item_size), COLORS["muted"], align="left")
        y += item_gap


def boundary_card(draw, box, title, body, accent):
    x1, y1, x2, y2 = box
    rounded(draw, box, COLORS["paper"], COLORS["line"], radius=16, width=2)
    draw.rounded_rectangle((x1, y1, x1 + 7, y2), radius=4, fill=accent)
    draw_wrapped(draw, (x1 + 28, y1 + 14, x2 - 24, y1 + 48), title, font(20, True), COLORS["ink"], align="left")
    draw_wrapped(draw, (x1 + 28, y1 + 54, x2 - 24, y2 - 14), body, font(16), COLORS["muted"], align="left", gap=5)


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    width, height = 3200, 1800
    image = Image.new("RGB", (width, height), COLORS["bg"])
    draw = ImageDraw.Draw(image)

    rounded(draw, (80, 70, 3120, 1728), COLORS["paper"], "#E7EBF0", radius=24, width=2)

    draw.text((140, 118), "AI 新品推荐 Agent 运行架构图", font=font(52, True), fill=COLORS["ink"])
    draw.text(
        (144, 190),
        "用一张图说明：算法离线生成推荐，Agent 在线受控调用工具，并把结果解释给采购。",
        font=font(23),
        fill=COLORS["muted"],
    )
    pill(draw, (2520, 128, 3025, 174), "工作流型 Agent + 工具调用型 Harness", COLORS["blue_soft"], COLORS["blue_dark"], size=17)

    callout_y = 262
    boundary_items = [
        ("大计算离线完成", "算法结果提前写入 Doris / 数据服务", COLORS["blue"]),
        ("API 是唯一入口", "后端工具读取推荐表和证据表", COLORS["green"]),
        ("大模型只解释", "不直接查小票，不实时重算算法", COLORS["amber"]),
    ]
    for i, (title, body, accent) in enumerate(boundary_items):
        x = 140 + i * 990
        boundary_card(draw, (x, callout_y, x + 915, callout_y + 105), title, body, accent)

    section_header(draw, 140, 440, "A", "离线推荐生产", "数据开发和调度系统按数据合同、算法卡定时产出结果。")
    top_y = 552
    card_w, card_h, gap = 430, 205, 44
    xs = [140 + i * (card_w + gap) for i in range(4)]
    offline_cards = [
        ("基础数据表", "Doris 小票、门店、商品、价格、毛利损耗、可订可售、竞品数据。"),
        ("算法证据表", "算法 01～07 产出画像、门店等级、SKU、价格、购物篮、竞品趋势。"),
        ("机会引擎", "08 候选标准化；09 证据合成与风险门禁；10 优先级编排。"),
        ("推荐结果表", "mart_opportunity_recommendation\n保存方向、优先级、证据、风险、试点建议。"),
    ]
    for x, (title, body) in zip(xs, offline_cards):
        card(draw, (x, top_y, x + card_w, top_y + card_h), title, body)
    for i in range(3):
        arrow(draw, (xs[i] + card_w + 8, top_y + card_h / 2), (xs[i + 1] - 12, top_y + card_h / 2))

    list_card(
        draw,
        (2180, top_y, 3025, top_y + card_h),
        "数据开发交付边界",
        [
            "基础表、公共过滤、质量校验",
            "算法 01～10 结果表",
            "推荐结果表、版本和调度",
        ],
        accent=COLORS["blue"],
    )
    arrow(draw, (xs[-1] + card_w + 8, top_y + card_h / 2), (2140, top_y + card_h / 2))

    section_header(draw, 140, 845, "B", "在线 Agent 回答", "采购提问后，Harness 控制工具调用，再让大模型解释结构化结果。")
    mid_y = 958
    q_box = (140, mid_y, 515, mid_y + 220)
    harness_box = (640, mid_y - 20, 1510, mid_y + 240)
    api_box = (1640, mid_y, 2145, mid_y + 220)
    answer_box = (2280, mid_y, 3025, mid_y + 220)

    card(draw, q_box, "采购提问", "例：上海牛肉类有没有适合开发的新品机会？", accent=COLORS["green"])
    large_card(
        draw,
        harness_box,
        "Agent Harness 控制层",
        "把自然语言问题变成可控、可追溯的工具调用流程。",
        ["意图识别", "参数抽取", "工具路由", "轻量重排", "安全护栏"],
        accent=COLORS["blue"],
    )
    list_card(
        draw,
        api_box,
        "固定工具 / 后端 API",
        [
            "search_opportunities",
            "get_opportunity_detail",
            "get_*_evidence",
            "log_purchase_feedback",
        ],
        accent=COLORS["blue"],
        item_size=15,
        item_gap=35,
    )
    card(
        draw,
        answer_box,
        "解释与展示",
        "大模型基于 API 返回结果，生成推荐理由、价格建议、风险说明和下一步动作。\n前端展示列表、详情、证据和反馈入口。",
        accent=COLORS["green"],
    )
    arrow(draw, (q_box[2] + 10, mid_y + 110), (harness_box[0] - 18, mid_y + 110))
    arrow(draw, (harness_box[2] + 12, mid_y + 110), (api_box[0] - 18, mid_y + 110))
    arrow(draw, (api_box[2] + 12, mid_y + 110), (answer_box[0] - 18, mid_y + 110))

    elbow_arrow(
        draw,
        [(xs[-1] + card_w / 2, top_y + card_h), (xs[-1] + card_w / 2, 805), (1890, 805), (1890, mid_y - 8)],
        COLORS["blue"],
        width=4,
        direction="down",
    )
    draw_wrapped(draw, (1740, 760, 2310, 800), "在线只读取推荐表和证据表", font(18, True), COLORS["blue_dark"])

    section_header(draw, 140, 1288, "C", "反馈回流", "采购动作进入反馈表，用于后续验收和下一轮离线复盘。")
    fb_y = 1395
    feedback_cards = [
        ("采购反馈", "采纳、驳回、补充原因、供应商沟通结果、试点表现。", COLORS["green"]),
        ("日志与反馈表", "fact_ai_selection_request_log\nfact_ai_selection_feedback", COLORS["blue"]),
        ("下一轮复盘", "反馈用于业务验收、参数校准和离线重跑，不实时改写当次推荐。", COLORS["amber"]),
    ]
    fb_xs = [140, 850, 1560]
    fb_w = 610
    for x, (title, body, accent) in zip(fb_xs, feedback_cards):
        card(draw, (x, fb_y, x + fb_w, fb_y + 170), title, body, accent=accent, fill="#FBFCFE")
    arrow(draw, (fb_xs[0] + fb_w + 10, fb_y + 85), (fb_xs[1] - 16, fb_y + 85))
    arrow(draw, (fb_xs[1] + fb_w + 10, fb_y + 85), (fb_xs[2] - 16, fb_y + 85))
    dashed(
        draw,
        [(1865, fb_y), (1865, 1240), (3050, 1240), (3050, 390), (355, 390), (355, 440)],
        COLORS["amber"],
        width=4,
    )
    arrow_head(draw, (355, 440), "down", COLORS["amber"])

    list_card(
        draw,
        (2280, fb_y, 3025, fb_y + 170),
        "开发评审顺序",
        [
            "数据合同 -> 算法卡 -> 推荐表设计",
            "后端工具 API -> Agent Harness",
            "前端工作台 -> 反馈闭环",
        ],
        accent=COLORS["blue"],
    )

    draw.line((140, 1646, 3025, 1646), fill=COLORS["line"], width=2)
    draw_wrapped(
        draw,
        (140, 1666, 3025, 1704),
        "给开发的一句话：数据开发负责把机会算出来；后端 API 负责把机会查出来；Harness 负责让 Agent 按规则调用；大模型负责把结果讲清楚。",
        font(21, True),
        COLORS["blue_dark"],
    )

    image.save(OUTPUT)
    return OUTPUT


if __name__ == "__main__":
    print(build())
