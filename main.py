import os
import threading
from flask import Flask
import telebot
import yt_dlp

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# 1. Render ke liye ek chhota sa dummy web server
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive and running!"

def run_flask():
    # Render jo PORT deta hai, us par server bind karna zaroori hai
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# 2. Telegram Bot Handlers
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Hello! Mujhe YouTube video ka link bhejein, main aapko MP3 audio bhej dunga.")

@bot.message_handler(func=lambda message: True)
def download_audio(message):
    url = message.text
    if "youtube.com" not in url and "youtu.be" not in url:
        bot.reply_to(message, "Kripya ek valid YouTube video link bhejein.")
        return

    bot.reply_to(message, "Audio download ho raha hai, thoda intezaar karein...")

    ydl_opts = {
        'format': 'bestaudio/best',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        },
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128',
        }],
        'outtmpl': 'downloaded_audio.%(ext)s',
    }

    audio_file = None
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            audio_file = filename.rsplit(".", 1)[0] + ".mp3"

        bot.reply_to(message, "Audio bheja ja raha hai...")
        with open(audio_file, 'rb') as audio:
            bot.send_audio(message.chat.id, audio)

        if os.path.exists(audio_file):
            os.remove(audio_file)

    except Exception as e:
        bot.reply_to(message, f"Kuch error aa gaya: {str(e)}")

if __name__ == '__main__':
    print("Bot aur Web Server chalu ho rahe hain...")
    try:
        bot.remove_webhook()
    except Exception:
        pass

    # Flask ko alag thread me chalate hain taaki bot polling me ruk na jaye
    server_thread = threading.Thread(target=run_flask)
    server_thread.start()

    # Bot polling start karein
    bot.infinity_polling()
