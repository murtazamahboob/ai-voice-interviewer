"""Offline voice channel: a deterministic tone codec + energy VAD.

The codec is the offline stand-in for a microphone + STT/TTS pair: each
character is encoded as a short sine tone at a character-specific frequency
(``encode_text``) and decoded back by spectral peak-picking
(``decode_audio``). It is a toy codec, not a speech recogniser — but the
interview logic built on top of it (listening, turn-taking, timing) is real,
and the round trip is exact, so a whole mock interview can be run and tested
with no microphone, no network and no paid API. A real Whisper / mic adapter
can replace :class:`ToneCodec` behind the same interface.
"""
from __future__ import annotations

import wave

import numpy as np

SAMPLE_RATE = 16000
CHAR_MS = 70
CHAR_SAMPLES = SAMPLE_RATE * CHAR_MS // 1000  # 1120 samples

# Characters the tone codec can carry. Anything else is normalised away.
CHARSET = " abcdefghijklmnopqrstuvwxyz0123456789.,?'!-*+/=%"
BASE_FREQ = 300.0
FREQ_STEP = 35.0


def normalize_text(text: str) -> str:
    """Lower-case and drop characters outside the codec alphabet."""
    return "".join(ch for ch in text.lower() if ch in CHARSET)


def char_freq(ch: str) -> float:
    return BASE_FREQ + CHARSET.index(ch) * FREQ_STEP


def rms(samples: np.ndarray) -> float:
    samples = np.asarray(samples, dtype=np.float32)
    return float(np.sqrt(np.mean(samples**2))) if len(samples) else 0.0


def is_speech(frame: np.ndarray, threshold: float = 0.05) -> bool:
    """Energy voice-activity detection: loud enough to be a tone, or not."""
    return rms(frame) > threshold


class ToneCodec:
    """Encode text as tones and decode tones back to text."""

    def encode_text(self, text: str) -> np.ndarray:
        text = normalize_text(text)
        if not text:
            return np.zeros(0, dtype=np.float32)
        t = np.arange(CHAR_SAMPLES, dtype=np.float32) / SAMPLE_RATE
        window = np.hanning(CHAR_SAMPLES).astype(np.float32)
        out = np.empty(len(text) * CHAR_SAMPLES, dtype=np.float32)
        for i, ch in enumerate(text):
            tone = 0.5 * np.sin(2 * np.pi * char_freq(ch) * t) * window
            out[i * CHAR_SAMPLES : (i + 1) * CHAR_SAMPLES] = tone
        return out

    def decode_frame(self, frame: np.ndarray) -> str:
        """Decode one 70 ms frame to its character (nearest candidate tone)."""
        frame = np.asarray(frame, dtype=np.float32)
        if rms(frame) < 0.05:
            return " "  # silence inside an utterance reads as a space
        spectrum = np.abs(np.fft.rfft(frame * np.hanning(len(frame)), n=4096))
        freqs = np.fft.rfftfreq(4096, d=1.0 / SAMPLE_RATE)
        best, best_mag = " ", -1.0
        for ch in CHARSET:
            idx = int(np.argmin(np.abs(freqs - char_freq(ch))))
            if spectrum[idx] > best_mag:
                best, best_mag = ch, spectrum[idx]
        return best

    def decode_audio(self, samples: np.ndarray) -> str:
        samples = np.asarray(samples, dtype=np.float32)
        chars = []
        for start in range(0, len(samples) - CHAR_SAMPLES + 1, CHAR_SAMPLES):
            chars.append(self.decode_frame(samples[start : start + CHAR_SAMPLES]))
        return "".join(chars).strip()


def write_wav(path: str, samples: np.ndarray, sample_rate: int = SAMPLE_RATE) -> str:
    """Write float32 mono audio (-1..1) as a 16-bit PCM WAV file."""
    pcm = np.clip(np.asarray(samples, dtype=np.float32), -1.0, 1.0)
    pcm = (pcm * 32767).astype(np.int16)
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        f.writeframes(pcm.tobytes())
    return path
