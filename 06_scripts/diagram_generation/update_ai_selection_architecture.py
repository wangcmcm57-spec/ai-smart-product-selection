from pathlib import Path

from PIL import Image, ImageDraw

from generate_ai_selection_diagrams import (
    COLORS,
    arrow,
    card,
    draw_wrapped,
    font,
    legend,
    rounded_box,
    title_block,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs" / "ai_selection_architecture.png"


def build():
    width, height = 3200, 2500
    image = Image.new("RGB", (width, height), COLORS["bg"])
    draw = ImageDraw.Draw(image)

    title_block(
        draw,
        "AI选品 V1 正式架构图",
        "当前只做新品推荐：已有小票和经营数据进入 Doris，经定时算法加工后生成新品机会；供应商、库存明细、促销优惠券不在当前项目范围内。",
        width,
    )
    legend(draw, 80, 230)

    columns = [
        ("第一层：基础数据层", 70, 590, "table"),
        ("第二层：算法加工层", 700, 590, "job"),
        ("第三层：选品主题表", 1330, 590, "table"),
        ("第四层：机会推荐层", 1960, 590, "engine"),
        ("第五层：采购应用层", 2590, 540, "app"),
    ]
    top, bottom = 300, 2290
    for title, x, w, kind in columns:
        fill = {
            "table": COLORS["table_fill"],
            "job": COLORS["job_fill"],
            "engine": COLORS["engine_fill"],
            "app": COLORS["app_fill"],
        }[kind]
        border = {
            "table": COLORS["table_border"],
            "job": COLORS["job_border"],
            "engine": COLORS["engine_border"],
            "app": COLORS["app_border"],
        }[kind]
        rounded_box(draw, (x, top, x + w, bottom), COLORS["surface"], COLORS["line_dark"], radius=20, width=3)
        draw.rounded_rectangle((x, top, x + w, top + 90), radius=20, fill=fill, outline=border, width=3)
        draw.rectangle((x, top + 55, x + w, top + 90), fill=fill)
        draw_wrapped(draw, (x + 18, top + 16, x + w - 18, top + 78), title, font(29, medium=True), COLORS["text"], valign="center")

    for i in range(len(columns) - 1):
        x1 = columns[i][1] + columns[i][2]
        x2 = columns[i + 1][1]
        arrow(draw, (x1 + 5, 1300), (x2 - 8, 1300), COLORS["gray_border"], width=5, head=18)

    cards = {
        0: [
            ("已有 Doris 小票明细", "fact_order_item\n会员/门店/SKU/金额/时间/折扣", "table"),
            ("门店基础表", "dim_store\n门店编码/城市/区域/状态", "table"),
            ("商品基础表", "dim_sku\n品类/SPU/规格/单位/品牌/存储/自加工", "table"),
            ("毛利损耗表", "dim_sku_margin_loss\n销售/毛利/损耗/折扣经营指标", "table"),
            ("门店商品日价格表", "门店+商品+日期\n采购/出库/售价/含税成本", "table"),
            ("久谦接口原始表", "竞品 API 原始返回\n批次/请求/原始 JSON", "table"),
            ("竞品 SKU 基础表", "稳定属性\n平台/城市/SKU/名称/规格/图片", "table"),
            ("竞品每日快照表", "每日变化\n价格/销量/评价/促销/覆盖门店", "table"),
        ],
        1: [
            ("会员画像算法", "时间行为/家庭规模/频次/价格态度", "job"),
            ("门店品类等级算法", "销售/客数/毛利/19点前/折扣/损耗", "job"),
            ("画像贡献算法", "门店群品类下画像销售与买家贡献", "job"),
            ("SKU表现算法", "目标画像下销售/客数/复购/时段/价格", "job"),
            ("价格带算法", "P25/P50/P75/加权成交价", "job"),
            ("购物篮关联算法", "FP-Growth/support/confidence/lift", "job"),
            ("竞品趋势算法", "价格/规格/销量/评价/趋势聚合", "job"),
            ("风险识别算法", "折扣/损耗/同质化/样本风险", "risk"),
        ],
        2: [
            ("会员画像标签表", "dim_customer_profile", "table"),
            ("门店品类等级表", "mart_store_category_level", "table"),
            ("画像贡献表", "mart_profile_contribution", "table"),
            ("目标画像 SKU 表现表", "mart_sku_behavior_by_profile", "table"),
            ("价格带表", "mart_price_band", "table"),
            ("购物篮关联表", "mart_basket_association", "table"),
            ("竞品趋势汇总表", "mart_competitor_summary", "table"),
            ("风险信号表", "mart_risk_signal", "table"),
        ],
        3: [
            ("① 新品候选方向生成", "画像/门店/SKU共性/价格带/竞品\n先生成品类、小类、规格、价格方向，属性按需补充", "engine"),
            ("② 新品机会评分", "需求/画像/门店/价格/竞品/经营可行性\n风险扣分，输出机会分与置信度", "engine"),
            ("③ 推荐结果存储", "mart_opportunity_recommendation\n推荐方向/证据/风险/试点动作", "table"),
        ],
        4: [
            ("采购使用入口", "工作台/表单/对话/混合形态待定", "app"),
            ("新品推荐结果", "商品方向/规格/口味/价格/证据/风险", "app"),
            ("采购Agent能力", "理解需求/查询结果/解释证据\n不直接替代算法计算", "app"),
            ("上海试点复盘", "新品销售/复购/毛利/损耗/采购反馈", "app"),
        ],
    }

    for idx, items in cards.items():
        _, x, w, _ = columns[idx]
        y = top + 120
        gap = 15
        available = bottom - y - 24
        card_h = (available - gap * (len(items) - 1)) / len(items)
        for title, body, kind in items:
            card(draw, (x + 16, y, x + w - 16, y + card_h), title, body, kind, title_size=24, body_size=18, pad=14)
            y += card_h + gap

    note_y = 2330
    rounded_box(draw, (70, note_y, 3130, 2420), COLORS["surface"], COLORS["line"], radius=16, width=2)
    draw_wrapped(
        draw,
        (100, note_y + 12, 3100, note_y + 78),
        "当前边界：小票已存在；基础数据只包含门店、商品、毛利损耗、日价格和久谦三张竞品表。商品小类可先用于识别即烹/即热，商品属性加工按后续分析需要决定。",
        font(23, medium=True),
        COLORS["text"],
        align="center",
        valign="center",
    )
    image.save(OUTPUT, quality=96)
    return OUTPUT


if __name__ == "__main__":
    print(build())
