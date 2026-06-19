import os
import requests
from flask import Flask, render_template, jsonify
import urllib3

# Отключаем предупреждения об SSL-сертификатах для DDoS-Guard
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# СЮДА ВСТАВЬТЕ ВАШ СВЕЖИЙ Bearer-ТОКЕН, ЕСЛИ ОН ОБНОВИЛСЯ ПОСЛЕ ВВОДА КАПЧИ
ROSPLAT_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoidHJhZGVyIiwiaWQiOjMzMzgzOCwibG9naW4iOiJzb2xldm9pIiwibG9naW5BdCI6MTc4MDc4MTQ1MDQxNiwiaWF0IjoxNzgwNzgxNDUwLCJleHAiOjE3OTYzMzM0NTB9.F4PiZDC957bKK8DGY0VGliENPB3YIwpFqsunzChAdTw"

# Ваши новые куки DDoS-Guard собранные в правильную строку
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

# 1. Сбор Сделок
@app.route('/api/rosplat-data')
def get_deals():
    try:
        url = "https://rosplat.cash"
        res = requests.get(url, headers=HEADERS, verify=False, timeout=10)
        if res.status_code == 200:
            return jsonify({"status": "success", "data": res.json()})
        else:
            print(f"РосПлат Сделки вернул статус: {res.status_code}")
    except Exception as e:
        print(f"Ошибка запроса сделок: {e}")
    return jsonify({"status": "success", "data": []})

# 2. Сбор Выплат
@app.route('/api/rosplat-payouts')
def get_payouts():
    try:
        url = "https://rosplat.cash"
        res = requests.get(url, headers=HEADERS, verify=False, timeout=10)
        
        if res.status_code == 200:
            raw_data = res.json()
            payouts = []
            
            if isinstance(raw_data, list):
                for row in raw_data:
                    if isinstance(row, list) and len(row) >= 6:
                        payouts.append({
                            "id": row[0],
                            "method": row[1],
                            "details": f"{row[2]} | {row[3]}" if len(row) > 4 else row[2],
                            "amount": row[4] if len(row) > 4 else row[3],
                            "status": "В ожидании",
                            "date": f"{row[5]} {row[6]}" if len(row) > 6 else row[5]
                        })
            return jsonify({"status": "success", "data": payouts})
        else:
            print(f"РосПлат Выплаты вернул статус: {res.status_code}")
    except Exception as e:
        print(f"Ошибка запроса выплат: {e}")
    return jsonify({"status": "success", "data": []})

if __name__ == '__main__':
    app.run(debug=True)
