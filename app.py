import os
from flask import Flask, render_template, jsonify
from playwright.sync_api import sync_playwright

app = Flask(__name__)

def fetch_rosplat_data():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        page.goto("https://trade.rosplat.cash/")
        
        # Заполнение формы авторизации
        page.fill('input[placeholder*="Логин"], input[type="text"], input[type="email"]', 'Solevoi')
        page.fill('input[type="password"]', '112nataliA')
        page.click('button[type="submit"]')
        
        page.wait_for_load_state("networkidle")
        
        page.goto("https://trade.rosplat.cash/dashboard/deviceprofiles/active")
        
        # Ждем загрузку таблицы или любого элемента с данными
        page.wait_for_selector("table, tr, td, .table", timeout=15000)
        
        devices = []
        rows = page.query_selector_all("tr")
        for row in rows:
            cells = row.query_selector_all("td")
            if cells and len(cells) >= 2:
                devices.append({
                    "name": cells[0].inner_text().strip(),
                    "status": cells[1].inner_text().strip(),
                    "info": cells[2].inner_text().strip() if len(cells) > 2 else ""
                })
                
        browser.close()
        return devices

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/rosplat-data')
def get_data():
    try:
        data = fetch_rosplat_data()
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
