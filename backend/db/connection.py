import os
import psycopg

def get_db_connection():
    con = psycopg.connect(os.environ["DB_URL"])
    return con