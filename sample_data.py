from datetime import date
from cashflow import add_months

OPENING_DATE = date(2026,10,1)
OPENING_CASH = 120_000_000
DEFAULT_AS_OF = date(2026,10,28)

def load_demo():
    projects, events = [], []
    for idx,(name,offset,cost,sale,loan) in enumerate([
        ('湾岸冷凍倉庫用地（架空）',0,100_000_000,128_000_000,70_000_000),
        ('北部物流用地（架空）',3,150_000_000,188_000_000,100_000_000),
        ('西部自動倉庫用地（架空）',8,90_000_000,115_000_000,60_000_000),
    ],1):
        pid=f'P{idx:03}'
        buy=add_months(date(2026,10,15),offset)
        sell=add_months(buy,6)
        projects.append({'project_id':pid,'project_name':name,'location':'架空地域','loan_principal':loan,'annual_interest_rate':0.03})
        def add(suffix,when,category,amount,counterparty):
            paid=when<=DEFAULT_AS_OF
            events.append({'event_id':f'{pid}-{suffix}','project_id':pid,'counterparty':counterparty,'category':category,'planned_date':str(when),'planned_amount':amount,'actual_date':str(when) if paid else None,'actual_amount':amount if paid else None})
        add('draw',buy,'loan_draw',loan,'架空金融機関')
        add('land',buy,'land_purchase',-cost,'架空土地所有者')
        add('survey',add_months(buy,1),'survey',-2_000_000,'架空調査設計会社')
        add('tax',add_months(buy,2),'tax_fee',-3_000_000,'架空税費用先')
        for m in range(1,7):
            add(f'interest-{m}',add_months(buy,m),'interest',-round(loan*.03/12),'架空金融機関')
        add('sale',sell,'land_sale',sale,'架空開発ファンド')
        add('repay',sell,'principal_repayment',-loan,'架空金融機関')
        for m in range(7,13):
            add(f'fee-{m}',add_months(buy,m),'management_fee',500_000,'架空開発ファンド')
    return projects,events
