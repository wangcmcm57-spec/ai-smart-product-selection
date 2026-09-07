# Doris 表字段清单：data_db

生成日期：2026-09-07

连接信息：

```text
Host：10.111.105.243
Port：9030
Database：data_db
Protocol：MySQL
User：root
Password：不记录
```

说明：字段清单来自 `information_schema.tables` 和 `information_schema.columns`；`TABLE_ROWS` 为 Doris 元数据返回值，仅作数据规模参考。

## 1. 表清单

| 序号 | 表名 | 类型 | 行数 | 数据量字节 | 表说明 | 创建时间 | 更新时间 | 字段数 |
|---:|---|---|---:|---:|---|---|---|---:|
| 1 | `dim_shop` | BASE TABLE | 5912 | 5555580 | 门店信息维度表 | 2026-07-21 10:52:26 | 2026-07-27 09:26:48 | 110 |
| 2 | `dim_shop_cbd` | BASE TABLE | 3097 | 2083358 | 门店商圈宽表 | 2026-07-16 17:07:59 | 2026-07-16 17:08:34 | 94 |
| 3 | `dim_sku` | BASE TABLE | 123352 | 51138600 | 商品基本信息表 | 2026-08-06 11:08:24 | 2026-08-18 16:04:33 | 112 |
| 4 | `dwd_date_shop` | BASE TABLE | 89438 | 89098048 | 门店日粒度指标宽表 | 2026-07-16 16:25:29 | 2026-07-16 16:26:44 | 235 |
| 5 | `dwd_date_shop_sku` | BASE TABLE | 101975051 | 14354129466 | 门店商品日粒度指标宽表（当日动销 SKU） | 2026-07-28 12:51:02 | 2026-08-05 21:14:49 | 72 |
| 6 | `dwd_date_shop_sku_monthly_backup_20260728` | BASE TABLE | 11847 | 3326506 | 门店商品日粒度指标宽表（当日动销 SKU） | 2026-07-26 10:27:00 | 2026-07-28 11:20:26 | 42 |
| 7 | `dwd_date_shop_sku_p20260630_backup_20260728` | BASE TABLE | 12311 | 3588956 | 门店商品日粒度指标宽表（当日动销 SKU） | 2026-07-28 17:09:19 | 2026-07-28 17:09:20 | 42 |
| 8 | `dwd_date_shop_sku_pre_full_switch_20260729` | BASE TABLE | 3660346 | 543952413 | 门店商品日粒度指标宽表（当日动销 SKU） | 2026-07-28 11:41:57 | 2026-07-28 17:09:46 | 42 |
| 9 | `dwd_date_shop_sku_qdm_brand` | BASE TABLE | 137884 | 35674690 | QDM品牌指定SKU门店商品日指标表 | 2026-08-05 23:48:34 | 2026-09-07 00:05:13 | 54 |
| 10 | `dwd_date_shop_sku_qdm_brand_static_backup_20260805234833` | BASE TABLE | 0 | 0 | QDM品牌指定SKU门店商品日指标表（2026年6月） | 2026-08-05 21:58:16 | 2026-08-05 21:58:16 | 53 |
| 11 | `dwd_date_shop_sku_qdm_brand_view` | VIEW | -1 | 0 |  | 2026-08-06 13:10:25 |  | 86 |

## 2. 字段清单

### dim_shop

表说明：门店信息维度表

| 序号 | 字段名 | 字段类型 | 是否可空 | 键类型 | 默认值 | 字段注释 |
|---:|---|---|---|---|---|---|
| 1 | `sp_store_id` | `varchar(64)` | YES | DUP |  | 中台门店编码 |
| 2 | `sp_store_name` | `varchar(255)` | YES |  |  | 门店名称 |
| 3 | `sp_type` | `varchar(20)` | YES |  |  | 门店类型 20加盟/10直营 |
| 4 | `sp_level` | `varchar(20)` | YES |  |  | BI店铺等级 |
| 5 | `dist_id` | `varchar(255)` | YES |  |  | 区县id |
| 6 | `dist_description` | `varchar(255)` | YES |  |  | 区县名称 |
| 7 | `city_id` | `varchar(20)` | YES |  |  | 城市id |
| 8 | `city_description` | `varchar(255)` | YES |  |  | 城市名称 |
| 9 | `pro_id` | `varchar(20)` | YES |  |  | 省份id |
| 10 | `pro_description` | `varchar(255)` | YES |  |  | 省份名称 |
| 11 | `area_id` | `varchar(20)` | YES |  |  | BI运营区域id |
| 12 | `area_description` | `varchar(255)` | YES |  |  | 运营区域名称 |
| 13 | `sp_purchasing_center_id` | `varchar(20)` | YES |  |  | 已弃用_采购中心id |
| 14 | `sp_company_id` | `varchar(20)` | YES |  |  | 归属公司 |
| 15 | `sp_purchasing_area` | `varchar(255)` | YES |  |  | 归属采购地区 |
| 16 | `sp_store_status` | `int(11)` | YES |  |  | BI店铺状态 |
| 17 | `sp_store_effective_date` | `varchar(50)` | YES |  |  | 已弃用_店铺生效日期 |
| 18 | `open_days` | `varchar(20)` | YES |  |  | 开业天数 |
| 19 | `sp_phone1` | `varchar(50)` | YES |  |  | 店长电话 |
| 20 | `sp_phone2` | `varchar(50)` | YES |  |  | 加盟主电话 |
| 21 | `sp_phone3` | `varchar(50)` | YES |  |  | 已弃用_加盟主姓名 |
| 22 | `sp_address` | `varchar(500)` | YES |  |  | 店铺地址 |
| 23 | `eblc_longitude` | `varchar(50)` | YES |  |  | TMS_经度 |
| 24 | `eblc_latitude` | `varchar(50)` | YES |  |  | TMS_纬度 |
| 25 | `sp_origin_start_date` | `varchar(50)` | YES |  |  | 原始开店日期 |
| 26 | `sp_final_end_date` | `varchar(50)` | YES |  |  | 原始闭店日期 |
| 27 | `group_manager_code` | `varchar(50)` | YES |  |  | 督导id |
| 28 | `group_manager` | `varchar(255)` | YES |  |  | 督导姓名 |
| 29 | `sp_scale` | `varchar(20)` | YES |  |  | 店型 |
| 30 | `sp_rsv_status` | `varchar(20)` | YES |  |  | 已弃用_备用状态 |
| 31 | `sp_sign_date` | `varchar(50)` | YES |  |  | 签铺日期 |
| 32 | `sp_table_flag` | `varchar(20)` | YES |  |  | 门店类型标志 |
| 33 | `sp_closed_reason` | `varchar(20)` | YES |  |  | 闭店原因id |
| 34 | `sp_currency` | `varchar(20)` | YES |  |  | 币种 |
| 35 | `sp_master_area` | `varchar(20)` | YES |  |  | 已弃用_主档区域 |
| 36 | `op_area_id` | `varchar(20)` | YES |  |  | 已弃用_运营区域id |
| 37 | `total_area` | `decimalv3(19, 4)` | YES |  |  | 门店面积大小 |
| 38 | `area_description_alias` | `varchar(255)` | YES |  |  | 已弃用_运营区域名称别名 |
| 39 | `new_sp_store_id` | `varchar(64)` | YES |  |  | SAP门店编号 |
| 40 | `new_sp_store_name` | `varchar(255)` | YES |  |  | 门店名称 |
| 41 | `mandt` | `varchar(20)` | YES |  |  | 集团 |
| 42 | `zone_manager` | `varchar(255)` | YES |  |  | 运营主管 |
| 43 | `zone_id` | `varchar(50)` | YES |  |  | 运营主管编码 |
| 44 | `opera_manager` | `varchar(255)` | YES |  |  | 已弃用_大区经理 |
| 45 | `opera_id` | `varchar(50)` | YES |  |  | 已弃用_大区经理编码 |
| 46 | `new_sp_level` | `varchar(20)` | YES |  |  | 门店类型标志 |
| 47 | `group_manager_tel` | `varchar(50)` | YES |  |  | 督导电话 |
| 48 | `transfer_date` | `varchar(50)` | YES |  |  | 转让日期 |
| 49 | `transfer_store_id` | `varchar(64)` | YES |  |  | 转让后门店编码 |
| 50 | `stop_start_date` | `varchar(50)` | YES |  |  | 停业开始日期 |
| 51 | `stop_end_date` | `varchar(50)` | YES |  |  | 停业结束日期 |
| 52 | `stop_reason_id` | `varchar(20)` | YES |  |  | 停业原因code |
| 53 | `stop_reason` | `varchar(255)` | YES |  |  | 停业原因 |
| 54 | `restart_date` | `varchar(50)` | YES |  |  | 重开业日期 |
| 55 | `business_area` | `varchar(255)` | YES |  |  | 所在商圈 |
| 56 | `area_id_sap` | `varchar(20)` | YES |  |  | 运营区域编码 |
| 57 | `area_id_purchase` | `varchar(20)` | YES |  |  | 已弃用_采购原逻辑纬度 |
| 58 | `operate_id_purchase` | `varchar(20)` | YES |  |  | 已弃用_采购门店逻辑纬度 |
| 59 | `area2_id` | `varchar(20)` | YES |  |  | BI销售区域ID |
| 60 | `area2_name` | `varchar(255)` | YES |  |  | 运营大区名称 |
| 61 | `area2_id_sap` | `varchar(50)` | YES |  |  | 运营大区编码 |
| 62 | `operate_name_purchase` | `varchar(255)` | YES |  |  | 已弃用_采购地区名称 |
| 63 | `zone_supper_manager` | `varchar(255)` | YES |  |  | 运营经理 |
| 64 | `zone_supper_id` | `varchar(50)` | YES |  |  | 运营经理ID |
| 65 | `zone_supper_phone` | `varchar(50)` | YES |  |  | 运营经理电话 |
| 66 | `zone_phone` | `varchar(50)` | YES |  |  | 运营主管电话 |
| 67 | `franchisee_id` | `varchar(50)` | YES |  |  | 加盟商编码 |
| 68 | `zzlksrq` | `varchar(50)` | YES |  |  | 租赁开始日期 |
| 69 | `zzljsrq` | `varchar(50)` | YES |  |  | 租赁结束日期 |
| 70 | `area_type` | `varchar(255)` | YES |  |  | 已弃用_区域种类 |
| 71 | `measuring_area` | `decimalv3(19, 4)` | YES |  |  | 量尺面积 |
| 72 | `franchisee_name` | `varchar(255)` | YES |  |  | 加盟商姓名 |
| 73 | `stop_reason_apply` | `varchar(5000)` | YES |  |  | 申请闭店原因 |
| 74 | `old_id` | `varchar(64)` | YES |  |  | 已弃用_旧门店编码 |
| 75 | `contract_franchisee_id` | `varchar(50)` | YES |  |  | 签约加盟商编码 |
| 76 | `contract_franchisee_name` | `varchar(255)` | YES |  |  | 签约加盟商名称 |
| 77 | `contract_franchisee_phone` | `varchar(50)` | YES |  |  | 签约加盟商电话 |
| 78 | `expand_staff_id` | `varchar(50)` | YES |  |  | 拓展员工编码 |
| 79 | `expand_staff_name` | `varchar(255)` | YES |  |  | 拓展员工姓名 |
| 80 | `new_sp_level_name` | `varchar(255)` | YES |  |  | 店铺等级名称 |
| 81 | `target_sales_amt` | `decimalv3(19, 4)` | YES |  |  | 全天销售目标 |
| 82 | `target_bf19_cust_num` | `int(11)` | YES |  |  | 19点前客流目标 |
| 83 | `target_cust_num` | `int(11)` | YES |  |  | 全天客流目标 |
| 84 | `targer_allowance_profit` | `decimalv3(19, 4)` | YES |  |  | 补贴后毛利额目标 |
| 85 | `price_strategy_start_date` | `date` | YES |  |  | 2023定价策略开始日期 |
| 86 | `sap_store_status_id` | `varchar(20)` | YES |  |  | SAP门店状态编码 |
| 87 | `sap_store_status_name` | `varchar(255)` | YES |  |  | SAP门店状态名称 |
| 88 | `store_type_name` | `varchar(255)` | YES |  |  | 门店类型名称 |
| 89 | `store_flag_name` | `varchar(255)` | YES |  |  | 门店类型标志名称 |
| 90 | `closed_reason_name` | `varchar(255)` | YES |  |  | 闭店原因 |
| 91 | `manage_area_id` | `varchar(50)` | YES |  |  | 管理区域编码 |
| 92 | `manage_area_name` | `varchar(255)` | YES |  |  | 管理区域名称 |
| 93 | `region_id` | `varchar(50)` | YES |  |  | 片区编码 |
| 94 | `region_name` | `varchar(255)` | YES |  |  | 片区名称 |
| 95 | `store_guide_user` | `varchar(255)` | YES |  |  | 带店人 |
| 96 | `sap_area_id` | `varchar(50)` | YES |  |  | 运营区域编码 |
| 97 | `sap_area_name` | `varchar(255)` | YES |  |  | 运营区域名称 |
| 98 | `sap_area2_id` | `varchar(50)` | YES |  |  | 销售区域编码 |
| 99 | `sap_area2_name` | `varchar(255)` | YES |  |  | 销售区域名称 |
| 100 | `bunk_id` | `varchar(100)` | YES |  |  | 铺位id |
| 101 | `store_service_range` | `varchar(500)` | YES |  |  | 门店业务开通编码 |
| 102 | `store_service_name` | `varchar(500)` | YES |  |  | 门店业务开通名称 |
| 103 | `mall_supervisor_phone` | `varchar(50)` | YES |  |  | 电商督导电话 |
| 104 | `mall_supervisor_name` | `varchar(255)` | YES |  |  | 电商督导名称 |
| 105 | `zman_id` | `varchar(50)` | YES |  |  | 管理方式编码 |
| 106 | `zman_name` | `varchar(255)` | YES |  |  | 管理方式名称 |
| 107 | `original_store_id` | `varchar(64)` | YES |  |  | 转店前最原始门店编码 |
| 108 | `dt` | `date` | YES |  |  | 日分区 |
| 109 | `pt` | `varchar(20)` | YES |  |  | 区域 |
| 110 | `store_layer` | `varchar(20)` | YES |  |  | 门店分层(头部/中上/中下/尾部/未参与分层) |

