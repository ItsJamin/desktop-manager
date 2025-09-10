import keyboard
import sounddevice as sd
import numpy as np
import whisper
import tempfile
import os
import shutil
import time # Import time for sleep

class VoiceRecorder:
    def __init__(self, sample_rate=16000, channels=1, dtype='int16', hotkey="ctrl+space"):
        self.sample_rate = sample_rate
        self.channels = channels
        self.dtype = dtype
        self.hotkey = hotkey
        self.recording = False
        self.audio_data = []
        self.stream = None
        self.model = None
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
            print("Recording started... Release hotkey to stop.")
            self.recording = True
            self.audio_data = []
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.dtype,
                callback=self._callback
            )
            self.stream.start()

    def stop_recording_and_transcribe(self):
        if not self.recording:
            return

        print("Recording stopped. Transcribing...")
        self.recording = False

        # Stop and close the audio stream safely
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        if not self.audio_data:
            print("No audio recorded.")
            return

        # Concatenate recorded blocks
        recorded_audio = np.concatenate(self.audio_data, axis=0)

        # Convert to mono if necessary
        if recorded_audio.ndim > 1:
            recorded_audio = recorded_audio.mean(axis=1)

        # Convert to float32 in range [-1, 1]
        recorded_audio = recorded_audio.astype(np.float32)
        max_val = np.max(np.abs(recorded_audio))
        if max_val > 0:
            recorded_audio /= max_val

        try:
            if self.model is None:
                print("Loading Whisper model (this may take a moment)...")
                model_cache_dir = os.path.join(tempfile.gettempdir(), "whisper_models")
                os.makedirs(model_cache_dir, exist_ok=True)
                self.model = whisper.load_model("base", download_root=model_cache_dir)

            # Transcribe directly from NumPy array
            result = self.model.transcribe(
                audio=recorded_audio,
                fp16=False
            )
            print(f"You said: {result['text']}")
        except Exception as e:
            print(f"Error during transcription: {e}")

    def run(self):
        print(f"Press and hold '{self.hotkey}' to record, release to transcribe.")
        print("Press 'esc' to exit.")

        while True:
            if keyboard.is_pressed('esc'):
                print("Exiting program.")
                break

            if keyboard.is_pressed(self.hotkey):
                if not self.recording:
                    self.start_recording()
            else:
                if self.recording:
                    self.stop_recording_and_transcribe()
            
            time.sleep(0.05) # Small delay to prevent high CPU usage


if __name__ == "__main__":
    recorder = VoiceRecorder()
    recorder.run()
