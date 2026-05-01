# test_postgres.py
import psycopg2

# ←←← CHANGE THIS TO YOUR ACTUAL PASSWORD ←←←
PASSWORD = "!2jHJn093sf0K&A"

try:
    conn = psycopg2.connect(
        dbname="Nails_By_Mykala",
        user="postgres",
        password=PASSWORD,
        host="localhost"
    )
    print("✅ Successfully connected to PostgreSQL!")

    cur = conn.cursor()
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    
    tables = cur.fetchall()
    print(f"\n📋 Tables found in database 'Nails_By_Mykala':")
    for table in tables:
        print(f"   • {table[0]}")
    
    cur.close()
    conn.close()

except Exception as e:
    print("❌ Connection failed!")
    print(e)