### dim_shop_cbd

表说明：门店商圈宽表

| 序号 | 字段名 | 字段类型 | 是否可空 | 键类型 | 默认值 | 字段注释 |
|---:|---|---|---|---|---|---|
| 1 | `shop_id` | `varchar(64)` | NO | UNI |  | 门店ID |
| 2 | `city_code` | `varchar(255)` | YES |  |  | 城市编码 |
| 3 | `city_name` | `varchar(255)` | YES |  |  | 城市名称 |
| 4 | `point_name` | `varchar(255)` | YES |  |  | 商圈点位名称 |
| 5 | `werks` | `varchar(255)` | YES |  |  | 工厂编码 |
| 6 | `store_name` | `varchar(255)` | YES |  |  | 门店名称 |
| 7 | `shop_name` | `varchar(255)` | YES |  |  | 店铺名称 |
| 8 | `report_name` | `varchar(255)` | YES |  |  | 报告名称 |
| 9 | `report_date` | `varchar(255)` | YES |  |  | 报告版本或日期标识 |
| 10 | `region_area` | `decimalv3(19, 4)` | YES |  |  | 商圈区域占比 |
| 11 | `resident_or_flow` | `bigint(20)` | YES |  |  | 常住或流动人口数 |
| 12 | `report_id` | `bigint(20)` | YES |  |  | 报告ID |
| 13 | `resident_population` | `bigint(20)` | YES |  |  | 常住人口数 |
| 14 | `daily_passenger_flow` | `bigint(20)` | YES |  |  | 日均客流量 |
| 15 | `wealth_city_level_mid_num` | `decimalv3(19, 4)` | YES |  |  | 财富城市中等人数占比 |
| 16 | `wealth_city_level_low_num` | `decimalv3(19, 4)` | YES |  |  | 财富城市低等人数占比 |
| 17 | `wealth_city_level_sublow_num` | `decimalv3(19, 4)` | YES |  |  | 财富城市次低等人数占比 |
| 18 | `wealth_city_level_subhigh_num` | `decimalv3(19, 4)` | YES |  |  | 财富城市次高等人数占比 |
| 19 | `wealth_city_level_high_num` | `decimalv3(19, 4)` | YES |  |  | 财富城市高等人数占比 |
| 20 | `wealth_city_level_mid_tgi` | `decimalv3(19, 4)` | YES |  |  | 财富城市中等TGI |
| 21 | `wealth_city_level_low_tgi` | `decimalv3(19, 4)` | YES |  |  | 财富城市低等TGI |
| 22 | `wealth_city_level_sublow_tgi` | `decimalv3(19, 4)` | YES |  |  | 财富城市次低等TGI |
| 23 | `wealth_city_level_subhigh_tgi` | `decimalv3(19, 4)` | YES |  |  | 财富城市次高等TGI |
| 24 | `wealth_city_level_high_tgi` | `decimalv3(19, 4)` | YES |  |  | 财富城市高等TGI |
| 25 | `child_age_0_2_num` | `decimalv3(19, 4)` | YES |  |  | 子女人群 0至2 人数占比 |
| 26 | `child_age_13_18_num` | `decimalv3(19, 4)` | YES |  |  | 子女人群 13至18 人数占比 |
| 27 | `child_age_3_5_num` | `decimalv3(19, 4)` | YES |  |  | 子女人群 3至5 人数占比 |
| 28 | `child_age_6_12_num` | `decimalv3(19, 4)` | YES |  |  | 子女人群 6至12 人数占比 |
| 29 | `child_age_none_num` | `decimalv3(19, 4)` | YES |  |  | 子女人群 none 人数占比 |
| 30 | `child_age_0_2_tgi` | `decimalv3(19, 4)` | YES |  |  | 子女人群 0至2 TGI |
| 31 | `child_age_13_18_tgi` | `decimalv3(19, 4)` | YES |  |  | 子女人群 13至18 TGI |
| 32 | `child_age_3_5_tgi` | `decimalv3(19, 4)` | YES |  |  | 子女人群 3至5 TGI |
| 33 | `child_age_6_12_tgi` | `decimalv3(19, 4)` | YES |  |  | 子女人群 6至12 TGI |
| 34 | `child_age_none_tgi` | `decimalv3(19, 4)` | YES |  |  | 子女人群 none TGI |
| 35 | `age_0_17_num` | `decimalv3(19, 4)` | YES |  |  | 年龄 0至17 人数占比 |
| 36 | `age_18_24_num` | `decimalv3(19, 4)` | YES |  |  | 年龄 18至24 人数占比 |
| 37 | `age_25_30_num` | `decimalv3(19, 4)` | YES |  |  | 年龄 25至30 人数占比 |
| 38 | `age_31_35_num` | `decimalv3(19, 4)` | YES |  |  | 年龄 31至35 人数占比 |
| 39 | `age_36_40_num` | `decimalv3(19, 4)` | YES |  |  | 年龄 36至40 人数占比 |
| 40 | `age_41_45_num` | `decimalv3(19, 4)` | YES |  |  | 年龄 41至45 人数占比 |
| 41 | `age_46_60_num` | `decimalv3(19, 4)` | YES |  |  | 年龄 46至60 人数占比 |
| 42 | `age_61_plus_num` | `decimalv3(19, 4)` | YES |  |  | 年龄 61至plus 人数占比 |
| 43 | `age_0_17_tgi` | `decimalv3(19, 4)` | YES |  |  | 年龄 0至17 TGI |
| 44 | `age_18_24_tgi` | `decimalv3(19, 4)` | YES |  |  | 年龄 18至24 TGI |
| 45 | `age_25_30_tgi` | `decimalv3(19, 4)` | YES |  |  | 年龄 25至30 TGI |
| 46 | `age_31_35_tgi` | `decimalv3(19, 4)` | YES |  |  | 年龄 31至35 TGI |
| 47 | `age_36_40_tgi` | `decimalv3(19, 4)` | YES |  |  | 年龄 36至40 TGI |
| 48 | `age_41_45_tgi` | `decimalv3(19, 4)` | YES |  |  | 年龄 41至45 TGI |
| 49 | `age_46_60_tgi` | `decimalv3(19, 4)` | YES |  |  | 年龄 46至60 TGI |
| 50 | `age_61_plus_tgi` | `decimalv3(19, 4)` | YES |  |  | 年龄 61至plus TGI |
| 51 | `work_home_dist_1km_num` | `decimalv3(19, 4)` | YES |  |  | 工作地居住地距离 1km 人数占比 |
| 52 | `work_home_dist_1_3km_num` | `decimalv3(19, 4)` | YES |  |  | 工作地居住地距离 1至3km 人数占比 |
| 53 | `work_home_dist_3_5km_num` | `decimalv3(19, 4)` | YES |  |  | 工作地居住地距离 3至5km 人数占比 |
| 54 | `work_home_dist_5_10km_num` | `decimalv3(19, 4)` | YES |  |  | 工作地居住地距离 5至10km 人数占比 |
| 55 | `work_home_dist_10_15km_num` | `decimalv3(19, 4)` | YES |  |  | 工作地居住地距离 10至15km 人数占比 |
| 56 | `work_home_dist_15_25km_num` | `decimalv3(19, 4)` | YES |  |  | 工作地居住地距离 15至25km 人数占比 |
| 57 | `work_home_dist_25_40km_num` | `decimalv3(19, 4)` | YES |  |  | 工作地居住地距离 25至40km 人数占比 |
| 58 | `work_home_dist_1km_tgi` | `decimalv3(19, 4)` | YES |  |  | 工作地居住地距离 1km TGI |
| 59 | `work_home_dist_1_3km_tgi` | `decimalv3(19, 4)` | YES |  |  | 工作地居住地距离 1至3km TGI |
| 60 | `work_home_dist_3_5km_tgi` | `decimalv3(19, 4)` | YES |  |  | 工作地居住地距离 3至5km TGI |
| 61 | `work_home_dist_5_10km_tgi` | `decimalv3(19, 4)` | YES |  |  | 工作地居住地距离 5至10km TGI |
| 62 | `work_home_dist_10_15km_tgi` | `decimalv3(19, 4)` | YES |  |  | 工作地居住地距离 10至15km TGI |
| 63 | `work_home_dist_15_25km_tgi` | `decimalv3(19, 4)` | YES |  |  | 工作地居住地距离 15至25km TGI |
| 64 | `work_home_dist_25_40km_tgi` | `decimalv3(19, 4)` | YES |  |  | 工作地居住地距离 25至40km TGI |
| 65 | `catering_freq_1_2_num` | `decimalv3(19, 4)` | YES |  |  | 每周就餐频次 1至2 人数占比 |
| 66 | `catering_freq_3_4_num` | `decimalv3(19, 4)` | YES |  |  | 每周就餐频次 3至4 人数占比 |
| 67 | `catering_freq_5_6_num` | `decimalv3(19, 4)` | YES |  |  | 每周就餐频次 5至6 人数占比 |
| 68 | `catering_freq_7_8_num` | `decimalv3(19, 4)` | YES |  |  | 每周就餐频次 7至8 人数占比 |
| 69 | `catering_freq_9_10_num` | `decimalv3(19, 4)` | YES |  |  | 每周就餐频次 9至10 人数占比 |
| 70 | `catering_freq_11_plus_num` | `decimalv3(19, 4)` | YES |  |  | 每周就餐频次 11至plus 人数占比 |
| 71 | `catering_freq_1_2_tgi` | `decimalv3(19, 4)` | YES |  |  | 每周就餐频次 1至2 TGI |
| 72 | `catering_freq_3_4_tgi` | `decimalv3(19, 4)` | YES |  |  | 每周就餐频次 3至4 TGI |
| 73 | `catering_freq_5_6_tgi` | `decimalv3(19, 4)` | YES |  |  | 每周就餐频次 5至6 TGI |
| 74 | `catering_freq_7_8_tgi` | `decimalv3(19, 4)` | YES |  |  | 每周就餐频次 7至8 TGI |
| 75 | `catering_freq_9_10_tgi` | `decimalv3(19, 4)` | YES |  |  | 每周就餐频次 9至10 TGI |
| 76 | `catering_freq_11_plus_tgi` | `decimalv3(19, 4)` | YES |  |  | 每周就餐频次 11至plus TGI |
| 77 | `married_num` | `decimalv3(19, 4)` | YES |  |  | 已婚人数占比 |
| 78 | `unmarried_num` | `decimalv3(19, 4)` | YES |  |  | 未婚人数占比 |
| 79 | `married_tgi` | `decimalv3(19, 4)` | YES |  |  | 已婚TGI |
| 80 | `unmarried_tgi` | `decimalv3(19, 4)` | YES |  |  | 未婚TGI |
| 81 | `business_traveler_yes_num` | `decimalv3(19, 4)` | YES |  |  | 商务出行人群占比 |
| 82 | `business_traveler_no_num` | `decimalv3(19, 4)` | YES |  |  | 非商务出行人群占比 |
| 83 | `business_traveler_yes_tgi` | `decimalv3(19, 4)` | YES |  |  | 商务出行人群TGI |
| 84 | `business_traveler_no_tgi` | `decimalv3(19, 4)` | YES |  |  | 非商务出行人群TGI |
| 85 | `life_stage_office_num` | `decimalv3(19, 4)` | YES |  |  | 职场人群占比 |
| 86 | `life_stage_middle_school_num` | `decimalv3(19, 4)` | YES |  |  | 中学生人群占比 |
| 87 | `life_stage_college_num` | `decimalv3(19, 4)` | YES |  |  | 大学生人群占比 |
| 88 | `life_stage_freelance_num` | `decimalv3(19, 4)` | YES |  |  | 自由职业人群占比 |
| 89 | `life_stage_retired_num` | `decimalv3(19, 4)` | YES |  |  | 退休人群占比 |
| 90 | `life_stage_office_tgi` | `decimalv3(19, 4)` | YES |  |  | 职场人群TGI |
| 91 | `life_stage_middle_school_tgi` | `decimalv3(19, 4)` | YES |  |  | 中学生人群TGI |
| 92 | `life_stage_college_tgi` | `decimalv3(19, 4)` | YES |  |  | 大学生人群TGI |
| 93 | `life_stage_freelance_tgi` | `decimalv3(19, 4)` | YES |  |  | 自由职业人群TGI |
| 94 | `life_stage_retired_tgi` | `decimalv3(19, 4)` | YES |  |  | 退休人群TGI |

### dim_sku

表说明：商品基本信息表

