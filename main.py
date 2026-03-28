import discord
from discord import app_commands
from discord.ext import commands
import re
import asyncio

# --- AYARLAR ---
TOKEN = 'MTQ4NzQ1NTc3NjkzNDE5OTQwNw.G4al0W.Tesq_-OImof2-2BKfGLkX41myRmdDkNyYcczN0'
KATEGORI_ID =  1487456333299974276 # Kumarhane odaları kategorisi
OTO_ROL_ID = 1487520928182308976   # Yeni gelenlere verilecek rol ID
VARSAYILAN_FOTOGRAF = "https://media.discordapp.net/attachments/1486745717744865323/1487456786620354610/HCEEuUVXwAARc0B.png?ex=69c93595&is=69c7e415&hm=63e5dc21ce0fc9787f63633dfbcc4ab433e0d6ad9c9060a0fe58fe1dd6eec5ce&format=webp&quality=lossless&width=960&height=960&" 

# Küfür listesi (Burayı istediğin kadar genişletebilirsin)
KUFUR_LISTESI = ["küfür1", "küfür2", "anan", "bacın"] 
# ----------------

class OdaAcButonu(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎰 Oda Oluştur", style=discord.ButtonStyle.blurple, custom_id="kumarhane_oda_ac")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        category = guild.get_channel(KATEGORI_ID)

        if not category:
            return await interaction.response.send_message("❌ Kategori bulunamadı!", ephemeral=True)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, connect=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        channel = await guild.create_text_channel(name=f"🎰-{interaction.user.name}", category=category, overwrites=overwrites)
        await interaction.response.send_message(f"✅ Odan hazır: {channel.mention}", ephemeral=True)
        
        embed = discord.Embed(title="🎰 Özel Masan Hazır!", description=f"Hoş geldin {interaction.user.mention}, bol şans!", color=0xFF00FF)
        await channel.send(embed=embed)

class KumarhaneBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True # Oto rol için gerekli
        intents.message_content = True # Koruma sistemleri için gerekli
        super().__init__(command_prefix="!", intents=intents)
        self.anti_spam_counter = {}

    async def setup_hook(self):
        self.add_view(OdaAcButonu())
        await self.tree.sync()

    async def on_ready(self):
        print(f'{self.user} aktif! Sistemler yüklendi.')

bot = KumarhaneBot()

# --- 1. OTO ROL SİSTEMİ ---
@bot.event
async def on_member_join(member):
    role = member.guild.get_role(OTO_ROL_ID)
    if role:
        try:
            await member.add_roles(role)
            print(f"✅ {member.display_name} kişisine oto rol verildi.")
        except Exception as e:
            print(f"❌ Rol verme hatası: {e}")

# --- 2. KORUMA SİSTEMLERİ (KÜFÜR, URL, SPAM) ---
@bot.event
async def on_message(message):
    if message.author.bot or message.author.guild_permissions.administrator:
        return # Botları ve yöneticileri korumadan muaf tutar

    content = message.content.lower()

    # A. Küfür Koruma
    if any(kufur in content for kufur in KUFUR_LISTESI):
        await message.delete()
        await message.channel.send(f"🚫 {message.author.mention}, bu sunucuda küfür yasaktır!", delete_after=3)
        return

    # B. URL / Reklam Koruma
    # "discord.gg" veya "http" içeren mesajları yakalar
    url_pattern = r"(https?://\S+|discord\.gg/\S+)"
    if re.search(url_pattern, content):
        await message.delete()
        await message.channel.send(f"🚫 {message.author.mention}, reklam veya link paylaşımı yasaktır!", delete_after=3)
        return

    # C. Spam Koruma (Basit Mantık: 5 saniyede 5 mesaj)
    user_id = message.author.id
    if user_id not in bot.anti_spam_counter:
        bot.anti_spam_counter[user_id] = []
    
    current_time = asyncio.get_event_loop().time()
    bot.anti_spam_counter[user_id].append(current_time)
    
    # 5 saniyeden eski mesajları listeden temizle
    bot.anti_spam_counter[user_id] = [t for t in bot.anti_spam_counter[user_id] if current_time - t < 5]

    if len(bot.anti_spam_counter[user_id]) > 5:
        await message.delete()
        await message.channel.send(f"🚫 {message.author.mention}, yavaşla! Spam yapma.", delete_after=3)
        return

    await bot.process_commands(message)

# --- 3. PANEL KOMUTU ---
@bot.tree.command(name="panel", description="Kumarhane oda açma panelini kurar.")
@app_commands.describe(gorsel_url="Panelde görünecek fotoğrafın linki")
async def panel(interaction: discord.Interaction, gorsel_url: str = None):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Bu komutu sadece yöneticiler kullanabilir!", ephemeral=True)

    embed = discord.Embed(
        title="🎰 Kumarhane Girişi",
        description="Aşağıdaki butona basarak size özel kumarhane odası açabilirsiniz.\n\n**Kurallar:**\n⚠️ Küfür ve Spam yasaktır.\n⚠️ Reklam yapmak yasaktır.",
        color=0xFF00FF
    )
    
    foto = gorsel_url if gorsel_url else VARSAYILAN_FOTOGRAF
    embed.set_image(url=foto)
    
    await interaction.response.send_message("Panel kuruluyor...", ephemeral=True)
    await interaction.channel.send(embed=embed, view=OdaAcButonu())

bot.run(TOKEN)
