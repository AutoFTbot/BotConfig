from telethon import *
import asyncio
import sqlite3
import os

api_id = '15995433'
api_hash = '6fc6fd0c77e5494c14724442abe46e5e'
bot_token = '7472225187:AAGfIphvCT8BNX68WROq4JklZUlyPJKw1ZA' #GANTI DENGAN TOKEN BOT KALIAN

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

os.makedirs('agin', exist_ok=True)

conn = sqlite3.connect('agin/Berkas.db')
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    file_path TEXT
);
""")
conn.commit()

admin_id = [6691212410, 6235243365, 1901832020, ]

@bot.on(events.NewMessage(pattern='/up'))
async def config(event):
    if event.message.sender_id not in admin_id:
        await event.respond('Fitur Hanya Untuk Admin')
        return
    if event.message.document:
        file = await bot.download_media(event.message, "agin/Berkas")
        user_id = event.message.sender_id
        c.execute("INSERT INTO files (user_id, file_path) VALUES (?, ?)", (user_id, file))
        conn.commit()
        agin = await event.respond('berhasil diunggah!')
        await asyncio.sleep(5)
        await agin.delete()
    else:
        await event.respond('Kirim config terus reply /up')

@bot.on(events.CallbackQuery(data=b'config'))
async def cnfgmnu_(event):
    c.execute("SELECT id, file_path FROM files")
    result = c.fetchall()
    if result:
        buttons = []
        for idx, row in enumerate(result, start=1):
            buttons.append([
                Button.inline(f"📁 {os.path.basename(row[1])} 📥", data=f"ambil_{row[0]}"),
                Button.inline("❌ Hapus", data=f"hapus_{row[0]}")
            ])
        buttons.append([Button.inline("🔙 Kembali", data="start")])
        agin = await event.edit('👇 **Berikut adalah daftar file Config** 👇', buttons=buttons)
        await asyncio.sleep(60)
        await agin.delete()
    else:
        agin = await event.edit('❌ Tidak ada file yang ditemukan.')
        await agin.delete()

@bot.on(events.CallbackQuery(data=lambda data: data.startswith(b'ambil_')))
async def ambil(event):
    file_id = event.data.decode('utf-8').split('_', 1)[-1]
    c.execute("SELECT file_path FROM files WHERE id=?", (file_id,))
    result = c.fetchone()
    if result:
        file_path = result[0]
        if os.path.exists(file_path):
            agin = await event.respond('Semoga Bermanfaat!!!', file=await event.client.upload_file(file_path))
            await asyncio.sleep(180)
            await agin.delete()
        else:
            agin = await event.respond('File tidak ditemukan di disk.')
            await agin.delete()
    else:
        agin = await event.respond('File tidak ditemukan di database.')
        await agin.delete()
        

@bot.on(events.CallbackQuery(data=lambda data: data.startswith(b'hapus_')))
async def hapus(event):
    if event.sender_id not in admin_id:
        await event.answer('Fitur Hanya Untuk Admin')
        return
    file_id = event.data.decode('utf-8').split('_', 1)[-1]
    c.execute("SELECT file_path FROM files WHERE id=?", (file_id,))
    result = c.fetchone()
    if result:
        file_path = result[0]
        if os.path.exists(file_path):
            os.remove(file_path)
        c.execute("DELETE FROM files WHERE id=?", (file_id,))
        conn.commit()
        await event.answer('File berhasil dihapus!')
    else:
        await event.answer('File tidak ditemukan di database.')

@bot.on(events.CallbackQuery(data=b'start'))
@bot.on(events.NewMessage(pattern='/start|config|/config'))
async def start(event):
    sender = await event.get_sender()
    username = sender.username or "AutoFtBot"
    buttons = [
        [Button.inline("MENU CONFIG", data="config")]
    ]
    welcome_message = f"Selamat datang, **{username}** ! Bot ini adalah kumpulan Config"
    await event.respond(welcome_message, buttons=buttons)


print("Bot is starting...")
bot.run_until_disconnected()
print("Bot stopped.")
