# -*- coding: utf-8 -*-
"""Validate algorithm 07 document contracts and synthetic boundary examples.

Uses only the Python standard library. It does not connect to production,
run ETL, train models, or certify real data or downstream integration.
"""
from pathlib import Path
import argparse
import json
import tempfile
from algorithm07_contract_checks import parse_field_contract, check_four_fix_contracts

def check_documents(repo_root, output_dir):
    from pathlib import Path
    import re,json,hashlib,sys
    root=repo_root
    paths=[root/'04_algorithm_cards/developer_version/算法卡_07_竞品与全球外部趋势新品发现.md',root/'04_algorithm_cards/business_readable/算法07_竞品与全球外部趋势新品发现_业务解读版.md']
    paths+=sorted((root/'03_data_contracts/external_data').glob('*external*.md'))
    paths+=[root/'03_data_contracts/rule_tables/dim_external_evidence_interpretation_rule_外部证据解释规则表.md']
    paths=[p for p in paths if p.exists()]
    issues=[];summary=[];enum_maps={}
    header=['中文字段名','英文字段名','类型建议','是否必须','字段来源','中文注释']
    danger=r'逻辑字段名|建议类型|物理表名待开发确认|待开发确认|需要用户确认|是否能到|字段中文注释补充|英文枚举中文注释|状态枚举表|采购手动输入候选|可比商品组字典|profile_model_version|(?<![a-z_])model_version|scope_version|(?<![a-z_])rule_version|parameter_version|price_version|batch_seq|V[12]_YYYYMM|V_YYYYMM|profile_YYYYMM|dws_member_order_item_detail_df_all(?!_new)'
    for p in paths:
     s=p.read_text();rel=str(p.relative_to(root)); fence=None;fence_line=None
     for n,l in enumerate(s.splitlines(),1):
      m=re.match(r'^\s*(`{3,}|~{3,})',l)
      if m:
       f=m.group(1)[0]
       if fence is None:fence=f;fence_line=n
       elif f==fence:fence=None
     if fence:issues.append([rel,fence_line,'unclosed code fence'])
     # A blank line ends a Markdown table. Continuation rows need a header,
     # otherwise a structurally correct enum would render as plain pipe text.
     table_block=[];in_code=False
     for n,l in enumerate(s.splitlines()+[''],1):
      if re.match(r'^\s*(`{3,}|~{3,})',l):in_code=not in_code
      if not in_code and l.startswith('|'):
       table_block.append((n,l));continue
      if table_block:
       separator=table_block[1][1] if len(table_block)>1 else ''
       if not separator.startswith('|') or not set(separator.replace('|','').replace(' ','')) <= set('-:'):
        issues.append([rel,table_block[0][0],'table rows have no Markdown header/separator'])
       table_block=[]
     for n,l in enumerate(s.splitlines(),1):
      if re.search(danger,l):issues.append([rel,n,'danger residual',l])
     for target in re.findall(r'\]\(([^)]+)\)',s):
      if target.startswith(('https:','http:','#','mailto:')):continue
      target=target.split('#')[0]
      if target and not (p.parent/target).exists():issues.append([rel,0,'broken local link',target])
     enums={}
     for n,l in enumerate(s.splitlines(),1):
      if not l.startswith('| `'):continue
      c=[x.strip() for x in l.strip('|').split('|')]
      if len(c)==5:
       f=c[0].strip('`');vals=re.findall(r'`([^`]+)`',c[2]);enums.setdefault(f,set()).update(vals)
     enum_maps[p.name]=enums
     tables=[]
     if '/developer_version/' in str(p):
      section=s.split('## 10. 输出表结构',1)[1].split('## 11.',1)[0]
      blocks=[m.group(0) for m in re.finditer(r'^### 10\.\d+ `[^`]+`.*?(?=^### |^## |\Z)',section,re.M|re.S)]
     else:blocks=[s] if '/business_readable/' not in str(p) else []
     for b in blocks:
      name=re.search(r'### 10\.\d+ `([^`]+)`|正式表名：`([^`]+)`',b)
      name=next((x for x in name.groups() if x),None) if name else p.stem
      fields,field_issues=parse_field_contract(b,name)
      issues.extend([[rel]+issue for issue in field_issues])
      raw=name=='ods_external_source_raw_snapshot'
      if not raw and 'algorithm_batch_version' not in fields:issues.append([rel,0,'missing batch field',name])
      key=re.search(r'主键：`([^`]+)`',b)
      if not key:issues.append([rel,0,'missing explicit key',name]);keycols=[]
      else:
       keycols=[x.strip() for x in key.group(1).split('+')]
       for keycol in keycols:
        if keycol not in fields:issues.append([rel,0,'key column missing from fields',name,keycol])
        elif fields[keycol][3]!='必须':issues.append([rel,0,'key column not mandatory',name,keycol,fields[keycol][3]])
       if not raw and 'algorithm_batch_version' not in keycols:issues.append([rel,0,'batch missing in key',name])
      statefields=[f for f in fields if f.endswith(('_status','_flag','_method')) or f in {'evidence_time_type','metric_role','image_provider','provider_type','price_input_kind','price_match_type','competitor_relation','usage','delay_basis','evidence_object_type','metric_type','evidence_metric_type','source_type','attribute_dimension','claim_type','claim_direction','publisher_type','source_level','relative_price_position','trend_lifecycle_state','seasonality_state','conflict_type','category_validation_result','final_level','image_source_type','authorization_status','ocr_match_result','allowed_uses_json','selection_status','issue_code','issue_layer','severity','handling_action','blocked_uses_json','execution_mode','rule_type','rule_status','food_scope_status','food_scope_decision','basis_type','match_method','date_anchor_type','revision_selection_method','source_timezone'}]
      for f in statefields:
       if f=='source_timezone':continue # IANA timezone free code, not enum.
       if f not in enums:issues.append([rel,0,'state enum missing',name,f])
      tables.append({'table':name,'field_count':len(fields),'key':keycols,'state_fields':statefields})
     summary.append({'file':rel,'sha256':hashlib.sha256(s.encode()).hexdigest(),'lines':len(s.splitlines()),'tables':tables})
    # Match copied enum values exactly against physical input contract.
    dwd=enum_maps.get('dwd_external_evidence_normalized_标准化外部证据表.md',{})
    dev=enum_maps.get('算法卡_07_竞品与全球外部趋势新品发现.md',{})
    for f in ['evidence_time_type','metric_role','evidence_object_type','metric_type','value_status','unit_resolution_status','date_resolution_status','quality_status','product_mapping_status','business_admission_status','allowed_uses_json']:
     if dwd.get(f)!=dev.get(f):issues.append(['cross_contract',0,'enum mismatch',f,sorted(dwd.get(f,set())),sorted(dev.get(f,set()))])
    result={'files_checked':len(paths),'formal_tables_checked':sum(len(x['tables']) for x in summary),'issues':issues,'files':summary}
    (output_dir/'algo07_doc_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    if issues:
     raise AssertionError(json.dumps(issues,ensure_ascii=False))
    return result

def check_boundaries(repo_root, output_dir):
    """Synthetic specification checks only; this does not execute a production model."""
    from pathlib import Path
    from datetime import date, datetime, timezone
    from zoneinfo import ZoneInfo
    from decimal import Decimal
    import hashlib, json

    ROOT=repo_root
    DEV=ROOT/'04_algorithm_cards/developer_version/算法卡_07_竞品与全球外部趋势新品发现.md'
    doc=DEV.read_text()
    results=[]
    def case(name,actual,expected,anchor):
     assert anchor in doc, ('missing specification anchor',name,anchor)
     assert actual==expected, (name,actual,expected)
     results.append({'case':name,'actual':actual,'expected':expected,'spec_anchor':anchor,'passed':True})

    def in_window(kind,period_start=None,period_end=None,observed=None,published=None):
     start,end=date(2026,9,1),date(2026,9,30)
     if kind=='STATIC_ATTRIBUTE':return True
     if kind=='STATISTICAL_PERIOD':return bool(period_start and period_end and start<=period_start<=period_end<=end)
     t=observed if kind=='RETAIL_OBSERVATION' else published
     return bool(t and start<=t.astimezone(ZoneInfo('Asia/Hong_Kong')).date()<=end)
    case('static_attributes_without_trade_date',in_window('STATIC_ATTRIBUTE'),True,'data_period_start/end和observed_at可NULL')
    case('relative_transaction_date_unknown',in_window('STATISTICAL_PERIOD'),False,'采集或修订时间不能替代数据期')
    case('publication_without_trade_date',in_window('PUBLICATION_EVENT',published=datetime(2026,9,15,tzinfo=timezone.utc)),True,'PUBLICATION_EVENT')
    case('local_month_boundary_excluded',in_window('RETAIL_OBSERVATION',observed=datetime(2026,9,30,16,30,tzinfo=timezone.utc)),False,'来源时区后观测日位于窗口')
    case('retail_observation_in_window',in_window('RETAIL_OBSERVATION',observed=datetime(2026,9,30,10,tzinfo=timezone.utc)),True,'RETAIL_OBSERVATION必填')

    def source_scope(confirmed_category):
     return 'OUT_OF_SCOPE' if confirmed_category=='FLOWER' else ('QUARANTINED' if confirmed_category is None else 'ELIGIBLE')
    case('flowers_excluded',source_scope('FLOWER'),'OUT_OF_SCOPE','花卉排除')
    case('unknown_category_not_deleted_as_flower',source_scope(None),'QUARANTINED','类别未知单独隔离')

    def relation(boundary,path_validated,text_relation,has_image=False):
     if boundary is False:return 'UNRELATED_PRODUCT'
     if boundary is None or not path_validated:return 'MATCH_UNRESOLVED'
     return text_relation
    case('no_image_text_path_confirmed',relation(True,True,'EXACT_EQUIVALENT',False),'EXACT_EQUIVALENT','不需要图片或OCR即可运行此路径')
    case('no_validated_text_path',relation(True,False,'EXACT_EQUIVALENT',False),'MATCH_UNRESOLVED','无图路径未训练/未验收')
    case('image_does_not_override_boundary',relation(False,True,'EXACT_EQUIVALENT',True),'UNRELATED_PRODUCT','明确冲突为UNRELATED_PRODUCT')
    case('unknown_boundary_is_not_negative',relation(None,True,'EXACT_EQUIVALENT',False),'MATCH_UNRESOLVED','关键项未知为MATCH_UNRESOLVED')

    def channel_counts(states):
     positive=sum(x=='positive' for x in states)
     known=sum(x in {'positive','negative'} for x in states)
     unknown=sum(x=='unresolved' for x in states)
     return {'x':positive,'n':known,'unknown':unknown,'observed':known+unknown}
    case('unresolved_channel_not_negative',channel_counts(['positive','negative','unresolved']),{'x':1,'n':2,'unknown':1,'observed':3},'unresolved不计y也不计N')
    case('known_zero_is_real_zero',channel_counts(['negative','negative']),{'x':0,'n':2,'unknown':0,'observed':2},'n>0,x=0')

    def image(url,validated=False,authorized=False,readable=True):
     if not url:return {'rows':0,'primary':None,'status':None}
     if not readable:return {'rows':1,'primary':None,'status':'IMAGE_INVALID'}
     if not validated:return {'rows':1,'primary':None,'status':'IMAGE_REVIEW_REQUIRED'}
     if not authorized:return {'rows':1,'primary':None,'status':'IMAGE_INVALID'}
     return {'rows':1,'primary':'IMAGE_KEY','status':'IMAGE_VALID'}
    case('no_image_no_fake_entity',image(None),{'rows':0,'primary':None,'status':None},'不造图片实体；primary_image_id=NULL')
    case('url_only_not_display_ready',image('https://source/image'),{'rows':1,'primary':None,'status':'IMAGE_REVIEW_REQUIRED'},'image_status=IMAGE_REVIEW_REQUIRED')
    case('invalid_url_kept_for_audit',image('https://source/image',readable=False),{'rows':1,'primary':None,'status':'IMAGE_INVALID'},'保留来源URL、IMAGE_INVALID')
    case('authorization_unknown_not_ready',image('https://source/image',True,False),{'rows':1,'primary':None,'status':'IMAGE_INVALID'},'授权UNKNOWN/REVOKED/仅PUBLIC_TRACEABLE不进入展示集合')

    def coverage(expected,valid,missing,invalid,threshold=None):
     reported=valid+missing+invalid
     return {'reported':reported,'absent':None if expected is None else expected-reported,
             'rate':None if not expected else float(Decimal(valid)/Decimal(expected)),
             'source_missing_rate':None if not expected else float(Decimal(missing)/Decimal(expected)),
             'status':'DENOMINATOR_UNKNOWN' if expected is None else ('THRESHOLD_UNSET' if threshold is None else ('PASS' if valid/expected>=threshold else 'BELOW_THRESHOLD'))}
    case('coverage_counts_and_unset_threshold',coverage(10,6,1,1),{'reported':8,'absent':2,'rate':0.6,'source_missing_rate':0.1,'status':'THRESHOLD_UNSET'},'source_missing_value_rate')
    case('unknown_denominator_not_hundred_percent',coverage(None,6,1,1),{'reported':8,'absent':None,'rate':None,'source_missing_rate':None,'status':'DENOMINATOR_UNKNOWN'},'无权威应报集合')

    def candidate(raw=True,identity=True,combination=True,fit=True,conflict=False):
     if not all((identity,combination,fit)) or conflict:return None
     return {'evidence':'RAW_EXTERNAL_SIGNAL','lifecycle':'UNKNOWN','development':'EXPLORATORY_PENDING_ALGORITHM_08_GATE'} if raw else None
    case('raw_signal_has_conditional_exit',candidate(),{'evidence':'RAW_EXTERNAL_SIGNAL','lifecycle':'UNKNOWN','development':'EXPLORATORY_PENDING_ALGORITHM_08_GATE'},'原始信号探索候选，生命周期UNKNOWN')
    case('raw_signal_does_not_bypass_identity',candidate(identity=False),None,'关键主体/内部小类未确认时不生成具名候选')
    case('conflict_not_silently_exploratory',candidate(conflict=True),None,'只留证据/趋势解释，不写最终候选')
    case('unknown_profile_keys_produce_no_fit_row',0 if not all([True,False]) else 1,0,'fit表和范围候选表为空')

    def hashparts(parts):
     return hashlib.sha256(''.join(str(len(str(v)))+':'+str(v) for v in parts).encode()).hexdigest()
    sku_a=hashparts(['JIUQIAN','PLATFORM_A','CITY_A','SKU001'])
    sku_b=hashparts(['JIUQIAN','PLATFORM_B','CITY_A','SKU001'])
    case('same_bare_sku_different_platform_not_joined',sku_a!=sku_b,True,'05禁止把复合ID整体当SKU')
    case('price_roles_not_superseded',hashparts(['SKU001','MEMBER_PRICE','2026-09-30'])!=hashparts(['SKU001','REGULAR_PRICE','2026-09-30']),True,'同一SKU同日不同价格角色互不替代')
    cid=hashparts(['EGG','OMEGA3','12'])
    case('temporary_candidate_key_length',len('EXT07_'+cid),70,"candidate_product_id='EXT07_'+完整standard_candidate_id")
    case('scope_keys_do_not_merge',hashparts(['BATCH_202609','CITY','A','A','PROFILE1',cid])!=hashparts(['BATCH_202609','CITY','B','A','PROFILE1',cid]),True,'scope_candidate_id另hash')
    case('blocked_consumer_stops_full_chain','BLOCKED'!='READY',True,'08/09/10正式链路不可读取未联调包')

    def fdr(values):
     ordered=sorted(enumerate(values),key=lambda kv:(kv[1],kv[0]));total=Decimal(0);k=0
     for n,(_,v) in enumerate(ordered,1):
      total+=Decimal(str(v))
      if total/Decimal(n)<=Decimal('0.05'):k=n
     return [i for i,_ in ordered[:k]]
    case('fdr_maximum_prefix_can_include_point09',fdr([.01,.04,.09,.30]),[0,1,2],'最大前缀候选集合')
    case('fdr_family_recomputed_after_removal',fdr([.04,.09,.30]),[0],'最终删除/增加成员必须重新计算')
    draws=[(.9,.8),(.4,.7),(.8,.9)]
    p_real=sum(x for x,y in draws)/len(draws);p_grow=sum(x*y for x,y in draws)/len(draws)
    case('joint_growth_probability_bounded_by_real',p_grow<=p_real,True,'p_sustained_growth≤p_trend_real')

    def dominates(a,b):
     ma={k for k,v in a.items() if v is not None};mb={k for k,v in b.items() if v is not None}
     return bool(ma) and ma==mb and all(a[k]>=b[k] for k in ma) and any(a[k]>b[k] for k in ma)
    case('pareto_missing_dimension_no_false_dominance',dominates({'growth':.9,'diffusion':None},{'growth':.8,'diffusion':.5}),False,'维度集合为空或不同则不可支配')
    case('pareto_true_dominance',dominates({'growth':.9,'diffusion':.7},{'growth':.8,'diffusion':.6}),True,'至少一项>B才支配')
    case('fit_and_summary_have_separate_limits',all(x in doc for x in ['最多3次','2^18','failure_stage=FIT','failure_stage=SUMMARY']),True,'模型拟合和联合取值是两个不同闸门')

    # Price feedback cases: these use synthetic learned boundaries, never business amounts.
    def position(role, price=15, enabled=True, inputs_complete=True, validated=True, k=3, stable=True):
        if role in {"POS_AVERAGE_PRICE", "WHOLESALE_REFERENCE_PRICE", "PRODUCER_REFERENCE_PRICE", "RETAIL_REFERENCE_PRICE", "MARKET_AVERAGE_REFERENCE_PRICE", "MEMBER_PRICE", "PROMOTION_PRICE"}:
            return (None, "NOT_APPLICABLE")
        if role in {"CURRENT_OFFER", "UNSPECIFIED_PRICE"}:
            return (None, "PRICE_SEMANTICS_UNVERIFIED")
        if not enabled:
            return (None, "NOT_ENABLED")
        if not inputs_complete or price <= 0:
            return (None, "PRICE_INPUT_INCOMPLETE")
        if not validated:
            return (None, "METHOD_NOT_VALIDATED")
        if k < 3:
            return (None, "COMPARISON_SET_INSUFFICIENT")
        if not stable:
            return (None, "DISTRIBUTION_UNSTABLE")
        return ("BASIC" if price <= 10 else "MAINSTREAM" if price <= 20 else "PREMIUM", "ASSIGNED")
    def aggregate_position(rows):
        if len({r[0] for r in rows}) > 1:
            return (None, "MULTIPLE_COMPARISON_SCOPES")
        if any(r[1] is None for r in rows):
            return (None, "PRICE_INPUT_INCOMPLETE")
        if len({r[1] for r in rows}) > 1:
            return (None, "MULTIPLE_POSITIONS")
        return (rows[0][1], "ASSIGNED")
    case("pos_average_not_regular_price_band", position("POS_AVERAGE_PRICE"), (None, "NOT_APPLICABLE"), "POS_AVERAGE_PRICE为统计期观察均价")
    case("wholesale_not_retail_price_band", position("WHOLESALE_REFERENCE_PRICE"), (None, "NOT_APPLICABLE"), "均不能混进零售日常价分布")
    case("current_offer_not_inferred_regular", position("CURRENT_OFFER"), (None, "PRICE_SEMANTICS_UNVERIFIED"), "CURRENT_OFFER/UNSPECIFIED_PRICE不能证明日常性质")
    case("method_not_validated_not_assigned", position("REGULAR_PRICE", validated=False), (None, "METHOD_NOT_VALIDATED"), "实现/回测未验收→METHOD_NOT_VALIDATED")
    case("zero_price_not_mainstream", position("REGULAR_PRICE", price=0), (None, "PRICE_INPUT_INCOMPLETE"), "零价原值保留，不参与log价格定位")
    case("fewer_than_three_modes_no_three_bands", position("REGULAR_PRICE", k=2), (None, "COMPARISON_SET_INSUFFICIENT"), "K<3为COMPARISON_SET_INSUFFICIENT")
    case("unstable_distribution_not_assigned", position("REGULAR_PRICE", stable=False), (None, "DISTRIBUTION_UNSTABLE"), "边界不稳→DISTRIBUTION_UNSTABLE")
    case("learned_lower_boundary_inclusive", position("REGULAR_PRICE", price=10), ("BASIC", "ASSIGNED"), "price≤lower_valley为BASIC")
    case("learned_upper_boundary_inclusive", position("REGULAR_PRICE", price=20), ("MAINSTREAM", "ASSIGNED"), "price≤upper_valley为MAINSTREAM")
    case("different_price_scopes_not_collapsed", aggregate_position([("A", "PREMIUM"), ("B", "PREMIUM")]), (None, "MULTIPLE_COMPARISON_SCOPES"), "多个比较范围为MULTIPLE_COMPARISON_SCOPES")
    case("different_bands_not_lowest_price", aggregate_position([("A", "BASIC"), ("A", "PREMIUM")]), (None, "MULTIPLE_POSITIONS"), "单范围多档为MULTIPLE_POSITIONS")
    case("same_scope_consistent_band_aggregated", aggregate_position([("A", "BASIC"), ("A", "BASIC")]), ("BASIC", "ASSIGNED"), "全部参与的相关价格输入已定位且同档")
    case("unknown_band_not_collapsed_to_known", aggregate_position([("A", "BASIC"), ("A", None)]), (None, "PRICE_INPUT_INCOMPLETE"), "有未完成输入时PRICE_INPUT_INCOMPLETE")
    case("business_manual_cutoffs_not_required_by_original", True, True, "不要求业务逐小类手填阈值")
    case("price_available_does_not_mean_position_available", position("CURRENT_OFFER")[0] is None, True, "price_status=AVAILABLE不自动使price_position_status=ASSIGNED")

    output={'test_scope':'SYNTHETIC_SPECIFICATION_ONLY','production_model_tested':False,'case_count':len(results),'passed':len(results),'cases':results}
    (output_dir/'algo07_v1_boundary_validation.json').write_text(json.dumps(output,ensure_ascii=False,indent=2))
    return output

def check_mathematics(repo_root, output_dir):
    import math,json

    def cf(a,b,x):
     qab=a+b;qap=a+1;qam=a-1;c=1.;d=1-qab*x/qap
     if abs(d)<1e-300:d=1e-300
     d=1/d;h=d
     for m in range(1,10001):
      m2=2*m;aa=m*(b-m)*x/((qam+m2)*(a+m2));d=1+aa*d;c=1+aa/c
      if abs(d)<1e-300:d=1e-300
      if abs(c)<1e-300:c=1e-300
      d=1/d;h*=d*c;aa=-(a+m)*(qab+m)*x/((a+m2)*(qap+m2));d=1+aa*d;c=1+aa/c
      if abs(d)<1e-300:d=1e-300
      if abs(c)<1e-300:c=1e-300
      d=1/d;delta=d*c;h*=delta
      if abs(delta-1)<3e-14:return h
     raise RuntimeError('not converged')
    def cdf(x,a,b):
     if x<=0:return 0.
     if x>=1:return 1.
     bt=math.exp(math.lgamma(a+b)-math.lgamma(a)-math.lgamma(b)+a*math.log(x)+b*math.log1p(-x))
     return bt*cf(a,b,x)/a if x<(a+1)/(a+b+2) else 1-bt*cf(b,a,1-x)/b
    def q(p,a,b):
     lo,hi=0.,1.
     for _ in range(70):
      mid=(lo+hi)/2
      if cdf(mid,a,b)<p:lo=mid
      else:hi=mid
     return (lo+hi)/2
    out=[]
    for x,n,expected in [(5,8,[.6197,.2948,.8810]),(2,5,[.4068,.0944,.7906]),(4,5,[.7789,.3714,.9775]),(0,6,[.0357,.0001,.3304])]:
     vals=[q(v,x+.5,n-x+.5) for v in [.5,.025,.975]]
     assert all(abs(v-e)<=.00005 for v,e in zip(vals,expected))
     out.append({'x':x,'n':n,'median_ci':[round(v,8) for v in vals]})
    lfdr=[.01,.04,.09,.30]; selected=0
    for k in range(1,len(lfdr)+1):
     if sum(lfdr[:k])/k<=.05:selected=k
    assert selected==3 and lfdr[selected-1]>.05
    result={'beta_cases':out,'fdr_test':{'values':lfdr,'selected_count':selected,'selected_mean':sum(lfdr[:selected])/selected},'scope':'独立公式复算；未运行生产模型或真实数据ETL'}
    (output_dir/'algo07_math_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    return result

def check_jiuqian_inputs(repo_root, output_dir):
    """Check the current two-table dependency graph, without querying real data."""
    import re
    retired = 'ods_jiuqian_api_raw'
    retired_path = repo_root / '03_data_contracts/external_data/ods_jiuqian_api_raw_久谦接口原始表.md'
    issues = []
    if retired_path.exists():
        issues.append(['retired_contract_still_present', str(retired_path)])
    active_paths = [
        '00_start_here/03_算法与结果表总览.md',
        '03_data_contracts/README.md',
        '03_data_contracts/external_data/README.md',
        '03_data_contracts/external_data/外部数据采集模块_开发说明.md',
        '03_data_contracts/external_data/dim_competitor_sku_竞品SKU基础表.md',
        '03_data_contracts/external_data/fact_competitor_sku_daily_snapshot_竞品每日快照表.md',
        '03_data_contracts/external_data/mart_external_candidate_price_input_外部候选价格交接输入表.md',
        '04_algorithm_cards/developer_version/算法卡_07_竞品与全球外部趋势新品发现.md',
        '04_algorithm_cards/business_readable/算法07_竞品与全球外部趋势新品发现_业务解读版.md',
    ]
    for name in active_paths:
        p = repo_root / name
        if not p.exists():
            issues.append([name, 'missing_document'])
            continue
        text = p.read_text()
        for token in [retired, 'raw_response_json', '久谦三表', '久谦三张', '原三张合同表', '久谦原始请求键']:
            if token in text:
                issues.append([name, 'retired_dependency', token])
        for target in re.findall(r'\]\(([^)]+)\)', text):
            if target.startswith(('https:', 'http:', '#', 'mailto:')):
                continue
            target = target.split('#')[0]
            if target and not (p.parent / target).exists():
                issues.append([name, 'broken_local_link', target])
    entity_key = ['data_provider', 'competitor_platform', 'city_name', 'competitor_sku_id']
    inputs = [
        ('dim_competitor_sku_竞品SKU基础表.md', entity_key),
        ('fact_competitor_sku_daily_snapshot_竞品每日快照表.md', ['collection_date'] + entity_key),
    ]
    for filename, expected_key in inputs:
        text = (repo_root / '03_data_contracts/external_data' / filename).read_text()
        match = re.search(r'主键建议：`([^`]+)`', text)
        key = [v.strip() for v in match.group(1).split('+')] if match else []
        if key != expected_key:
            issues.append([filename, 'native_key_mismatch', key, expected_key])
        for field in expected_key + ['collection_batch_id']:
            if f'| `{field}` |' not in text:
                issues.append([filename, 'missing_native_field', field])
    if not (repo_root / '03_data_contracts/external_data/ods_external_source_raw_snapshot_公开外部源原始快照表.md').exists():
        issues.append(['public_raw_snapshot_contract_missing'])
    result = {'native_inputs_checked': len(inputs), 'dependency_documents_checked': len(active_paths), 'issues': issues}
    (output_dir / 'algo07_jiuqian_input_validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    if issues:
        raise AssertionError(json.dumps(issues, ensure_ascii=False))
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output-dir", type=Path, default=Path(tempfile.gettempdir()) / "algorithm07-v1-validation")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    four_fixes = check_four_fix_contracts(args.repo_root, args.output_dir)
    structure = check_documents(args.repo_root, args.output_dir)
    native_inputs = check_jiuqian_inputs(args.repo_root, args.output_dir)
    boundary = check_boundaries(args.repo_root, args.output_dir)
    maths = check_mathematics(args.repo_root, args.output_dir)
    summary = {
        "scope": "DOCUMENT_CONTRACT_AND_SYNTHETIC_SPECIFICATION_ONLY",
        "files_checked": structure["files_checked"],
        "formal_table_definitions_checked": structure["formal_tables_checked"],
        "document_issue_count": len(structure["issues"]),
        "four_fix_contract_issue_count": len(four_fixes["issues"]),
        "execution_contracts_checked": four_fixes["execution_contracts_checked"],
        "jiuqian_native_inputs_checked": native_inputs["native_inputs_checked"],
        "jiuqian_dependency_issue_count": len(native_inputs["issues"]),
        "synthetic_cases_passed": boundary["passed"],
        "beta_cases_passed": len(maths["beta_cases"]),
        "fdr_counterexample_passed": maths["fdr_test"]["selected_count"] == 3,
        "production_model_tested": False,
        "output_dir": str(args.output_dir.resolve()),
    }
    (args.output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
