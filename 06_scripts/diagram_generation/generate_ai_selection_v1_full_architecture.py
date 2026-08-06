from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "05_architecture" / "diagrams" / "ai_selection_v1_full_architecture.png"

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
    "amber": "#D97706",
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


def draw_wrapped(draw, box, text, fnt, fill, align="center", valign="center", gap=8):
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
        pts = [(x, y), (x - 20, y - 11), (x - 20, y + 11)]
    elif direction == "left":
        pts = [(x, y), (x + 20, y - 11), (x + 20, y + 11)]
    elif direction == "down":
        pts = [(x, y), (x - 11, y - 20), (x + 11, y - 20)]
    else:
        pts = [(x, y), (x - 11, y + 20), (x + 11, y + 20)]
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


def pill(draw, box, label, color):
    rounded(draw, box, COLORS["surface"], color, radius=18, width=2)
    draw_wrapped(draw, (box[0] + 16, box[1], box[2] - 16, box[3]), label, font(23, True), color)


def card(draw, box, label, title, body, color, body_size=21):
    x1, y1, x2, y2 = box
    rounded(draw, box, COLORS["surface"], COLORS["line"], radius=24, width=2)
    draw.rounded_rectangle((x1, y1, x1 + 14, y2), radius=8, fill=color)
    draw_wrapped(draw, (x1 + 34, y1 + 22, x1 + 94, y1 + 58), label, font(24, True), color, align="left")
    draw_wrapped(draw, (x1 + 96, y1 + 18, x2 - 28, y1 + 64), title, font(29, True), COLORS["ink"], align="left")
    draw_wrapped(draw, (x1 + 34, y1 + 82, x2 - 34, y2 - 24), body, font(body_size), COLORS["muted"], align="left", gap=7)


def group_box(draw, box, label, title, color):
    x1, y1, x2, y2 = box
    rounded(draw, box, COLORS["surface"], COLORS["line"], radius=28, width=2)
    pill(draw, (x1 + 28, y1 + 24, x1 + 132, y1 + 76), label, color)
    draw_wrapped(draw, (x1 + 150, y1 + 18, x2 - 28, y1 + 82), title, font(32, True), COLORS["ink"], align="left")


