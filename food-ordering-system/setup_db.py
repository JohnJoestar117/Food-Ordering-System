"""Run once: creates the database, tables, sample menu and a default admin account."""
import mysql.connector
from db import get_connection, run_query
from auth import hash_password


def main():
    with open("schema.sql", encoding="utf-8") as f:
        statements = [s.strip() for s in f.read().split(";") if s.strip()]

    conn = get_connection(use_db=False)
    cur = conn.cursor()
    for stmt in statements:
        cur.execute(stmt)
    conn.commit()
    cur.close()
    conn.close()

    exists = run_query("SELECT 1 FROM users WHERE username=%s", ("admin",), fetch=True)
    if not exists:
        run_query("INSERT INTO users (username, password, role) VALUES (%s,%s,'admin')",
                  ("admin", hash_password("admin123")))
        print("Default admin created -> username: admin / password: admin123 (change it!)")
    print("Database ready.")


if __name__ == "__main__":
    try:
        main()
    except mysql.connector.Error as e:
        print("MySQL error:", e)
