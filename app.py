import os
import requests
from flask import Flask, render_template, jsonify
import urllib3

# Отключаем предупреждения об SSL-сертификатах для DDoS-Guard
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# Ваш актуальный токен авторизации
ROSPLAT_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoidHJhZGVyIiwiaWQiOjMzMzgzOCwibG9naW4iOiJzb2xldm9pIiwibG9naW5BdCI6MTc4MTg5MjI2NzA3NCwiaWF0IjoxNzgxODkyMjY3LCJleHAiOjE3OTc0NDQyNjd9.vheit8hLH0eA9EhlCaL6qoQAd6LP11RYnzz1O5wXp9k"

# Заголовки с вашими свежими куками DDoS-Guard из последнего лога
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:151.0) Gecko/20100101 Firefox/151.0",
    "Accept": "application/json",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Content-Type": "application/json",
    "Origin": "https://trade.rosplat.cash",
    "Referer": "https://trade.rosplat.cash/",
    "authorization": ROSPLAT_TOKEN,
    "Cookie": "__ddg1_=F6rfTUgz3jwGilwj1Evv; __ddg8_=09rX93KqBqknG2Hn; __ddg9_=83.139.147.88; __ddg10_=1781892815"
}

@app.route('/')
def home():
    return render_template('index.html')

# 1. Сбор Сделок (ИСПРАВЛЕНО под архитектуру /trader/)
@app.route('/api/rosplat-data')
def get_deals():
    try:
        url = "https://api.rosplat.cash/api/trader/deals/all"
        res = requests.get(url, headers=HEADERS, verify=False, timeout=10)
        if res.status_code == 200:
            return jsonify({"status": "success", "data": res.json()})
        else:
            print(f"РосПлат Сделки вернул статус: {res.status_code}")
    except Exception as e:
        print(f"Ошибка запроса сделок: {e}")
    return jsonify({"status": "success", "data": []})

# 2. Сбор Выплат (ИСПРАВЛЕНО под архитектуру /trader/)
@app.route('/api/rosplat-payouts')
def get_payouts():
    try:
        url = "https://api.rosplat.cash/api/trader/payoutrequests/pending"
        res = requests.get(url, headers=HEADERS, verify=False, timeout=10)
        
        if res.status_code == 200:
            raw_data = res.json()
            payouts = []
            
            if isinstance(raw_data, list):
                for row in raw_data:
                    # Вариант 1: Элемент списка — это массив строк (нарезка по колонкам)
                    if isinstance(row, list) and len(row) >= 6:
                        payouts.append({
                            "id": row[0],                                        # ID заявки
                            "method": row[1],                                    # Банк
                            "details": f"{row[2]} | {row[3]}" if len(row) > 3 else row[2], # Реквизиты
                            "amount": row[4] if len(row) > 4 else "0 ₽",         # Сумма вывода
                            "status": "В ожидании",                              # Статус операции
                            "date": f"{row[5]}" if len(row) > 5 else ""          # Время и Дата
                        })
                    # Вариант 2: Элемент списка — это готовый объект (словарь ключей)
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
        else:
            print(f"РосПлат Выплаты вернул статус: {res.status_code}")
    except Exception as e:
        print(f"Ошибка запроса выплат: {e}")
    return jsonify({"status": "success", "data": []})

if __name__ == '__main__':
    app.run(debug=True)