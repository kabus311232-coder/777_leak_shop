import os
from flask import Flask, render_template_string, request, redirect, session, url_for
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = "777leak_shop_macho_edition"

# --- AYARLAR ---
ADMIN_USER = "adminsl"
ADMIN_PASS = "3112"

# --- MAĞAZA ÜRÜNLERİ ---
# image_url kısımlarına Discord'a yüklediğin resimlerin linklerini koyabilirsin.
# Resimler kare (square) formatında ve kaliteli olursa daha iyi görünür.
products = [
    {
        "name": "MACHO",
        "description": "Premium Cheat, Undetected Bypass.",
        "price": "1500TL",
        "image_url": "GÖRSEL_LINKI_BURAYA", 
        "glow_color": "#ff0000" # Kırmızı LED
    },
    {
        "name": "SUSANO",
        "description": "Universal Aimbot, ESP, Silent Aim.",
        "price": "1200TL",
        "image_url": "GÖRSEL_LINKI_BURAYA", 
        "glow_color": "#8a2be2" # Mor LED
    },
    {
        "name": "FMA LUA",
        "description": "Script Executor for Advanced Executions.",
        "price": "900TL",
        "image_url": "GÖRSEL_LINKI_BURAYA", 
        "glow_color": "#00ffff" # Turkuaz LED
    },
    {
        "name": "SPOOFER",
        "description": "HWID Ban Removal tool. Undetected.",
        "price": "1800TL",
        "image_url": "GÖRSEL_LINKI_BURAYA", 
        "glow_color": "#ffd700" # Altın LED
    },
    {
        "name": "REDENGINE",
        "description": "The Ultimate GTA V Mod Menu.",
        "price": "2000TL",
        "image_url": "GÖRSEL_LINKI_BURAYA", 
        "glow_color": "#ff1493" # Pembe LED
    }
]

# IP'leri hafızada tutan liste
visitor_logs = []

def send_discord_log(ip, ua):
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if webhook_url:
        data = {
            "embeds": [{
                "title": "🛒 777LEAK SHOP - Giriş!",
                "description": f"**IP:** `{ip}`\n**Cihaz:** `{ua}`",
                "color": 8421504,
                "footer": {"text": f"Zaman: {datetime.now().strftime('%H:%M:%S')}"}
            }]
        }
        try: requests.post(webhook_url, json=data, timeout=5)
        except: pass

# --- TASARIM (CSS) ---
UI_STYLE = """
<style>
    :root { --main-purple: #8a2be2; --deep-black: #050505; --card-black: #0a0a0a; --text-color: #fff; }
    body { background-color: var(--deep-black); color: var(--text-color); font-family: 'Segoe UI', sans-serif; margin: 0; padding: 0; overflow-x: hidden; }
    
    .navbar { display: flex; justify-content: space-between; align-items: center; padding: 20px 50px; background-color: rgba(0,0,0,0.9); backdrop-filter: blur(10px); position: fixed; width: 100%; top: 0; z-index: 1000; border-bottom: 1px solid #1a1a1a; box-sizing: border-box; }
    .brand { display: flex; align-items: center; gap: 15px; }
    .brand-text { font-size: 24px; font-weight: 900; letter-spacing: 2px; text-transform: uppercase; text-shadow: 0 0 15px #ff00ff; }
    .nav-links a { color: #aaa; text-decoration: none; margin: 0 15px; font-weight: bold; transition: 0.3s; }
    .nav-links a:hover { color: #ff00ff; }
    .btn-discord { background: #5865F2; color: #fff; border: none; padding: 10px 25px; border-radius: 8px; cursor: pointer; font-weight: bold; }

    .hero { text-align: center; margin-top: 150px; }
    .hero h1 { font-size: 55px; font-weight: 900; letter-spacing: 5px; text-transform: uppercase; margin: 0; text-shadow: 0 0 20px var(--main-purple); }
    .hero p { color: #666; font-size: 18px; margin-top: 10px; }

    .search-container { position: relative; width: 80%; max-width: 600px; margin: 40px auto; }
    .search-input { width: 100%; background: #000; border: 1px solid #222; padding: 18px 25px; border-radius: 30px; color: #fff; font-size: 1.1rem; outline: none; border-bottom: 2px solid var(--main-purple); box-sizing: border-box; }

    .product-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; width: 90%; max-width: 1200px; margin: 50px auto; }
    .product-card { background: var(--card-black); border-radius: 15px; border: 1px solid #111; overflow: hidden; transition: 0.3s; position: relative; }
    .product-card:hover { transform: translateY(-10px); border-color: var(--main-purple); }
    .img-box { height: 250px; position: relative; background: #000; display: flex; align-items: center; justify-content: center; overflow: hidden; }
    .img-box img { width: 100%; height: 100%; object-fit: cover; opacity: 0.8; }
    .glow { position: absolute; bottom: -20px; width: 100%; height: 40px; filter: blur(30px); opacity: 0.5; }
    
    .info { padding: 20px; border-top: 1px solid #1a1a1a; }
    .title { font-size: 20px; font-weight: bold; text-transform: uppercase; margin: 0; }
    .desc { color: #666; font-size: 14px; margin: 5px 0 15px 0; height: 35px; overflow: hidden; }
    .price-box { display: flex; justify-content: space-between; align-items: center; }
    .price { color: var(--main-purple); font-weight: bold; font-size: 1.2rem; background: rgba(138,43,226,0.1); border: 1px solid var(--main-purple); padding: 5px 15px; border-radius: 20px; }
    .btn-buy { background: linear-gradient(45deg, #8a2be2, #ff00ff); border: none; color: #fff; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold; transition: 0.3s; }
    .btn-buy:hover { box-shadow: 0 0 15px #ff00ff; }

    /* Admin Panel */
    .admin-container { padding: 100px 50px; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 12px; }
    th, td { border: 1px solid #222; padding: 12px; text-align: left; }
    th { color: var(--main-purple); }
    .ip-green { color: #00ff00; font-weight: bold; }
</style>
"""

