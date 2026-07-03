import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Yoww! Ku soo dhawaaw Universal Downloader Bot. Noo soo dir link kasta (TikTok, Instagram, YouTube, FB) si aan kuugu soo dejiyo! 🚀")

async def download_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    await update.message.reply_text("Waan helay link-gaaga. Hadda ayaan bilaabayaa soo xajinta... ⏳")
    
    # Cobalt v10 Endpoint-ka cusub (Halkan ayaa laga beddelay)
    api_url = "https://api.cobalt.tools" 
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "url": url,
        "videoQuality": "720",
    }
    
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        data = response.json()
        
        # Cobalt v10 wuxuu soo celiyaa 'url' toos ah haddii uu guuleysto
        if "url" in data:
            video_url = data.get("url")
            await update.message.reply_text("Waa la helay! Haddana waxaan u soo rari lahaa Telegram... 📤")
            await update.message.reply_video(video=video_url)
        elif "text" in data:
            await update.message.reply_text(f"❌ API-gii baa diiday: {data.get('text')}")
        else:
            await update.message.reply_text("❌ Waan ka xumahay, link-gan ma taageeri karo hadda ama hab aan la aqoon baa dhacay.")
            
    except Exception as e:
        await update.message.reply_text(f"❌ Khalad baa dhacay: {str(e)}")

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_link))
    application.run_polling()

if __name__ == '__main__':
    main()
    
