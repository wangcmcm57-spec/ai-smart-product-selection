from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "05_architecture" / "diagrams" / "ai_selection_v1_sequence.png"

COLORS = {
    "bg": "#F8FAFC",
    "surface": "#FFFFFF",
    "ink": "#111827",
    "muted": "#64748B",
    "soft": "#F1F5F9",
    "line": "#CBD5E1",
    "blue": "#2563EB",
    "teal": "#0891B2",
    "green": "#059669",
    "purple": "#7C3AED",
    "rose": "#E11D48",
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
        draw.text((x, y), line, font=fnt, fill=fill)
        y += h + gap


def rounded(draw, box, fill, outline, radius=22, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def arrow_head(draw, point, direction, color):
    x, y = point
    if direction == "right":
        pts = [(x, y), (x - 19, y - 10), (x - 19, y + 10)]
    elif direction == "left":
        pts = [(x, y), (x + 19, y - 10), (x + 19, y + 10)]
    elif direction == "down":
        pts = [(x, y), (x - 10, y - 19), (x + 10, y - 19)]
    else:
        pts = [(x, y), (x - 10, y + 19), (x + 10, y + 19)]
    draw.polygon(pts, fill=color)


def arrow(draw, start, end, color=None, width=4):
    color = color or COLORS["muted"]
    draw.line((start[0], start[1], end[0], end[1]), fill=color, width=width)
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    if abs(dx) >= abs(dy):
        arrow_head(draw, end, "right" if dx >= 0 else "left", color)
    else:
        arrow_head(draw, end, "down" if dy >= 0 else "up", color)


def dashed_line(draw, points, color, width=4, dash=18, gap=12):
    for start, end in zip(points, points[1:]):
        x1, y1 = start
        x2, y2 = end
        length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        if length == 0:
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


def dashed_arrow(draw, points, color, direction, width=4):
    dashed_line(draw, points, color, width=width)
    arrow_head(draw, points[-1], direction, color)


def lane(draw, box, title, subtitle, color):
    x1, y1, x2, y2 = box
    rounded(draw, box, COLORS["surface"], COLORS["line"], radius=30, width=2)
    draw.rounded_rectangle((x1, y1, x1 + 16, y2), radius=8, fill=color)
    draw_wrapped(draw, (x1 + 34, y1 + 22, x2 - 34, y1 + 62), title, font(32, True), COLORS["ink"], align="left")
    draw_wrapped(draw, (x1 + 34, y1 + 66, x2 - 34, y1 + 104), subtitle, font(20), COLORS["muted"], align="left")


def step(draw, box, no, title, body, color):
    x1, y1, x2, y2 = box
    rounded(draw, box, COLORS["soft"], COLORS["line"], radius=20, width=2)
    draw.ellipse((x1 + 20, y1 + 20, x1 + 58, y1 + 58), fill=color)
    draw_wrapped(draw, (x1 + 20, y1 + 18, x1 + 58, y1 + 60), no, font(20, True), COLORS["surface"])
    draw_wrapped(draw, (x1 + 70, y1 + 17, x2 - 18, y1 + 58), title, font(23, True), COLORS["ink"], align="left")
    draw_wrapped(draw, (x1 + 22, y1 + 74, x2 - 22, y2 - 18), body, font(18), COLORS["muted"], align="left", gap=5)


def note(draw, box, text, color):
    rounded(draw, box, COLORS["surface"], COLORS["line"], radius=22, width=2)
    draw_wrapped(draw, (box[0] + 26, box[1], box[2] - 26, box[3]), text, font(23, True), color)


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    width, height = 3200, 1880
    image = Image.new("RGB", (width, height), COLORS["bg"])
    draw = ImageDraw.Draw(image)

    draw.text((100, 58), "AI 选品 V1 运行时序图", font=font(58, True), fill=COLORS["ink"])
    draw.text(
        (104, 142),
        "两段执行：离线批量产表；在线查询解释。反馈只进入下一轮离线复盘，不实时改写当次推荐。",
        font=font(26),
        fill=COLORS["muted"],
    )

    note(
        draw,
        (100, 215, 3100, 318),
        "核心原则：数据开发先产出正式结果表；后端 API 查结果和证据；Harness 控制工具调用；大模型只解释结构化结果。",
        COLORS["ink"],
    )

    offline_lane = (100, 390, 3100, 850)
    online_lane = (100, 945, 3100, 1375)
    feedback_lane = (100, 1470, 3100, 1760)
    lane(
        draw,
        offline_lane,
        "A. 离线批量产表",
        "由数据开发和调度系统执行，产出正式算法结果表和证据表。",
        COLORS["blue"],
    )
    lane(
        draw,
        online_lane,
        "B. 在线查询解释",
        "由采购工作台、Agent Harness、后端 API 和大模型解释层执行，只读取结果和证据，不实时重算算法。",
        COLORS["teal"],
    )
    lane(
        draw,
        feedback_lane,
        "C. 反馈回流",
        "采购反馈和试点复盘进入反馈表，再回到 A 段的下一轮离线重跑入口。",
        COLORS["rose"],
    )

    top_y = 535
    step_w = 365
    step_h = 190
    gap = 42
    xs = [160 + i * (step_w + gap) for i in range(7)]
    offline_steps = [
        ("1", "基础数据准备", "Doris 小票、商品、门店、城市区域、毛利损耗、价格、可订可售、外部竞品。", COLORS["green"]),
        ("2", "数据合同与质量", "统一主键粒度、字段口径、有效交易过滤、质量校验、调度批次和版本血缘。", COLORS["blue"]),
        ("3", "01 / 02 并行", "01 会员画像；02 门店品类等级。先分别产出上游正式表。", COLORS["blue"]),
        ("4", "03 画像贡献", "读取 01、02，连接画像、门店群和品类，产出贡献结果。", COLORS["blue"]),
        ("5", "04～06 经营证据", "SKU 表现、价格带、购物篮新品关联，产出可复用经营证据。", COLORS["blue"]),
        ("6", "07～10 机会引擎", "07 外部趋势；08 候选标准化；09 风险门禁；10 推荐展示。", COLORS["purple"]),
        ("7", "算法 10 推荐表", "沉淀推荐优先级主表、展示摘要、自动解释和输入快照。", COLORS["teal"]),
    ]
    for x, args in zip(xs, offline_steps):
        step(draw, (x, top_y, x + step_w, top_y + step_h), *args)
    for i in range(len(xs) - 1):
        arrow(draw, (xs[i] + step_w + 10, top_y + step_h / 2), (xs[i + 1] - 10, top_y + step_h / 2), COLORS["muted"], width=4)

    middle_y = 1080
    step_w2 = 392
    gap2 = 54
    xs2 = [230 + i * (step_w2 + gap2) for i in range(6)]
    online_steps = [
        ("1", "采购查询", "输入城市、品类、门店等级、目标画像、价格诉求或候选方向。", COLORS["rose"]),
        ("2", "Harness", "意图识别、参数抽取、工具路由；缺关键条件时追问。", COLORS["rose"]),
        ("3", "后端 API", "按条件读取算法 10 推荐表，并按推荐 ID 查询证据明细。", COLORS["teal"]),
        ("4", "结果和证据表", "返回推荐方向、画像、品类、门店群、价格、风险、摘要和解释。", COLORS["teal"]),
        ("5", "轻量重排 + 解释", "Harness 组装结构化结果，大模型解释推荐理由、定价和风险。", COLORS["blue"]),
        ("6", "前端展示", "展示推荐列表、详情、证据、风险提示、试点建议和反馈入口。", COLORS["rose"]),
    ]
    for x, args in zip(xs2, online_steps):
        step(draw, (x, middle_y, x + step_w2, middle_y + step_h), *args)
    for i in range(len(xs2) - 1):
        arrow(draw, (xs2[i] + step_w2 + 10, middle_y + step_h / 2), (xs2[i + 1] - 10, middle_y + step_h / 2), COLORS["muted"], width=4)

    fb_y = 1570
    feedback_table = (2060, fb_y, 2860, fb_y + 145)
    rerun_entry = (520, fb_y, 1320, fb_y + 145)
    step(draw, feedback_table, "7", "采购反馈表", "收藏、否决、补充信息、试点结果、销售表现、毛利损耗和风险复盘。", COLORS["rose"])
    step(draw, rerun_entry, "8", "下一轮离线重跑入口", "用于后续验收、参数调整、规则补充和算法重跑；不实时改写当次推荐。", COLORS["purple"])

    arrow(draw, (xs2[-1] + step_w2 / 2, middle_y + step_h + 18), (2460, fb_y - 12), COLORS["rose"], width=4)
    dashed_arrow(draw, [(2050, fb_y + 62), (1335, fb_y + 62)], COLORS["rose"], "left", width=4)
    dashed_arrow(
        draw,
        [(920, fb_y - 10), (920, 870), (750, 870), (750, top_y + step_h + 14)],
        COLORS["purple"],
        "up",
        width=4,
    )
    draw_wrapped(
        draw,
        (980, 855, 1540, 935),
        "明确回到 A 段离线复盘 / 重跑\n不是回到在线查询",
        font(21, True),
        COLORS["purple"],
        align="left",
    )

    draw_wrapped(
        draw,
        (140, 1800, 3060, 1844),
        "开发阅读方式：完整架构图看分层；本图看运行顺序；算法卡看每张结果表的字段、公式和验收。",
        font(22, True),
        COLORS["muted"],
    )

    image.save(OUTPUT, quality=96)
    return OUTPUT


if __name__ == "__main__":
    print(build())
