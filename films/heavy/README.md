# HEAVY. | An Animated Short Film (2:46)

He never forgot anything. Every slight became a red stone with a name on it, dropped into the sack on his back, until he could not climb the hill to meet his old friends. At the top, the friend whose stone was the heaviest was laughing, carrying nothing. He'd forgotten it years ago.

Captions only, in the reference films' style: no narrator, the villain whispers "never forget.", the music carries the feeling.

- `release/HEAVY_master_1080p.mp4` master, 1920x1080, 30 fps, H.264 CRF 18, AAC 256k stereo
- `release/HEAVY_1080p_download.mp4` download copy; `release/HEAVY_phone_720p.mp4` phone copy
- `release/HEAVY_thumbnail_1280x720.png`, `packaging/PUBLISHING_PACKAGE.md`
- `release/FINAL_CONTACT_SHEET.png` frames pulled from the finished mp4

Rebuild (from this folder, with the toolkit venv and KOKORO_DIR set):
`python make_voices.py && python sound_build.py && python check.py contact && python render_film.py`
