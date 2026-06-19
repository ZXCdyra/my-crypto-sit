import os
from flask import Flask, render_template, jsonify
from playwright.sync_api import sync_playwright

app = Flask(__name__)

# Общая функция авторизации, которая возвращает объект страницы
def login_to_rosplat(p):
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    
    page.goto("https://rosplat.cash")
    page.fill('input[placeholder*="Логин"], input[type="text"], input[type="email"]', 'Solevoi')
    page.fill('input[type="password"]', '112nataliA')
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")
    
    return browser, page

# Универсальный парсер таблиц РосПлата
def parse_table_data(page, url):
    page.goto(url)
    try:
        page.wait_for_selector("table, tr, td", timeout=10000)
    except:
        return [] # Если таблица пустая или не загрузилась
        
    data_list = []
    rows = page.query_selector_all("tr")
    for row in rows:
        cells = row.query_selector_all("td")
        if cells and len(cells) >= 4: # Минимальное количество колонок для данных
            # Собираем все текстовые ячейки в массив strings
            data_list.append([cell.inner_text().strip() for cell in cells])
    return data_list

@app.route('/')
def home():
    return render_template('index.html')

# 1. API для Сделок
@app.route('/api/rosplat-data')
def get_deals():
    try:
        with sync_playwright() as p:
            browser, page = login_to_rosplat(p)
            raw_data = parse_table_data(page, "https://rosplat.cashdashboard/deviceprofiles/active")
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

# 2. Новое API для Выплат
@app.route('/api/rosplat-payouts')
def get_payouts():
    try:
        with sync_playwright() as p:
            browser, page = login_to_rosplat(p)
            # Внимание: замените URL ниже на точный адрес страницы выплат на РосПлате, если он отличается
            raw_data = parse_table_data(page, "https://rosplat.cashdashboard/payouts")
            browser.close()
            
            payouts = []
            for row in raw_data:
                # Адаптируем под структуру колонок выплат РосПлата
                payouts.append({
                    "id": row[0] if len(row) > 0 else "---",
                    "method": row[1] if len(row) > 1 else "---",
                    "details": row[2] if len(row) > 2 else "---",
                    "amount": row[3] if len(row) > 3 else "0 ₽",
                    "status": row[4] if len(row) > 4 else "В обработке",
                    "date": row[5] if len(row) > 5 else ""
                })
            return jsonify({"status": "success", "data": payouts})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