| 序号 | 字段名 | 字段类型 | 是否可空 | 键类型 | 默认值 | 字段注释 |
|---:|---|---|---|---|---|---|
| 1 | `article_id` | `varchar(355)` | YES | UNI |  | 商品编码 |
| 2 | `article_name` | `string` | YES |  |  | 商品名称 |
| 3 | `category_level3_id` | `string` | YES |  |  | 小类编码id |
| 4 | `category_level3_description` | `string` | YES |  |  | 小类编码名称 |
| 5 | `category_level2_id` | `string` | YES |  |  | 中编码id |
| 6 | `category_level2_description` | `string` | YES |  |  | 中类编码名称 |
| 7 | `category_level1_id` | `string` | YES |  |  | 大类编码id |
| 8 | `category_level1_description` | `string` | YES |  |  | 大类编码名称 |
| 9 | `sales_unit_id` | `string` | YES |  |  | 销售单位id |
| 10 | `sale_unit` | `string` | YES |  |  | 销售单位 |
| 11 | `order_unit_id` | `string` | YES |  |  | 订购单位id |
| 12 | `order_unit` | `string` | YES |  |  | 订购单位 |
| 13 | `brand` | `string` | YES |  |  | 品牌 |
| 14 | `product_address` | `string` | YES |  |  | 华南产地 |
| 15 | `norms` | `string` | YES |  |  | 规格 |
| 16 | `logistics_process_tag` | `string` | YES |  |  | 是否物流加工 |
| 17 | `logistics_scrap_tag` | `string` | YES |  |  | 是否物流报废 |
| 18 | `online_tag` | `string` | YES |  |  | 电商商品标识 销售渠道应该可以标识线上线下？ |
| 19 | `private` | `string` | YES |  |  | 保质期 |
| 20 | `barcode` | `string` | YES |  |  | 商品条码 |
| 21 | `min_order_unit` | `string` | YES |  |  | 最小订购单元 |
| 22 | `min_order_times` | `string` | YES |  |  | 最小订购倍数 |
| 23 | `max_order_times` | `string` | YES |  |  | 最大订购倍数 |
| 24 | `xx_sl` | `string` | YES |  |  | 销项税率 |
| 25 | `jx_sl` | `string` | YES |  |  | 进项税率 |
| 26 | `order_frequency` | `string` | YES |  |  | 订购频率 |
| 27 | `status_code` | `string` | YES |  |  | 状态编码 |
| 28 | `commodity_attribute` | `string` | YES |  |  | 商品属性:01 正常商品，02 W商品，03 大妈工坊商品 |
| 29 | `load_time` | `string` | YES |  |  | 数据更新时间 |
| 30 | `life_cycle` | `string` | YES |  |  | 生命周期 |
| 31 | `unit_weight` | `double` | YES |  |  | 单位重量 |
| 32 | `onlineshop_flag` | `string` | YES |  |  | 是否线上店 |
| 33 | `offlineshop_flag` | `string` | YES |  |  | 是否线下店 |
| 34 | `vegetablebar_flag` | `string` | YES |  |  | 是否菜吧 |
| 35 | `package_attribute` | `string` | YES |  |  | 包装属性 |
| 36 | `type` | `string` | YES |  |  | 商品属性 |
| 37 | `article_type` | `string` | YES |  |  | 商品类型 |
| 38 | `weight_flag` | `string` | YES |  |  | 称重标识 |
| 39 | `commodity_attribute_name` | `string` | YES |  |  | 商品属性名称 |
| 40 | `package_attribute_name` | `string` | YES |  |  | 包装属性名称 |
| 41 | `status_name` | `string` | YES |  |  | 状态编码名称 |
| 42 | `type_name` | `string` | YES |  |  | 商品区分名称 |
| 43 | `abi_volume_ratio` | `double` | YES |  |  | 体重比 |
| 44 | `abi_purchasecategory_id` | `string` | YES |  |  | 采购小分类 |
| 45 | `abi_srmcategory` | `bigint(20)` | YES |  |  | SRM小分类 |
| 46 | `abi_quality_days` | `bigint(20)` | YES |  |  | 保质天数 |
| 47 | `abi_outer_packing_spec` | `string` | YES |  |  | 外包装规格 |
| 48 | `abi_create_reason` | `string` | YES |  |  | 创建原因 |
| 49 | `abi_outer_packing_lwh` | `string` | YES |  |  | 外包装长宽高 |
| 50 | `abi_purchase_group` | `string` | YES |  |  | 采购组 |
| 51 | `abi_new_category_id` | `string` | YES |  |  | 商品新小分类 |
| 52 | `old_article_id` | `string` | YES |  |  | old_商品编码 |
| 53 | `old_article_name` | `string` | YES |  |  | old_商品名称 |
| 54 | `old_category_level3_id` | `string` | YES |  |  | old_小类编码id |
| 55 | `old_category_level3_description` | `string` | YES |  |  | old_小类编码名称 |
| 56 | `old_category_level2_id` | `string` | YES |  |  | old_中编码id |
| 57 | `old_category_level2_description` | `string` | YES |  |  | old_中类编码名称 |
| 58 | `old_category_level1_id` | `string` | YES |  |  | 大类编码id |
| 59 | `old_category_level1_description` | `string` | YES |  |  | old_大类编码名称 |
| 60 | `article_matnr` | `string` | YES |  |  | 物料编号 |
| 61 | `matnr_unit_id` | `string` | YES |  |  | 物料的基本计量单位id |
| 62 | `matnr_unit` | `string` | YES |  |  | 物料的基本计量单位 |
| 63 | `zglfz` | `double` | YES |  |  | 基本计量单位转换分子 |
| 64 | `zglfm` | `double` | YES |  |  | 转换为基本计量单位的分母 |
| 65 | `sp_info` | `string` | YES |  |  | 储存条件温度 |
| 66 | `mtart` | `string` | YES |  |  | Z001商品,Z002物料,Z003虚拟商品 |
| 67 | `in_date` | `string` | YES |  |  | 生效时间 |
| 68 | `create_date1` | `string` | YES |  |  | 创建时间 |
| 69 | `out_date` | `string` | YES |  |  | 失效时间 |
| 70 | `matnr` | `string` | YES |  |  | 物料号 |
| 71 | `abi_purchase_group_name` | `string` | YES |  |  | 采购小组名称 |
| 72 | `sp_info_name` | `string` | YES |  |  | 储存条件文本 |
| 73 | `brand_id` | `string` | YES |  |  | 品牌编码 |
| 74 | `sale_areas` | `string` | YES |  |  | 销售区域 |
| 75 | `use_types` | `string` | YES |  |  | 使用类型 |
| 76 | `resent_use_date` | `string` | YES |  |  | 最近使用日期 |
| 77 | `matnr_in_date` | `string` | YES |  |  | 物料创建时间 |
| 78 | `purchase_department` | `string` | YES |  |  | 采购部门 |
| 79 | `purchase_department_id` | `string` | YES |  |  | 采购部门编号 |
| 80 | `min_pack_weight` | `double` | YES |  |  | 最小包装重 |
| 81 | `shelf_time` | `string` | YES |  |  | 可上架时段 |
| 82 | `freeze_id` | `string` | YES |  |  | 冻结标识 |
| 83 | `atob_value` | `string` | YES |  |  | 标记是否A进B出商品编码值 |
| 84 | `atob_name` | `string` | YES |  |  | 标记是否A进B出商品名称 |
| 85 | `relation_matnr` | `string` | YES |  |  | 关联商品码 为SPU的上级 |
| 86 | `matnr_name` | `string` | YES |  |  | 物料描述 |
| 87 | `article_belong_id` | `string` | YES |  |  | 商品归属编码 |
| 88 | `article_belong_name` | `string` | YES |  |  | 商品归属名称 |
| 89 | `if_settle_unit` | `int(11)` | YES |  |  | 是否结算单位 1是 0否 |
| 90 | `superior_purchase_department_id` | `string` | YES |  |  | 采购商品部门上级编码 |
| 91 | `superior_purchase_department_name` | `string` | YES |  |  | 采购商品部门上级名称 |
| 92 | `category_material_label_id` | `string` | YES |  |  | 商品大类归属编码 |
| 93 | `category_material_label_name` | `string` | YES |  |  | 商品大类归属名称 |
| 94 | `spu_id` | `string` | YES |  |  | spu编码 |
| 95 | `spu_name` | `string` | YES |  |  | spu名称 |
| 96 | `article_series_id` | `string` | YES |  |  | 商品系列编码 |
| 97 | `article_series_name` | `string` | YES |  |  | 商品系列名称 |
| 98 | `temperature_layer_id` | `string` | YES |  |  | 温层编码 |
| 99 | `temperature_layer_name` | `string` | YES |  |  | 温层名称 |
| 100 | `import_flag` | `string` | YES |  |  | 进口标识 1进口 0国产 |
| 101 | `blackwhite_pig_id` | `string` | YES |  |  | 黑白猪编码 01黑猪 02白猪 |
| 102 | `blackwhite_pig_name` | `string` | YES |  |  | 黑白猪名称 |
| 103 | `norms_lower_limit` | `double` | YES |  |  | 规格下限 |
| 104 | `norms_upper_limit` | `double` | YES |  |  | 规格上限 |
| 105 | `inc_day` | `string` | YES |  |  | 增量日期 |
| 106 | `update_time` | `string` | YES |  |  | 更新时间 |
| 107 | `zcplx` | `string` | YES |  |  | EAN主档产品类型编码，来源ods_sap.zmmt002.zcplx |
| 108 | `zcplx_name` | `string` | YES |  |  | EAN主档产品类型名称，A67: 1=SC加工类, 2=生鲜类 |
| 109 | `is_process_product` | `int(11)` | YES |  |  | 是否加工商品，1是，0否，null未知 |
| 110 | `zzmarayl1` | `string` | YES |  |  | 商品主档标品编码，来源ods_sap.mara.zzmarayl1 |
| 111 | `zzmarayl1_name` | `string` | YES |  |  | 商品主档标品名称，A43: 1=是, 0=否 |
| 112 | `is_standard_product` | `int(11)` | YES |  |  | 是否标品，1是，0否，null未知 |

### dwd_date_shop

表说明：门店日粒度指标宽表

