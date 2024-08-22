import soundfile as sf

class LocalStorage:
    def load_audio(self, file_path):
        audio_data, sample_rate = sf.read(file_path)
        return audio_data, sample_rate

    def save_audio(self, audio_data, sample_rate, output_file="peak_audio.wav"):
        sf.write(output_file, audio_data, sample_rate)
        return output_file
