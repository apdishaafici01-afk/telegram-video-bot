"""
Telegram Video Downloader Bot
------------------------------
Bot-kani wuxuu aqbalaa link kasta oo ka socda ku dhawaad 1000 website
(YouTube, TikTok, Instagram, Facebook, Twitter/X, Pinterest, Snapchat, iwm)
oo uu isticmaalo yt-dlp si uu u soo dejiyo, ka dibna uu ku diro user-ka
Telegram gudaheeda.

Waxa uu sidoo kale taageeraa TikTok "Photo Slideshow" (sawirro isku xiran +
muusig) — kuwaas oo si kale loo geeyaa (album sawir ah, ma aha video).

U baahan:
    pip install pyTelegramBotAPI yt-dlp --break-system-packages

TOKEN-ka waxaa lagu geliyaa Railway -> Variables (magaca BOT_TOKEN),
KOMA JIRO koodhkan si loo ilaaliyo ammaankiisa.

COOKIES (loogu talagalay YouTube/Instagram oo dalbanaya xaqiijin/login):
    Ku dar Railway Variable magaceeda COOKIES_B64 oo ah cookies.txt-kaaga
    oo la beddelay base64. Koodhkani wuu si toos ah u dejin doonaa marka
    bot-ku bilaabmo.
"""

import os
import glob
import base64
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
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")

# ------------------- COOKIES SETUP -------------------
# Haddii Railway Variable COOKIES_B64 la geliyay, waxaan ka dhisaynaa cookies.txt
# si yt-dlp u isticmaalo marka uu la kulmo YouTube/Instagram oo xaqiijin dalbanaya.
COOKIES_FILE = "cookies.txt"
cookies_b64 = os.environ.get("COOKIES_B64")
if cookies_b64:
    try:
        with open(COOKIES_FILE, "wb") as f:
            f.write(base64.b64decode(cookies_b64))
        print("✅ Cookies waa la dejiyay.")
    except Exception as e:
        print(f"⚠️ Cookies lama dejin karin: {e}")
        COOKIES_FILE = None
else:
    COOKIES_FILE = None
    print("ℹ️ COOKIES_B64 lama helin — YouTube/Instagram qaar ka mid ah way khaldami karaan.")


# ------------------- COMMANDS -------------------
@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(
        message,
        "👋 Salaam! Ii soo dir link (YouTube, TikTok, Instagram, Facebook, Twitter/X, "
        "Pinterest, iwm) waanan kuu soo dejin doonaa — xitaa TikTok photo slideshow-yada.\n\n"
        "Tusaale: https://www.tiktok.com/@user/video/123456789"
    )


def cleanup(job_id):
    """Tirtir dhammaan faylasha la soo dejiyay ee leh job_id-gan."""
    for f in glob.glob(os.path.join(DOWNLOAD_DIR, f"{job_id}*")):
        try:
            os.remove(f)
        except OSError:
            pass


# ------------------- MAIN LINK HANDLER -------------------
@bot.message_handler(func=lambda msg: msg.text and msg.text.startswith("http"))
def handle_link(message):
    url = message.text.strip()
    status_msg = bot.reply_to(message, "⏳ Soo dejinta ayaa socota, fadlan sug...")

    job_id = str(message.message_id)  # magac gaar u ah fariintan, si aan faylal isugu qasin

    try:
        ydl_opts = {
            "outtmpl": os.path.join(DOWNLOAD_DIR, f"{job_id}.%(ext)s"),
            "format": "mp4/bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
            "quiet": True,
            "noplaylist": True,
        }

        # Haddii cookies la helay, ku dar si YouTube/Instagram u ogolaadaan
        if COOKIES_FILE and os.path.exists(COOKIES_FILE):
            ydl_opts["cookiefile"] = COOKIES_FILE

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        # Isku daawo dhammaan faylasha la soo dejiyay ee leh job_id-gan
        downloaded_files = sorted(glob.glob(os.path.join(DOWNLOAD_DIR, f"{job_id}.*")))

        if not downloaded_files:
            bot.edit_message_text(
                "❌ Wax lama soo dejin karin. Hubi in link-ku sax yahay ama la taageero.",
                message.chat.id, status_msg.message_id
            )
            return

        image_files = [f for f in downloaded_files if f.lower().endswith(IMAGE_EXTENSIONS)]
        video_files = [f for f in downloaded_files if not f.lower().endswith(IMAGE_EXTENSIONS)]

        # ---- HADDII AY TAHAY TIKTOK PHOTO SLIDESHOW (sawirro badan) ----
        if image_files:
            media_group = []
            for i, img in enumerate(image_files[:10]):
                with open(img, "rb") as f:
                    data = f.read()
                caption = "✅ Waa kuwan sawirrada slideshow-ga!" if i == 0 else None
                media_group.append(telebot.types.InputMediaPhoto(data, caption=caption))

            bot.send_media_group(message.chat.id, media_group)

            audio_files = [f for f in video_files if f.lower().endswith((".mp3", ".m4a", ".webm"))]
            for audio in audio_files:
                with open(audio, "rb") as f:
                    bot.send_audio(message.chat.id, f, caption="🎵 Muusigga slideshow-ga")

            bot.delete_message(message.chat.id, status_msg.message_id)

        # ---- HADDII AY TAHAY VIDEO CAADI AH ----
        elif video_files:
            file_path = video_files[0]
            size_mb = os.path.getsize(file_path) / (1024 * 1024)

            if size_mb > MAX_FILE_SIZE_MB:
                bot.edit_message_text(
                    f"⚠️ Video-gu waa {size_mb:.1f}MB, wuu ka weyn yahay xadka Telegram "
                    f"({MAX_FILE_SIZE_MB}MB). Isku day link kale ama qulqul (quality) hoosaysa.",
                    message.chat.id, status_msg.message_id
                )
                return

            with open(file_path, "rb") as video:
                bot.send_video(message.chat.id, video, caption="✅ Waa kan video-gaaga!")

            bot.delete_message(message.chat.id, status_msg.message_id)

    except yt_dlp.utils.DownloadError as e:
        error_text = str(e)
        if "Sign in to confirm" in error_text or "cookies" in error_text.lower():
            bot.edit_message_text(
                "❌ Site-kan wuxuu dalbanayaa xaqiijin (cookies). Hubi in COOKIES_B64 "
                "si sax ah loo geliyay Railway Variables, ama cookies-ku way dhacay "
                "(waa inaad mar labaad soo dejisid oo cusboonaysiisid).",
                message.chat.id, status_msg.message_id
            )
        else:
            bot.edit_message_text(
                "❌ Ma soo dejin karin. Ama link-gu waa qaldan yahay, ama website-kani "
                "weli lama taageero. Isku day link kale.",
                message.chat.id, status_msg.message_id
            )

    except Exception as e:
        bot.edit_message_text(f"❌ Khalad ayaa dhacay: {e}", message.chat.id, status_msg.message_id)

    finally:
        cleanup(job_id)


# ------------------- RUN BOT -------------------
if __name__ == "__main__":
    print("🤖 Bot-ku wuu shaqeynayaa...")
    bot.infinity_polling()
