from pathlib import Path
from math import atan2, cos, sin, pi

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FONT_REGULAR = "/System/Library/Fonts/Hiragino Sans GB.ttc"
FONT_MEDIUM = "/System/Library/Fonts/STHeiti Medium.ttc"

COLORS = {
    "bg": "#F5F7FA",
    "surface": "#FFFFFF",
    "text": "#202735",
    "muted": "#667085",
    "line": "#DDE3EA",
    "line_dark": "#B7C0CC",
    "table_fill": "#E3F4EE",
    "table_border": "#18866A",
    "job_fill": "#E8F0FF",
    "job_border": "#3371FF",
    "engine_fill": "#FFF1D9",
    "engine_border": "#C57900",
    "llm_fill": "#F1E9FF",
    "llm_border": "#7652B7",
    "app_fill": "#E8F4E9",
    "app_border": "#3A7B44",
    "risk_fill": "#FFF0ED",
    "risk_border": "#C85E45",
    "gray_fill": "#EEF1F4",
    "gray_border": "#7D8795",
    "offline": "#3371FF",
    "online": "#C57900",
    "return": "#18866A",
}


def font(size, medium=False):
    return ImageFont.truetype(FONT_MEDIUM if medium else FONT_REGULAR, size=size)


def text_width(draw, text, fnt):
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0]


def wrap_text(draw, text, fnt, max_width):
    lines = []
    for paragraph in str(text).split("\n"):
        if paragraph == "":
            lines.append("")
            continue
        current = ""
        for char in paragraph:
            trial = current + char
            if current and text_width(draw, trial, fnt) > max_width:
                lines.append(current.rstrip())
                current = char.lstrip()
            else:
                current = trial
        if current:
            lines.append(current.rstrip())
    return lines


def draw_wrapped(draw, box, text, fnt, fill, align="left", valign="top", spacing=8):
    x1, y1, x2, y2 = box
    lines = wrap_text(draw, text, fnt, x2 - x1)
    line_heights = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line or "口", font=fnt)
        line_heights.append(bbox[3] - bbox[1])
    total = sum(line_heights) + spacing * max(0, len(lines) - 1)
    y = y1
    if valign == "center":
        y = y1 + max(0, (y2 - y1 - total) / 2)
    elif valign == "bottom":
        y = y2 - total
    for line, height in zip(lines, line_heights):
        width = text_width(draw, line, fnt)
        x = x1
        if align == "center":
            x = x1 + max(0, (x2 - x1 - width) / 2)
        elif align == "right":
            x = x2 - width
        draw.text((x, y), line, font=fnt, fill=fill)
        y += height + spacing
    return y


def rounded_box(draw, box, fill, outline, radius=18, width=3):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def card(draw, box, title, body, kind="table", title_size=28, body_size=22, pad=18):
    palette = {
        "table": (COLORS["table_fill"], COLORS["table_border"]),
        "job": (COLORS["job_fill"], COLORS["job_border"]),
        "engine": (COLORS["engine_fill"], COLORS["engine_border"]),
        "llm": (COLORS["llm_fill"], COLORS["llm_border"]),
        "app": (COLORS["app_fill"], COLORS["app_border"]),
        "risk": (COLORS["risk_fill"], COLORS["risk_border"]),
        "gray": (COLORS["gray_fill"], COLORS["gray_border"]),
    }
    fill, outline = palette[kind]
    rounded_box(draw, box, fill, outline, radius=16, width=3)
    x1, y1, x2, y2 = box
    title_font = font(title_size, medium=True)
    body_font = font(body_size)
    title_bottom = draw_wrapped(
        draw,
        (x1 + pad, y1 + pad, x2 - pad, y1 + 80),
        title,
        title_font,
        COLORS["text"],
        valign="top",
        spacing=5,
    )
    if body:
        draw_wrapped(
            draw,
            (x1 + pad, title_bottom + 8, x2 - pad, y2 - pad),
            body,
            body_font,
            COLORS["muted"],
            valign="top",
            spacing=6,
        )


