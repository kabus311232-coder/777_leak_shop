import os
from flask import Flask, render_template_string, request, redirect, session, url_for, flash
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = "777leak_extreme_secret_key"

# --- AYARLAR & VERİTABANI (RAM ÜZERİNDE) ---
ADMIN_USER = "adminsl"
ADMIN_PASS = "3112"
MEMO_CODE = """--[[ 777LEAK SCRIPT AKTIF ]]
loadstring(game:HttpGet('https://raw.githubusercontent.com/Documantation12/Universal-Vehicle-Script/main/Main.lua'))()"""

# Not: Render ücretsiz olduğu için site kapanınca bu veriler sıfırlanır.
users = {} # {username: password}
visitor_logs = []

def send_discord_log(title, message):
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if webhook_url:
        data = {"embeds": [{"title": title, "description": message, "color": 12517631}]}
        try: requests.post(webhook_url, json=data)
        except: pass

# --- CSS TASARIM ---
COMMON_STYLE = """
<style>
    body { background: #050505; color: #fff; font-family: 'Segoe UI', sans-serif; display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; flex-direction: column; }
    .card { background: #000; border: 2px solid #8a2be2; box-shadow: 0 0 20px #8a2be2; padding: 30px; border-radius: 15px; width: 350px; text-align: center; position: relative; }
    h1, h2 { color: #ff00ff; text-shadow: 0 0 10px #ff00ff; letter-spacing: 2px; }
    input { background: #111; border: 1px solid #333; color: #fff; padding: 12px; margin: 10px 0; width: 90%; border-radius: 5px; transition: 0.3s; }
    input:focus { border-color: #ff00ff; outline: none; box-shadow: 0 0 10px #ff00ff; }
    .btn { background: linear-gradient(45deg, #8a2be2, #ff00ff); color: #fff; border: none; padding: 12px; width: 100%; border-radius: 5px; cursor: pointer; font-weight: bold; margin-top: 10px; }
    .btn:hover { transform: scale(1.02); box-shadow: 0 0 15px #ff00ff; }
    a { color: #aaa; text-decoration: none; font-size: 12px; margin-top: 15px; display: inline-block; }
    a:hover { color: #ff00ff; }
    .alert { color: #ff4444; font-size: 13px; margin-bottom: 10px; }
    table { width: 95%; border-collapse: collapse; background: #000; margin-top: 20px; border: 1px solid #333; }
    th, td { border: 1px solid #222; padding: 10px; text-align: left; font-size: 12px; }
    th { color: #ff00ff; }
</style>
"""

# --- YOLLAR (ROUTES) ---

@app.before_request
def log_visitor():
    # Admin paneli ve statik dosyalar hariç her girişi kaydet
    if request.path == '/' or request.path == '/register' or request.path == '/login':
        ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0]
        ua = request.headers.get('User-Agent')
        zaman = datetime.now().strftime("%H:%M:%S")
        if not any(log['ip'] == ip and log['time'] == zaman for log in visitor_logs[:1]):
            visitor_logs.insert(0, {"ip": ip, "ua": ua, "time": zaman})
            send_discord_log("🌐 Yeni Ziyaretçi", f"**IP:** `{ip}`\n**Sayfa:** `{request.path}`")

@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    return render_template_string(f"""
    {COMMON_STYLE}
    <div class="card" style="width: 80%; max-width: 800px;">
        <h1>777LEAK SCRIPT</h1>
        <p>Hoş geldin, {session['user']}!</p>
        <div style="position: relative;">
            <button class="btn" onclick="copy()" style="width: auto; position: absolute; top: 10px; right: 10px; padding: 5px 10px;">KOPYALA</button>
            <pre id="code" style="background:#111; padding:20px; color:#00ff00; text-align:left; overflow-x:auto; border:1px solid #333; border-radius:10px;">{{{{ code }}}}</pre>
        </div>
        <a href="/logout" style="color:red;">OTURUMU KAPAT</a>
    </div>
    <script>
        function copy() {{
            var text = document.getElementById('code').innerText;
            navigator.clipboard.writeText(text);
            alert('Kod kopyalandı!');
        }}
    </script>
    """, code=MEMO_CODE)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = request.form.get('user')
        pw = request.form.get('pass')
        if user in users:
            flash("Bu kullanıcı adı zaten alınmış!")
        else:
            users[user] = pw
            send_discord_log("📝 Yeni Kayıt", f"**Kullanıcı:** `{user}`")
            return redirect(url_for('login'))
    return render_template_string(f"""
    {COMMON_STYLE}
    <div class="card">
        <h2>KAYIT OL</h2>
        <form method="POST">
            <input type="text" name="user" placeholder="Kullanıcı Adı" required>
            <input type="password" name="pass" placeholder="Şifre" required>
            <button type="submit" class="btn">HESAP OLUŞTUR</button>
        </form>
        <a href="/login">Zaten hesabın var mı? Giriş yap</a>
    </div>
    """)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('user')
        pw = request.form.get('pass')
        if user in users and users[user] == pw:
            session['user'] = user
            return redirect(url_for('home'))
        elif user == ADMIN_USER and pw == ADMIN_PASS:
            session['admin'] = True
            return redirect(url_for('admin_panel'))
        else:
            flash("Hatalı kullanıcı adı veya şifre!")
    
    return render_template_string(f"""
    {COMMON_STYLE}
    <div class="card">
        <h2>GİRİŞ YAP</h2>
        <form method="POST">
            <input type="text" name="user" placeholder="Kullanıcı Adı" required>
            <input type="password" name="pass" placeholder="Şifre" required>
            <button type="submit" class="btn">GİRİŞ</button>
        </form>
        <a href="/register">Yeni misin? Kayıt ol</a>
    </div>
    """)

@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin'):
        return redirect(url_for('login'))
    return render_template_string(f"""
    {COMMON_STYLE}
    <div style="width: 90%; text-align:center;">
        <h1>ADMIN KONTROL PANELİ</h1>
        <a href="/logout" style="color:red; font-weight:bold;">[ GÜVENLİ ÇIKIŞ ]</a>
        
        <h2>IP LOGLARI</h2>
        <table>
            <tr><th>IP</th><th>Cihaz</th><th>Zaman</th></tr>
            {{% for log in logs %}}
            <tr><td>{{ log.ip }}</td><td>{{ log.ua }}</td><td>{{ log.time }}</td></tr>
            {{% endfor %}}
        </table>

        <h2>KAYITLI KULLANICILAR</h2>
        <ul style="list-style:none; padding:0; color:#00ff00;">
            {{% for user in u_list %}}
            <li>{{ user }}</li>
            {{% endfor %}}
        </ul>
    </div>
    """, logs=visitor_logs, u_list=users.keys())

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
