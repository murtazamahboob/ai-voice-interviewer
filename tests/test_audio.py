from pathlib import Path

import numpy as np

from interviewer.audio import ToneCodec, char_freq, is_speech, normalize_text, rms, write_wav


def test_normalize_drops_unknown_chars():
    assert normalize_text("Hello, World! 123") == "hello, world! 123"
    assert normalize_text("ABC_xyz") == "abcxyz"


def test_char_freq_increases_with_charset():
    assert char_freq("a") < char_freq("b") < char_freq("z")


def test_codec_round_trip_exact():
    codec = ToneCodec()
    text = "a list is mutable, a tuple is immutable."
    assert codec.decode_audio(codec.encode_text(text)) == text


def test_codec_empty_text():
    codec = ToneCodec()
    assert codec.encode_text("").size == 0
    assert codec.decode_audio(np.zeros(0, dtype=np.float32)) == ""


def test_vad_silence_vs_tone():
    codec = ToneCodec()
    assert not is_speech(np.zeros(320, dtype=np.float32))
    assert is_speech(codec.encode_text("hello")[:320])
    assert rms(np.zeros(10, dtype=np.float32)) == 0.0


def test_write_wav_round_trip(tmp_path):
    codec = ToneCodec()
    path = write_wav(str(tmp_path / "q.wav"), codec.encode_text("hello"))
    assert Path(path).stat().st_size > 44