def arrow(draw, start, end, color, width=5, head=16, dashed=False):
    x1, y1 = start
    x2, y2 = end
    if dashed:
        steps = 20
        for i in range(0, steps, 2):
            a = i / steps
            b = min((i + 1) / steps, 1)
            draw.line(
                (x1 + (x2 - x1) * a, y1 + (y2 - y1) * a,
                 x1 + (x2 - x1) * b, y1 + (y2 - y1) * b),
                fill=color,
                width=width,
            )
    else:
        draw.line((x1, y1, x2, y2), fill=color, width=width)
    angle = atan2(y2 - y1, x2 - x1)
    left = (x2 - head * cos(angle - pi / 6), y2 - head * sin(angle - pi / 6))
    right = (x2 - head * cos(angle + pi / 6), y2 - head * sin(angle + pi / 6))
    draw.polygon([(x2, y2), left, right], fill=color)


def title_block(draw, title, subtitle, width):
    draw.text((80, 54), title, font=font(54, medium=True), fill=COLORS["text"])
    draw_wrapped(draw, (82, 126, width - 80, 196), subtitle, font(25), COLORS["muted"], spacing=6)
    draw.line((80, 208, width - 80, 208), fill=COLORS["line"], width=3)


def legend(draw, x, y):
    items = [
        ("Doris表", "table"),
        ("定时任务/算法", "job"),
        ("机会引擎/服务", "engine"),
        ("大模型/应用", "llm"),
    ]
    cursor = x
    for label, kind in items:
        fill = {
            "table": COLORS["table_fill"],
            "job": COLORS["job_fill"],
            "engine": COLORS["engine_fill"],
            "llm": COLORS["llm_fill"],
        }[kind]
        border = {
            "table": COLORS["table_border"],
            "job": COLORS["job_border"],
            "engine": COLORS["engine_border"],
            "llm": COLORS["llm_border"],
        }[kind]
        draw.rounded_rectangle((cursor, y, cursor + 34, y + 24), radius=6, fill=fill, outline=border, width=2)
        draw.text((cursor + 44, y - 4), label, font=font(22), fill=COLORS["muted"])
        cursor += 190


