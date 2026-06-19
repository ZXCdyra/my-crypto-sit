import os
import requests
from flask import Flask, render_template, jsonify
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# Токен авторизации
ROSPLAT_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoidHJhZ昌ZXIiLCJpZCI6MzMzODM4LCJsb2dpbiI6InNvbGV2b2kiLCJsb2dpbkF0IjoxNzgxODkwNDYzMzIwLCJpYXQiOjE3ODE4OTA0NjMsImV4cCI6MTc5NzQ0MjQ2M30.wZBywaGECMcRdEgp9-HBkv2kaElh_t_QR1m_aUyxu-4"

# Заголовки и актуальные куки DDoS-Guard
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:151.0) Gecko/20100101 Firefox/15",
    "Accept": "application/json",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Content-Type": "application/json",
    "Origin": "https://rosplat.cash",
    "Referer": "https://rosplat.cash/",
    "authorization": ROSPLAT_TOKEN,
    "Cookie": "__ddg1_=QJcg549VFuU09XEmV4PE; __ddg8_=r0lrSjXx4tjh8Mxm; __ddg9_=89.105.212.138; __ddg10_=1781890718"
}

@app.route('/')
def home():
    return render_template('index.html')

# 1. API для Сделок
@app.route('/api/rosplat-data')
def get_deals():
    try:
        url = "https://rosplat.cash"
        res = requests.get(url, headers=HEADERS, verify=False, timeout=10)
        if res.status_code == 200:
            return jsonify({"status": "success", "data": res.json()})
    except Exception as e:
        print(f"Ошибка запроса сделок: {e}")
    return jsonify({"status": "success", "data": []})

# 2. API для Выплат (Универсальный разбор под любой ответ сервера)
@app.route('/api/rosplat-payouts')
def get_payouts():
    try:
        url = "https://rosplat.cash"
        res = requests.get(url, headers=HEADERS, verify=False, timeout=10)
        
        if res.status_code == 200:
            raw_data = res.json()
            payouts = []
            
            # Если РосПлат вернул массив (базовый контейнер)
            if isinstance(raw_data, list):
                for row in raw_data:
                    # Вариант 1: Элемент списка — это массив строк (как в сделках)
                    if isinstance(row, list) and len(row) >= 5:
                        payouts.append({
                            "id": row[0],
                            "method": row[1],
                            "details": f"{row[2]} | {row[3]}" if len(row) > 4 else row[2],
                            "amount": row[4] if len(row) > 4 else "0 ₽",
                            "status": "В ожидании",
                            "date": row[5] if len(row) > 5 else ""
                        })
                    # Вариант 2: Элемент списка — это готовый объект (словарь)
                    elif isinstance(row, dict):
                        payouts.append({
                            "id": row.get("id") or row.get("orderId") or "---",
                            "method": row.get("bankName") or row.get("method") or "---",
                            "details": row.get("credentials") or row.get("details") or row.get("wallet") or "---",
                            "amount": f"{row.get('amount', 0)} ₽",
                            "status": row.get("status") or "В ожидании",
                            "date": row.get("createdAt") or row.get("date") or ""
                        })
            return jsonify({"status": "success", "data": payouts})
    except Exception as e:
        print(f"Ошибка запроса выплат: {e}")
    return jsonify({"status": "success", "data": []})

if __name__ == '__main__':
    app.run(debug=True)