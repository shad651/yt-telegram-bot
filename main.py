import os
import telebot
import yt_dlp

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

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
    
    # Yahan preferredquality ko 128k ya 96k rakhne se bade videos ka size bhi 10MB ke andar hi ban jata hai
    ydl_opts = {
        'format': 'bestaudio/best',
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
    print("Bot chalu ho raha hai...")
    bot.infinity_polling()
