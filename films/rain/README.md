# RAIN. | An Animated Short Film (2:43)

He complained about everything, and every complaint fed a small grey cloud over his head that rained on him and on anyone near him. His friends opened umbrellas at dinner. Then he learned that Nia, who listened to all of it, had had the worst month of anyone, and had never said a word: "you never asked."

Captions only, in the reference films' style: no narrator, the villain whispers "it's not fair.", the music and the rain carry the feeling.

- `release/RAIN_master_1080p.mp4` master, 1920x1080, 30 fps, H.264 CRF 18, AAC 256k stereo
- `release/RAIN_1080p_download.mp4` download copy; `release/RAIN_phone_720p.mp4` phone copy
- `release/RAIN_thumbnail_1280x720.png` (A) and `packaging/RAIN_thumbnail_B_1280x720.png` (B), `packaging/PUBLISHING_PACKAGE.md`
- `release/FINAL_CONTACT_SHEET.png` frames pulled from the finished mp4

Rebuild (from this folder, with the toolkit venv and KOKORO_DIR set):
`python make_voices.py && python sound_build.py && python check.py contact && python render_film.py`
