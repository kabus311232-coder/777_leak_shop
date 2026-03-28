import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import random
import asyncio
import time
from flask import Flask
from threading import Thread

# --- AYARLAR ---
ADMIN_ROLE_ID = 1487436124765814825  # Kendi Admin Rol ID'ni buraya yaz
MY_ID = 1465806846538547440                  # Kendi Discord ID'ni buraya yaz (Bildirimler için)
TOKEN = "MTQ4NzQ2MDM3MDUzMTQ4ODAwNw.GiVYKz.gZQn1pckDyA8V0OJYRpPzavJ1tP6FSasrptgME"              # Bot Token'ını buraya yaz
DB_FILE = "economy.json" 


# --- VERİTABANI SİSTEMİ ---
def load_data():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f: json.dump({}, f)
        return {}
    with open(DB_FILE, "r") as f:
        try: return json.load(f)
        except: return {}

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_user(data, uid):
    uid = str(uid)
    if uid not in data:
        data[uid] = {"bakiye": 1000, "ciftlik": False, "inekler": []}
    return data[uid]

class MeritBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"{self.user} Giriş Yaptı | Tüm Sistemler Aktif!")

bot = MeritBot()

# --- YETKİ KONTROLÜ ---
def is_admin():
    async def predicate(interaction: discord.Interaction):
        has_role = any(role.id == ADMIN_ROLE_ID for role in interaction.user.roles)
        if not has_role:
            await interaction.response.send_message("❌ Yetkin yok!", ephemeral=True)
            return False
        return True
    return app_commands.check(predicate)

# --- EKONOMİ VE CÜZDAN ---

@bot.tree.command(name="para-bak", description="Mevcut Coin bakiyeni gör.")
async def para_bak(interaction: discord.Interaction):
    data = load_data()
    user = get_user(data, interaction.user.id)
    embed = discord.Embed(title="💰 Merit Cüzdan", description=f"Bakiye: **{user['bakiye']} Coin**", color=0xffd700)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="para-bas", description="[ADMİN] Kullanıcıya Coin ekle.")
@is_admin()
async def para_bas(interaction: discord.Interaction, miktar: int, kullanıcı: discord.Member):
    data = load_data()
    user = get_user(data, kullanıcı.id)
    user['bakiye'] += miktar
    save_data(data)
    await interaction.response.send_message(f"✅ {kullanıcı.mention} hesabına **{miktar} Coin** eklendi.")

# --- ÇİFTLİK VE İNEK SİSTEMİ ---

@bot.tree.command(name="çiftlik", description="Çiftliğini yönet veya satın al.")
async def ciftlik(interaction: discord.Interaction):
    data = load_data(); uid = str(interaction.user.id); user = get_user(data, uid)
    
    if not user["ciftlik"]:
        view = discord.ui.View()
        btn = discord.ui.Button(label="Çiftlik Kur (5000C)", style=discord.ButtonStyle.green)
        async def buy_cb(inter):
            if user["bakiye"] < 5000: return await inter.response.send_message("❌ Yetersiz bakiye!", ephemeral=True)
            user["bakiye"] -= 5000; user["ciftlik"] = True; save_data(data)
            await inter.response.edit_message(content="🎉 Çiftliğin kuruldu! Artık inek alabilirsin.", view=None)
        btn.callback = buy_cb; view.add_item(btn)
        return await interaction.response.send_message("🚜 Henüz bir çiftliğin yok!", view=view)

    embed = discord.Embed(title="🚜 Senin Çiftliğin", color=0x2ecc71)
    if not user["inekler"]:
        embed.description = "Ahır boş. `/inek-al` ile inek alabilirsin."
    else:
        for idx, inek in enumerate(user["inekler"]):
            kalan = int(inek["buyume_zamani"] - time.time())
            durum = "✅ Satışa Hazır!" if kalan <= 0 else f"⏳ {kalan//60}dk {kalan%60}sn kaldı."
            embed.add_field(name=f"🐄 İnek #{idx+1}", value=durum, inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="inek-al", description="1000 Coin'e inek al (20 dk sonra büyür).")
async def inek_al(interaction: discord.Interaction):
    data = load_data(); uid = str(interaction.user.id); user = get_user(data, uid)
    if not user["ciftlik"]: return await interaction.response.send_message("❌ Önce çiftlik kurmalısın!", ephemeral=True)
    if user["bakiye"] < 1000: return await interaction.response.send_message("❌ Yetersiz bakiye!", ephemeral=True)
    
    user["bakiye"] -= 1000
    user["inekler"].append({"buyume_zamani": time.time() + 1200})
    save_data(data)
    await interaction.response.send_message("🐄 İnek ahıra eklendi! 20 dakika sonra /inek-sat ile satabilirsin.")

@bot.tree.command(name="inek-sat", description="Büyümüş ineği 2500 Coin'e sat.")
async def inek_sat(interaction: discord.Interaction, inek_no: int):
    data = load_data(); uid = str(interaction.user.id); user = get_user(data, uid)
    if inek_no > len(user["inekler"]) or inek_no <= 0: return await interaction.response.send_message("❌ Geçersiz inek!", ephemeral=True)
    
    inek = user["inekler"][inek_no-1]
    if inek["buyume_zamani"] > time.time(): return await interaction.response.send_message("❌ Bu inek henüz büyümedi!", ephemeral=True)
    
    user["inekler"].pop(inek_no-1); user["bakiye"] += 2500; save_data(data)
    await interaction.response.send_message(f"💰 İnek başarıyla satıldı! **+2500 Coin**.")

