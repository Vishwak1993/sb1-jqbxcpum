"""Generate every line once with the neural voices and record their lengths."""
import json, os, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "toolkit"))
os.environ.setdefault("KOKORO_DIR", str(HERE / "models"))
from studio import voice as V
from studio.sound import SR
import numpy as np
from lines import LINES

out = {}
(HERE / "build").mkdir(exist_ok=True)
for k, (kind, spoken, shown) in LINES.items():
    fn = {"narr": V.narrate, "vill": V.villain_whisper, "phone": V.on_phone, "him": V.speak}[kind]
    x = fn(spoken) if kind != "him" else V.speak(spoken)
    np.save(HERE / "build" / f"line_{k}.npy", x)
    out[k] = round(len(x) / SR, 2)
    print(k, out[k])
json.dump(out, open(HERE / "build" / "line_lengths.json", "w"), indent=1)
