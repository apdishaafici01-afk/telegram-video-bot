import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Yoww! Ku soo dhawaaw Universal Downloader Bot. Noo soo dir link kasta (TikTok, Instagram, YouTube) si aan kuugu soo dejiyo! 🚀")

async def download_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    await update.message.reply_text("Waan helay link-gaaga. Hadda ayaan bilaabayaa soo xajinta... ⏳")
    
    # Habaynta rasmiga ah ee yt-dlp iyadoo la isticmaalayo Browser Fake User-Agent
    ydl_opts = {
        'outtmpl': 'video.%(ext)s',
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
        await update.message.reply_text("Waa la soo dejiyay! Hadda ayaan u soo rari lahaa Telegram... 📤")
        
        with open(filename, 'rb') as video:
            await update.message.reply_video(video=video)
            
        os.remove(filename)
        
    except Exception as e:
        # Haddii uu link-gu yahay TikTok gaaban, mararka qaarkood wuxuu u baahan yahay inuu si toos ah u dhaafo nidaamka
        await update.message.reply_text(f"❌ Khalad baa dhacay: Server-ka ayaa mashquul ah ama link-ga ayaa khaldan.")

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_link))
    application.run_polling()

if __name__ == '__main__':
    main()
    
