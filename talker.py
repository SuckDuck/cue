import io
import wave
import threading

import numpy as np
import sounddevice as sd
from piper import PiperVoice
from piper.config import SynthesisConfig


class Talker:
    def __init__(self, model="en_US-lessac-medium.onnx"):
        self.voice = PiperVoice.load(model)
        self.thread = None
        self.lock = threading.Lock()
        self.cancel_event = threading.Event()

    def speak(self, text):
        with self.lock:
            if self.thread and self.thread.is_alive():
                return False

            self.cancel_event.clear()
            self.thread = threading.Thread(
                target=self._speak,
                args=(text,),
                daemon=True
            )
            self.thread.start()
            return True

    def _speak(self, text):
        try:
            audio = io.BytesIO()

            with wave.open(audio, "wb") as wav:
                config = SynthesisConfig(length_scale=1.2)
                self.voice.synthesize_wav(text, wav, syn_config=config)

            if self.cancel_event.is_set():
                return

            audio.seek(0)

            with wave.open(audio, "rb") as wav:
                sample_rate = wav.getframerate()
                channels = wav.getnchannels()
                samples = wav.readframes(wav.getnframes())

            audio_data = np.frombuffer(samples, dtype=np.int16)

            if channels > 1:
                audio_data = audio_data.reshape(-1, channels)

            if self.cancel_event.is_set():
                return

            sd.play(audio_data, sample_rate)

            while not self.cancel_event.is_set():
                if not sd.get_stream().active:
                    break
                self.cancel_event.wait(0.02)

            if not self.cancel_event.is_set():
                sample_rate = 44100
                duration = 0.12
                frequency = 880

                t = np.arange(int(sample_rate * duration)) / sample_rate
                beep_audio = 0.2 * np.sin(2 * np.pi * frequency * t)

                sd.play(beep_audio.astype(np.float32), sample_rate)
                sd.wait()

        finally:
            if self.cancel_event.is_set():
                sd.stop()

    def is_speaking(self):
        return self.thread is not None and self.thread.is_alive()

    def beep(self):
        sample_rate = 44100
        duration = 0.12
        frequency = 880

        t = np.arange(int(sample_rate * duration)) / sample_rate
        audio = 0.2 * np.sin(2 * np.pi * frequency * t)

        sd.play(audio.astype(np.float32), sample_rate)
        sd.wait()