| 序号 | 字段名 | 字段类型 | 是否可空 | 键类型 | 默认值 | 字段注释 |
|---:|---|---|---|---|---|---|
| 1 | `dt` | `date` | NO | UNI |  | 营业日期 |
| 2 | `shop_id` | `varchar(64)` | NO | UNI |  | 门店 ID |
| 3 | `shop_name` | `varchar(255)` | NO |  |  | 门店名称 |
| 4 | `bf19_member_cust_num` | `bigint(20)` | YES |  |  | 19点前会员客数 |
| 5 | `bf19_member_num` | `bigint(20)` | YES |  |  | 19点前会员数 |
| 6 | `bf19_member_sale_amt` | `decimalv3(19, 4)` | YES |  |  | 19点前会员销售额 |
| 7 | `bf19_per_cust_amt` | `decimalv3(19, 4)` | YES |  |  | 19点前客单价 |
| 8 | `bf19_cust_num` | `bigint(20)` | YES |  |  | 19点前客数 |
| 9 | `bf19_usual_cust_num` | `bigint(20)` | YES |  |  | 19点前有效客数 |
| 10 | `bf19_online_member_cust_num` | `bigint(20)` | YES |  |  | 19点前线上会员客数 |
| 11 | `bf19_offline_member_cust_num` | `bigint(20)` | YES |  |  | 19点前线下会员客数 |
| 12 | `bf19_offline_cust_num` | `bigint(20)` | YES |  |  | 19点前线下客数 |
| 13 | `bf19_offline_sale_qty` | `decimalv3(19, 4)` | YES |  |  | 19点前线下销售数量 |
| 14 | `bf19_offline_sale_amt` | `decimalv3(19, 4)` | YES |  |  | 19点前线下销售额 |
| 15 | `bf19_sale_piece` | `bigint(20)` | YES |  |  | 19点前销售件数 |
| 16 | `bf19_sale_rate` | `decimalv3(19, 6)` | YES |  |  | 19点前销售占比 |
| 17 | `bf19_sale_qty` | `decimalv3(19, 4)` | YES |  |  | 19点前销售数量 |
| 18 | `bf19_sale_weight` | `decimalv3(19, 4)` | YES |  |  | 19点前销售重量 |
| 19 | `bf19_sale_amt` | `decimalv3(19, 4)` | YES |  |  | 19点前销售额 |
| 20 | `bf19_shop_promotion_rate` | `decimalv3(19, 6)` | YES |  |  | 19点前门店发起促销折扣率 |
| 21 | `bf19_shop_promotion_amt` | `decimalv3(19, 4)` | YES |  |  | 19点前门店发起促销折扣额 |
| 22 | `af19_member_num` | `bigint(20)` | YES |  |  | 19点后会员数 |
| 23 | `af19_per_cust_amt` | `decimalv3(19, 4)` | YES |  |  | 19点后客单价 |
| 24 | `af19_cust_num` | `bigint(20)` | YES |  |  | 19点后客数 |
| 25 | `af19_custom_num` | `bigint(20)` | YES |  |  | 19点后用户数 |
| 26 | `af19_offline_cust_num` | `bigint(20)` | YES |  |  | 19点后线下客数 |
| 27 | `af19_offline_sale_amt` | `decimalv3(19, 4)` | YES |  |  | 19点后线下销售额 |
| 28 | `af19_sale_qty` | `decimalv3(19, 4)` | YES |  |  | 19点后销售数量 |
| 29 | `af19_sale_weight` | `decimalv3(19, 4)` | YES |  |  | 19点后销售重量 |
| 30 | `af19_sale_amt` | `decimalv3(19, 4)` | YES |  |  | 19点后销售额 |
| 31 | `franchisee_per_stores` | `bigint(20)` | YES |  |  | 人均持店数 |
| 32 | `promotion_amt` | `decimalv3(19, 4)` | YES |  |  | 优惠金额 |
| 33 | `trans_times` | `decimalv3(19, 4)` | YES |  |  | 会员人均交易频次 |
| 34 | `per_member_amt` | `decimalv3(19, 4)` | YES |  |  | 会员人均销售额 |
| 35 | `member_coupon_store_amt` | `decimalv3(19, 4)` | YES |  |  | 会员券（门店） |
| 36 | `repurchase_member_trans_times` | `bigint(20)` | YES |  |  | 会员复购次数 |
| 37 | `per_member_cust_amt` | `decimalv3(19, 4)` | YES |  |  | 会员客单价 |
| 38 | `member_cust_num` | `bigint(20)` | YES |  |  | 会员客数 |
| 39 | `member_cust_rate` | `decimalv3(19, 6)` | YES |  |  | 会员客数占比 |
| 40 | `member_discount_rate` | `decimalv3(19, 6)` | YES |  |  | 会员折扣率 |
| 41 | `member_discount_amt` | `decimalv3(19, 4)` | YES |  |  | 会员折扣额 |
| 42 | `member_sale_amt` | `decimalv3(19, 4)` | YES |  |  | 会员销售额 |
| 43 | `balance_pay_amt` | `decimalv3(19, 4)` | YES |  |  | 余额支付金额 |
| 44 | `vendor_bear_cost` | `decimalv3(19, 4)` | YES |  |  | 供应商承担优惠金额 |
| 45 | `vender_bear_amt_total` | `decimalv3(19, 4)` | YES |  |  | 供应商承担让利金额（含集采仓） |
| 46 | `vender_bear_gift_qty` | `decimalv3(19, 4)` | YES |  |  | 供应商承担赠品让利数量（含集采仓） |
| 47 | `vender_bear_gift_amt` | `decimalv3(19, 4)` | YES |  |  | 供应商承担赠品让利金额（含集采仓） |
| 48 | `vendor_bear_nogift_amt` | `decimalv3(19, 4)` | YES |  |  | 供应商承担非赠品让利金额 |
| 49 | `scm_store_profit_rate` | `decimalv3(19, 6)` | YES |  |  | 供应链到店毛利率 |
| 50 | `scm_store_profit_notax_rate` | `decimalv3(19, 6)` | YES |  |  | 供应链到店毛利率（不含税） |
| 51 | `scm_store_profit_amt` | `decimalv3(19, 4)` | YES |  |  | 供应链到店毛利额 |
| 52 | `scm_store_profit_amt_notax` | `decimalv3(19, 4)` | YES |  |  | 供应链到店毛利额（不含税） |
| 53 | `scm_store_profit_proportion` | `decimalv3(19, 4)` | YES |  |  | 供应链门店毛利配比 |
| 54 | `promotion_discount_rate` | `decimalv3(19, 6)` | YES |  |  | 促销折扣率 |
| 55 | `promotion_discount_amt` | `decimalv3(19, 4)` | YES |  |  | 促销折扣额 |
| 56 | `stop_business_stores` | `bigint(20)` | YES |  |  | 停业门店数 |
| 57 | `full_link_store_profit_rate` | `decimalv3(19, 6)` | YES |  |  | 全链路到店毛利率 |
| 58 | `full_link_store_profit_notax_rate` | `decimalv3(19, 6)` | YES |  |  | 全链路到店毛利率（不含税） |
| 59 | `full_link_store_profit_amt` | `decimalv3(19, 4)` | YES |  |  | 全链路到店毛利额 |
| 60 | `full_link_store_profit_amt_notax` | `decimalv3(19, 4)` | YES |  |  | 全链路到店毛利额（不含税） |
| 61 | `company_cost_rate` | `decimalv3(19, 6)` | YES |  |  | 公司成本费用率 |
| 62 | `company_cost_amt` | `decimalv3(19, 4)` | YES |  |  | 公司成本费用额 |
| 63 | `company_promo_amt` | `decimalv3(19, 4)` | YES |  |  | 公司承担优惠金额 |
| 64 | `qdm_bear_promotion_fee` | `decimalv3(19, 4)` | YES |  |  | 公司承担促销费用 |
| 65 | `qdm_bear_positive_amt_total` | `decimalv3(19, 4)` | YES |  |  | 公司承担让利金额 |
| 66 | `qdm_bear_negative_amt_total` | `decimalv3(19, 4)` | YES |  |  | 公司承担负让利金额 |
| 67 | `qdm_bear_gift_qty` | `decimalv3(19, 4)` | YES |  |  | 公司承担赠品让利数量 |
| 68 | `qdm_bear_gift_amt` | `decimalv3(19, 4)` | YES |  |  | 公司承担赠品让利金额 |
| 69 | `qdm_bear_nogift_positive_amt` | `decimalv3(19, 4)` | YES |  |  | 公司承担非赠品让利金额 |
| 70 | `qdm_bear_nogift_negative_amt` | `decimalv3(19, 4)` | YES |  |  | 公司承担非赠品负让利金额 |
| 71 | `other_store_return_num` | `bigint(20)` | YES |  |  | 其他类退货订单次数 |
| 72 | `increase_stores` | `bigint(20)` | YES |  |  | 净增店数 |
| 73 | `out_stock_article_num` | `bigint(20)` | YES |  |  | 出库到店SKU次数 |
| 74 | `out_stock_copies` | `bigint(20)` | YES |  |  | 出库到店份数 |
| 75 | `out_stock_copies_wms` | `bigint(20)` | YES |  |  | 出库到店份数（WMS） |
| 76 | `out_stock_cost` | `decimalv3(19, 4)` | YES |  |  | 出库到店成本 |
| 77 | `out_stock_qty` | `decimalv3(19, 4)` | YES |  |  | 出库到店数量 |
| 78 | `out_stock_weight` | `decimalv3(19, 4)` | YES |  |  | 出库到店重量 |
| 79 | `out_stock_pay_amt` | `decimalv3(19, 4)` | YES |  |  | 出库到店金额 |
| 80 | `out_stock_pay_amt_notax` | `decimalv3(19, 4)` | YES |  |  | 出库到店金额（不含税） |
| 81 | `scm_promotion_total_rate` | `decimalv3(19, 6)` | YES |  |  | 出库折让率 |
| 82 | `scm_promotion_amt_total` | `decimalv3(19, 4)` | YES |  |  | 出库让利总额 |
| 83 | `afcoupon_profit_rate` | `decimalv3(19, 6)` | YES |  |  | 券后毛利率 |
| 84 | `afcoupon_profit_amt` | `decimalv3(19, 4)` | YES |  |  | 券后毛利额 |
| 85 | `afcoupon_sale_amt` | `decimalv3(19, 4)` | YES |  |  | 券后销售额 |
| 86 | `original_price_sale_amt` | `decimalv3(19, 4)` | YES |  |  | 原价销售额 |
| 87 | `store_can_order_num` | `bigint(20)` | YES |  |  | 可订门店次数 |
| 88 | `stock_stores` | `bigint(20)` | YES |  |  | 存量门店数 |
| 89 | `pre_price_profit_rate` | `decimalv3(19, 6)` | YES |  |  | 定价毛利率 |
| 90 | `pre_price_profit_amt` | `decimalv3(19, 4)` | YES |  |  | 定价毛利额 |
| 91 | `per_cust_amt` | `decimalv3(19, 4)` | YES |  |  | 客单价 |
| 92 | `know_lost_qty` | `decimalv3(19, 4)` | YES |  |  | 已知损耗数量 |
| 93 | `know_lost_weight` | `decimalv3(19, 4)` | YES |  |  | 已知损耗重量 |
| 94 | `know_lost_amt` | `decimalv3(19, 4)` | YES |  |  | 已知损耗金额 |
| 95 | `platform_promo_amt` | `decimalv3(19, 4)` | YES |  |  | 平台承担优惠金额 |
| 96 | `avg_out_stock_price` | `decimalv3(19, 4)` | YES |  |  | 平均出库价 |
| 97 | `avg_out_stock_price_notax` | `decimalv3(19, 4)` | YES |  |  | 平均出库价（不含税） |
| 98 | `avg_receive_price` | `decimalv3(19, 4)` | YES |  |  | 平均进货价 |
| 99 | `avg_sale_price` | `decimalv3(19, 4)` | YES |  |  | 平均销售价 |
| 100 | `avg_original_sale_price` | `decimalv3(19, 4)` | YES |  |  | 平均销售原价 |
| 101 | `water_rent` | `decimalv3(19, 4)` | YES |  |  | 店铺水电费 |
| 102 | `unopen_stores` | `bigint(20)` | YES |  |  | 待开业门店数 |
| 103 | `promotion_rate` | `decimalv3(19, 6)` | YES |  |  | 成本费用率 |
| 104 | `cost_amt` | `decimalv3(19, 4)` | YES |  |  | 成本费用额 |
| 105 | `discount_rate` | `decimalv3(19, 6)` | YES |  |  | 折扣率 |
| 106 | `discount_amt` | `decimalv3(19, 4)` | YES |  |  | 折扣额 |
| 107 | `lost_rate` | `decimalv3(19, 6)` | YES |  |  | 损耗率 |
| 108 | `quantity_store_return_num` | `bigint(20)` | YES |  |  | 数量类退货订单次数 |
| 109 | `quatity_store_return_shop_rate` | `decimalv3(19, 6)` | YES |  |  | 数量类门店退货率_测试 |
| 110 | `open_stores` | `bigint(20)` | YES |  |  | 新开门店数 |
| 111 | `hour_discount_rate` | `decimalv3(19, 6)` | YES |  |  | 时段折扣率 |
| 112 | `hour_discount_amt` | `decimalv3(19, 4)` | YES |  |  | 时段折扣额 |
| 113 | `offline_hour_discount_rate` | `decimalv3(19, 6)` | YES |  |  | 时段折扣额线下占比 |
| 114 | `nothing_store_return_num` | `bigint(20)` | YES |  |  | 有单无货订单次数 |
| 115 | `unknow_lost_weight` | `decimalv3(19, 4)` | YES |  |  | 未知损耗重量 |
| 116 | `cust_num` | `bigint(20)` | YES |  |  | 来客数 |
| 117 | `premium_amt` | `decimalv3(19, 4)` | YES |  |  | 溢价金额 |
| 118 | `member_repurchase_rate` | `decimalv3(19, 6)` | YES |  |  | 滚动7天会员复购率 |
| 119 | `buy_again_member_num` | `bigint(20)` | YES |  |  | 滚动7天复购会员数 |
| 120 | `theory_lost_amt` | `decimalv3(19, 4)` | YES |  |  | 理论损耗额 |
| 121 | `theory_receive_amt` | `decimalv3(19, 4)` | YES |  |  | 理论进货额 |
| 122 | `theory_sale_amt` | `decimalv3(19, 4)` | YES |  |  | 理论销售额 |
| 123 | `credit_pay_amt` | `decimalv3(19, 4)` | YES |  |  | 积分支付金额 |
| 124 | `contract_franchisees` | `bigint(20)` | YES |  |  | 签约加盟商数 |
| 125 | `online_member_cust_num` | `bigint(20)` | YES |  |  | 线上会员客数 |
| 126 | `online_cust_num` | `bigint(20)` | YES |  |  | 线上客数 |
| 127 | `online_cust_num_rate` | `decimalv3(19, 6)` | YES |  |  | 线上客数占比 |
| 128 | `online_sale_rate` | `decimalv3(19, 6)` | YES |  |  | 线上销售占比 |
| 129 | `online_sale_qty` | `decimalv3(19, 4)` | YES |  |  | 线上销售数量 |
| 130 | `online_sale_amt` | `decimalv3(19, 4)` | YES |  |  | 线上销售额 |
| 131 | `offline_member_cust_num` | `bigint(20)` | YES |  |  | 线下会员客数 |
| 132 | `offline_original_price_sale_amt` | `decimalv3(19, 4)` | YES |  |  | 线下原价销售额 |
| 133 | `offline_cust_num` | `bigint(20)` | YES |  |  | 线下客数 |
| 134 | `offline_sale_qty` | `decimalv3(19, 4)` | YES |  |  | 线下销售数量 |
| 135 | `offline_sale_amt` | `decimalv3(19, 4)` | YES |  |  | 线下销售额 |
| 136 | `business_stores` | `bigint(20)` | YES |  |  | 营业中门店数 |
| 137 | `sale_days` | `bigint(20)` | YES |  |  | 营业店日数 |
| 138 | `stores` | `bigint(20)` | YES |  |  | 营业门店数 |
| 139 | `allowance_profit_rate` | `decimalv3(19, 6)` | YES |  |  | 补贴后毛利率 |
| 140 | `allowance_profit_amt` | `decimalv3(19, 4)` | YES |  |  | 补贴后毛利额 |
| 141 | `allowance_amt` | `decimalv3(19, 4)` | YES |  |  | 补贴额 |
| 142 | `satisfied_qty` | `decimalv3(19, 4)` | YES |  |  | 订单满足数量 |
| 143 | `satisfied_num` | `bigint(20)` | YES |  |  | 订单满足次数 |
| 144 | `satisfied_amt` | `decimalv3(19, 4)` | YES |  |  | 订单满足金额 |
| 145 | `order_article_num` | `bigint(20)` | YES |  |  | 订购SKU数 |
| 146 | `store_order_qty` | `decimalv3(19, 4)` | YES |  |  | 订购数量（订购单位） |
| 147 | `store_order_num` | `bigint(20)` | YES |  |  | 订购订单次数 |
| 148 | `store_order_weight` | `decimalv3(19, 4)` | YES |  |  | 订购重量 |
| 149 | `order_store_num` | `bigint(20)` | YES |  |  | 订购门店次数 |
| 150 | `quatity_store_return_num` | `bigint(20)` | YES |  |  | 质量类退货订单次数 |
| 151 | `gift_out_stock_cost_notax` | `decimalv3(19, 4)` | YES |  |  | 赠品出库到店成本（不含税） |
| 152 | `gift_out_stock_qty` | `decimalv3(19, 4)` | YES |  |  | 赠品出库到店数量 |
| 153 | `gift_outstock_weight` | `decimalv3(19, 4)` | YES |  |  | 赠品总出库重量 |
| 154 | `scm_promotion_gift_rate` | `decimalv3(19, 6)` | YES |  |  | 赠品折让率 |
| 155 | `scm_ppromotion_gift_amt` | `decimalv3(19, 4)` | YES |  |  | 赠品让利金额 |
| 156 | `receive_qty` | `decimalv3(19, 4)` | YES |  |  | 进货数量 |
| 157 | `receive_weight` | `decimalv3(19, 4)` | YES |  |  | 进货重量 |
| 158 | `receive_amt` | `decimalv3(19, 4)` | YES |  |  | 进货额 |
| 159 | `return_article_num` | `bigint(20)` | YES |  |  | 退货SKU数 |
| 160 | `store_return_article_num` | `bigint(20)` | YES |  |  | 退货SKU次数 |
| 161 | `sale_return_custom_num` | `bigint(20)` | YES |  |  | 退货用户数 |
| 162 | `store_return_num` | `bigint(20)` | YES |  |  | 退货订单次数 |
| 163 | `sale_piece` | `bigint(20)` | YES |  |  | 销售件数 |
| 164 | `sale_cost_amt` | `decimalv3(19, 4)` | YES |  |  | 销售成本 |
| 165 | `sale_qty` | `decimalv3(19, 4)` | YES |  |  | 销售数量 |
| 166 | `cut_time_return_amt` | `bigint(20)` | YES |  |  | 销售渠道截单后顾客退货额 |
| 167 | `sale_weight` | `decimalv3(19, 4)` | YES |  |  | 销售重量 |
| 168 | `sale_amt` | `decimalv3(19, 4)` | YES |  |  | 销售额 |
| 169 | `deposit_member_num` | `bigint(20)` | YES |  |  | 门店会员充值人数 |
| 170 | `deposit_order_num` | `bigint(20)` | YES |  |  | 门店会员充值次数 |
| 171 | `deposit_amt` | `decimalv3(19, 4)` | YES |  |  | 门店会员充值金额 |
| 172 | `member_sale_amt_rate` | `decimalv3(19, 6)` | YES |  |  | 门店会员销售占比 |
| 173 | `other_store_return_shop_rate` | `decimalv3(19, 6)` | YES |  |  | 门店其他类退货率 |
| 174 | `other_store_return_amt_shop` | `decimalv3(19, 4)` | YES |  |  | 门店其他类退货额 |
| 175 | `shop_promotion_rate` | `decimalv3(19, 6)` | YES |  |  | 门店发起促销折扣率 |
| 176 | `shop_promotion_amt` | `decimalv3(19, 4)` | YES |  |  | 门店发起促销折扣额 |
| 177 | `store_examine_return_qty` | `decimalv3(19, 4)` | YES |  |  | 门店审核退货数量 |
| 178 | `know_lost_rate` | `decimalv3(19, 6)` | YES |  |  | 门店已知损耗率 |
| 179 | `avg_store_return_price` | `decimalv3(19, 4)` | YES |  |  | 门店平均退货价 |
| 180 | `shop_cost_rate` | `decimalv3(19, 6)` | YES |  |  | 门店成本费用率 |
| 181 | `shop_coupon_promo_amt` | `decimalv3(19, 4)` | YES |  |  | 门店成本费用额 |
| 182 | `store_bear_cost` | `decimalv3(19, 4)` | YES |  |  | 门店承担优惠金额 |
| 183 | `lost_amt` | `decimalv3(19, 4)` | YES |  |  | 门店损耗额 |
| 184 | `quantity_store_return_shop_rate` | `decimalv3(19, 6)` | YES |  |  | 门店数量类退货率 |
| 185 | `quantity_store_return_amt_shop` | `decimalv3(19, 4)` | YES |  |  | 门店数量类退货额 |
| 186 | `store_init_stock_qty` | `decimalv3(19, 4)` | YES |  |  | 门店期初库存数量 |
| 187 | `store_init_stock_amt` | `decimalv3(19, 4)` | YES |  |  | 门店期初库存金额 |
| 188 | `store_end_stock_qty` | `decimalv3(19, 4)` | YES |  |  | 门店期末库存数量 |
| 189 | `store_end_stock_amt` | `decimalv3(19, 4)` | YES |  |  | 门店期末库存金额 |
| 190 | `unknow_lost_qty` | `decimalv3(19, 4)` | YES |  |  | 门店未知损耗数量 |
| 191 | `unknow_lost_rate` | `decimalv3(19, 6)` | YES |  |  | 门店未知损耗率 |
| 192 | `unknow_lost_amt` | `decimalv3(19, 4)` | YES |  |  | 门店未知损耗金额 |
| 193 | `profit_rate` | `decimalv3(19, 6)` | YES |  |  | 门店毛利率 |
| 194 | `profit_lost_rate` | `decimalv3(19, 6)` | YES |  |  | 门店毛利率（分析） |
| 195 | `profit_amt` | `decimalv3(19, 4)` | YES |  |  | 门店毛利额 |
| 196 | `profit_lost_amt` | `decimalv3(19, 4)` | YES |  |  | 门店毛利额（分析） |
| 197 | `allowance_amt_rate` | `decimalv3(19, 6)` | YES |  |  | 门店补贴额占比 |
| 198 | `store_order_copies` | `bigint(20)` | YES |  |  | 门店订购份数 |
| 199 | `order_store_rate` | `decimalv3(19, 6)` | YES |  |  | 门店订购渗透率 |
| 200 | `store_order_amt` | `decimalv3(19, 4)` | YES |  |  | 门店订购额 |
| 201 | `quality_store_return_shop_rate` | `decimalv3(19, 6)` | YES |  |  | 门店质量类退货率 |
| 202 | `quality_store_return_amt_shop` | `decimalv3(19, 4)` | YES |  |  | 门店质量类退货额 |
| 203 | `store_return_cost` | `decimalv3(19, 4)` | YES |  |  | 门店退货成本 |
| 204 | `store_return_cost_notax` | `decimalv3(19, 4)` | YES |  |  | 门店退货成本（不含税） |
| 205 | `store_return_qty` | `decimalv3(19, 4)` | YES |  |  | 门店退货数量（SAP） |
| 206 | `store_return_qty_shop` | `decimalv3(19, 4)` | YES |  |  | 门店退货数量（中台） |
| 207 | `store_return_rate` | `decimalv3(19, 6)` | YES |  |  | 门店退货率（SAP） |
| 208 | `store_return_shop_rate` | `decimalv3(19, 6)` | YES |  |  | 门店退货率（中台） |
| 209 | `store_return_weight` | `decimalv3(19, 4)` | YES |  |  | 门店退货重量（SAP） |
| 210 | `store_return_amt` | `decimalv3(19, 4)` | YES |  |  | 门店退货额（SAP） |
| 211 | `store_return_amt_notax` | `decimalv3(19, 4)` | YES |  |  | 门店退货额（SAP）（不含税） |
| 212 | `store_return_amt_shop` | `decimalv3(19, 4)` | YES |  |  | 门店退货额（中台） |
| 213 | `customer_store_return_shop_rate` | `decimalv3(19, 6)` | YES |  |  | 门店顾客类退货率 |
| 214 | `customer_store_return_amt_shop` | `decimalv3(19, 4)` | YES |  |  | 门店顾客类退货额 |
| 215 | `pre_profit_rate` | `decimalv3(19, 6)` | YES |  |  | 门店预期销售毛利率 |
| 216 | `pre_profit_amt` | `decimalv3(19, 4)` | YES |  |  | 门店预期销售毛利额 |
| 217 | `close_rate` | `decimalv3(19, 6)` | YES |  |  | 闭店率 |
| 218 | `close_stores` | `bigint(20)` | YES |  |  | 闭店门店数 |
| 219 | `zero_out_stock_order_amt` | `decimalv3(19, 4)` | YES |  |  | 零出库理论到店金额 |
| 220 | `zero_out_stock_order_num` | `bigint(20)` | YES |  |  | 零出库订单次数 |
| 221 | `zero_out_stock_order_qty` | `decimalv3(19, 4)` | YES |  |  | 零出库订购数量 |
| 222 | `nomember_discount_rate` | `decimalv3(19, 6)` | YES |  |  | 非会员折扣率 |
| 223 | `nomember_discount_amt` | `decimalv3(19, 4)` | YES |  |  | 非会员折扣额 |
| 224 | `nonquantity_store_return_num` | `bigint(20)` | YES |  |  | 非数量类退货订单次数 |
| 225 | `value_out_stock_qty` | `decimalv3(19, 4)` | YES |  |  | 非赠品出库到店数量 |
| 226 | `avg_nogift_outstock_price` | `decimalv3(19, 4)` | YES |  |  | 非赠品平均出库价 |
| 227 | `avg_nogift_outstock_price_notax` | `decimalv3(19, 4)` | YES |  |  | 非赠品平均出库价（不含税） |
| 228 | `scm_nogift_promotion_rate` | `decimalv3(19, 6)` | YES |  |  | 非赠品折让率 |
| 229 | `scm_ppromotion_nogift_amt` | `decimalv3(19, 4)` | YES |  |  | 非赠品让利金额 |
| 230 | `customer_store_return_num` | `bigint(20)` | YES |  |  | 顾客类退货订单次数 |
| 231 | `return_cust_num` | `bigint(20)` | YES |  |  | 顾客退货客数 |
| 232 | `sale_return_amt` | `decimalv3(19, 4)` | YES |  |  | 顾客退货额 |
| 233 | `expect_out_to_store_stock_amt` | `decimalv3(19, 4)` | YES |  |  | 预期出库到店金额 |
| 234 | `store_order_amt_goal` | `decimalv3(19, 4)` | YES |  |  | 预算订购额 |
| 235 | `store_order_amt_finish_rate` | `decimalv3(19, 6)` | YES |  |  | 预算订购额达成率 |

