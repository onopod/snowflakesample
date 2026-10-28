"""Public, read-only fictional land-development cash-flow portfolio."""
import os
from datetime import date
import pandas as pd
import streamlit as st
from cashflow import LABELS, add_months, dated_npv, monthly_cashflows, project_cashflows, to_date, future_totals, plan_actual_variances
from sample_data import DEFAULT_AS_OF, OPENING_CASH, OPENING_DATE, load_demo
from data_source import load_snowflake

st.set_page_config(page_title='土地事業の資金収支', page_icon='📊', layout='wide')
st.title('土地事業の資金収支')
st.caption('架空の3案件・日本円。土地取得から売却までの自社キャッシュフローを確認できます。')
try:
    settings = dict(st.secrets.get('app', {}))
except FileNotFoundError:
    settings = {}
mode = os.environ.get('DATA_MODE', settings.get('mode', 'demo')).lower()

@st.cache_data(ttl=300, max_entries=1, show_spinner=False)
def fetch_data(source):
    if source == 'demo':
        return load_demo()
    if source != 'snowflake':
        raise ValueError('Invalid data mode')
    return load_snowflake(st.secrets['snowflake'])

try:
    projects, events = fetch_data(mode)
    if not projects or not events:
        raise ValueError('Empty data')
except Exception:
    st.error('データ取得に失敗しました。管理者が接続設定・読取権限・サンプルデータを確認してください。デモへの自動切替は行いません。')
    st.stop()
if mode == 'demo':
    st.warning('デモモード：同梱の架空データを表示中。Snowflakeには接続していません。')
else:
    st.success('Snowflake接続：架空データを取得済み（最大5分キャッシュ）。')

with st.sidebar:
    st.header('表示条件')
    names = {p['project_id']:p['project_name'] for p in projects}
    chosen = st.multiselect('案件', list(names), default=list(names), format_func=names.get)
    month_options = [str(add_months(OPENING_DATE, i))[:7] for i in range(36)]
    period = st.select_slider('表示期間（月）', options=month_options, value=(month_options[0], month_options[23]))
    last_actual = max([to_date(e['actual_date']) for e in events if e.get('actual_date')] or [OPENING_DATE])
    as_of = st.date_input('実績の基準日', value=max(DEFAULT_AS_OF,last_actual), min_value=last_actual)
    scenario = st.selectbox('シナリオ', ['標準', '売却3か月遅延', 'カスタム'])
    delay = 3 if scenario=='売却3か月遅延' else 0
    change = 0
    if scenario=='カスタム':
        delay = st.slider('売却・元本返済の遅延（月）', 0, 12, 0)
        change = st.slider('売却価格の増減（%）', -30, 30, 0)
    opening = st.number_input('開始時の現金残高（円）', min_value=0, value=OPENING_CASH, step=1_000_000)
    rate = st.slider('NPVの年割引率（%）', 0.0, 20.0, 5.0, 0.5)/100
    st.caption('条件変更はこの画面内だけに適用され、DBには保存されません。')
if not chosen:
    st.info('左側で案件を選択してください。')
    st.stop()
selected_projects = [p for p in projects if p['project_id'] in chosen]
selected_events = [e for e in events if e['project_id'] in chosen]
try:
    flows = project_cashflows(selected_projects, selected_events, as_of, delay, change)
except ValueError as exc:
    st.error(str(exc))
    st.stop()
start = date.fromisoformat(period[0]+'-01')
end = add_months(date.fromisoformat(period[1]+'-01'), 1)
months = (end.year-start.year)*12+end.month-start.month
rows = monthly_cashflows(flows, opening, start, months)
df = pd.DataFrame(rows).set_index('月')
actual_balance = opening + sum(e['amount'] for e in flows if e['kind']=='実績' and e['date']<=as_of)
cols = st.columns(3)
cols[0].metric('実績現金残高', f'{actual_balance:,.0f} 円')
minimum = min(rows, key=lambda r:r['月末残高'])
cols[1].metric('表示期間内の最低月末残高', f'{minimum["月末残高"]:,.0f} 円')
cols[1].caption(f'最低残高月：{minimum["月"]}（同額の場合は最初の月）')
cols[2].metric('表示期間末の予測残高', f'{rows[-1]["月末残高"]:,.0f} 円')
future_in, future_out = future_totals(flows, as_of, start, end)
future_cols = st.columns(2)
future_cols[0].metric('今後の入金（表示期間内）', f'{future_in:,.0f} 円')
future_cols[1].metric('今後の出金（表示期間内）', f'{future_out:,.0f} 円')
st.caption(f'表示 {period[0]}〜{period[1]}（{months}か月） ／ 初期残高の基準日 {OPENING_DATE} ／ 実績基準日 {as_of} ／ 入金は＋、出金は−。案件を絞った場合、選択外の入出金を除いた参考残高です。')
if min(r['月末残高'] for r in rows)<0:
    st.error('月末資金不足が発生する予測です。月中の最低残高はこのグラフでは判定できません。')
