import subprocess

class FFmpegConverter:
    def convert_to_wav(self, input_file, output_file="processed_audio.wav"):
        command = ['ffmpeg', '-i', input_file, output_file]
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output_file