### dwd_date_shop_sku

表说明：门店商品日粒度指标宽表（当日动销 SKU）

| 序号 | 字段名 | 字段类型 | 是否可空 | 键类型 | 默认值 | 字段注释 |
|---:|---|---|---|---|---|---|
| 1 | `dt` | `date` | NO | UNI |  | 营业日期 |
| 2 | `shop_id` | `varchar(64)` | NO | UNI |  | 门店 ID |
| 3 | `sku_id` | `varchar(64)` | NO | UNI |  | 商品编码（CMR articleId） |
| 4 | `shop_name` | `varchar(255)` | NO |  |  | 门店名称；维度值解析补全:storeId；非Metric |
| 5 | `category_level1_id` | `varchar(64)` | NO |  |  | 大分类编码；维度值解析补全:articleId；非Metric |
| 6 | `category_level1_name` | `varchar(255)` | NO |  |  | 大分类名称；维度值解析补全:articleId；非Metric |
| 7 | `category_level2_id` | `varchar(64)` | NO |  |  | 中分类编码；维度值解析补全:articleId；非Metric |
| 8 | `category_level2_name` | `varchar(255)` | NO |  |  | 中分类名称；维度值解析补全:articleId；非Metric |
| 9 | `category_level3_id` | `varchar(64)` | NO |  |  | 小分类编码；维度值解析补全:articleId；非Metric |
| 10 | `category_level3_name` | `varchar(255)` | NO |  |  | 小分类名称；维度值解析补全:articleId；非Metric |
| 11 | `spu_id` | `varchar(64)` | NO |  |  | SPU 编码；维度值解析补全:articleId；非Metric |
| 12 | `spu_name` | `varchar(255)` | NO |  |  | SPU 名称；维度值解析补全:articleId；非Metric |
| 13 | `sku_name` | `varchar(255)` | NO |  |  | 商品名称；维度值解析补全:articleId；非Metric |
| 14 | `bf19_category_store_cust_rate` | `decimalv3(38, 6)` | YES |  |  | 19点前PI值；本期无明确metric-cli Metric |
| 15 | `bf19_per_piece_amt` | `decimalv3(19, 4)` | YES |  |  | 19点前件单价；metric-cli:bf19PerPieceAmt；非本期主指标 |
| 16 | `bf19_avg_piece_num` | `decimalv3(19, 4)` | YES |  |  | 19点前单均件数；metric-cli:bf19AvgPieceNum；非本期主指标 |
| 17 | `bf19_member_repurchase_rate` | `decimalv3(38, 6)` | YES |  |  | 19点前复购率；metric-cli:bf19MemberRepurchaseRate；非本期主指标 |
| 18 | `bf19_per_cust_amt` | `decimalv3(19, 4)` | YES |  |  | 19点前客单价；metric-cli:bf19PerCustAmt |
| 19 | `bf19_cust_num` | `bigint(20)` | YES |  |  | 19点前客数；metric-cli:bf19CustNum |
| 20 | `bf19_sale_rate` | `decimalv3(38, 6)` | YES |  |  | 19点前销售占比；metric-cli:bf19SaleRate；非本期主指标 |
| 21 | `bf19_sale_weight` | `decimalv3(19, 4)` | YES |  |  | 19点前销售重量；metric-cli:bf19SaleWeight；非本期主指标 |
| 22 | `scm_store_profit_notax_rate` | `decimalv3(38, 6)` | YES |  |  | 供应链毛利率；metric-cli:scmStoreProfitNotaxRate |
| 23 | `scm_store_profit_amt_notax` | `decimalv3(19, 4)` | YES |  |  | 供应链毛利额；metric-cli:scmStoreProfitAmtNotax |
| 24 | `promotion_discount_rate` | `decimalv3(38, 6)` | YES |  |  | 促销折扣率；metric-cli:promotionDiscountRate |
| 25 | `full_link_store_profit_notax_rate` | `decimalv3(38, 6)` | YES |  |  | 全链路毛利率；metric-cli:fullLinkStoreProfitNotaxRate |
| 26 | `full_link_store_profit_amt_notax` | `decimalv3(19, 4)` | YES |  |  | 全链路毛利额；metric-cli:fullLinkStoreProfitAmtNotax |
| 27 | `scm_promotion_total_rate` | `decimalv3(38, 6)` | YES |  |  | 出库折让率；metric-cli:scmPromotionTotalRate；非本期主指标 |
| 28 | `store_can_orders` | `decimalv3(38, 6)` | YES |  |  | 可订门店数（CMR原值）；近似metric-cli:storeCanOrderNum；口径待确认 |
| 29 | `brand_product_effectiveness` | `decimalv3(19, 4)` | YES |  |  | 品效；本期无明确metric-cli Metric |
| 30 | `order_article_rate` | `decimalv3(38, 6)` | YES |  |  | 商品订购渗透率；本期无明确metric-cli Metric；不替代orderStoreRate |
| 31 | `pre_price_profit_rate` | `decimalv3(38, 6)` | YES |  |  | 定价毛利率；metric-cli:prePriceProfitRate |
| 32 | `per_cust_amt` | `decimalv3(19, 4)` | YES |  |  | 客单价；metric-cli:perCustAmt |
| 33 | `cust_num` | `bigint(20)` | YES |  |  | 客数；metric-cli:custNum |
| 34 | `cust_penetration_rate` | `decimalv3(38, 6)` | YES |  |  | 客数渗透率；本期无明确metric-cli Metric |
| 35 | `lost_rate` | `decimalv3(38, 6)` | YES |  |  | 损耗率；metric-cli:lostRate |
| 36 | `hour_discount_rate` | `decimalv3(38, 6)` | YES |  |  | 时段折扣率；metric-cli:hourDiscountRate |
| 37 | `satisfied_rate` | `decimalv3(38, 6)` | YES |  |  | 订单满足率；metric-cli:satisfiedRate；非本期主指标 |
| 38 | `order_stores` | `decimalv3(38, 6)` | YES |  |  | 订购门店数（CMR原值）；metric-cli:orderStores；非订购渗透率 |
| 39 | `sale_amt` | `decimalv3(19, 4)` | YES |  |  | 销售额；metric-cli:saleAmt |
| 40 | `profit_rate` | `decimalv3(38, 6)` | YES |  |  | 门店毛利率；metric-cli:profitRate |
| 41 | `profit_amt` | `decimalv3(19, 4)` | YES |  |  | 门店毛利额；metric-cli:profitAmt |
| 42 | `pre_profit_rate` | `decimalv3(38, 6)` | YES |  |  | 预期毛利率；metric-cli:preProfitRate |
| 43 | `scm_store_profit_amt` | `decimalv3(20, 4)` | YES |  |  | 供应链到店毛利额（含税）；metric-cli:scmStoreProfitAmt |
| 44 | `scm_store_profit_rate` | `decimalv3(38, 6)` | YES |  |  | 供应链到店毛利率（含税）；metric-cli:scmStoreProfitRate |
| 45 | `sale_days` | `decimalv3(20, 4)` | YES |  |  | 营业店日数；metric-cli:saleDays |
| 46 | `stores` | `decimalv3(20, 4)` | YES |  |  | 营业门店数；metric-cli:stores |
| 47 | `order_store_rate` | `decimalv3(38, 6)` | YES |  |  | 门店订购渗透率；metric-cli:orderStoreRate |
| 48 | `store_order_amt` | `decimalv3(20, 4)` | YES |  |  | 订购额；metric-cli:storeOrderAmt |
| 49 | `store_order_qty` | `decimalv3(20, 4)` | YES |  |  | 订购数量（订购单位）；metric-cli:storeOrderQty |
| 50 | `receive_amt` | `decimalv3(20, 4)` | YES |  |  | 进货额；metric-cli:receiveAmt |
| 51 | `receive_qty` | `decimalv3(20, 4)` | YES |  |  | 进货数量；metric-cli:receiveQty |
| 52 | `bf19_sale_amt` | `decimalv3(20, 4)` | YES |  |  | 19点前销售额；metric-cli:bf19SaleAmt |
| 53 | `af19_sale_amt` | `decimalv3(20, 4)` | YES |  |  | 19点后销售额；metric-cli:af19SaleAmt |
| 54 | `sale_qty` | `decimalv3(20, 4)` | YES |  |  | 销售数量；metric-cli:saleQty |
| 55 | `bf19_sale_qty` | `decimalv3(20, 4)` | YES |  |  | 19点前销售数量；metric-cli:bf19SaleQty |
| 56 | `af19_sale_qty` | `decimalv3(20, 4)` | YES |  |  | 19点后销售数量；metric-cli:af19SaleQty |
| 57 | `af19_cust_num` | `decimalv3(20, 4)` | YES |  |  | 19点后客数；metric-cli:af19CustNum |
| 58 | `af19_per_cust_amt` | `decimalv3(20, 4)` | YES |  |  | 19点后客单价；metric-cli:af19PerCustAmt |
| 59 | `discount_amt` | `decimalv3(20, 4)` | YES |  |  | 折扣额；metric-cli:discountAmt |
| 60 | `discount_rate` | `decimalv3(38, 6)` | YES |  |  | 折扣率；metric-cli:discountRate |
| 61 | `promotion_discount_amt` | `decimalv3(20, 4)` | YES |  |  | 促销折扣额；metric-cli:promotionDiscountAmt |
| 62 | `hour_discount_amt` | `decimalv3(20, 4)` | YES |  |  | 时段折扣额；metric-cli:hourDiscountAmt |
| 63 | `promotion_rate` | `decimalv3(38, 6)` | YES |  |  | 成本费用率；metric-cli:promotionRate |
| 64 | `shop_promotion_amt` | `decimalv3(20, 4)` | YES |  |  | 门店发起促销折扣额；metric-cli:shopPromotionAmt |
| 65 | `shop_promotion_rate` | `decimalv3(38, 6)` | YES |  |  | 门店发起促销折扣率；metric-cli:shopPromotionRate |
| 66 | `lost_amt` | `decimalv3(20, 4)` | YES |  |  | 损耗额；metric-cli:lostAmt |
| 67 | `allowance_profit_amt` | `decimalv3(20, 4)` | YES |  |  | 补贴后毛利额；metric-cli:allowanceProfitAmt |
| 68 | `afcoupon_profit_amt` | `decimalv3(20, 4)` | YES |  |  | 券后毛利额；metric-cli:afcouponProfitAmt |
| 69 | `profit_lost_rate` | `decimalv3(38, 6)` | YES |  |  | 门店毛利率（分析）；metric-cli:profitLostRate |
| 70 | `scm_store_profit_proportion` | `decimalv3(38, 6)` | YES |  |  | 供应链门店毛利配比；metric-cli:scmStoreProfitProportion |
| 71 | `full_link_store_profit_amt` | `decimalv3(20, 4)` | YES |  |  | 全链路到店毛利额（含税）；metric-cli:fullLinkStoreProfitAmt |
| 72 | `full_link_store_profit_rate` | `decimalv3(38, 6)` | YES |  |  | 全链路到店毛利率（含税）；metric-cli:fullLinkStoreProfitRate |

