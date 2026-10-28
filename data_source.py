"""Server-side connection only. No anonymous SQL or user supplied identifiers."""
from contextlib import closing
import os

# Key-pair auth does not need cloud metadata. Disable optional SDK platform
# detection before importing/initializing the connector to avoid metadata probes.
os.environ["SNOWFLAKE_DISABLE_PLATFORM_DETECTION"] = "true"

PROJECT_QUERY = 'SELECT PROJECT_ID, PROJECT_NAME, LOCATION, LOAN_PRINCIPAL, ANNUAL_INTEREST_RATE FROM CF_DEMO.MART.PUBLIC_PROJECTS'
EVENT_QUERY = 'SELECT EVENT_ID, PROJECT_ID, COUNTERPARTY, CATEGORY, PLANNED_DATE, PLANNED_AMOUNT, ACTUAL_DATE, ACTUAL_AMOUNT FROM CF_DEMO.MART.PUBLIC_CASH_EVENTS'

def load_snowflake(config):
    import snowflake.connector
    # Dedicated read-only service user; configured by owner, never end-user browser.
    allowed = {'account','user','password','private_key','private_key_file','private_key_file_pwd','warehouse','database','schema','role','authenticator','token'}
    kwargs={k:v for k,v in dict(config).items() if k in allowed}
    if config.get('private_key_pem'):
        from cryptography.hazmat.primitives import serialization
        key = serialization.load_pem_private_key(config['private_key_pem'].encode(), password=None)
        kwargs['private_key'] = key.private_bytes(serialization.Encoding.DER, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    kwargs.update(login_timeout=15, network_timeout=30, session_parameters={'STATEMENT_TIMEOUT_IN_SECONDS':30, 'QUERY_TAG':'snowflakesample_public_readonly'})
    with closing(snowflake.connector.connect(**kwargs)) as conn:
        with closing(conn.cursor()) as cursor:
            result=[]
            for query in (PROJECT_QUERY,EVENT_QUERY):
                cursor.execute(query)
                keys=[d[0].lower() for d in cursor.description]
                result.append([dict(zip(keys,row)) for row in cursor.fetchall()])
    return tuple(result)
