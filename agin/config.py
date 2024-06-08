from telethon import *
import asyncio
import sqlite3
import os

itil = '15995433'
basah = '6fc6fd0c77e5494c14724442abe46e5e'
kuyup = '6918566731:AAF8DtU_mHMsTIN13WGTQSNo_2XDWUMGXAw' #Ganti token bot di sini

if not os.path.exists('agin/Berkas.db'):
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
else:
    conn = sqlite3.connect('agin/Berkas.db')
    c = conn.cursor()

cangcut = [6691212410, 6235243365]

bot = TelegramClient('bot', itil, basah).start(bot_token=kuyup)

@bot.on(events.NewMessage(pattern='/start|config|/config'))
async def start(event):
    buttons = [
        [Button.inline("Lihat Berkas", data="config")]
    ]
    await event.respond('Halo! Saya adalah Bot File Config', buttons=buttons)

@bot.on(events.NewMessage(pattern='/up'))
async def config(event):
    if event.message.sender_id not in cangcut:
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
        await event.respond('kirim config terus reply /up')

@bot.on(events.CallbackQuery(data=b'config'))
async def cnfgmnu_(event):
    c.execute("SELECT id, file_path FROM files")
    result = c.fetchall()
    if result:
        buttons = []
        for idx, row in enumerate(result, start=1):
            buttons.append([
                Button.inline(f"📁 {os.path.basename(row[1])} 📥", data=f"ambil_{row[0]}"),
                Button.inline("❌", data=f"hapus_{row[0]}")
            ])
        reply_markup = bot.build_reply_markup(buttons)
        pesan = await event.edit('👇 ** Berikut adalah daftar file Config ** 👇', buttons=reply_markup)
        await asyncio.sleep(10)
        await pesan.delete()
    else:
        await event.edit('❌ Tidak ada file yang ditemukan.')


@bot.on(events.CallbackQuery(data=lambda data: data.startswith(b'ambil_')))
async def ambil(event):
    file_id = event.data.decode('utf-8').split('_', 1)[-1]
    c.execute("SELECT file_path FROM files WHERE id=?", (file_id,))
    result = c.fetchone()
    if result:
        file_path = result[0]
        await event.respond('Semoga Bermanfaat!!!', file=await event.client.upload_file(file_path))
    else:
        await event.respond('File tidak ditemukan.')

@bot.on(events.CallbackQuery(data=lambda data: data.startswith(b'hapus_')))
async def hapus(event):
    if event.sender_id not in cangcut:
        await event.answer('Fitur Hanya Untuk Admin')
        return
    file_id = event.data.decode('utf-8').split('_', 1)[-1]
    c.execute("SELECT file_path FROM files WHERE id=?", (file_id,))
    result = c.fetchone()
    if result:
        file_path = result[0]
        os.remove(file_path)
        c.execute("DELETE FROM files WHERE id=?", (file_id,))
        conn.commit()
        await event.answer('File berhasil dihapus!')
    else:
        await event.answer('File tidak ditemukan.')

print("Bot is starting...")
bot.run_until_disconnected()
print("Bot stopped.")
