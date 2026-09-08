import sqlite3
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('kyc.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS customers
                 (id INTEGER PRIMARY KEY, name TEXT, country TEXT, risk TEXT, blocked INTEGER)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    conn = sqlite3.connect('kyc.db')
    c = conn.cursor()
    c.execute("SELECT * FROM customers")
    rows = c.fetchall()
    conn.close()
    return render_template('index.html', customers=rows)

@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    country = request.form['country']
    risk = 'HIGH' if country in ['Iran','North Korea','Syria'] else 'LOW'
    blocked = 1 if risk == 'HIGH' else 0
    conn = sqlite3.connect('kyc.db')
    c = conn.cursor()
    c.execute("INSERT INTO customers (name,country,risk,blocked) VALUES (?,?,?,?)", (name,country,risk,blocked))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)