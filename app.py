from flask import Flask, request, jsonify, render_template
import random

app = Flask(__name__)

users = {1: {"name": "Jaswanth (Jashu)", "kyc_status": "PENDING", "kyc_score": 0}}
transfers = []

# Mock data
sanctioned_countries = ["IRAN", "NORTH KOREA", "SYRIA"]
forex_rates = {"USD": 83.5, "EUR": 90.2, "GBP": 105.3}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/kyc/verify/<int:user_id>', methods=['POST'])
def verify_kyc(user_id):
    data = request.json
    # For demo, give high score always for Jashu so it always VERIFIED
    score = random.randint(85, 95)
    status = "VERIFIED" if score > 80 else "PENDING"
    users[user_id]["kyc_score"] = score
    users[user_id]["kyc_status"] = status
    return jsonify({"user_id": user_id, "name": "Jaswanth", "kyc_score": score, "kyc_status": status, "doc": data.get("doc_type")})

@app.route('/api/transfer/create', methods=['POST'])
def create_transfer():
    data = request.json
    user_id = data.get("user_id")
    amount = data.get("amount_inr")
    currency = data.get("currency")
    country = data.get("country")

    # 1. KYC Check
    if users[user_id]["kyc_status"] != "VERIFIED":
        return jsonify({"error": "KYC NOT VERIFIED - Please verify first"}), 400
    
    # 2. Sanction Check
    if country.upper() in sanctioned_countries:
        return jsonify({"error": f"BLOCKED: {country} is Sanctioned"}), 403

    # 3. Forex
    converted = round(amount / forex_rates.get(currency, 83.5), 2)
    
    # 4. Risk
    risk = "LOW" if amount < 50000 else "MEDIUM" if amount < 200000 else "HIGH"
    
    transfer_id = len(transfers) + 1
    transfers.append({"id": transfer_id, "user": "Jaswanth", **data})
    
    return jsonify({"transfer_id": transfer_id, "amount_inr": amount, "converted": converted, "currency": currency, "country": country, "risk": risk, "status": "COMPLETED"})

if __name__ == '__main__':
    app.run(debug=True)