# Test script to verify connection
import snowflake.connector

try:
    conn = snowflake.connector.connect(
        user='your username here',
        password='your password here',
        account='account identifier here',
        warehouse='FINAI_WH',
        database='FINAI_DB',
        schema='FINAI_SCHEMA'
    )
    print("✅ Snowflake connection successful!")
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")