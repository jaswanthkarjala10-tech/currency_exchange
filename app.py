from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)
DB = 'kyc.db'

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS customers
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT, country TEXT, risk TEXT, blocked INTEGER)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM customers ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return render_template('index.html', customers=rows)

@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    country = request.form['country']
    # BNP Compliance Logic
    high_risk = ['Iran','North Korea','Syria','Russia']
    risk = 'HIGH' if country in high_risk else 'LOW'
    blocked = 1 if risk == 'HIGH' else 0

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO customers (name,country,risk,blocked) VALUES (?,?,?,?)",
              (name,country,risk,blocked))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)