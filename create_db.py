# create_db.py
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Change this password to your actual PostgreSQL superuser password
DB_PASSWORD = "!2jHJn093sf0K&A"

conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password=DB_PASSWORD,
    host="localhost"
)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

cur = conn.cursor()
cur.execute('CREATE DATABASE "Nails_By_Mykala";')
print("Database 'Nails_By_Mykala' created successfully!")
cur.close()
conn.close()