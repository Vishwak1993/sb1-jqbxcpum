"""Neural text-to-speech with Kokoro (local, free, no account). Cached per line.

Set KOKORO_DIR to the folder holding kokoro-v1.0.onnx and voices-v1.0.bin.
"""
import hashlib
import json
import os
from pathlib import Path

import numpy as np

from .sound import SR, resample, trim, normalize_rms, whisperize, phone_line, hp, simple_reverb

_k = None


def _kokoro():
    global _k
    if _k is None:
        from kokoro_onnx import Kokoro
        d = Path(os.environ.get("KOKORO_DIR", "models"))
        _k = Kokoro(str(d / "kokoro-v1.0.onnx"), str(d / "voices-v1.0.bin"))
    return _k


def say(text, voice, speed=1.0, cache_dir="voice_cache"):
    """Raw TTS at 48 kHz, trimmed. Cached on disk by (text, voice, speed)."""
    cache = Path(cache_dir)
    cache.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha1(json.dumps([text, voice, speed]).encode()).hexdigest()[:16]
    f = cache / f"{voice}_{key}.npy"
    if f.exists():
        return np.load(f)
    lang = "en-gb" if voice.startswith("b") else "en-us"
    a, sr = _kokoro().create(text, voice=voice, speed=speed, lang=lang)
    x = trim(resample(np.asarray(a, np.float32), sr), 0.004)
    np.save(f, x)
    return x


# Cast (see STYLE_BIBLE.md): one narrator for every film, a voice per role.
NARRATOR = dict(voice="af_heart", speed=0.88)
HIM = dict(voice="am_michael", speed=0.92)
VILLAIN = dict(voice="am_onyx", speed=0.9)


def narrate(text, **kw):
    x = say(text, **{**NARRATOR, **kw})
    return simple_reverb(normalize_rms(hp(x, 90), -19), mix=0.06)


def speak(text, role=HIM, **kw):
    return normalize_rms(hp(say(text, **{**role, **kw}), 90), -20)


def villain_whisper(text):
    return whisperize(say(text, **VILLAIN), SR, pitch=0.84)


def on_phone(text, voice="af_bella", speed=0.95):
    return phone_line(say(text, voice=voice, speed=speed))
