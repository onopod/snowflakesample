import unittest
from copy import deepcopy
from datetime import date
from cashflow import add_months, dated_npv, monthly_cashflows, project_cashflows, future_totals, plan_actual_variances
from sample_data import load_demo, DEFAULT_AS_OF, OPENING_DATE, OPENING_CASH
class CashflowTests(unittest.TestCase):
 def setUp(self): self.p,self.e=load_demo()
 def run_flow(self,**kw): return project_cashflows(self.p,self.e,DEFAULT_AS_OF,**kw)
 def test_normal_data_and_cash(self):
  f=self.run_flow();self.assertEqual(len(f),54)
  m=monthly_cashflows(f,OPENING_CASH,OPENING_DATE)
  self.assertEqual(len(m),24);self.assertEqual(m[0]['月末残高'],90_000_000)
  self.assertEqual(m[-1]['月末残高'],201_550_000)
 def test_actual_replaces_plan(self):
  self.e[1]['actual_amount']=-101_000_000
  f=self.run_flow(); self.assertEqual(len(f),54)
  self.assertEqual(sum(x['amount'] for x in f if x['kind']=='実績'),-31_000_000)
 def test_delay_and_interest(self):
  b=self.run_flow(); d=self.run_flow(delay_months=3)
  self.assertEqual(len(d),63)
  sale=next(x for x in d if x['event_id']=='P001-sale')
  self.assertEqual(sale['date'],date(2027,7,15))
  self.assertEqual(sum(x['amount'] for x in b)-sum(x['amount'] for x in d),1_725_000)
 def test_fee_delay(self):
  d=self.run_flow(delay_months=3)
  self.assertEqual(next(x['date'] for x in d if x['event_id']=='P001-fee-7'),date(2027,8,15))
 def test_price_change(self):
  f=self.run_flow(sale_change_pct=-10)
  self.assertEqual(next(x['amount'] for x in f if x['event_id']=='P001-sale'),115_200_000)
 def test_immutable(self):
  original=deepcopy(self.e);self.run_flow(delay_months=3);self.assertEqual(self.e,original)
 def test_overdue_not_actual(self):
  self.e[2]['planned_date']='2026-10-01'
  f=self.run_flow();x=next(x for x in f if x['event_id']==self.e[2]['event_id'])
  self.assertEqual(x['date'],date(2026,10,29));self.assertEqual(x['kind'],'予測')
 def test_month_end(self): self.assertEqual(add_months(date(2024,1,31),1),date(2024,2,29))
 def test_npv_excludes_debt(self):
  rows=[{'date':date(2026,1,1),'category':'land_purchase','amount':-100},{'date':date(2027,1,1),'category':'land_sale','amount':110},{'date':date(2026,1,1),'category':'loan_draw','amount':500}]
  self.assertAlmostEqual(dated_npv(rows,.1,date(2026,1,1)),0)
 def test_period_carries_opening_balance(self):
  f=self.run_flow(); all_rows=monthly_cashflows(f,OPENING_CASH,OPENING_DATE,24)
  subset=monthly_cashflows(f,OPENING_CASH,date(2027,1,1),12)
  self.assertEqual(subset,all_rows[3:15])
 def test_future_totals_exclude_actual(self):
  f=self.run_flow()
  self.assertEqual(future_totals(f,DEFAULT_AS_OF,OPENING_DATE,date(2028,10,1)),(600_000_000,488_450_000))
 def test_variance_null_pending_zero_actual(self):
  self.e[1]['actual_amount']=0
  comparisons=plan_actual_variances(self.e,OPENING_DATE,date(2028,10,1))
  actual=next(e for e in comparisons if e['event_id']==self.e[1]['event_id'])
  self.assertEqual(actual['variance'],100_000_000)
  self.assertEqual(actual['status'],'確定')
  self.assertTrue(all(e['variance'] is None for e in comparisons if e['status']=='未確定'))
 def test_future_actual_rejected(self):
  self.e[0]['actual_date']='2028-01-01'
  with self.assertRaises(ValueError): self.run_flow()
 def test_incomplete_actual_rejected(self):
  self.e[0]['actual_amount']=None
  with self.assertRaises(ValueError): self.run_flow()
 def test_duplicate_rejected(self):
  self.e.append(self.e[0].copy())
  with self.assertRaises(ValueError):self.run_flow()
if __name__=='__main__': unittest.main()
