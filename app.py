import os
from flask import Flask, render_template, request, redirect
import sqlite3

# Try to import postgres lib, if not installed it will still work with sqlite
try:
    import psycopg2
    HAS_PG = True
except:
    HAS_PG = False

app = Flask(__name__)

DATABASE_URL = os.environ.get('DATABASE_URL')
HIGH_RISK_COUNTRIES = ['Iran', 'North Korea', 'Syria', 'Russia', 'Cuba']

def get_db_connection():
    if DATABASE_URL and HAS_PG:
        # Cloud Postgres
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    else:
        # Local SQLite (fallback)
        conn = sqlite3.connect('kyc.db')
        return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    if DATABASE_URL and HAS_PG:
        cur.execute('''CREATE TABLE IF NOT EXISTS customers
                       (id SERIAL PRIMARY KEY, name TEXT, country TEXT, risk TEXT, blocked INTEGER)''')
    else:
        cur.execute('''CREATE TABLE IF NOT EXISTS customers
                       (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, country TEXT, risk TEXT, blocked INTEGER)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM customers ORDER BY id DESC')
    customers = cur.fetchall()
    conn.close()
    return render_template('index.html', customers=customers)

@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    country = request.form['country']
    
    if country in HIGH_RISK_COUNTRIES:
        risk, blocked = 'HIGH', 1
    else:
        risk, blocked = 'LOW', 0

    conn = get_db_connection()
    cur = conn.cursor()
    if DATABASE_URL and HAS_PG:
        cur.execute('INSERT INTO customers (name, country, risk, blocked) VALUES (%s,%s,%s,%s)', (name, country, risk, blocked))
    else:
        cur.execute('INSERT INTO customers (name, country, risk, blocked) VALUES (?,?,?,?)', (name, country, risk, blocked))
    conn.commit()
    conn.close()
    return redirect('/')

# Init on start
init_db()

if __name__ == '__main__':
    app.run(debug=True)