from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from application.services.audio_service import AudioService
from infrastructure.converters.ffmpeg_converter import FFmpegConverter
from infrastructure.downloaders.telegram_downloader import TelegramDownloader
from infrastructure.storages.local_storage import LocalStorage

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

async def start(update: Update, context):
    await update.message.reply_text("سلام! من یک ربات هستم که قسمت اوج آهنگ‌ها را برش می‌زنم.")

async def download_and_process_audio(update: Update, context):
    file_info = await update.message.audio.get_file()
    file_size_mb = file_info.file_size / (1024 * 1024)

    downloader = TelegramDownloader(context.bot)
    converter = FFmpegConverter()
    storage = LocalStorage()
    service = AudioService(converter, storage, downloader)

    try:
        peak_audio_path = service.process_and_store_audio(file_info, segment_duration=30)
        await context.bot.send_voice(chat_id=update.effective_chat.id, voice=open(peak_audio_path, "rb"), reply_to_message_id=update.message.message_id)
    except Exception as e:
        await update.message.reply_text(f"خطا در پردازش فایل صوتی: {e}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.AUDIO, download_and_process_audio))
    app.run_polling()

if __name__ == '__main__':
    main()