def mini(draw, box, title, body, color):
    x1, y1, x2, y2 = box
    rounded(draw, box, COLORS["soft"], COLORS["line"], radius=20, width=2)
    draw.ellipse((x1 + 24, y1 + 23, x1 + 42, y1 + 41), fill=color)
    draw_wrapped(draw, (x1 + 56, y1 + 16, x2 - 20, y1 + 54), title, font(22, True), COLORS["ink"], align="left")
    draw_wrapped(draw, (x1 + 24, y1 + 62, x2 - 24, y2 - 20), body, font(18), COLORS["muted"], align="left", gap=5)


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    width, height = 3200, 2120
    image = Image.new("RGB", (width, height), COLORS["bg"])
    draw = ImageDraw.Draw(image)

    draw.text((100, 62), "AI 选品 V1 完整项目架构图", font=font(58, True), fill=COLORS["ink"])
    draw.text(
        (104, 145),
        "从采购新品推荐需求出发，经过数据底座、算法主题表和机会引擎，生成可解释的新品推荐，再进入前端 / Agent / 反馈闭环。",
        font=font(26),
        fill=COLORS["muted"],
    )

    rounded(draw, (100, 215, 3100, 318), COLORS["surface"], COLORS["line"], radius=26, width=2)
    draw.rounded_rectangle((100, 215, 114, 318), radius=8, fill=COLORS["blue"])
    draw_wrapped(
        draw,
        (145, 230, 3060, 302),
        "核心原则：离线算法算结果；后端和 Agent 读结果表做解释；V1 只服务新品推荐。",
        font(31, True),
        COLORS["ink"],
    )

    business = (130, 375, 3070, 515)
    card(
        draw,
        business,
        "01",
        "业务入口：采购发起新品推荐需求",
        "输入城市 / 区域、品类、门店等级、目标消费者画像、候选方向或开发目标；系统回答哪些新品方向值得做、为什么、价格区间、风险和试点建议是什么。",
        COLORS["amber"],
        body_size=22,
    )

    data = (130, 620, 1535, 815)
    quality = (1665, 620, 3070, 815)
    arrow(draw, (1600, 525), (1600, 595), COLORS["muted"])
    card(
        draw,
        data,
        "02",
        "数据底座",
        "内部：Doris 小票、商品、门店、城市算法区域、毛利损耗、门店商品日价格、可订可售。\n外部：久谦原始接口、竞品 SKU、竞品每日快照。",
        COLORS["green"],
    )
    card(
        draw,
        quality,
        "03",
        "数据合同与质量",
        "统一主键、粒度、字段口径、有效交易过滤、数据质量校验、调度批次和版本血缘。\n先确认字段事实，再开发算法。",
        COLORS["teal"],
    )
    arrow(draw, (1548, 718), (1640, 718), COLORS["muted"])

    algo = (130, 920, 3070, 1228)
    group_box(draw, algo, "04", "算法主题表层：把业务证据算成可复用结果表", COLORS["blue"])
    mini_w = 890
    mini_y = 1015
    mini(
        draw,
        (180, mini_y, 180 + mini_w, mini_y + 170),
        "01～03：先确定谁和哪里",
        "01 会员画像 / 02 门店品类等级 / 03 门店群消费者画像贡献\n回答：什么门店群、什么品类、什么主力消费者值得关注。",
        COLORS["blue"],
    )
    mini(
        draw,
        (1155, mini_y, 1155 + mini_w, mini_y + 170),
        "04～06：再看买什么和怎么组合",
        "04 目标画像 SKU 表现 / 05 目标画像商品价格带 / 06 购物篮新品关联\n回答：买什么、多少钱、和什么同票出现。",
        COLORS["blue"],
    )
    mini(
        draw,
        (2130, mini_y, 2130 + mini_w, mini_y + 170),
        "07：外部趋势与竞品验证",
        "验证外部是否有类似机会、趋势是否扩散、竞品价格和规格是否可参考。\n当前状态：更新中。",
        COLORS["purple"],
    )
    arrow(draw, (1600, 830), (1600, 895), COLORS["muted"])

    engine = (130, 1328, 3070, 1548)
    arrow(draw, (1600, 1245), (1600, 1303), COLORS["muted"])
    group_box(draw, engine, "05", "新品机会引擎层：把证据变成可执行新品方向", COLORS["purple"])
    mini(
        draw,
        (180, 1420, 1020, 1510),
        "08 证据合成与风险门禁",
        "合并内部需求、经营可行性、外部趋势和风险约束。",
        COLORS["purple"],
    )
    mini(
        draw,
        (1180, 1420, 2020, 1510),
        "09 新品候选标准化与合并",
        "把相似候选方向合并成采购能理解的标准新品方向。",
        COLORS["purple"],
    )
    mini(
        draw,
        (2180, 1420, 3020, 1510),
        "10 推荐优先级与开发需求编排",
        "输出优先级、开发动作、试点建议和需要补充的信息。",
        COLORS["purple"],
    )

    result = (130, 1650, 1535, 1838)
    app = (1665, 1650, 3070, 1838)
    arrow(draw, (1600, 1564), (1600, 1625), COLORS["muted"])
    card(
        draw,
        result,
        "06",
        "AI 新品机会推荐结果",
        "沉淀推荐结果表：新品方向、目标品类、目标画像、适用门店群、推荐理由、价格区间、经营约束、外部证据、风险提示和试点建议。",
        COLORS["teal"],
        body_size=20,
    )
    card(
        draw,
        app,
        "07",
        "应用与 Agent 层",
        "后端接口、采购工作台或对话入口读取正式结果表。Agent 负责理解查询条件、调用工具、组装证据并解释推荐原因。",
        COLORS["rose"],
        body_size=20,
    )
    arrow(draw, (1548, 1744), (1640, 1744), COLORS["muted"])

    feedback = (130, 1920, 3070, 2035)
    arrow(draw, (2365, 1850), (2365, 1895), COLORS["rose"])
    card(
        draw,
        feedback,
        "08",
        "反馈闭环",
        "采购反馈、试点销售、复购、毛利、损耗和风险复盘进入下一轮离线复盘，用于业务验收、参数调整和后续算法迭代。",
        COLORS["rose"],
        body_size=21,
    )
    dashed_arrow(
        draw,
        [(3025, 1978), (3140, 1978), (3140, 718), (3092, 718)],
        COLORS["rose"],
        "left",
        width=4,
    )
    draw_wrapped(
        draw,
        (2645, 865, 3130, 955),
        "反馈进入下一轮\n离线复盘 / 重跑",
        font(22, True),
        COLORS["rose"],
        align="center",
    )

    draw_wrapped(
        draw,
        (130, 2058, 3070, 2098),
        "当前状态：算法 01～06 已整理为开发版算法卡；算法 07～10 更新中；本次评审优先让基础数据表和 01～03 开工。",
        font(22, True),
        COLORS["muted"],
    )

    image.save(OUTPUT, quality=96)
    return OUTPUT


if __name__ == "__main__":
    print(build())
