import numpy as np
import librosa

def find_peak_segment(audio_data, sample_rate, segment_duration=30):
    energy = librosa.feature.rms(y=audio_data)[0]
    max_energy_frame = np.argmax(energy)
    
    start_sample = max(0, (max_energy_frame * 512) - sample_rate * (segment_duration // 2))
    end_sample = start_sample + sample_rate * segment_duration
    
    return start_sample / sample_rate, end_sample / sample_rate