def architecture_diagram():
    width, height = 3200, 1900
    image = Image.new("RGB", (width, height), COLORS["bg"])
    draw = ImageDraw.Draw(image)
    title_block(
        draw,
        "AI选品 V1 总体完整架构图",
        "从业务数据进入Doris，到定时算法生成主题表，再由机会引擎和大模型为采购提供可解释的商品机会建议。",
        width,
    )
    legend(draw, 80, 230)

    columns = [
        ("1 数据源", 80, 360, "gray"),
        ("2 Doris基础数据", 468, 430, "table"),
        ("3 定时算法加工", 926, 430, "job"),
        ("4 选品主题表", 1384, 430, "table"),
        ("5 机会引擎", 1842, 430, "engine"),
        ("6 服务与大模型", 2300, 430, "llm"),
        ("7 产品与试点", 2758, 360, "app"),
    ]
    top, bottom = 300, 1730
    for title, x, w, kind in columns:
        rounded_box(draw, (x, top, x + w, bottom), COLORS["surface"], COLORS["line_dark"], radius=20, width=3)
        fill = {
            "gray": COLORS["gray_fill"],
            "table": COLORS["table_fill"],
            "job": COLORS["job_fill"],
            "engine": COLORS["engine_fill"],
            "llm": COLORS["llm_fill"],
            "app": COLORS["app_fill"],
        }[kind]
        border = {
            "gray": COLORS["gray_border"],
            "table": COLORS["table_border"],
            "job": COLORS["job_border"],
            "engine": COLORS["engine_border"],
            "llm": COLORS["llm_border"],
            "app": COLORS["app_border"],
        }[kind]
        draw.rounded_rectangle((x, top, x + w, top + 90), radius=20, fill=fill, outline=border, width=3)
        draw.rectangle((x, top + 55, x + w, top + 90), fill=fill)
        draw_wrapped(draw, (x + 18, top + 18, x + w - 18, top + 74), title, font(30, medium=True), COLORS["text"], valign="center")

    for i in range(len(columns) - 1):
        x1 = columns[i][1] + columns[i][2]
        x2 = columns[i + 1][1]
        arrow(draw, (x1 + 6, 1000), (x2 - 8, 1000), COLORS["gray_border"], width=5, head=18)

    column_cards = {
        0: [
            ("业务交易系统", "订单/会员/门店/SKU/金额/时间/折扣", "gray"),
            ("商品与门店主数据", "品类/规格/品牌/城市/区域/状态", "gray"),
            ("经营与价格系统", "毛利/损耗/采购价/出库价/门店售价", "gray"),
            ("久谦竞品API", "平台/商品/价格/销量/促销/图片", "gray"),
        ],
        1: [
            ("fact_order_item", "小票商品明细", "table"),
            ("dim_store / dim_sku", "门店与商品基础维表", "table"),
            ("毛利损耗经营表", "门店-商品-日/周期", "table"),
            ("门店商品日价格表", "成本/出库/原价/成交价", "table"),
            ("竞品原始+SKU+快照", "API追溯与历史变化", "table"),
        ],
        2: [
            ("会员画像", "时间/家庭规模/频次/价格态度", "job"),
            ("门店品类等级", "销售/客数/毛利/折扣/损耗", "job"),
            ("画像贡献与SKU共性", "画像贡献/复购/时段/商品属性", "job"),
            ("价格带与购物篮", "p25/p50/p75 + 关联规则", "job"),
            ("竞品趋势与风险", "连续快照/折扣/损耗/同质化", "job"),
        ],
        3: [
            ("会员画像标签表", "dim_customer_profile", "table"),
            ("门店品类等级表", "mart_store_category_level", "table"),
            ("画像贡献/SKU表现", "profile_contribution / sku_behavior", "table"),
            ("价格带/购物篮", "price_band / basket_association", "table"),
            ("竞品趋势/风险", "competitor_summary / risk_signal", "table"),
        ],
        4: [
            ("① 候选方向生成", "内部延展/缺口/竞品/采购指定", "engine"),
            ("② 基础机会评分", "需求/画像/门店/竞品/毛利/风险", "engine"),
            ("③ 场景化重排", "扩品/替换/试点/毛利改善", "engine"),
            ("④ 证据与风险组装", "指标/数据周期/评分版本/置信度", "engine"),
            ("⑤ 推荐结果存储", "mart_opportunity_recommendation", "table"),
        ],
        5: [
            ("结构化请求服务", "城市/品类/目标/画像/候选", "engine"),
            ("受控工具/API", "发现机会/评估候选/查看证据", "engine"),
            ("大模型意图解析", "采购语言 → 结构化参数", "llm"),
            ("大模型结果解释", "确定数据 → 采购可读建议", "llm"),
            ("请求与反馈日志", "调用/结果/版本/耗时/反馈", "table"),
        ],
        6: [
            ("采购使用入口", "工作台/对话/表单/混合形态待定", "app"),
            ("商品开发建议", "方向/规格/口味/价格/证据/风险", "app"),
            ("上海试点与复盘", "销售/复购/毛利/损耗/采购反馈", "app"),
        ],
    }

    for idx, items in column_cards.items():
        _, x, w, _ = columns[idx]
        y = top + 120
        available = bottom - y - 25
        gap = 18
        card_h = (available - gap * (len(items) - 1)) / len(items)
        for title, body, kind in items:
            card(draw, (x + 18, y, x + w - 18, y + card_h), title, body, kind, title_size=27, body_size=21, pad=16)
            y += card_h + gap

    rounded_box(draw, (80, 1770, 3120, 1850), COLORS["surface"], COLORS["line"], radius=16, width=2)
    draw_wrapped(
        draw,
        (110, 1786, 3090, 1838),
        "核心原则：Doris表负责保存事实和结果；定时算法负责重计算；机会引擎负责候选、评分和重排；大模型只负责理解、调用与解释。",
        font(27, medium=True),
        COLORS["text"],
        valign="center",
        align="center",
    )
    path = OUTPUT_DIR / "ai_selection_complete_architecture.png"
    image.save(path, quality=96)
    return path


def participant(draw, x, y, w, name, kind):
    card(draw, (x, y, x + w, y + 78), name, "", kind, title_size=24, body_size=18, pad=12)