### dwd_date_shop_sku_monthly_backup_20260728

表说明：门店商品日粒度指标宽表（当日动销 SKU）

| 序号 | 字段名 | 字段类型 | 是否可空 | 键类型 | 默认值 | 字段注释 |
|---:|---|---|---|---|---|---|
| 1 | `dt` | `date` | NO | UNI |  | 营业日期 |
| 2 | `shop_id` | `varchar(64)` | NO | UNI |  | 门店 ID |
| 3 | `sku_id` | `varchar(64)` | NO | UNI |  | 商品编码（CMR articleId） |
| 4 | `shop_name` | `varchar(255)` | NO |  |  | 门店名称 |
| 5 | `category_level1_id` | `varchar(64)` | NO |  |  | 大分类编码 |
| 6 | `category_level1_name` | `varchar(255)` | NO |  |  | 大分类名称 |
| 7 | `category_level2_id` | `varchar(64)` | NO |  |  | 中分类编码 |
| 8 | `category_level2_name` | `varchar(255)` | NO |  |  | 中分类名称 |
| 9 | `category_level3_id` | `varchar(64)` | NO |  |  | 小分类编码 |
| 10 | `category_level3_name` | `varchar(255)` | NO |  |  | 小分类名称 |
| 11 | `spu_id` | `varchar(64)` | NO |  |  | SPU 编码 |
| 12 | `spu_name` | `varchar(255)` | NO |  |  | SPU 名称 |
| 13 | `sku_name` | `varchar(255)` | NO |  |  | 商品名称 |
| 14 | `bf19_category_store_cust_rate` | `decimalv3(19, 6)` | YES |  |  | 19点前PI值 |
| 15 | `bf19_per_piece_amt` | `decimalv3(19, 4)` | YES |  |  | 19点前件单价 |
| 16 | `bf19_avg_piece_num` | `decimalv3(19, 4)` | YES |  |  | 19点前单均件数 |
| 17 | `bf19_member_repurchase_rate` | `decimalv3(19, 6)` | YES |  |  | 19点前复购率 |
| 18 | `bf19_per_cust_amt` | `decimalv3(19, 4)` | YES |  |  | 19点前客单价 |
| 19 | `bf19_cust_num` | `bigint(20)` | YES |  |  | 19点前客数 |
| 20 | `bf19_sale_rate` | `decimalv3(19, 6)` | YES |  |  | 19点前销售占比 |
| 21 | `bf19_sale_weight` | `decimalv3(19, 4)` | YES |  |  | 19点前销售重量 |
| 22 | `scm_store_profit_notax_rate` | `decimalv3(19, 6)` | YES |  |  | 供应链毛利率 |
| 23 | `scm_store_profit_amt_notax` | `decimalv3(19, 4)` | YES |  |  | 供应链毛利额 |
| 24 | `promotion_discount_rate` | `decimalv3(19, 6)` | YES |  |  | 促销折扣率 |
| 25 | `full_link_store_profit_notax_rate` | `decimalv3(19, 6)` | YES |  |  | 全链路毛利率 |
| 26 | `full_link_store_profit_amt_notax` | `decimalv3(19, 4)` | YES |  |  | 全链路毛利额 |
| 27 | `scm_promotion_total_rate` | `decimalv3(19, 6)` | YES |  |  | 出库折让率 |
| 28 | `store_can_orders` | `decimalv3(19, 6)` | YES |  |  | 可订门店数（CMR原值） |
| 29 | `brand_product_effectiveness` | `decimalv3(19, 4)` | YES |  |  | 品效 |
| 30 | `order_article_rate` | `decimalv3(19, 6)` | YES |  |  | 商品订购渗透率 |
| 31 | `pre_price_profit_rate` | `decimalv3(19, 6)` | YES |  |  | 定价毛利率 |
| 32 | `per_cust_amt` | `decimalv3(19, 4)` | YES |  |  | 客单价 |
| 33 | `cust_num` | `bigint(20)` | YES |  |  | 客数 |
| 34 | `cust_penetration_rate` | `decimalv3(19, 6)` | YES |  |  | 客数渗透率 |
| 35 | `lost_rate` | `decimalv3(19, 6)` | YES |  |  | 损耗率 |
| 36 | `hour_discount_rate` | `decimalv3(19, 6)` | YES |  |  | 时段折扣率 |
| 37 | `satisfied_rate` | `decimalv3(19, 6)` | YES |  |  | 订单满足率 |
| 38 | `order_stores` | `decimalv3(19, 6)` | YES |  |  | 订购门店数（CMR原值） |
| 39 | `sale_amt` | `decimalv3(19, 4)` | YES |  |  | 销售额 |
| 40 | `profit_rate` | `decimalv3(19, 6)` | YES |  |  | 门店毛利率 |
| 41 | `profit_amt` | `decimalv3(19, 4)` | YES |  |  | 门店毛利额 |
| 42 | `pre_profit_rate` | `decimalv3(19, 6)` | YES |  |  | 预期毛利率 |

### dwd_date_shop_sku_p20260630_backup_20260728

表说明：门店商品日粒度指标宽表（当日动销 SKU）

| 序号 | 字段名 | 字段类型 | 是否可空 | 键类型 | 默认值 | 字段注释 |
|---:|---|---|---|---|---|---|
| 1 | `dt` | `date` | NO | UNI |  | 营业日期 |
| 2 | `shop_id` | `varchar(64)` | NO | UNI |  | 门店 ID |
| 3 | `sku_id` | `varchar(64)` | NO | UNI |  | 商品编码（CMR articleId） |
| 4 | `shop_name` | `varchar(255)` | NO |  |  | 门店名称 |
| 5 | `category_level1_id` | `varchar(64)` | NO |  |  | 大分类编码 |
| 6 | `category_level1_name` | `varchar(255)` | NO |  |  | 大分类名称 |
| 7 | `category_level2_id` | `varchar(64)` | NO |  |  | 中分类编码 |
| 8 | `category_level2_name` | `varchar(255)` | NO |  |  | 中分类名称 |
| 9 | `category_level3_id` | `varchar(64)` | NO |  |  | 小分类编码 |
| 10 | `category_level3_name` | `varchar(255)` | NO |  |  | 小分类名称 |
| 11 | `spu_id` | `varchar(64)` | NO |  |  | SPU 编码 |
| 12 | `spu_name` | `varchar(255)` | NO |  |  | SPU 名称 |
| 13 | `sku_name` | `varchar(255)` | NO |  |  | 商品名称 |
| 14 | `bf19_category_store_cust_rate` | `decimalv3(38, 6)` | YES |  |  | 19点前PI值 |
| 15 | `bf19_per_piece_amt` | `decimalv3(19, 4)` | YES |  |  | 19点前件单价 |
| 16 | `bf19_avg_piece_num` | `decimalv3(19, 4)` | YES |  |  | 19点前单均件数 |
| 17 | `bf19_member_repurchase_rate` | `decimalv3(38, 6)` | YES |  |  | 19点前复购率 |
| 18 | `bf19_per_cust_amt` | `decimalv3(19, 4)` | YES |  |  | 19点前客单价 |
| 19 | `bf19_cust_num` | `bigint(20)` | YES |  |  | 19点前客数 |
| 20 | `bf19_sale_rate` | `decimalv3(38, 6)` | YES |  |  | 19点前销售占比 |
| 21 | `bf19_sale_weight` | `decimalv3(19, 4)` | YES |  |  | 19点前销售重量 |
| 22 | `scm_store_profit_notax_rate` | `decimalv3(38, 6)` | YES |  |  | 供应链毛利率 |
| 23 | `scm_store_profit_amt_notax` | `decimalv3(19, 4)` | YES |  |  | 供应链毛利额 |
| 24 | `promotion_discount_rate` | `decimalv3(38, 6)` | YES |  |  | 促销折扣率 |
| 25 | `full_link_store_profit_notax_rate` | `decimalv3(38, 6)` | YES |  |  | 全链路毛利率 |
| 26 | `full_link_store_profit_amt_notax` | `decimalv3(19, 4)` | YES |  |  | 全链路毛利额 |
| 27 | `scm_promotion_total_rate` | `decimalv3(38, 6)` | YES |  |  | 出库折让率 |
| 28 | `store_can_orders` | `decimalv3(38, 6)` | YES |  |  | 可订门店数（CMR原值） |
| 29 | `brand_product_effectiveness` | `decimalv3(19, 4)` | YES |  |  | 品效 |
| 30 | `order_article_rate` | `decimalv3(38, 6)` | YES |  |  | 商品订购渗透率 |
| 31 | `pre_price_profit_rate` | `decimalv3(38, 6)` | YES |  |  | 定价毛利率 |
| 32 | `per_cust_amt` | `decimalv3(19, 4)` | YES |  |  | 客单价 |
| 33 | `cust_num` | `bigint(20)` | YES |  |  | 客数 |
| 34 | `cust_penetration_rate` | `decimalv3(38, 6)` | YES |  |  | 客数渗透率 |
| 35 | `lost_rate` | `decimalv3(38, 6)` | YES |  |  | 损耗率 |
| 36 | `hour_discount_rate` | `decimalv3(38, 6)` | YES |  |  | 时段折扣率 |
| 37 | `satisfied_rate` | `decimalv3(38, 6)` | YES |  |  | 订单满足率 |
| 38 | `order_stores` | `decimalv3(38, 6)` | YES |  |  | 订购门店数（CMR原值） |
| 39 | `sale_amt` | `decimalv3(19, 4)` | YES |  |  | 销售额 |
| 40 | `profit_rate` | `decimalv3(38, 6)` | YES |  |  | 门店毛利率 |
| 41 | `profit_amt` | `decimalv3(19, 4)` | YES |  |  | 门店毛利额 |
| 42 | `pre_profit_rate` | `decimalv3(38, 6)` | YES |  |  | 预期毛利率 |

