import sqlite3

connection = sqlite3.connect("data/app.db")
try:
    print(connection.execute("SELECT name FROM users WHERE id = 1").fetchone()[0])
finally:
    connection.close()
