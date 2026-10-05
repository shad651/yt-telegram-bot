import os
import telebot
import yt_dlp
from pydub import AudioSegment

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Hello! Mujhe YouTube video ka link bhejein, main aapko MP3 audio bhej dunga (10MB se bada hone par compress kar dunga).")

def compress_audio_if_needed(file_path, target_size_mb=10):
    # Check file size in MB
    file_size = os.path.getsize(file_path) / (1024 * 1024)
    if file_size <= target_size_mb:
        return file_path  # Agar 10MB se chota ya barabar hai toh waise hi return karo

    print(f"File size {file_size:.2f}MB hai, compress kiya ja raha hai...")
    compressed_path = "compressed_" + file_path
    
    # Pydub se audio load karein
    audio = AudioSegment.from_file(file_path)
    
    # Bitrate kam karke size reduce karne ki koshish (jaise 96k ya 64k)
    # Target size ke hisab se bitrate adjust hoti hai
    audio.export(compressed_path, format="mp3", bitrate="96k")
    
    # Check karein ki compression ke baad size 10MB se kam hua ya nahi
    new_size = os.path.getsize(compressed_path) / (1024 * 1024)
    if new_size > target_size_mb:
        # Agar fir bhi bada hai toh aur kam bitrate karein (64k)
        audio.export(compressed_path, format="mp3", bitrate="64k")

    return compressed_path

@bot.message_handler(func=lambda message: True)
def download_audio(message):
    url = message.text
    if "youtube.com" not in url and "youtu.be" not in url:
        bot.reply_to(message, "Kripya ek valid YouTube video link bhejein.")
        return

    bot.reply_to(message, "Audio download ho raha hai, thoda intezaar karein...")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'downloaded_audio.%(ext)s',
    }

    audio_file = None
    final_file = None
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            audio_file = filename.rsplit(".", 1)[0] + ".mp3"

        # 10MB check & compression function call
        final_file = compress_audio_if_needed(audio_file, target_size_mb=10)

        bot.reply_to(message, "Audio bheja ja raha hai...")
        with open(final_file, 'rb') as audio:
            bot.send_audio(message.chat.id, audio)
        
        # Cleanup files
        if audio_file and os.path.exists(audio_file):
            os.remove(audio_file)
        if final_file and os.path.exists(final_file) and final_file != audio_file:
            os.remove(final_file)
            
    except Exception as e:
        bot.reply_to(message, f"Kuch error aa gaya: {str(e)}")

if __name__ == '__main__':
    print("Bot chalu ho raha hai...")
    bot.infinity_polling()