def sequence_panel(draw, box, title, subtitle, participants, messages, panel_color):
    x1, y1, x2, y2 = box
    rounded_box(draw, box, COLORS["surface"], COLORS["line_dark"], radius=22, width=3)
    draw.text((x1 + 28, y1 + 24), title, font=font(34, medium=True), fill=COLORS["text"])
    draw.text((x1 + 30, y1 + 75), subtitle, font=font(22), fill=COLORS["muted"])
    px1, px2 = x1 + 150, x2 - 150
    p_y = y1 + 125
    p_w = 250
    count = len(participants)
    centers = [px1 + i * ((px2 - px1) / (count - 1)) for i in range(count)]
    for center, (name, kind) in zip(centers, participants):
        participant(draw, center - p_w / 2, p_y, p_w, name, kind)
        draw.line((center, p_y + 78, center, y2 - 45), fill=COLORS["line_dark"], width=2)

    message_top = p_y + 125
    row_gap = (y2 - 55 - message_top) / max(1, len(messages))
    fnt = font(20)
    for index, msg in enumerate(messages):
        source, target, label, direction, dashed = msg
        y = message_top + index * row_gap
        sx, tx = centers[source], centers[target]
        color = {"offline": COLORS["offline"], "online": COLORS["online"], "return": COLORS["return"]}[direction]
        arrow(draw, (sx, y), (tx, y), color, width=4, head=14, dashed=dashed)
        label_width = min(500, abs(tx - sx) - 30)
        if label_width < 120:
            label_width = 220
        mid = (sx + tx) / 2
        label_lines = wrap_text(draw, f"{index + 1}. {label}", fnt, label_width)
        label_text = "\n".join(label_lines)
        bbox = draw.multiline_textbbox((0, 0), label_text, font=fnt, spacing=4, align="center")
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.rounded_rectangle((mid - tw / 2 - 10, y - th - 15, mid + tw / 2 + 10, y - 3), radius=8, fill=COLORS["surface"])
        draw.multiline_text((mid - tw / 2, y - th - 10), label_text, font=fnt, fill=color, spacing=4, align="center")


def sequence_diagram():
    width, height = 3200, 2300
    image = Image.new("RGB", (width, height), COLORS["bg"])
    draw = ImageDraw.Draw(image)
    title_block(
        draw,
        "AI选品 V1 完整时序图",
        "上半部分展示离线预计算：系统提前准备主题表和基础推荐；下半部分展示在线请求：采购发起需求后只做轻量查询、重排和解释。",
        width,
    )
    legend(draw, 80, 230)

    offline_participants = [
        ("业务系统/API", "gray"),
        ("数据同步ETL", "job"),
        ("Doris基础表", "table"),
        ("质量闸门", "job"),
        ("算法调度", "job"),
        ("Doris主题表", "table"),
        ("机会引擎", "engine"),
        ("推荐结果表", "table"),
    ]
    offline_messages = [
        (0, 1, "源数据到达/竞品API采集", "offline", False),
        (1, 2, "写入门店、商品、经营、价格、竞品基础表", "offline", False),
        (2, 3, "触发主键、重复、空值、关联与周期检查", "offline", False),
        (3, 4, "质量通过后发布可用数据版本", "return", False),
        (4, 5, "运行画像、等级、共性、价格带、购物篮、趋势、风险", "offline", False),
        (5, 6, "主题表更新完成，触发候选生成与基础评分", "offline", False),
        (6, 7, "写入候选、机会分、证据、风险和评分版本", "offline", False),
    ]
    sequence_panel(
        draw,
        (70, 300, 3130, 1160),
        "A. 离线预计算时序",
        "特点：没有采购提问也会运行；重算法只在数据版本更新后执行。",
        offline_participants,
        offline_messages,
        COLORS["offline"],
    )

    online_participants = [
        ("采购", "app"),
        ("产品入口", "app"),
        ("大模型", "llm"),
        ("后端/工具", "engine"),
        ("机会引擎", "engine"),
        ("Doris结果", "table"),
        ("请求日志", "table"),
    ]
    online_messages = [
        (0, 1, "提交城市、品类、采购目标或指定候选", "online", False),
        (1, 2, "传入自然语言或页面条件", "online", False),
        (2, 3, "输出结构化请求；缺参数时返回追问", "online", False),
        (3, 4, "调用发现机会或评估候选工具", "online", False),
        (4, 5, "查询基础推荐、主题指标和数据新鲜度", "online", False),
        (5, 4, "返回确定候选、分数、证据、风险和版本", "return", False),
        (4, 3, "按扩品/替换/毛利改善轻量重排", "return", False),
        (3, 2, "提供经过校验的结构化证据包", "return", False),
        (2, 1, "组织采购可读解释，不修改事实和分数", "return", False),
        (1, 0, "展示商品方向、价格、证据、风险和动作", "return", False),
        (3, 6, "记录请求、工具、版本、耗时和反馈", "online", True),
    ]
    sequence_panel(
        draw,
        (70, 1210, 3130, 2200),
        "B. 在线采购请求时序",
        "特点：不重跑会员画像、购物篮等离线算法；只查询、校验、重排和解释。",
        online_participants,
        online_messages,
        COLORS["online"],
    )

    path = OUTPUT_DIR / "ai_selection_full_sequence.png"
    image.save(path, quality=96)
    return path


