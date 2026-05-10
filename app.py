from flask import Flask, render_template, request, send_file, redirect, url_for
import sqlite3, os, qrcode
from io import BytesIO

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)')
        conn.execute('INSERT OR IGNORE INTO settings (key, value) VALUES ("rate", "83.5")')
        conn.execute('INSERT OR IGNORE INTO settings (key, value) VALUES ("commission", "5")')
        conn.commit()

def get_settings():
    with sqlite3.connect(DB_PATH) as conn:
        rate_row = conn.execute('SELECT value FROM settings WHERE key="rate"').fetchone()
        comm_row = conn.execute('SELECT value FROM settings WHERE key="commission"').fetchone()
        rate = rate_row[0] if rate_row else "83.5"
        comm = comm_row[0] if comm_row else "5"
        return rate, comm

@app.route('/')
def index():
    init_db()
    rate, comm = get_settings()
    # Расчет цены для витрины: чистый курс + комиссия
    total_price = round(float(rate) * (1 + float(comm)/100), 2)
    return render_template('index.html', rate=total_price)

@app.route('/zxc_dyra', methods=['GET', 'POST'])
def admin():
    init_db()
    if request.method == 'POST':
        if 'rate' in request.form:
            new_rate = request.form.get('rate')
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute('UPDATE settings SET value=? WHERE key="rate"', (new_rate,))
        if 'commission' in request.form:
            new_comm = request.form.get('commission')
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute('UPDATE settings SET value=? WHERE key="commission"', (new_comm,))
        return redirect(url_for('admin'))
    
    rate, comm = get_settings()
    return render_template('admin.html', rate=rate, commission=comm)

@app.route('/generate_qr')
def generate_qr():
    amount = request.args.get('amount', '0')
    # Ссылка для теста (заменишь на Альфу потом)
    pay_link = f"https://onrender.com{amount}"
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
