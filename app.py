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
        conn.commit()

@app.route('/')
def index():
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute('SELECT value FROM settings WHERE key="rate"').fetchone()
        rate = row[0] if row else "83.5"
    return render_template('index.html', rate=rate)

@app.route('/payment-info')
def payment_info():
    return render_template('payment.html')

# ТВОЙ НОВЫЙ СЕКРЕТНЫЙ ВХОД
@app.route('/zxc_dyra', methods=['GET', 'POST'])
def admin():
    init_db()
    if request.method == 'POST':
        new_rate = request.form.get('rate')
        if new_rate:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute('UPDATE settings SET value=? WHERE key="rate"', (new_rate,))
                conn.commit()
    
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute('SELECT value FROM settings WHERE key="rate"').fetchone()
        rate = row[0] if row else "83.5"
    return render_template('admin.html', rate=rate)

# СТРАНИЦА УСПЕШНОЙ ОПЛАТЫ
@app.route('/success')
def success():
    return render_template('success.html')

# ГЕНЕРАТОР QR
@app.route('/generate_qr')
def generate_qr():
    amount = request.args.get('amount', '0')
    # Ссылка, которая зашита в QR (пока ведет на твою страницу успеха)
    pay_link = f"https://onrender.com{amount}"
    
    img = qrcode.make(pay_link)
    buf = BytesIO()
    img.save(buf, 'PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
