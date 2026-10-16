"""Generate the villain's whispers once with the neural voice and record their lengths."""
import json, os, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "toolkit"))
os.environ.setdefault("KOKORO_DIR", str(HERE / "models"))
from studio import voice as V
from studio.sound import SR
import numpy as np
from lines import VILLAIN

out = {}
(HERE / "build").mkdir(exist_ok=True)
for k, text in VILLAIN.items():
    x = V.villain_whisper(text)
    np.save(HERE / "build" / f"line_{k}.npy", x)
    out[k] = round(len(x) / SR, 2)
    print(k, out[k], text)
json.dump(out, open(HERE / "build" / "line_lengths.json", "w"), indent=1)