# --- KUMAR OYUNLARI (SLOT, CRASH, AT YARIŞI, HOROZ) ---

@bot.tree.command(name="slot", description="Şansını slotta dene!")
async def slot(interaction: discord.Interaction, miktar: int):
    data = load_data(); uid = str(interaction.user.id); user = get_user(data, uid)
    if miktar <= 0 or user["bakiye"] < miktar: return await interaction.response.send_message("❌ Bakiye yetersiz!", ephemeral=True)

    items = ["💎", "🍒", "🍋", "🔔", "⭐", "7️⃣"]
    r1, r2, r3 = [random.choice(items) for _ in range(3)]
    
    if r1 == r2 == r3:
        win = miktar * 10; user["bakiye"] += win; res = f"🔥 **JACKPOT! +{win}**"
    elif r1 == r2 or r2 == r3 or r1 == r3:
        win = miktar * 2; user["bakiye"] += win; res = f"✨ **KAZANDIN! +{win}**"
    else:
        user["bakiye"] -= miktar; res = "💀 **KAYBETTİN...**"
    
    save_data(data)
    await interaction.response.send_message(f"[ {r1} | {r2} | {r3} ]\n\n{res}")

@bot.tree.command(name="at-yarışı", description="Bir ata oyna (x3 kazandırır).")
async def at_yarisi(interaction: discord.Interaction, at_no: int, miktar: int):
    if not 1 <= at_no <= 3: return await interaction.response.send_message("1, 2 veya 3 seç!", ephemeral=True)
    data = load_data(); user = get_user(data, interaction.user.id)
    if user["bakiye"] < miktar: return await interaction.response.send_message("Yetersiz bakiye!", ephemeral=True)
    
    user["bakiye"] -= miktar; save_data(data)
    await interaction.response.send_message("🏇 Atlar start aldı...")
    await asyncio.sleep(3)
    
    kazanan = random.randint(1, 3)
    if at_no == kazanan:
        win = miktar * 3; user["bakiye"] += win; save_data(data)
        await interaction.edit_original_response(content=f"🏆 Kazanan {kazanan}. At! **+{win} Coin** kazandın!")
    else:
        await interaction.edit_original_response(content=f"❌ Kazanan {kazanan}. At! Kaybettin.")

@bot.tree.command(name="horoz-dövüşü", description="Horozunu dövüştür!")
async def horoz(interaction: discord.Interaction, miktar: int):
    data = load_data(); user = get_user(data, interaction.user.id)
    if user["bakiye"] < miktar: return await interaction.response.send_message("Yetersiz bakiye!", ephemeral=True)
    
    user["bakiye"] -= miktar; save_data(data)
    await interaction.response.send_message("🐓 Horozlar ringde...")
    await asyncio.sleep(2)
    
    if random.choice([True, False]):
        win = miktar * 2; user["bakiye"] += win; save_data(data)
        await interaction.edit_original_response(content=f"👑 Senin horoz kazandı! **+{win} Coin**")
    else:
        await interaction.edit_original_response(content="🍗 Horozun nakavt oldu... Kaybettin.")

@bot.tree.command(name="crash", description="Uçak patlamadan çekil!")
async def crash(interaction: discord.Interaction, miktar: int):
    data = load_data(); uid = str(interaction.user.id); user = get_user(data, uid)
    if miktar <= 0 or user["bakiye"] < miktar: return await interaction.response.send_message("Bakiye yetersiz!", ephemeral=True)
    
    user["bakiye"] -= miktar; save_data(data)
    mult = 1.0; crash_point = round(random.uniform(1.1, 4.5), 1); active = True

    view = discord.ui.View()
    btn = discord.ui.Button(label="NAKİT ÇEK", style=discord.ButtonStyle.green)
    async def cb(inter):
        nonlocal active
        if inter.user.id != interaction.user.id: return
        active = False
        kazanc = int(miktar * mult)
        d = load_data(); u = get_user(d, uid); u["bakiye"] += kazanc; save_data(d)
        await inter.response.edit_message(content=f"💰 Kazandın! **{kazanc} Coin** (x{mult})", view=None)
    btn.callback = cb; view.add_item(btn)

    await interaction.response.send_message(f"🚀 Çarpan: **x{mult}**", view=view)
    msg = await interaction.original_response()

    while active:
        await asyncio.sleep(1.5); mult = round(mult + 0.3, 1)
        if mult >= crash_point:
            active = False
            await msg.edit(content=f"💥 PATLADI! x{crash_point}", view=None)
            break
        if active: await msg.edit(content=f"🚀 Çarpan: **x{mult}**")

# --- KEEP ALIVE & RUN ---
app = Flask('')
@app.route('/')
def home(): return "MeritBot 7/24 Aktif!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run); t.start()

if __name__ == "__main__":
    keep_alive()
    bot.run(TOKEN)
