"""Run with dependencies installed: python -m unittest discover -s tests -v."""
import os
import unittest
from pathlib import Path
from unittest.mock import patch
try:
 from streamlit.testing.v1 import AppTest
except ImportError:
 AppTest=None
APP=str(Path(__file__).resolve().parents[1]/'streamlit_app.py')
@unittest.skipIf(AppTest is None, 'Streamlit is not installed')
class UITests(unittest.TestCase):
 def new(self):
  with patch.dict(os.environ,{'DATA_MODE':'demo'}):
   return AppTest.from_file(APP, default_timeout=15).run()
 def test_normal_and_delay(self):
  at=self.new();self.assertEqual(len(at.exception),0)
  self.assertIn('未接続',at.warning[0].value.replace('には接続していません','未接続'))
  self.assertEqual(at.metric[0].value,'90,000,000 円')
  self.assertEqual(at.metric[2].value,'201,550,000 円')
  at.selectbox[0].select('売却3か月遅延').run()
  self.assertEqual(len(at.exception),0)
  self.assertEqual(at.metric[2].value,'199,825,000 円')
  at.selectbox[0].select('標準').run()
  self.assertEqual(at.metric[2].value,'201,550,000 円')
 def test_filter_empty_and_restore(self):
  at=self.new();at.multiselect[0].set_value([]).run()
  self.assertEqual(len(at.exception),0);self.assertEqual(len(at.metric),0)
  at.multiselect[0].set_value(['P001']).run()
  self.assertEqual(len(at.exception),0);self.assertEqual(len(at.metric),5)
 def test_custom_controls(self):
  at=self.new();at.selectbox[0].select('カスタム').run()
  at.slider[0].set_value(3).run();at.slider[1].set_value(-10).run()
  self.assertEqual(len(at.exception),0)
 def test_period_and_future_totals(self):
  at=self.new()
  self.assertEqual(at.metric[3].value,'600,000,000 円')
  self.assertEqual(at.metric[4].value,'488,450,000 円')
  at.select_slider[0].set_value(('2027-01','2027-12')).run()
  self.assertEqual(len(at.exception),0)
  self.assertEqual(len(at.dataframe[0].value),12)
  self.assertEqual(at.dataframe[0].value.index[0],'2027-01')
  self.assertTrue(any('最低残高月：' in e.value for e in at.caption))
 def test_project_dates_and_variance(self):
  at=self.new()
  project_table=at.dataframe[1].value
  self.assertIn('売却日（見込/実績）',project_table.columns)
  self.assertIn('2027-04-15',project_table.iloc[0]['売却日（見込/実績）'])
  variance=at.dataframe[2].value
  self.assertEqual((variance['状態']=='確定').sum(),2)
  self.assertTrue(variance.loc[variance['状態']=='未確定','差額（円）'].isna().all())
  at.selectbox[0].select('売却3か月遅延').run()
  self.assertIn('2027-07-15',at.dataframe[1].value.iloc[0]['売却日（見込/実績）'])
 def test_single_month_no_events(self):
  at=self.new();at.select_slider[0].set_value(('2029-09','2029-09')).run()
  self.assertEqual(len(at.exception),0)
  self.assertEqual(len(at.dataframe[0].value),1)
  self.assertEqual(at.metric[3].value,'0 円')
  self.assertEqual(len(at.dataframe[3].value),0)
 def test_invalid_source_stops(self):
  with patch.dict(os.environ,{'DATA_MODE':'invalid'}):
   at=AppTest.from_file(APP,default_timeout=15).run()
  self.assertEqual(len(at.exception),0);self.assertEqual(len(at.error),1)
  self.assertEqual(len(at.metric),0)
if __name__=='__main__':unittest.main()
