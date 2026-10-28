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
  self.assertEqual(len(at.exception),0);self.assertEqual(len(at.metric),3)
 def test_custom_controls(self):
  at=self.new();at.selectbox[0].select('カスタム').run()
  at.slider[0].set_value(3).run();at.slider[1].set_value(-10).run()
  self.assertEqual(len(at.exception),0)
 def test_invalid_source_stops(self):
  with patch.dict(os.environ,{'DATA_MODE':'invalid'}):
   at=AppTest.from_file(APP,default_timeout=15).run()
  self.assertEqual(len(at.exception),0);self.assertEqual(len(at.error),1)
  self.assertEqual(len(at.metric),0)
if __name__=='__main__':unittest.main()
