import os
import requests
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Ваш перехваченный токен и актуальные заголовки
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:151.0) Gecko/20100101 Firefox/15",
    "Accept": "application/json",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Content-Type": "application/json",
    "Origin": "https://trade.rosplat.cash",
    "Referer": "https://trade.rosplat.cash/",
    "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoidHJhZGVyIiwiaWQiOjMzMzgzOCwibG9naW4iOiJzb2xldm9pIiwibG9naW5BdCI6MTc4MDc4MTQ1MDQxNiwiaWF0IjoxNzgwNzgxNDUwLCJleHAiOjE3OTYzMzM0NTB9.F4PiZDC957bKK8DGY0VGliENPB3YIwpFqsunzChAdTw"
}

@app.route('/')
def home():
    return render_template('index.html')

# 1. API для Сделок
@app.route('/api/rosplat-data')
def get_deals():
    try:
        # Тянем сделки напрямую из API
        res = requests.get("https://rosplat.cash", headers=HEADERS, timeout=10)
        if res.status_code == 200:
            return jsonify({"status": "success", "data": res.json()})
    except Exception as e:
        print(f"Ошибка запроса сделок: {e}")
    return jsonify({"status": "success", "data": []})

# 2. API для Выплат
@app.route('/api/rosplat-payouts')
def get_payouts():
    try:
        # Тянем выплаты напрямую из API
        res = requests.get("https://rosplat.cash", headers=HEADERS, timeout=10)
        
        if res.status_code == 200:
            raw_data = res.json()
            payouts = []
            
            # Если это список объектов (стандарт для API)
            if isinstance(raw_data, list):
                for item in raw_data:
                    payouts.append({
                        "id": item.get("id") or item.get("orderId") or "---",
                        "method": item.get("method") or item.get("bankName") or "---",
                        "details": item.get("wallet") or item.get("details") or item.get("card") or "---",
                        "amount": f"{item.get('amount', 0)} ₽",
                        "status": item.get("status") or "В ожидании",
                        "date": item.get("createdAt") or item.get("date") or ""
                    })
            return jsonify({"status": "success", "data": payouts})
            
    except Exception as e:
        print(f"Ошибка запроса выплат: {e}")
    return jsonify({"status": "success", "data": []})

if __name__ == '__main__':
    app.run(debug=True)