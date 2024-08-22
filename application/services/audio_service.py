from core.entities.audio_segment import AudioSegment
from core.usecases.process_audio import process_audio

class AudioService:
    def __init__(self, converter, storage, downloader):
        self.converter = converter
        self.storage = storage
        self.downloader = downloader

    def process_and_store_audio(self, file_info, segment_duration=30):
        # دانلود فایل
        file_path = self.downloader.download(file_info)
        # تبدیل فایل به WAV
        wav_path = self.converter.convert_to_wav(file_path)
        # بارگذاری فایل صوتی
        audio_data, sample_rate = self.storage.load_audio(wav_path)
        audio_segment = AudioSegment(audio_data, sample_rate)
        # پردازش فایل
        peak_audio_data = process_audio(audio_segment, file_info.size_mb)
        # ذخیره بخش اوج
        peak_path = self.storage.save_audio(peak_audio_data, sample_rate)
        return peak_path
