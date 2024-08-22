class TelegramDownloader:
    def __init__(self, bot):
        self.bot = bot

    async def download(self, file_info, destination_path):
        # دانلود فایل به مسیر مشخص
        await file_info.download_to_drive(destination_path)
        return destination_path
