import sounddevice as sd
import numpy as np
import shutil
import time # Import time for sleep

class VoiceRecorder:
    def __init__(self, sample_rate=16000, channels=1, dtype='int16'):
        self.sample_rate = sample_rate
        self.channels = channels
        self.dtype = dtype
        self.recording = False
        self.audio_data = []
        self.stream = None
        self._check_ffmpeg()  # Check for ffmpeg on initialization

    def _check_ffmpeg(self):
        if shutil.which("ffmpeg") is None:
            print("Warning: FFmpeg not found. Whisper may fail for some formats.")
            print("Install FFmpeg from https://ffmpeg.org/download.html and add it to PATH.")

    def _callback(self, indata, frames, time, status):
        """Called for each audio block."""
        if status:
            print(status)
        if self.recording:
            self.audio_data.append(indata.copy())

    def start_recording(self):
        if not self.recording:
            print("Recording started...")
            self.recording = True
            self.audio_data = []
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.dtype,
                callback=self._callback
            )
            self.stream.start()

    def stop_recording(self):
        if not self.recording:
            return None

        print("Recording stopped. Processing audio...")
        self.recording = False

        # Stop and close the audio stream safely
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        if not self.audio_data:
            print("No audio recorded.")
            return None

        # Concatenate recorded blocks
        recorded_audio = np.concatenate(self.audio_data, axis=0)
        self.audio_data = [] # Clear audio data after processing

        # Convert to mono if necessary
        if recorded_audio.ndim > 1:
            recorded_audio = recorded_audio.mean(axis=1)

        # Convert to float32 in range [-1, 1]
        recorded_audio = recorded_audio.astype(np.float32)
        max_val = np.max(np.abs(recorded_audio))
        if max_val > 0:
            recorded_audio /= max_val
        
        return recorded_audio
