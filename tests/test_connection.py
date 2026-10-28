import os
import unittest
from unittest.mock import MagicMock, patch
try:
 import snowflake.connector
except ImportError:
 snowflake=None
from data_source import load_snowflake
@unittest.skipIf(snowflake is None, 'Snowflake connector not installed')
class ConnectionTests(unittest.TestCase):
 def test_platform_detection_disabled_before_connection(self):
  conn=MagicMock();cursor=conn.cursor.return_value
  cursor.description=[('PROJECT_ID',)]
  cursor.fetchall.return_value=[('P001',)]
  def connect(**kw):
   self.assertEqual(os.environ.get('SNOWFLAKE_DISABLE_PLATFORM_DETECTION'),'true')
   self.assertEqual(kw['session_parameters']['STATEMENT_TIMEOUT_IN_SECONDS'],30)
   return conn
  with patch('snowflake.connector.connect',side_effect=connect):
   result=load_snowflake({'account':'example','user':'reader','unsupported':'ignored'})
  self.assertEqual(len(result),2)
  self.assertEqual(cursor.execute.call_count,2)
  conn.close.assert_called_once();cursor.close.assert_called_once()
if __name__=='__main__': unittest.main()
