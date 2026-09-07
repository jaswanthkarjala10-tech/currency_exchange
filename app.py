import os
from flask import Flask, render_template, request, jsonify
import mysql.connector, random
from datetime import datetime

app = Flask(__name__)

SANCTIONED_COUNTRIES = ["IRAN", "NORTH KOREA", "SYRIA", "RUSSIA"]
FOREX_RATES = {"USD": 0.012, "EUR": 0.011, "GBP": 0.0095, "INR": 1}

def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "Jashu@2006"),
        database=os.getenv("DB_NAME", "bnp_hackathon")
    )

@app.route('/')
def home():
    return render_template('index.html', team="Jaswanth (Jashu)")

@app.route('/kyc', methods=['POST'])
def kyc_verify():
    data = request.json
    name = data.get('name', 'Unknown')
    score = random.randint(85, 96)
    status = "VERIFIED" if score >= 80 else "REJECTED"
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO customers (name, kyc_score, status, created_at) VALUES (%s,%s,%s,%s)",
                   (name, score, status, datetime.now()))
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({"name": name, "kyc_score": score, "status": status})

@app.route('/transfer', methods=['POST'])
def transfer():
    data = request.json
    to_country = data.get('to_country', '').upper()
    amount = float(data.get('amount', 0))
    to_currency = data.get('to_currency', 'USD')
    customer_name = data.get('customer_name', 'Jashu Customer')
    
    conn = get_db()
    cursor = conn.cursor()

    if to_country in SANCTIONED_COUNTRIES:
        # NOW WE SAVE FAILED TOO FOR AUDIT!
        cursor.execute("INSERT INTO transfers (customer_name, from_currency, to_currency, amount, converted_amount, status, risk, created_at) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                       (customer_name, "INR", to_currency, amount, 0, "BLOCKED", "CRITICAL", datetime.now()))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"status": "BLOCKED", "message": f"BLOCKED: {to_country} is Sanctioned! Sanction Check FAILED", "risk": "CRITICAL"})

    rate = FOREX_RATES.get(to_currency, 0.012)
    converted = round(amount * rate, 2)
    risk = "LOW" if amount < 50000 else "MEDIUM" if amount < 200000 else "HIGH"
    
    cursor.execute("INSERT INTO transfers (customer_name, from_currency, to_currency, amount, converted_amount, status, risk, created_at) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                   (customer_name, "INR", to_currency, amount, converted, "SUCCESS", risk, datetime.now()))
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({"status": "SUCCESS", "message": f"INR {amount} = {converted} {to_currency}", "converted": converted, "risk": risk})
@app.route('/admin')
def admin():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM customers ORDER BY id DESC")
    customers = cursor.fetchall()
    cursor.execute("SELECT * FROM transfers ORDER BY id DESC")
    transfers = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin.html', customers=customers, transfers=transfers)

if __name__ == '__main__':
    print("BNP Hackathon DB Connected: bnp_hackathon")
    app.run(debug=True)
