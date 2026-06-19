import os
from flask import Flask, render_template, jsonify
from playwright.sync_api import sync_playwright

app = Flask(__name__)

def login_to_rosplat(p):
    # Добавлен эмуляционный юзер-агент, чтобы сайт не видел, что это робот
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    page = context.new_page()
    
    print("Открываем страницу логина...")
    page.goto("https://rosplat.cash", timeout=30000)
    
    page.fill('input[placeholder*="Логин"], input[type="text"], input[type="email"]', 'Solevoi')
    page.fill('input[type="password"]', '112nataliA')
    page.click('button[type="submit"]')
    
    page.wait_for_load_state("networkidle")
    print("Авторизация выполнена успешно.")
    return browser, page

def parse_table_data(page, url):
    print(f"Переходим на страницу: {url}")
    page.goto(url, timeout=30000)
    try:
        page.wait_for_selector("table, tr, td, .table", timeout=15000)
        page.wait_for_timeout(2000) # Даем время дорендерить React-таблицу
    except Exception as e:
        print(f"Таблица не найдена или пуста на {url}. Ошибка: {e}")
        # Сохраняем скриншот для отладки, чтобы увидеть, что там происходит
        page.screenshot(path="error_screenshot.png")
        return []
        
    data_list = []
    rows = page.query_selector_all("tr")
    print(f"Найдено строк таблицы: {len(rows)}")
    
    for row in rows:
        cells = row.query_selector_all("td")
        if cells and len(cells) >= 4:
            data_list.append([cell.inner_text().strip() for cell in cells])
    return data_list

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/rosplat-data')
def get_deals():
    try:
        with sync_playwright() as p:
            browser, page = login_to_rosplat(p)
            raw_data = parse_table_data(page, "https://rosplat.cashdashboard/deals/all")
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

@app.route('/api/rosplat-payouts')
def get_payouts():
    try:
        with sync_playwright() as p:
            browser, page = login_to_rosplat(p)
            raw_data = parse_table_data(page, "https://rosplat.cashdashboard/payoutrequests/pending")
            browser.close()
            
            payouts = []
            for row in raw_data:
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