# Films studio (read me first)

Reusable 2D animation studio: every frame is drawn in Python (skia), music and effects are synthesized with numpy, voices come from the local Kokoro neural TTS, ffmpeg joins it all.

Before any film work read, in order:
1. `STYLE_BIBLE.md` – the look, the colour rules, the cast of voices.
2. `METHOD.md` – the steps, the checks, and every trap that already cost time.
3. `FILM_LIST.md` – what has been made, so the next film takes a new angle.
4. `references/REFERENCE_FILMS.md` – what each reference film does, the patterns they share, and which topics they have already taken.

Layout
- `toolkit/studio/` reusable code: `core.py` (wobble, glow, text, grain, letterbox, camera), `character.py` (rig, faces, IK, contact misses), `props.py` (furniture, phone UI, HUD, villain), `sound.py` (instruments, effects, mixing, phone levels), `voice.py` (neural voices), `render.py` (parallel render, contact sheets).
- `films/<title>/` one folder per film: `lines.py`, `timeline.py` (the only place times live), `scene.py`, `sound_build.py`, `check.py`, `render_film.py`, `packaging/`, `release/`.
- `references/thumbnails/` thumbnails from the reference channel: study material for packaging, never to be copied.
- `references/films/` timestamped contact sheets of the reference films, same rule.
- Film-specific code never goes into `toolkit/`.

Never jump from an idea to a final render. Pitch, story + timeline, scene sheets, contact check, sound, render, check the mp4 itself, package, then update the three files above.