# --- YOLLAR ---

@app.route('/')
def index():
    if request.headers.get('X-Forwarded-For'): ip = request.headers.get('X-Forwarded-For').split(',')[0]
    else: ip = request.remote_addr
    ua = request.headers.get('User-Agent')
    visitor_logs.insert(0, {"ip": ip, "ua": ua, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    send_discord_log(ip, ua)

    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head><meta charset="UTF-8"><title>777LEAK SHOP</title>{UI_STYLE}</head>
    <body>
        <nav class="navbar">
            <div class="brand">
                <span class="brand-text">777LEAK SHOP</span>
            </div>
            <div class="nav-links">
                <a href="/">Anasayfa</a>
                <a href="#">Scriptler</a>
                <a href="/admin">Yönetim</a>
            </div>
            <button class="btn-discord">Discord'a Katıl</button>
        </nav>

        <div class="hero">
            <h1>ÜRÜNLERİMİZ</h1>
            <p>777Leak Güvencesiyle En Kaliteli Yazılımlar</p>
        </div>

        <div class="search-container">
            <input type="text" class="search-input" placeholder="Ürün ara...">
        </div>

        <div class="product-grid">
            {{% for p in products %}}
            <div class="product-card">
                <div class="img-box">
                    <img src="{{{{ p.image_url }}}}" alt="{{{{ p.name }}}}">
                    <div class="glow" style="background:{{{{ p.glow_color }}}};"></div>
                </div>
                <div class="info">
                    <h3 class="title">{{{{ p.name }}}}</h3>
                    <p class="desc">{{{{ p.description }}}}</p>
                    <div class="price-box">
                        <span class="price">{{{{ p.price }}}}</span>
                        <button class="btn-buy">SATIN AL</button>
                    </div>
                </div>
            </div>
            {{% endfor %}}
        </div>
    </body>
    </html>
    """, products=products)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('u') == ADMIN_USER and request.form.get('p') == ADMIN_PASS:
            session['admin'] = True
            return redirect(url_for('admin'))
    
    if session.get('admin'):
        return render_template_string(f"""
        <!DOCTYPE html>
        <html>
        <head><title>Admin Panel</title>{UI_STYLE}</head>
        <body class="admin-container">
            <h1>ZİYARETÇİ LOGLARI</h1>
            <a href="/logout" style="color:red;">Çıkış Yap</a>
            <table>
                <tr><th>IP</th><th>Cihaz</th><th>Zaman</th></tr>
                {{% for log in logs %}}
                <tr><td class="ip-green">{{ log.ip }}</td><td>{{ log.ua }}</td><td>{{ log.time }}</td></tr>
                {{% endfor %}}
            </table>
        </body>
        </html>
        """, logs=visitor_logs)

    return render_template_string(f"""
    {UI_STYLE}
    <div style="height:100vh; display:flex; align-items:center; justify-content:center;">
        <form method="POST" style="border:1px solid var(--main-purple); padding:30px; border-radius:10px;">
            <h2 style="margin-top:0;">ADMIN GİRİŞİ</h2>
            <input type="text" name="u" placeholder="Admin ID" style="width:100%; background:#111; border:1px solid #333; color:#fff; padding:10px; margin-bottom:10px;"><br>
            <input type="password" name="p" placeholder="Şifre" style="width:100%; background:#111; border:1px solid #333; color:#fff; padding:10px; margin-bottom:20px;"><br>
            <button type="submit" class="btn-buy">GİRİŞ YAP</button>
        </form>
    </div>
    """)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
