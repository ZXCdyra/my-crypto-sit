import os
import requests
from flask import Flask, render_template, jsonify
import urllib3

# Отключаем системные предупреждения об SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# Базовые настройки для подключения к серверу РосПлат
BASE_API = "https://rosplat.cash"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://rosplat.cash",
    "Referer": "https://rosplat.cash/"
}

# Автоматическое получение свежего пропуска (токена) по логину и паролю
def get_active_session():
    try:
        payload = {"login": "Solevoi", "pass": "112nataliA"}
        res = requests.post(f"{BASE_API}/auth/login", json=payload, headers=HEADERS, verify=False, timeout=10)
        if res.status_code == 200:
            token = res.json().get("token") or res.json().get("accessToken")
            if token:
                auth_headers = HEADERS.copy()
                auth_headers["authorization"] = f"Bearer {token}"
                return auth_headers
    except Exception as e:
        print(f"Ошибка автоматического входа: {e}")
    return None

@app.route('/')
def home():
    return render_template('index.html')

# 1. Автоматический сбор Сделок
@app.route('/api/rosplat-data')
def get_deals():
    session_headers = get_active_session()
    if not session_headers:
        return jsonify({"status": "error", "message": "Не удалось авторизоваться на РосПлат"})
    
    try:
        res = requests.get(f"{BASE_API}/dashboard/deals/all", headers=session_headers, verify=False, timeout=10)
        if res.status_code == 200:
            return jsonify({"status": "success", "data": res.json()})
    except Exception as e:
        print(f"Ошибка сделок: {e}")
    return jsonify({"status": "success", "data": []})

# 2. Автоматический сбор Выплат
@app.route('/api/rosplat-payouts')
def get_payouts():
    session_headers = get_active_session()
    if not session_headers:
        return jsonify({"status": "error", "message": "Не удалось авторизоваться на РосПлат"})
    
    try:
        res = requests.get(f"{BASE_API}/dashboard/payoutrequests/pending", headers=session_headers, verify=False, timeout=10)
        if res.status_code == 200:
            raw_data = res.json()
            payouts = []
            if isinstance(raw_data, list):
                for item in raw_data:
                    payouts.append({
                        "id": item.get("id") or "---",
                        "method": item.get("method") or "---",
                        "details": item.get("details") or item.get("wallet") or "---",
                        "amount": f"{item.get('amount', 0)} ₽",
                        "status": item.get("status") or "В ожидании",
                        "date": item.get("createdAt") or ""
                    })
            return jsonify({"status": "success", "data": payouts})
    except Exception as e:
        print(f"Ошибка выплат: {e}")
    return jsonify({"status": "success", "data": []})

if __name__ == '__main__':
    app.run(debug=True)
