import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Yoww! Ku soo dhawaaw Universal Downloader Bot. Noo soo dir link kasta (TikTok, Instagram, YouTube) si aan kuugu soo dejiyo! 🚀")

async def download_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    await update.message.reply_text("Waan helay link-gaaga. Hadda ayaan bilaabayaa soo xajinta... ⏳")
    
    # Waxaan isticmaalaynaa API aad u deggan oo loogu talagalay soo dejinta aaladaha bulshada
    api_url = f"https://api.lolhuman.xyz/api/download/tiktok?apikey=freekey&url={url}"
    
    # Haddii uu yahay Instagram, waxaan u beddeleynaa endpoint-ka Instagram
    if "instagram.com" in url:
        api_url = f"https://api.lolhuman.xyz/api/instagram?apikey=freekey&url={url}"
    # Haddii uu yahay YouTube
    elif "youtube.com" in url or "youtu.be" in url:
        api_url = f"https://api.lolhuman.xyz/api/ytvideo?apikey=freekey&url={url}"

    try:
        response = requests.get(api_url)
        data = response.json()
        
        if data.get("status") == 200:
            result = data.get("result")
            
            # Qaab dhismeedka link-ga ee soo laabanaya wuu isbedelaa marna waa qoraal marna waa link toos ah
            video_url = result if isinstance(result, str) else result.get("link") or result.get("video")
            
            if video_url:
                await update.message.reply_text("Waa la helay! Haddana waxaan u soo rari lahaa Telegram... 📤")
                await update.message.reply_video(video=video_url)
            else:
                await update.message.reply_text("❌ Waan ka xumahay, wey ku adkaatay inaan soo saaro link-ga videoga.")
        else:
            # Haddii API-gii hore uu mashquul yahay, waxaan ku dhabar-jebinaynaa Cobalt-kii qaab kale
            await try_cobalt_fallback(update, url)
            
    except Exception as e:
        # Haddii uu khalad dhaco, isna Cobalt fallback ha isku dayo
        await try_cobalt_fallback(update, url)

async def try_cobalt_fallback(update, url):
    # Hab kale oo Cobalt ah oo isticmaalaya instance ka duwan kan rasmiga ah
    try:
        api_url = "https://api.cobalt.tools"
        payload = {"url": url, "videoQuality": "720"}
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        
        response = requests.post(api_url, json=payload, headers=headers)
        data = response.json()
        
        if "url" in data:
            await update.message.reply_text("Waa la helay (via Cobalt)! U soo raridda Telegram... 📤")
            await update.message.reply_video(video=data.get("url"))
        else:
            await update.message.reply_text("❌ Server-ka ayaa hadda mashquul ah, fadlan waxyar ka dib isku day mar kale.")
    except Exception:
        await update.message.reply_text("❌ Server-ka ayaa hadda mashquul ah, fadlan waxyar ka dib isku day mar kale.")

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_link))
    application.run_polling()

if __name__ == '__main__':
    main()
    
