import psycopg

def get_db_connection():
    con = psycopg.connect(
        dbname="att",
        user="postgres",
        password="avi",
        host="localhost",
        port="5432"
    )
    return con