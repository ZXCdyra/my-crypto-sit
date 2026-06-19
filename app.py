import os
import requests
from flask import Flask, render_template, jsonify
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

BASE_API = "https://rosplat.cash"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://rosplat.cash",
    "Referer": "https://rosplat.cash/"
}

@app.route('/')
def home():
    return render_template('index.html')

# Тестовый эндпоинт, который покажет, как именно РосПлат реагирует на авторизацию
@app.route('/api/rosplat-data')
def test_login():
    try:
        # Проверяем первый вариант названий полей формы
        payload1 = {"login": "Solevoi", "pass": "112nataliA"}
        res1 = requests.post(f"{BASE_API}/auth/login", json=payload1, headers=HEADERS, verify=False, timeout=10)
        
        # Проверяем второй вариант названий полей формы (на случай если там email/username)
        payload2 = {"username": "Solevoi", "password": "112nataliA"}
        res2 = requests.post(f"{BASE_API}/auth/login", json=payload2, headers=HEADERS, verify=False, timeout=10)
        
        return jsonify({
            "status": "debug",
            "response_variant_1_status": res1.status_code,
            "response_variant_1_body": res1.json() if res1.status_code == 200 else res1.text,
            "response_variant_2_status": res2.status_code,
            "response_variant_2_body": res2.json() if res2.status_code == 200 else res2.text
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# Временный дубль для выплат, чтобы сайт не выдавал ошибку сети
@app.route('/api/rosplat-payouts')
def test_payouts():
    return jsonify({"status": "success", "data": []})

if __name__ == '__main__':
    app.run(debug=True)