st.subheader('現金残高')
st.line_chart(df[['月末残高']], y_label='円')
st.subheader('月別入出金')
chart = df[['入金','出金']].copy()
chart['出金'] = -chart['出金']
st.bar_chart(chart, y_label='円', stack=False)
st.dataframe(df, width='stretch')
outside = [e for e in flows if e['date']>=end]
if outside:
    st.info(f'表示期間より後に {len(outside)} 件の入出金があります。NPVは全期間、入出金明細は表示期間内を対象としています。')
with st.expander('案件別収支・NPV'):
    result=[]
    for p in selected_projects:
        part=[e for e in flows if e['project_id']==p['project_id']]
        sales = [e for e in part if e['category']=='land_sale']
        acquisitions = [e for e in part if e['category']=='land_purchase']
        result.append({'案件':p['project_name'], '所在地':p['location'], '取得日（見込/実績）':', '.join(str(e['date']) for e in acquisitions), '当初売却予定日':', '.join(str(e['planned_date']) for e in sales), '売却日（見込/実績）':', '.join(str(e['date']) for e in sales), '売却状況':', '.join(e['kind'] for e in sales), '全期間の現金差引（円）':sum(e['amount'] for e in part), '事業NPV（円）':round(dated_npv(part,rate,OPENING_DATE))})
    st.dataframe(pd.DataFrame(result), hide_index=True, width='stretch')
    st.caption('NPVは開始日時点・ACT/365。借入、元本返済、利息を除いた事業キャッシュフローを割引。法人税・建物建築費は未設定。会社の現金残高や会計利益とは異なります。')
with st.expander('予実差（当初予定と実績）', expanded=False):
    comparisons = plan_actual_variances(selected_events, start, end)
    variance_columns = ['案件','費目','予定日','予定額（円）','実績日','実績額（円）','差額（円）','日数差','状態']
    variance = pd.DataFrame([{'案件':names[e['project_id']], '費目':LABELS[e['category']], '予定日':e['planned_date'], '予定額（円）':e['planned_amount'], '実績日':e['actual_date'], '実績額（円）':e['actual_amount'], '差額（円）':e['variance'], '日数差':e['delay_days'], '状態':e['status']} for e in comparisons], columns=variance_columns)
    st.dataframe(variance, hide_index=True, width='stretch')
    st.caption('予定日または実績日が表示期間内の明細。差額＝実績−当初予定、日数差＝実績日−予定日。未確定は空欄で、0円の実績とは区別します。シナリオの見込値を実績扱いしません。')
with st.expander('入出金明細', expanded=False):
    detail=pd.DataFrame([{'日付':str(e['date']), '案件':names[e['project_id']], '区分':e['kind'], '費目':LABELS[e['category']], '金額（円）':e['amount'], '相手先':e['counterparty']} for e in flows if start<=e['date']<end], columns=['日付','案件','区分','費目','金額（円）','相手先'])
    st.dataframe(detail, hide_index=True, width='stretch')
    st.download_button('表示明細をCSVで保存', detail.to_csv(index=False).encode('utf-8-sig'), 'fictional_cashflow.csv', 'text/csv')
with st.expander('計算ルール'):
    st.markdown('''- 実績がある明細は予定を置き換え、二重計上しません。部分入金は別明細に分割する設計です。
- 未入金・未払の過去予定は、基準日の翌日に繰り越します。将来の支払完了を自動判定しません。
- 遅延シナリオでは未実績の売却と元本返済を遅らせ、借入元本×年利÷12の追加利息を加えます。
- 売却後の管理報酬も売却遅延に合わせて後ろ倒しします。既存実績は変更しません。
- 元本一括返済の簡易モデルです。返済条件変更・複利・日割利息・消費税精算・法人税は未対応です。
- 公開用の架空データ専用です。実企業の財務情報や個人情報を登録しないでください。''')