### dwd_date_shop_sku_pre_full_switch_20260729

表说明：门店商品日粒度指标宽表（当日动销 SKU）

| 序号 | 字段名 | 字段类型 | 是否可空 | 键类型 | 默认值 | 字段注释 |
|---:|---|---|---|---|---|---|
| 1 | `dt` | `date` | NO | UNI |  | 营业日期 |
| 2 | `shop_id` | `varchar(64)` | NO | UNI |  | 门店 ID |
| 3 | `sku_id` | `varchar(64)` | NO | UNI |  | 商品编码（CMR articleId） |
| 4 | `shop_name` | `varchar(255)` | NO |  |  | 门店名称 |
| 5 | `category_level1_id` | `varchar(64)` | NO |  |  | 大分类编码 |
| 6 | `category_level1_name` | `varchar(255)` | NO |  |  | 大分类名称 |
| 7 | `category_level2_id` | `varchar(64)` | NO |  |  | 中分类编码 |
| 8 | `category_level2_name` | `varchar(255)` | NO |  |  | 中分类名称 |
| 9 | `category_level3_id` | `varchar(64)` | NO |  |  | 小分类编码 |
| 10 | `category_level3_name` | `varchar(255)` | NO |  |  | 小分类名称 |
| 11 | `spu_id` | `varchar(64)` | NO |  |  | SPU 编码 |
| 12 | `spu_name` | `varchar(255)` | NO |  |  | SPU 名称 |
| 13 | `sku_name` | `varchar(255)` | NO |  |  | 商品名称 |
| 14 | `bf19_category_store_cust_rate` | `decimalv3(38, 6)` | YES |  |  | 19点前PI值 |
| 15 | `bf19_per_piece_amt` | `decimalv3(19, 4)` | YES |  |  | 19点前件单价 |
| 16 | `bf19_avg_piece_num` | `decimalv3(19, 4)` | YES |  |  | 19点前单均件数 |
| 17 | `bf19_member_repurchase_rate` | `decimalv3(38, 6)` | YES |  |  | 19点前复购率 |
| 18 | `bf19_per_cust_amt` | `decimalv3(19, 4)` | YES |  |  | 19点前客单价 |
| 19 | `bf19_cust_num` | `bigint(20)` | YES |  |  | 19点前客数 |
| 20 | `bf19_sale_rate` | `decimalv3(38, 6)` | YES |  |  | 19点前销售占比 |
| 21 | `bf19_sale_weight` | `decimalv3(19, 4)` | YES |  |  | 19点前销售重量 |
| 22 | `scm_store_profit_notax_rate` | `decimalv3(38, 6)` | YES |  |  | 供应链毛利率 |
| 23 | `scm_store_profit_amt_notax` | `decimalv3(19, 4)` | YES |  |  | 供应链毛利额 |
| 24 | `promotion_discount_rate` | `decimalv3(38, 6)` | YES |  |  | 促销折扣率 |
| 25 | `full_link_store_profit_notax_rate` | `decimalv3(38, 6)` | YES |  |  | 全链路毛利率 |
| 26 | `full_link_store_profit_amt_notax` | `decimalv3(19, 4)` | YES |  |  | 全链路毛利额 |
| 27 | `scm_promotion_total_rate` | `decimalv3(38, 6)` | YES |  |  | 出库折让率 |
| 28 | `store_can_orders` | `decimalv3(38, 6)` | YES |  |  | 可订门店数（CMR原值） |
| 29 | `brand_product_effectiveness` | `decimalv3(19, 4)` | YES |  |  | 品效 |
| 30 | `order_article_rate` | `decimalv3(38, 6)` | YES |  |  | 商品订购渗透率 |
| 31 | `pre_price_profit_rate` | `decimalv3(38, 6)` | YES |  |  | 定价毛利率 |
| 32 | `per_cust_amt` | `decimalv3(19, 4)` | YES |  |  | 客单价 |
| 33 | `cust_num` | `bigint(20)` | YES |  |  | 客数 |
| 34 | `cust_penetration_rate` | `decimalv3(38, 6)` | YES |  |  | 客数渗透率 |
| 35 | `lost_rate` | `decimalv3(38, 6)` | YES |  |  | 损耗率 |
| 36 | `hour_discount_rate` | `decimalv3(38, 6)` | YES |  |  | 时段折扣率 |
| 37 | `satisfied_rate` | `decimalv3(38, 6)` | YES |  |  | 订单满足率 |
| 38 | `order_stores` | `decimalv3(38, 6)` | YES |  |  | 订购门店数（CMR原值） |
| 39 | `sale_amt` | `decimalv3(19, 4)` | YES |  |  | 销售额 |
| 40 | `profit_rate` | `decimalv3(38, 6)` | YES |  |  | 门店毛利率 |
| 41 | `profit_amt` | `decimalv3(19, 4)` | YES |  |  | 门店毛利额 |
| 42 | `pre_profit_rate` | `decimalv3(38, 6)` | YES |  |  | 预期毛利率 |

### dwd_date_shop_sku_qdm_brand

表说明：QDM品牌指定SKU门店商品日指标表

| 序号 | 字段名 | 字段类型 | 是否可空 | 键类型 | 默认值 | 字段注释 |
|---:|---|---|---|---|---|---|
| 1 | `dt` | `date` | NO | UNI |  | 营业日期 |
| 2 | `shop_id` | `varchar(64)` | NO | UNI |  | 门店ID |
| 3 | `sku_id` | `varchar(64)` | NO | UNI |  | 商品编码 |
| 4 | `scm_store_profit_amt_notax` | `decimalv3(20, 4)` | YES |  |  | 供应链到店毛利额(不含税) |
| 5 | `scm_store_profit_notax_rate` | `decimalv3(38, 6)` | YES |  |  | 供应链到店毛利率(不含税) |
| 6 | `scm_store_profit_amt` | `decimalv3(20, 4)` | YES |  |  | 供应链到店毛利额(含税) |
| 7 | `scm_store_profit_rate` | `decimalv3(38, 6)` | YES |  |  | 供应链到店毛利率(含税) |
| 8 | `pre_scm_profit_amt` | `decimalv3(20, 4)` | YES |  |  | 供应链预期毛利额 |
| 9 | `scm_pre_profit_rate` | `decimalv3(38, 6)` | YES |  |  | 供应链预期毛利率 |
| 10 | `sale_days` | `decimalv3(20, 4)` | YES |  |  | 营业店日数 |
| 11 | `stores` | `decimalv3(20, 4)` | YES |  |  | 营业门店数 |
| 12 | `active_sku_count` | `decimalv3(20, 4)` | YES |  |  | 动销SKU数 |
| 13 | `order_store_rate` | `decimalv3(38, 6)` | YES |  |  | 订购渗透率 |
| 14 | `store_order_amt` | `decimalv3(20, 4)` | YES |  |  | 订购额 |
| 15 | `store_order_qty` | `decimalv3(20, 4)` | YES |  |  | 订购数量 |
| 16 | `receive_amt` | `decimalv3(20, 4)` | YES |  |  | 进货额 |
| 17 | `receive_qty` | `decimalv3(20, 4)` | YES |  |  | 进货数量 |
| 18 | `sale_amt` | `decimalv3(20, 4)` | YES |  |  | 销售额 |
| 19 | `bf19_sale_amt` | `decimalv3(20, 4)` | YES |  |  | 19点前销售额 |
| 20 | `bf19_active_sku` | `decimalv3(20, 4)` | YES |  |  | 19点前动销 |
| 21 | `af19_sale_amt` | `decimalv3(20, 4)` | YES |  |  | 19点后销售额 |
| 22 | `sale_qty` | `decimalv3(20, 4)` | YES |  |  | 销售数量 |
| 23 | `bf19_sale_qty` | `decimalv3(20, 4)` | YES |  |  | 19点前销售数量 |
| 24 | `af19_sale_qty` | `decimalv3(20, 4)` | YES |  |  | 19点后销售数量 |
| 25 | `cust_num` | `decimalv3(20, 4)` | YES |  |  | 来客数 |
| 26 | `per_cust_amt` | `decimalv3(20, 4)` | YES |  |  | 客单价 |
| 27 | `bf19_cust_num` | `decimalv3(20, 4)` | YES |  |  | 19点前来客数 |
| 28 | `bf19_per_cust_amt` | `decimalv3(20, 4)` | YES |  |  | 19点前客单价 |
| 29 | `af19_cust_num` | `decimalv3(20, 4)` | YES |  |  | 19点后来客数 |
| 30 | `af19_per_cust_amt` | `decimalv3(20, 4)` | YES |  |  | 19点后客单价 |
| 31 | `discount_amt` | `decimalv3(20, 4)` | YES |  |  | 折扣额 |
| 32 | `discount_rate` | `decimalv3(38, 6)` | YES |  |  | 折扣率 |
| 33 | `promotion_discount_amt` | `decimalv3(20, 4)` | YES |  |  | 促销折扣额 |
| 34 | `promotion_discount_rate` | `decimalv3(38, 6)` | YES |  |  | 促销折扣率 |
| 35 | `hour_discount_amt` | `decimalv3(20, 4)` | YES |  |  | 时段折扣额 |
| 36 | `hour_discount_rate` | `decimalv3(38, 6)` | YES |  |  | 时段折扣率 |
| 37 | `promotion_rate` | `decimalv3(38, 6)` | YES |  |  | 成本费用率 |
| 38 | `shop_promotion_amt` | `decimalv3(20, 4)` | YES |  |  | 门店发起促销折扣额 |
| 39 | `shop_promotion_rate` | `decimalv3(38, 6)` | YES |  |  | 门店发起促销折扣率 |
| 40 | `lost_amt` | `decimalv3(20, 4)` | YES |  |  | 损耗额 |
| 41 | `lost_rate` | `decimalv3(38, 6)` | YES |  |  | 损耗率 |
| 42 | `allowance_profit_amt` | `decimalv3(20, 4)` | YES |  |  | 补贴后毛利额 |
| 43 | `allowance_profit_rate` | `decimalv3(38, 6)` | YES |  |  | 补贴后毛利率 |
| 44 | `afcoupon_profit_amt` | `decimalv3(20, 4)` | YES |  |  | 券后毛利额 |
| 45 | `profit_amt` | `decimalv3(20, 4)` | YES |  |  | 毛利额 |
| 46 | `profit_rate` | `decimalv3(38, 6)` | YES |  |  | 毛利率 |
| 47 | `profit_lost_rate` | `decimalv3(38, 6)` | YES |  |  | 门店毛利率（分析） |
| 48 | `pre_profit_rate` | `decimalv3(38, 6)` | YES |  |  | 预期销售毛利率 |
| 49 | `pre_price_profit_rate` | `decimalv3(38, 6)` | YES |  |  | 定价毛利率 |
| 50 | `scm_store_profit_proportion` | `decimalv3(38, 6)` | YES |  |  | 供应链门店毛利配比 |
| 51 | `full_link_store_profit_amt` | `decimalv3(20, 4)` | YES |  |  | 全链路到店毛利额(含税) |
| 52 | `full_link_store_profit_rate` | `decimalv3(38, 6)` | YES |  |  | 全链路到店毛利率(含税) |
| 53 | `full_link_store_profit_amt_notax` | `decimalv3(20, 4)` | YES |  |  | 全链路到店毛利额(不含税) |
| 54 | `full_link_store_profit_notax_rate` | `decimalv3(38, 6)` | YES |  |  | 全链路到店毛利率(不含税) |

### dwd_date_shop_sku_qdm_brand_static_backup_20260805234833

表说明：QDM品牌指定SKU门店商品日指标表（2026年6月）

