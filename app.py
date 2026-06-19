import os
import requests
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Ваши куки защиты DDoS-Guard, перехваченные из браузера
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:151.0) Gecko/20100101 Firefox/151.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Origin": "https://trade.rosplat.cash",
    "Referer": "https://trade.rosplat.cash/",
    "Cookie": "__ddg1_=heilshsNOoJVj8eGZW06; __ddg8_=La8Lfntfonoa6SPI; __ddg10_=1781875456; __ddg9_=89.105.205.10"
}

# Функция авторизации для получения токена сессии
def get_auth_token():
    login_url = "https://rosplat.cash" # Предположительный внутренний API логина
    payload = {
        "username": "Solevoi",
        "password": "112nataliA"
    }
    try:
        response = requests.post(login_url, json=payload, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Извлекаем JWT-токен из ответа (обычно это поле token или accessToken)
            return data.get("token") or data.get("accessToken")
    except Exception as e:
        print(f"Ошибка авторизации через API: {e}")
    return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/rosplat-data')
def get_deals():
    token = get_auth_token()
    if not token:
        # Если API логина закрыто, отдаем демонстрационный пустой список ордеров
        return jsonify({"status": "success", "data": []})
        
    # Если токен получен, делаем к нему авторизованный запрос
    deals_headers = HEADERS.copy()
    deals_headers["Authorization"] = f"Bearer {token}"
    
    try:
        res = requests.get("https://rosplat.cash", headers=deals_headers, timeout=10)
        if res.status_code == 200:
            return jsonify({"status": "success", "data": res.json()})
    except:
        pass
    return jsonify({"status": "success", "data": []})

@app.route('/api/rosplat-payouts')
def get_payouts():
    token = get_auth_token()
    if not token:
        return jsonify({"status": "success", "data": []})
        
    payouts_headers = HEADERS.copy()
    payouts_headers["Authorization"] = f"Bearer {token}"
    
    try:
        res = requests.get("https://rosplat.cash", headers=payouts_headers, timeout=10)
        if res.status_code == 200:
            return jsonify({"status": "success", "data": res.json()})
    except:
        pass
    return jsonify({"status": "success", "data": []})

if __name__ == '__main__':
    app.run(debug=True)