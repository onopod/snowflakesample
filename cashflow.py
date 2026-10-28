"""Deterministic, read-only fictional cash-flow projection. Amounts are integer JPY."""
from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

FINANCING = {'loan_draw', 'principal_repayment', 'interest'}
LABELS = {'land_purchase':'土地取得', 'survey':'調査設計', 'tax_fee':'税・諸費用', 'loan_draw':'借入実行', 'principal_repayment':'元本返済', 'interest':'利息', 'land_sale':'土地売却', 'management_fee':'管理報酬'}

def to_date(value):
    return value if isinstance(value, date) else date.fromisoformat(str(value)[:10])

def add_months(value, months):
    idx = value.year * 12 + value.month - 1 + months
    year, month = divmod(idx, 12)
    return date(year, month + 1, min(value.day, monthrange(year, month + 1)[1]))

def yen(value):
    return int(Decimal(str(value)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))

def validate(projects, events):
    project_ids = [p['project_id'] for p in projects]
    if len(set(project_ids)) != len(project_ids):
        raise ValueError('案件IDが重複しています')
    seen = set()
    for e in events:
        if e['event_id'] in seen: raise ValueError('明細IDが重複しています')
        seen.add(e['event_id'])
        if e['project_id'] not in project_ids: raise ValueError('不明な案件IDです')
        if e['category'] not in LABELS: raise ValueError('不明な費目です')
        to_date(e['planned_date'])
        if (e.get('actual_date') is None) != (e.get('actual_amount') is None):
            raise ValueError('実績日と実績金額は一緒に設定してください')
        for field in ['planned_amount', 'actual_amount']:
            if e.get(field) is not None and Decimal(str(e[field])) % 1:
                raise ValueError('金額は整数円で指定してください')
        if e.get('actual_date'): to_date(e['actual_date'])

def project_cashflows(projects, events, as_of, delay_months=0, sale_change_pct=0):
    """Actual replaces plan; unsettled overdue plans move to next day. Never mutate source."""
    validate(projects, events)
    as_of = to_date(as_of)
    if delay_months not in range(0, 13): raise ValueError('遅延月数は0〜12です')
    result = []
    for e in events:
        if e.get('actual_date') and to_date(e['actual_date']) > as_of:
            raise ValueError('基準日より未来の実績があります。基準日を進めてください')
        actual = e.get('actual_date') is not None
        d = to_date(e['actual_date'] if actual else e['planned_date'])
        amount = int(e['actual_amount'] if actual else e['planned_amount'])
        if not actual:
            if e['category'] in {'land_sale', 'principal_repayment', 'management_fee'}:
                d = add_months(d, delay_months)
            if e['category'] == 'land_sale':
                amount = yen(Decimal(amount) * (1 + Decimal(str(sale_change_pct))/100))
            d = max(d, as_of + timedelta(days=1))
        result.append({**e, 'date': d, 'amount': amount, 'kind': '実績' if actual else '予測'})
    # Simplified bullet loan: extra interest starts at original planned sale date.
    for p in projects:
        sales = [e for e in events if e['project_id']==p['project_id'] and e['category']=='land_sale' and not e.get('actual_date')]
        if delay_months and sales:
            sale_date = to_date(sales[0]['planned_date'])
            monthly = yen(Decimal(str(p['loan_principal'])) * Decimal(str(p['annual_interest_rate'])) / 12)
            for m in range(1, delay_months+1):
                result.append({'event_id':f"{p['project_id']}-delay-interest-{m}", 'project_id':p['project_id'], 'counterparty':'架空金融機関', 'category':'interest', 'planned_date':str(add_months(sale_date,m)), 'planned_amount':-monthly, 'actual_date':None, 'actual_amount':None, 'date':max(add_months(sale_date,m),as_of+timedelta(days=1)), 'amount':-monthly, 'kind':'予測'})
    return sorted(result, key=lambda e:(e['date'],e['event_id']))

def monthly_cashflows(events, opening_cash, start, months=24):
    start = to_date(start).replace(day=1)
    balance = int(opening_cash) + sum(e['amount'] for e in events if e['date'] < start)
    rows = []
    for i in range(months):
        left, right = add_months(start,i), add_months(start,i+1)
        values = [e['amount'] for e in events if left <= e['date'] < right]
        inflow, outflow = sum(v for v in values if v>0), -sum(v for v in values if v<0)
        balance += inflow-outflow
        rows.append({'月':str(left)[:7], '入金':inflow, '出金':outflow, '差引':inflow-outflow, '月末残高':balance})
    return rows

def dated_npv(events, rate, valuation_date):
    """Project pre-financing cash flow, not company cash balance; ACT/365, pre-tax demo."""
    if rate <= -1: raise ValueError('割引率は-100%より大きい必要があります')
    base = to_date(valuation_date)
    return sum(e['amount'] / (1+rate)**((e['date']-base).days/365) for e in events if e['category'] not in FINANCING)