| 序号 | 字段名 | 字段类型 | 是否可空 | 键类型 | 默认值 | 字段注释 |
|---:|---|---|---|---|---|---|
| 1 | `dt` | `date` | NO | UNI |  | 营业日期 |
| 2 | `shop_id` | `varchar(64)` | NO | UNI |  | 门店ID |
| 3 | `sku_id` | `varchar(64)` | NO | UNI |  | 商品编码 |
| 4 | `scm_store_profit_amt_notax` | `decimalv3(20, 4)` | YES |  |  | 供应链到店毛利额(不含税)；metric-cli:scmStoreProfitAmtNotax |
| 5 | `scm_store_profit_notax_rate` | `decimalv3(38, 6)` | YES |  |  | 供应链到店毛利率(不含税)；metric-cli:scmStoreProfitNotaxRate |
| 6 | `scm_store_profit_amt` | `decimalv3(20, 4)` | YES |  |  | 供应链到店毛利额(含税)；metric-cli:scmStoreProfitAmt |
| 7 | `scm_store_profit_rate` | `decimalv3(38, 6)` | YES |  |  | 供应链到店毛利率(含税)；metric-cli:scmStoreProfitRate |
| 8 | `scm_pre_profit_rate` | `decimalv3(38, 6)` | YES |  |  | 供应链预期毛利率；metric-cli未注册；本期为空 |
| 9 | `sale_days` | `decimalv3(20, 4)` | YES |  |  | 营业店日数；metric-cli:saleDays |
| 10 | `stores` | `decimalv3(20, 4)` | YES |  |  | 营业门店数；metric-cli:stores |
| 11 | `active_sku_count` | `decimalv3(20, 4)` | YES |  |  | 动销SKU数；metric-cli未注册；本期为空 |
| 12 | `order_store_rate` | `decimalv3(38, 6)` | YES |  |  | 订购渗透率；metric-cli:orderStoreRate |
| 13 | `store_order_amt` | `decimalv3(20, 4)` | YES |  |  | 订购额；metric-cli:storeOrderAmt |
| 14 | `store_order_qty` | `decimalv3(20, 4)` | YES |  |  | 订购数量；metric-cli:storeOrderQty |
| 15 | `receive_amt` | `decimalv3(20, 4)` | YES |  |  | 进货额；metric-cli:receiveAmt |
| 16 | `receive_qty` | `decimalv3(20, 4)` | YES |  |  | 进货数量；metric-cli:receiveQty |
| 17 | `sale_amt` | `decimalv3(20, 4)` | YES |  |  | 销售额；metric-cli:saleAmt |
| 18 | `bf19_sale_amt` | `decimalv3(20, 4)` | YES |  |  | 19点前销售额；metric-cli:bf19SaleAmt |
| 19 | `bf19_active_sku` | `decimalv3(20, 4)` | YES |  |  | 19点前动销；metric-cli未注册；本期为空 |
| 20 | `af19_sale_amt` | `decimalv3(20, 4)` | YES |  |  | 19点后销售额；metric-cli:af19SaleAmt |
| 21 | `sale_qty` | `decimalv3(20, 4)` | YES |  |  | 销售数量；metric-cli:saleQty |
| 22 | `bf19_sale_qty` | `decimalv3(20, 4)` | YES |  |  | 19点前销售数量；metric-cli:bf19SaleQty |
| 23 | `af19_sale_qty` | `decimalv3(20, 4)` | YES |  |  | 19点后销售数量；metric-cli:af19SaleQty |
| 24 | `cust_num` | `decimalv3(20, 4)` | YES |  |  | 来客数；metric-cli:custNum |
| 25 | `per_cust_amt` | `decimalv3(20, 4)` | YES |  |  | 客单价；metric-cli:perCustAmt |
| 26 | `bf19_cust_num` | `decimalv3(20, 4)` | YES |  |  | 19点前来客数；metric-cli:bf19CustNum |
| 27 | `bf19_per_cust_amt` | `decimalv3(20, 4)` | YES |  |  | 19点前客单价；metric-cli:bf19PerCustAmt |
| 28 | `af19_cust_num` | `decimalv3(20, 4)` | YES |  |  | 19点后来客数；metric-cli:af19CustNum |
| 29 | `af19_per_cust_amt` | `decimalv3(20, 4)` | YES |  |  | 19点后客单价；metric-cli:af19PerCustAmt |
| 30 | `discount_amt` | `decimalv3(20, 4)` | YES |  |  | 折扣额；metric-cli:discountAmt |
| 31 | `discount_rate` | `decimalv3(38, 6)` | YES |  |  | 折扣率；metric-cli:discountRate |
| 32 | `promotion_discount_amt` | `decimalv3(20, 4)` | YES |  |  | 促销折扣额；metric-cli:promotionDiscountAmt |
| 33 | `promotion_discount_rate` | `decimalv3(38, 6)` | YES |  |  | 促销折扣率；metric-cli:promotionDiscountRate |
| 34 | `hour_discount_amt` | `decimalv3(20, 4)` | YES |  |  | 时段折扣额；metric-cli:hourDiscountAmt |
| 35 | `hour_discount_rate` | `decimalv3(38, 6)` | YES |  |  | 时段折扣率；metric-cli:hourDiscountRate |
| 36 | `promotion_rate` | `decimalv3(38, 6)` | YES |  |  | 成本费用率；metric-cli:promotionRate |
| 37 | `shop_promotion_amt` | `decimalv3(20, 4)` | YES |  |  | 门店发起促销折扣额；metric-cli:shopPromotionAmt |
| 38 | `shop_promotion_rate` | `decimalv3(38, 6)` | YES |  |  | 门店发起促销折扣率；metric-cli:shopPromotionRate |
| 39 | `lost_amt` | `decimalv3(20, 4)` | YES |  |  | 损耗额；metric-cli:lostAmt |
| 40 | `lost_rate` | `decimalv3(38, 6)` | YES |  |  | 损耗率；metric-cli:lostRate |
| 41 | `allowance_profit_amt` | `decimalv3(20, 4)` | YES |  |  | 补贴后毛利额；metric-cli:allowanceProfitAmt |
| 42 | `allowance_profit_rate` | `decimalv3(38, 6)` | YES |  |  | 补贴后毛利率；metric-cli未注册；本期为空 |
| 43 | `afcoupon_profit_amt` | `decimalv3(20, 4)` | YES |  |  | 券后毛利额；metric-cli:afcouponProfitAmt |
| 44 | `profit_amt` | `decimalv3(20, 4)` | YES |  |  | 毛利额；metric-cli:profitAmt |
| 45 | `profit_rate` | `decimalv3(38, 6)` | YES |  |  | 毛利率；metric-cli:profitRate |
| 46 | `profit_lost_rate` | `decimalv3(38, 6)` | YES |  |  | 门店毛利率（分析）；metric-cli:profitLostRate |
| 47 | `pre_profit_rate` | `decimalv3(38, 6)` | YES |  |  | 预期销售毛利率；metric-cli:preProfitRate |
| 48 | `pre_price_profit_rate` | `decimalv3(38, 6)` | YES |  |  | 定价毛利率；metric-cli:prePriceProfitRate |
| 49 | `scm_store_profit_proportion` | `decimalv3(38, 6)` | YES |  |  | 供应链门店毛利配比；metric-cli:scmStoreProfitProportion |
| 50 | `full_link_store_profit_amt` | `decimalv3(20, 4)` | YES |  |  | 全链路到店毛利额(含税)；metric-cli:fullLinkStoreProfitAmt |
| 51 | `full_link_store_profit_rate` | `decimalv3(38, 6)` | YES |  |  | 全链路到店毛利率(含税)；metric-cli:fullLinkStoreProfitRate |
| 52 | `full_link_store_profit_amt_notax` | `decimalv3(20, 4)` | YES |  |  | 全链路到店毛利额(不含税)；metric-cli:fullLinkStoreProfitAmtNotax |
| 53 | `full_link_store_profit_notax_rate` | `decimalv3(38, 6)` | YES |  |  | 全链路到店毛利率(不含税)；metric-cli:fullLinkStoreProfitNotaxRate |

### dwd_date_shop_sku_qdm_brand_view

表说明：无

| 序号 | 字段名 | 字段类型 | 是否可空 | 键类型 | 默认值 | 字段注释 |
|---:|---|---|---|---|---|---|
| 1 | `dt` | `date` | NO |  |  |  |
| 2 | `store_id` | `varchar(64)` | NO |  |  |  |
| 3 | `store_name` | `varchar(255)` | YES |  |  |  |
| 4 | `group_manager_id` | `varchar(50)` | YES |  |  |  |
| 5 | `group_manager_name` | `varchar(255)` | YES |  |  |  |
| 6 | `zone_manager_id` | `varchar(50)` | YES |  |  |  |
| 7 | `zone_manager_name` | `varchar(255)` | YES |  |  |  |
| 8 | `city_id` | `varchar(20)` | YES |  |  |  |
| 9 | `city_name` | `varchar(255)` | YES |  |  |  |
| 10 | `sap_area_id` | `varchar(50)` | YES |  |  |  |
| 11 | `sap_area_name` | `varchar(255)` | YES |  |  |  |
| 12 | `manage_area_id` | `varchar(50)` | YES |  |  |  |
| 13 | `manage_area_name` | `varchar(255)` | YES |  |  |  |
| 14 | `sap_area2_id` | `varchar(50)` | YES |  |  |  |
| 15 | `sap_area2_name` | `varchar(255)` | YES |  |  |  |
| 16 | `article_id` | `varchar(64)` | NO |  |  |  |
| 17 | `article_name` | `string` | YES |  |  |  |
| 18 | `spu_id` | `string` | YES |  |  |  |
| 19 | `spu_name` | `string` | YES |  |  |  |
| 20 | `category_level3_id` | `string` | YES |  |  |  |
| 21 | `category_level3_name` | `string` | YES |  |  |  |
| 22 | `category_level2_id` | `string` | YES |  |  |  |
| 23 | `category_level2_name` | `string` | YES |  |  |  |
| 24 | `category_level1_id` | `string` | YES |  |  |  |
| 25 | `category_level1_name` | `string` | YES |  |  |  |
| 26 | `brand_id` | `string` | YES |  |  |  |
| 27 | `brand_name` | `string` | YES |  |  |  |
| 28 | `matnr_id` | `string` | YES |  |  |  |
| 29 | `matnr_name` | `string` | YES |  |  |  |
| 30 | `purchase_group_id` | `string` | YES |  |  |  |
| 31 | `purchase_group_name` | `string` | YES |  |  |  |
| 32 | `purchase_department_id` | `string` | YES |  |  |  |
| 33 | `purchase_department_name` | `string` | YES |  |  |  |
| 34 | `superior_purchase_department_id` | `string` | YES |  |  |  |
| 35 | `superior_purchase_department_name` | `string` | YES |  |  |  |
| 36 | `scm_store_profit_amt_notax` | `decimalv3(20, 4)` | YES |  |  |  |
| 37 | `scm_store_profit_notax_rate` | `decimalv3(38, 6)` | YES |  |  |  |
| 38 | `scm_store_profit_amt` | `decimalv3(20, 4)` | YES |  |  |  |
| 39 | `scm_store_profit_rate` | `decimalv3(38, 6)` | YES |  |  |  |
| 40 | `pre_scm_profit_amt` | `decimalv3(20, 4)` | YES |  |  |  |
| 41 | `scm_pre_profit_rate` | `decimalv3(38, 6)` | YES |  |  |  |
| 42 | `sale_days` | `decimalv3(20, 4)` | YES |  |  |  |
| 43 | `stores` | `decimalv3(20, 4)` | YES |  |  |  |
| 44 | `active_sku_count` | `decimalv3(20, 4)` | YES |  |  |  |
| 45 | `order_store_rate` | `decimalv3(38, 6)` | YES |  |  |  |
| 46 | `store_order_amt` | `decimalv3(20, 4)` | YES |  |  |  |
| 47 | `store_order_qty` | `decimalv3(20, 4)` | YES |  |  |  |
| 48 | `receive_amt` | `decimalv3(20, 4)` | YES |  |  |  |
| 49 | `receive_qty` | `decimalv3(20, 4)` | YES |  |  |  |
| 50 | `sale_amt` | `decimalv3(20, 4)` | YES |  |  |  |
| 51 | `bf19_sale_amt` | `decimalv3(20, 4)` | YES |  |  |  |
| 52 | `bf19_active_sku` | `decimalv3(20, 4)` | YES |  |  |  |
| 53 | `af19_sale_amt` | `decimalv3(20, 4)` | YES |  |  |  |
| 54 | `sale_qty` | `decimalv3(20, 4)` | YES |  |  |  |
| 55 | `bf19_sale_qty` | `decimalv3(20, 4)` | YES |  |  |  |
| 56 | `af19_sale_qty` | `decimalv3(20, 4)` | YES |  |  |  |
| 57 | `cust_num` | `decimalv3(20, 4)` | YES |  |  |  |
| 58 | `per_cust_amt` | `decimalv3(20, 4)` | YES |  |  |  |
| 59 | `bf19_cust_num` | `decimalv3(20, 4)` | YES |  |  |  |
| 60 | `bf19_per_cust_amt` | `decimalv3(20, 4)` | YES |  |  |  |
| 61 | `af19_cust_num` | `decimalv3(20, 4)` | YES |  |  |  |
| 62 | `af19_per_cust_amt` | `decimalv3(20, 4)` | YES |  |  |  |
| 63 | `discount_amt` | `decimalv3(20, 4)` | YES |  |  |  |
| 64 | `discount_rate` | `decimalv3(38, 6)` | YES |  |  |  |
| 65 | `promotion_discount_amt` | `decimalv3(20, 4)` | YES |  |  |  |
| 66 | `promotion_discount_rate` | `decimalv3(38, 6)` | YES |  |  |  |
| 67 | `hour_discount_amt` | `decimalv3(20, 4)` | YES |  |  |  |
| 68 | `hour_discount_rate` | `decimalv3(38, 6)` | YES |  |  |  |
| 69 | `promotion_rate` | `decimalv3(38, 6)` | YES |  |  |  |
| 70 | `shop_promotion_amt` | `decimalv3(20, 4)` | YES |  |  |  |
| 71 | `shop_promotion_rate` | `decimalv3(38, 6)` | YES |  |  |  |
| 72 | `lost_amt` | `decimalv3(20, 4)` | YES |  |  |  |
| 73 | `lost_rate` | `decimalv3(38, 6)` | YES |  |  |  |
| 74 | `allowance_profit_amt` | `decimalv3(20, 4)` | YES |  |  |  |
| 75 | `allowance_profit_rate` | `decimalv3(38, 6)` | YES |  |  |  |
| 76 | `afcoupon_profit_amt` | `decimalv3(20, 4)` | YES |  |  |  |
| 77 | `profit_amt` | `decimalv3(20, 4)` | YES |  |  |  |
| 78 | `profit_rate` | `decimalv3(38, 6)` | YES |  |  |  |
| 79 | `profit_lost_rate` | `decimalv3(38, 6)` | YES |  |  |  |
| 80 | `pre_profit_rate` | `decimalv3(38, 6)` | YES |  |  |  |
| 81 | `pre_price_profit_rate` | `decimalv3(38, 6)` | YES |  |  |  |
| 82 | `scm_store_profit_proportion` | `decimalv3(38, 6)` | YES |  |  |  |
| 83 | `full_link_store_profit_amt` | `decimalv3(20, 4)` | YES |  |  |  |
| 84 | `full_link_store_profit_rate` | `decimalv3(38, 6)` | YES |  |  |  |
| 85 | `full_link_store_profit_amt_notax` | `decimalv3(20, 4)` | YES |  |  |  |
| 86 | `full_link_store_profit_notax_rate` | `decimalv3(38, 6)` | YES |  |  |  |
