import os
from flask import Flask, render_template, jsonify
from playwright.sync_api import sync_playwright

app = Flask(__name__)

# Общая функция авторизации
def login_to_rosplat(p):
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    
    page.goto("https://trade.rosplat.cash/")
    
    # Заполнение формы авторизации
    page.fill('input[placeholder*="Логин"], input[type="text"], input[type="email"]', 'Solevoi')
    page.fill('input[type="password"]', '112nataliA')
    page.click('button[type="submit"]')
    
    # Ждем, пока исчезнет форма входа и прогрузится основной интерфейс
    page.wait_for_load_state("networkidle")
    return browser, page

# Универсальный парсер таблиц РосПлата с защитой от долгой загрузки React/Vue
def parse_table_data(page, url):
    page.goto(url)
    try:
        # ИСПРАВЛЕНО: Ждем загрузки именно строк таблицы (tr) или ячеек (td) до 15 секунд
        page.wait_for_selector("table, tr, td, .table", timeout=15000)
        # Даем еще 1 секунду на полную отрисовку скриптов РосПлата
        page.wait_for_timeout(1000)
    except Exception as e:
        print(f"Ошибка ожидания таблицы на {url}: {e}")
        return []
        
    data_list = []
    rows = page.query_selector_all("tr")
    for row in rows:
        cells = row.query_selector_all("td")
        if cells and len(cells) >= 4:
            # Собираем текстовое содержимое всех ячеек в строке
            data_list.append([cell.inner_text().strip() for cell in cells])
    return data_list

@app.route('/')
def home():
    return render_template('index.html')

# API для Сделок
@app.route('/api/rosplat-data')
def get_deals():
    try:
        with sync_playwright() as p:
            browser, page = login_to_rosplat(p)
            raw_data = parse_table_data(page, "https://trade.rosplat.cash/dashboard/deals/all")
            browser.close()
            
            deals = []
            for row in raw_data:
                if len(row) >= 7:
                    deals.append({
                        "id": row[0], "bank": row[1], "method": row[2],
                        "credentials": row[3], "amount": row[4], "time": row[5], "date": row[6]
                    })
            return jsonify({"status": "success", "data": deals})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# API для Выплат с ИСПРАВЛЕННЫМ реальным URL-адресом
@app.route('/api/rosplat-payouts')
def get_payouts():
    try:
        with sync_playwright() as p:
            browser, page = login_to_rosplat(p)
            # ИСПРАВЛЕНО: Установлен ваш точный адрес страницы выплат
            raw_data = parse_table_data(page, "https://trade.rosplat.cash/dashboard/payoutrequests/pending")
            browser.close()
            
            payouts = []
            for row in raw_data:
                # Нарезаем строки под формат таблицы выплат РосПлата
                payouts.append({
                    "id": row[0] if len(row) > 0 else "---",
                    "method": row[1] if len(row) > 1 else "---",
                    "details": row[2] if len(row) > 2 else "---",
                    "amount": row[3] if len(row) > 3 else "0 ₽",
                    "status": row[4] if len(row) > 4 else "В ожидании",
                    "date": row[5] if len(row) > 5 else ""
                })
            return jsonify({"status": "success", "data": payouts})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
