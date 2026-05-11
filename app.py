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

@app.route('/generate_qr')
def generate_qr():
    amount_str = request.args.get('amount', '0')
    amount = float(amount_str) if amount_str else 0
    rate, comm = get_settings()
    reward = round(amount * (float(comm) / (100 + float(comm))), 2)
    if amount > 0:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute('INSERT INTO orders (date, total, reward) VALUES (?, ?, ?)', 
                         (datetime.now().strftime("%d.%m.%Y %H:%M"), amount, reward))
            conn.commit()
    base_url = request.host_url.rstrip('/')
    pay_link = f"{base_url}/success?amount={amount}"
    img = qrcode.make(pay_link)
    buf = BytesIO()
    img.save(buf, 'PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

@app.route('/download_report')
def download_report():
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Дата', 'Сумма (руб)', 'Доход ИП (комиссия)'])
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute('SELECT * FROM orders ORDER BY id DESC').fetchall()
        cw.writerows(rows)
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=report.csv"
    output.headers["Content-type"] = "text/csv"
    return output

# ЮРИДИЧЕСКИЕ СТРАНИЦЫ ДЛЯ LAVA
@app.route('/policy')
def policy(): 
    return "<h1>Политика конфиденциальности</h1><p>ИП ЛЕСНЫХ НАТАЛЬЯ СЕРГЕЕВНА (ИНН 366314033477) обязуется не передавать персональные данные третьим лицам. Сбор данных осуществляется исключительно для предоставления доступа к сервису Analytics Pro.</p><a href='/'>Назад на сайт</a>"

@app.route('/return-rules')
def return_rules(): 
    return "<h1>Условия возврата</h1><p>Согласно законодательству РФ, возврат денежных средств за цифровые продукты (лицензионные ключи, доступ к ПО) после их активации или предоставления доступа не производится. При возникновении технических проблем, пожалуйста, пишите на natali.lesnyx@mail.ru.</p><a href='/'>Назад на сайт</a>"

@app.route('/offer')
def offer(): 
    return """<h1>Публичная оферта</h1>
    <p>Настоящая оферта является официальным предложением ИП ЛЕСНЫХ Н.С. заключить договор на предоставление лицензионного доступа к аналитическому ПО.</p>
    <ul>
        <li>Услуга: Доступ к терминалу Analytics Pro на 24 часа.</li>
        <li>Стоимость: Указывается в интерфейсе оплаты.</li>
        <li>Порядок: Доступ предоставляется мгновенно после подтверждения транзакции.</li>
    </ul>
    <a href='/'>Назад на сайт</a>"""

@app.route('/payment-info')
def payment_info(): return render_template('payment.html')

@app.route('/success')
def success(): return render_template('success.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
