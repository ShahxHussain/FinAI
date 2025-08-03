# Test script to verify connection
import snowflake.connector

try:
    conn = snowflake.connector.connect(
        user='shahxhussain',
        password='Snowflake#19288',
        account='YNJBSER-EX11402',
        warehouse='FINAI_WH',
        database='FINAI_DB',
        schema='FINAI_SCHEMA'
    )
    print("✅ Snowflake connection successful!")
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")