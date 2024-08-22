import os  # برای کار با سیستم فایل
import numpy as np  # برای کار با آرایه‌ها و محاسبات عددی
import librosa  # برای پردازش فایل‌های صوتی
import soundfile as sf  # برای خواندن و نوشتن فایل‌های صوتی
from telegram import Update  # برای کار با بروزرسانی‌های تلگرام
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters  # برای مدیریت دستورات و پیام‌ها
import subprocess  # برای اجرای دستورات خط فرمان
from pydub import AudioSegment  # برای تبدیل فرمت‌های صوتی

# توکن ربات تلگرام
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# حداکثر اندازه فایل به مگابایت
MAX_FILE_SIZE_MB = 20  

# پیام خوشامدگویی برای ربات
async def start(update: Update, context):
    await update.message.reply_text("سلام! من یک ربات هستم که قسمت اوج آهنگ‌ها را برش می‌زنم.")

# تابعی برای تبدیل فرمت فایل صوتی به WAV با استفاده از FFmpeg
def convert_to_wav(input_file, output_file):
    command = ['ffmpeg', '-i', input_file, output_file]  # تنظیم دستور FFmpeg
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # اجرای دستور

# تابعی برای پیدا کردن قسمت اوج یک فایل صوتی
def find_peak_segment(audio_path, segment_duration=30):
    y, sr = librosa.load(audio_path, sr=None)  # بارگذاری فایل صوتی
    energy = librosa.feature.rms(y=y)[0]  # محاسبه انرژی کلی سیگنال در هر فریم
    max_energy_frame = np.argmax(energy)  # پیدا کردن جایی که انرژی بیشترین مقدار را دارد

    # تعیین زمان شروع و پایان اوج
    start_sample = max(0, (max_energy_frame * 512) - sr * (segment_duration // 2))  
    end_sample = start_sample + sr * segment_duration

    return start_sample / sr, end_sample / sr  # برگرداندن زمان شروع و پایان به ثانیه

# تابعی برای دانلود و پردازش فایل صوتی
async def download_and_process_audio(update: Update, context):
    audio_file = await update.message.audio.get_file()  # دریافت فایل صوتی
    file_size_mb = audio_file.file_size / (1024 * 1024)  # تبدیل به مگابایت

    # شناسایی فرمت فایل
    file_path = audio_file.file_path
    file_extension = file_path.split('.')[-1]  # استخراج پسوند فایل

    # دانلود فایل به درایو
    await audio_file.download_to_drive(f"original_audio.{file_extension}")

    # بررسی وجود فایل دانلود شده
    if not os.path.exists(f"original_audio.{file_extension}"):
        await update.message.reply_text("فایل صوتی دانلود نشد.")
        return

    # تبدیل فایل صوتی به WAV
    try:
        convert_to_wav(f"original_audio.{file_extension}", "processed_audio.wav")
    except Exception as e:
        await update.message.reply_text(f"خطا در تبدیل فایل صوتی: {e}")
        return

    # بررسی وجود فایل پردازش شده
    if not os.path.exists("processed_audio.wav"):
        await update.message.reply_text("خطا در پردازش فایل صوتی.")
        return

    try:
        # بارگذاری فایل صوتی پردازش شده
        y, sr = librosa.load("processed_audio.wav", sr=None)

        # بررسی اندازه فایل برای تصمیم‌گیری در مورد پردازش
        if file_size_mb >= MAX_FILE_SIZE_MB:
            peak_audio = y[:30 * sr]  # برش ۳۰ ثانیه‌ی اول
        else:
            # پیدا کردن قسمت اوج فایل صوتی
            start_time, end_time = find_peak_segment("processed_audio.wav")
            start_sample = int(start_time * sr)
            end_sample = int(end_time * sr)
            peak_audio = y[start_sample:end_sample]  # برش قسمت اوج

        # ذخیره فایل اوج با استفاده از soundfile
        sf.write("peak_audio.wav", peak_audio, sr)

        # تبدیل فایل WAV به MP3 با استفاده از pydub
        audio_segment = AudioSegment.from_wav("peak_audio.wav")
        audio_segment.export("peak_audio.mp3", format="mp3")

    except Exception as e:
        await update.message.reply_text(f"خطا در پردازش فایل صوتی: {e}")
        return

    # ارسال فایل صوتی به کاربر
    await context.bot.send_voice(
        chat_id=update.effective_chat.id,
        voice=open("peak_audio.mp3", "rb"),  # باز کردن فایل صوتی
        reply_to_message_id=update.message.message_id  # پاسخ به پیام اصلی
    )

    # حذف فایل‌های موقت
    os.remove(f"original_audio.{file_extension}")
    os.remove("processed_audio.wav")
    os.remove("peak_audio.wav")
    os.remove("peak_audio.mp3")

# تابع اصلی برای راه‌اندازی ربات
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()  # ساخت اپلیکیشن با توکن ربات
    app.add_handler(CommandHandler("start", start))  # اضافه کردن هندلر برای دستور شروع
    app.add_handler(MessageHandler(filters.AUDIO, download_and_process_audio))  # اضافه کردن هندلر برای پیام‌های صوتی
    app.run_polling()  # شروع به کار با polling

# اجرای تابع اصلی
if __name__ == '__main__':
    main()
