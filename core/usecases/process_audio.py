from core.entities.audio_segment import AudioSegment
from core.usecases.find_peak_segment import find_peak_segment

def process_audio(audio_segment: AudioSegment, file_size_mb: float, max_file_size_mb: float = 20):
    if file_size_mb >= max_file_size_mb:
        return audio_segment.data[:30 * audio_segment.sample_rate]
    else:
        start_time, end_time = find_peak_segment(audio_segment.data, audio_segment.sample_rate)
        start_sample = int(start_time * audio_segment.sample_rate)
        end_sample = int(end_time * audio_segment.sample_rate)
        return audio_segment.data[start_sample:end_sample]
