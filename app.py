import os
import requests
from flask import Flask, render_template, jsonify
import urllib3

# Отключаем предупреждения об SSL-сертификатах для DDoS-Guard
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

# Тестовый эндпоинт, который выведет результат авторизации прямо на экран вашего сайта
@app.route('/api/rosplat-data')
def test_login():
    try:
        # Проверяем первый вариант названий полей формы
        payload1 = {"login": "Solevoi", "pass": "112nataliA"}
        res1 = requests.post(f"{BASE_API}/auth/login", json=payload1, headers=HEADERS, verify=False, timeout=10)
        
        # Проверяем второй вариант названий полей формы (username/password)
        payload2 = {"username": "Solevoi", "password": "112nataliA"}
        res2 = requests.post(f"{BASE_API}/auth/login", json=payload2, headers=HEADERS, verify=False, timeout=10)
        
        # Собираем ответы в один объект
        debug_info = {
            "variant_1_status": res1.status_code,
            "variant_1_body": res1.json() if res1.status_code == 200 else res1.text,
            "variant_2_status": res2.status_code,
            "variant_2_body": res2.json() if res2.status_code == 200 else res2.text
        }
        
        # Превращаем результат в массив строк, чтобы ваш index.html смог вывести его как таблицу ордеров
        return jsonify({
            "status": "success",
            "data": [{
                "id": "ТЕСТ_API",
                "bank": f"Вариант 1 Статус: {res1.status_code}",
                "method": "Кликните",
                "credentials": f"В1 Ответ: {str(debug_info['variant_1_body'])[:40]}...",
                "amount": f"В2 Статус: {res2.status_code}",
                "time": "Отладка",
                "date": f"В2 Ответ: {str(debug_info['variant_2_body'])[:30]}..."
            }]
        })
    except Exception as e:
        return jsonify({
            "status": "success",
            "data": [{"id": "ОШИБКА", "bank": str(e), "method": "ERR", "credentials": "", "amount": "", "time": "", "date": ""}]
        })

@app.route('/api/rosplat-payouts')
def test_payouts():
    return jsonify({"status": "success", "data": []})

if __name__ == '__main__':
    app.run(debug=True)
