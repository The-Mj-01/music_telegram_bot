class TelegramDownloader:
    def __init__(self, bot):
        self.bot = bot

    def download(self, file_info):
        file_path = file_info.download()
        return file_path
