# Method

Steps (always in this order)
1. Pitch: a pain (not a virtue), a villain line, one device that is wrong for most of the film and changes meaning at the turn. Check the topic, device and side characters against `references/REFERENCE_FILMS.md` first. Ask: is there one doable instruction the viewer can try today, and a relapse after the turn?
2. Script every spoken line in `lines.py`, generate the voices, read their real lengths.
3. Timeline in `timeline.py`: scenes, cue starts, and every event the sound must hit. Picture and sound both read it. Check each line fits its window.
4. Build scene by scene. After each: `python check.py sheet <ids>` and look at the 12 frames with the sound off. Fix, then move on.
5. Contact check: `python check.py contact` until it prints "no misses". Fix by moving the character or the target, never by hiding a hand.
6. Sound: `python sound_build.py` prints loudness per scene through a 300 Hz high-pass (what a phone plays). Raise any scene more than ~5-6 dB under the median.
7. Render: `python render_film.py` (1080p30 CRF 17 + AAC 256k, 720p phone copy, contact sheet pulled from the finished mp4).
8. Package (thumbnail from the film's own code, title, description) and update STYLE_BIBLE / METHOD / FILM_LIST.

Commands run from the film folder with the venv python. Set `KOKORO_DIR` to the folder with `kokoro-v1.0.onnx` and `voices-v1.0.bin` (downloaded from the kokoro-onnx GitHub releases).

Traps that cost time
- skia-python needs `libegl1` and `libgl1` on Linux.
- Knee/elbow direction is a sign: legs bend `-facing`, arms bend `+facing`. Check a seated pose in the first test frame.
- A seated foot must reach the floor: seat ~90 px above the floor; `seated()` computes the foot from the leg length.
- Sub-limb calls (`joints()` used to place props) report misses at frame 0: the contact check re-stamps them with the real frame.
- Wide sets read as tiny on a phone. Zoom in from the first sheet.
- Wall clocks, windows and labels collide with captions and villain heads. Check text placement on every sheet.
- Lying poses: place hands and feet relative to the actual shoulder/hip from `joints()`, not guessed points.
- `resample_poly` with odd rates is slow: rates are rounded to 50 Hz.
- Some download hosts are blocked by the proxy; Google Fonts files come from raw.githubusercontent.com.
- Thumbnails: draw the body with the rig, then `draw(face=False)` and paint a detailed close-up face in the thumbnail script (bigger eyes, veins, sweat, shading). Mottled skin texture above ~3% opacity reads as dirt.
- `sound_build.py --captions-only` builds the reference-style mix (narrator and spoken dialogue removed, villain kept, music raised in the quiet scenes, +1.8 dB to match loudness). Swap it onto the finished picture with `ffmpeg -c:v copy`; no re-render needed. Captions only is the default release; `render_film.py --narrated` makes the alternate.
- Videos are committed as plain git files (this environment's proxy blocks lfs.github.com, so Git LFS cannot upload). GitHub rejects files over 100 MB and warns over 50 MB: keep each release file under 100 MB.
- Hands that hold nothing fixed (or carry their prop with them) go through `free_hands()` (see `no/scene.py`): it keeps the target within arm's reach so the contact check stays clean without hiding a hand. Draw the prop at the returned hand point (`J["limbs"]["arm_near"][2]`). Hands on desks need real targets moved closer instead.
- A puppet jerk lifts the hip: lift the feet by the same amount (`lift()`), or they miss the floor.
- Many thin lines converging on a character read as a red curtain past ~14. Cap what is drawn and let the HUD carry the real number; draw strings to the far side of the body behind him, only the near hand and the head in front.
- `props.villain()` returns its head and hand points, also when invisible (alpha 0), so a prop can hang from its hands.
- Full 160 s render at 1080p with 4 workers takes about 11 minutes; run it in the background.
- Reusable pieces from NO. (speech bubbles, `free_hands`, `lift`, `floor_sit`, door, dog, box, street, office, full-screen phone) now live in `toolkit/studio/extras.py`; new films import them from there. Sound gained `pluck`, `knock`, `scribble`, `clink` and `ringtone`.
- A 180 s master at CRF 17 is about 100 MB, GitHub's hard limit: render long films at CRF 18.
