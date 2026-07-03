"""
Telegram Video Downloader Bot
------------------------------
Bot-kani wuxuu aqbalaa link (YouTube, TikTok, Instagram, Facebook, Twitter/X, iwm)
oo uu soo dejiyo video-ga isaga oo isticmaalaya yt-dlp, ka dibna uu ku diro user-ka
Telegram gudaheeda.

U baahan:
    pip install pyTelegramBotAPI yt-dlp --break-system-packages

TOKEN-ka waxaa lagu geliyaa Railway -> Variables (magaca BOT_TOKEN),
KOMA JIRO koodhkan si loo ilaaliyo ammaankiisa.
"""

import os
import telebot
import yt_dlp

# ------------------- SETUP -------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN lama helin! Ku dar Environment Variable magaceeda BOT_TOKEN.")

bot = telebot.TeleBot(BOT_TOKEN)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Xadka ugu badan ee Telegram ku ogolaan karo file (50MB bot API caadi ah)
MAX_FILE_SIZE_MB = 50


# ------------------- COMMANDS -------------------
@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(
        message,
        "👋 Salaam! Ii soo dir link video ah (YouTube, TikTok, Instagram, Facebook, iwm) "
        "waanan kuu soo dejin doonaa.\n\n"
        "Tusaale: https://www.tiktok.com/@user/video/123456789"
    )


# ------------------- MAIN VIDEO HANDLER -------------------
@bot.message_handler(func=lambda msg: msg.text and msg.text.startswith("http"))
def handle_link(message):
    url = message.text.strip()
    status_msg = bot.reply_to(message, "⏳ Soo dejinta ayaa socota, fadlan sug...")

    file_path = None
    try:
        ydl_opts = {
            "outtmpl": os.path.join(DOWNLOAD_DIR, "%(id)s.%(ext)s"),
            "format": "mp4/bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
            "quiet": True,
            "noplaylist": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            if not file_path.endswith(".mp4") and os.path.exists(file_path.rsplit(".", 1)[0] + ".mp4"):
                file_path = file_path.rsplit(".", 1)[0] + ".mp4"

        size_mb = os.path.getsize(file_path) / (1024 * 1024)

        if size_mb > MAX_FILE_SIZE_MB:
            bot.edit_message_text(
                f"⚠️ Video-gu waa {size_mb:.1f}MB, wuu ka weyn yahay xadka Telegram ({MAX_FILE_SIZE_MB}MB). "
                "Isku day link kale ama qulqul (quality) hoosaysa.",
                message.chat.id, status_msg.message_id
            )
            return

        with open(file_path, "rb") as video:
            bot.send_video(message.chat.id, video, caption="✅ Waa kan video-gaaga!")

        bot.delete_message(message.chat.id, status_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ Khalad ayaa dhacay: {e}", message.chat.id, status_msg.message_id)

    finally:
        # Nadaafad — tirtir file-ka kadib markii la diro
        if file_path and os.path.exists(file_path):
            os.remove(file_path)


# ------------------- RUN BOT -------------------
if __name__ == "__main__":
    print("🤖 Bot-ku wuu shaqeynayaa...")
    bot.infinity_polling()
