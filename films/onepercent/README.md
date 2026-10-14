# 1%. | An Animated Short Film (2:56)

He never stopped. Every push drains his BATTERY, while his phone charges to 100% every night on the desk beside him. He promises his little brother he'll be at his play on Friday, and runs out before he gets there.

Captions only, in the reference films' style: no narrator, the villain whispers "push through.", the music carries the feeling. One moment turns to the viewer: "Your turn. Drop your shoulders. Breathe out."

- `release/ONE_PERCENT_master_1080p.mp4` master, 1920x1080, 30 fps, H.264 CRF 18, AAC 256k stereo
- `release/ONE_PERCENT_1080p_download.mp4` download copy; `release/ONE_PERCENT_phone_720p.mp4` phone copy
- `release/ONE_PERCENT_thumbnail_1280x720.png`, `packaging/PUBLISHING_PACKAGE.md`
- `release/FINAL_CONTACT_SHEET.png` frames pulled from the finished mp4

Rebuild (from this folder, with the toolkit venv and KOKORO_DIR set):
`python make_voices.py && python sound_build.py && python check.py contact && python render_film.py`
