from flask import Flask, render_template, request, send_file, redirect, url_for, make_response
import sqlite3, os, qrcode, csv
from io import BytesIO, StringIO
from datetime import datetime

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)')
        conn.execute('CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, total REAL, reward REAL)')
        conn.execute('INSERT OR IGNORE INTO settings (key, value) VALUES ("daily_rate", "99")')
        conn.execute('INSERT OR IGNORE INTO settings (key, value) VALUES ("commission", "5")')
        conn.commit()

def get_settings():
    with sqlite3.connect(DB_PATH) as conn:
        rate_row = conn.execute('SELECT value FROM settings WHERE key="daily_rate"').fetchone()
        comm_row = conn.execute('SELECT value FROM settings WHERE key="commission"').fetchone()
        rate = rate_row[0] if rate_row else "99"
        comm = comm_row[0] if comm_row else "5"
        return rate, comm

@app.route('/')
def index():
    init_db()
    rate, comm = get_settings()
    # Итоговая цена на витрине за сутки: цена за день + наценка комиссии
    total_price = round(float(rate) * (1 + float(comm)/100), 2)
    return render_template('index.html', rate=total_price)

@app.route('/zxc_dyra', methods=['GET', 'POST'])
def admin():
    init_db()
    if request.method == 'POST':
        if 'rate' in request.form:
            new_rate = request.form.get('rate')
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute('UPDATE settings SET value=? WHERE key="daily_rate"', (new_rate,))
        if 'commission' in request.form:
            new_comm = request.form.get('commission')
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute('UPDATE settings SET value=? WHERE key="commission"', (new_comm,))
        return redirect(url_for('admin'))
    
    rate, comm = get_settings()
    return render_template('admin.html', rate=rate, commission=comm)

@app.route('/download_report')
def download_report():
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Дата и время', 'Сумма сделки (руб)', 'Доход ИП (Агентская комиссия)'])
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute('SELECT * FROM orders ORDER BY id DESC').fetchall()
        cw.writerows(rows)
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=agency_report.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@app.route('/generate_qr')
def generate_qr():
    amount_str = request.args.get('amount', '0')
    amount = float(amount_str) if amount_str and amount_str != '' else 0
    rate, comm = get_settings()
    
    # Считаем твой доход (например, 5% от суммы сделки)
    reward = round(amount * (float(comm) / (100 + float(comm))), 2)

    if amount > 0:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute('INSERT INTO orders (date, total, reward) VALUES (?, ?, ?)', 
                         (datetime.now().strftime("%d.%m.%Y %H:%M"), amount, reward))
            conn.commit()

    # Умная ссылка: сама поймет, какой сейчас домен (render или твой новый)
    base_url = request.host_url.rstrip('/')
    pay_link = f"{base_url}/success?amount={amount}"
    
    img = qrcode.make(pay_link)
    buf = BytesIO()
    img.save(buf, 'PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

@app.route('/payment-info')
def payment_info(): return render_template('payment.html')
@app.route('/policy')
def policy(): return render_template('policy.html')
@app.route('/return-rules')
def return_rules(): return render_template('return.html')
@app.route('/offer')
def offer(): return render_template('offer.html')
@app.route('/success')
def success(): return render_template('success.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