def runtime_table_diagram():
    width, height = 3400, 2700
    image = Image.new("RGB", (width, height), COLORS["bg"])
    draw = ImageDraw.Draw(image)
    title_block(
        draw,
        "AI选品 V1 底层完整运行表",
        "每一行说明一个组件到底是表、任务、服务还是大模型，以及它什么时候运行、读取什么、输出什么、落在哪里。",
        width,
    )
    legend(draw, 80, 230)

    x0, y0 = 80, 305
    col_widths = [100, 370, 260, 360, 650, 760, 680]
    headers = ["序号", "组件", "类型", "触发时间", "主要输入", "主要输出", "落点 / 责任"]
    rows = [
        ("01", "基础数据同步", "ETL任务", "每日或源数据到达后", "业务交易系统、主数据、经营价格系统、久谦API", "小票、门店、商品、毛利损耗、日价格和竞品基础表", "Doris / 数据开发"),
        ("02", "数据质量检查", "校验任务", "每次同步完成后", "本批次Doris基础表", "主键、重复、空值、编码关联、数据周期的通过或失败结果", "质量日志 / 数据开发"),
        ("03", "会员画像", "离线算法", "建议每周，待评审", "小票商品明细、会员、商品品类和时间窗口", "会员时间行为、家庭规模、频次、价格态度画像", "dim_customer_profile / 算法开发"),
        ("04", "门店品类等级", "离线算法", "建议每周，待评审", "小票、门店、商品、毛利损耗", "同品类门店A/B/C/D等级及指标明细", "mart_store_category_level / 算法开发"),
        ("05", "画像贡献与SKU共性", "离线算法", "上游主题表更新后", "画像、等级、小票、商品属性", "主力画像贡献、SKU销售复购时段折扣及属性共性", "profile_contribution / sku_behavior / 算法开发"),
        ("06", "价格带/购物篮/竞品趋势", "离线算法", "建议每周；竞品每日采集", "日价格、小票、画像、商品属性、竞品快照", "成交价格区间、关联规则、竞品方向趋势", "price_band / basket / competitor_summary"),
        ("07", "风险识别", "离线算法", "主题表更新后", "折扣、损耗、毛利、相似品、样本量和数据新鲜度", "折扣、损耗、同质化和数据不足风险", "mart_risk_signal / 算法开发"),
        ("08", "候选方向生成", "机会引擎离线任务", "所有主题表发布后", "画像、门店等级、SKU共性、价格带、购物篮、竞品和风险", "按城市/品类/门店等级/画像/属性组合的候选商品方向", "中间候选表或推荐表草稿 / 算法与数据"),
        ("09", "基础机会评分", "机会引擎离线任务", "候选池生成后", "候选方向、主题指标、评分配置和风险", "基础机会分、分项分、置信度、证据摘要和评分版本", "mart_opportunity_recommendation / 算法开发"),
        ("10", "采购请求解析", "大模型+后端", "采购提交需求时", "自然语言或页面条件", "城市、品类、目标、画像、门店等级、候选等结构化参数", "在线服务 / AI与后端开发"),
        ("11", "场景化轻量重排", "机会引擎在线服务", "每次有效请求", "结构化请求、基础推荐、主题表和场景权重", "符合扩品/替换/试点/毛利改善目标的候选排序", "后端服务或受控SQL / 后端与算法"),
        ("12", "证据组装与回答", "服务+大模型", "重排结果返回后", "候选、确定指标、竞品依据、风险、数据周期和版本", "采购可读的商品方向、原因、价格、风险和行动建议", "产品接口 / 后端与AI开发"),
        ("13", "请求与反馈记录", "日志表", "每次请求完成后", "请求参数、工具调用、结果、评分版本、耗时和采购反馈", "审计、排错、使用分析和模型复盘数据", "fact_ai_selection_request_log / 后端"),
    ]

    row_h = 158
    header_h = 96
    total_w = sum(col_widths)
    rounded_box(draw, (x0, y0, x0 + total_w, y0 + header_h + row_h * len(rows)), COLORS["surface"], COLORS["line_dark"], radius=18, width=3)

    x = x0
    for header, cw in zip(headers, col_widths):
        draw.rectangle((x, y0, x + cw, y0 + header_h), fill="#E9EDF3", outline=COLORS["line_dark"], width=2)
        draw_wrapped(draw, (x + 12, y0 + 10, x + cw - 12, y0 + header_h - 10), header, font(26, medium=True), COLORS["text"], align="center", valign="center")
        x += cw

    type_palette = {
        "ETL任务": (COLORS["job_fill"], COLORS["job_border"]),
        "校验任务": (COLORS["job_fill"], COLORS["job_border"]),
        "离线算法": (COLORS["job_fill"], COLORS["job_border"]),
        "机会引擎离线任务": (COLORS["engine_fill"], COLORS["engine_border"]),
        "机会引擎在线服务": (COLORS["engine_fill"], COLORS["engine_border"]),
        "大模型+后端": (COLORS["llm_fill"], COLORS["llm_border"]),
        "服务+大模型": (COLORS["llm_fill"], COLORS["llm_border"]),
        "日志表": (COLORS["table_fill"], COLORS["table_border"]),
    }

    for r_index, row in enumerate(rows):
        y = y0 + header_h + r_index * row_h
        base_fill = COLORS["surface"] if r_index % 2 == 0 else "#FAFBFC"
        x = x0
        for c_index, (value, cw) in enumerate(zip(row, col_widths)):
            fill = base_fill
            if c_index == 2:
                fill = type_palette.get(value, (COLORS["gray_fill"], COLORS["gray_border"]))[0]
            draw.rectangle((x, y, x + cw, y + row_h), fill=fill, outline=COLORS["line"], width=2)
            fnt = font(23, medium=(c_index in (0, 1)))
            align = "center" if c_index in (0, 2) else "left"
            draw_wrapped(
                draw,
                (x + 12, y + 12, x + cw - 12, y + row_h - 12),
                value,
                fnt,
                COLORS["text"] if c_index in (0, 1, 2) else COLORS["muted"],
                align=align,
                valign="center",
                spacing=5,
            )
            x += cw

    note_y = y0 + header_h + row_h * len(rows) + 26
    rounded_box(draw, (80, note_y, 3380, note_y + 105), COLORS["surface"], COLORS["line"], radius=16, width=2)
    draw_wrapped(
        draw,
        (110, note_y + 18, 3350, note_y + 88),
        "结论：机会引擎不是单表。V1最小实现可采用“离线SQL/算法任务生成基础推荐表 + 后端服务按采购目标重排 + 大模型解释结果”。",
        font(27, medium=True),
        COLORS["text"],
        align="center",
        valign="center",
    )
    path = OUTPUT_DIR / "ai_selection_runtime_table.png"
    image.save(path, quality=96)
    return path


def main():
    paths = [architecture_diagram(), sequence_diagram(), runtime_table_diagram()]
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
