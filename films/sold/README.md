# SOLD. | An Animated Short Film (2:55)

He bought something every night. Every box got a sticker with the feeling it was bought for (BORED, BAD DAY, LONELY, 2AM) and went on a tower in front of the window, and every one took a coin out of the jar he was saving for the sea. When the tower fell, most of the boxes were still taped shut: he wasn't buying things, he was buying a feeling.

Captions only, in the reference films' style: no narrator, the villain whispers "treat yourself.", the music carries the feeling.

- `release/SOLD_master_1080p.mp4` master, 1920x1080, 30 fps, H.264 CRF 18, AAC 256k stereo
- `release/SOLD_1080p_download.mp4` download copy; `release/SOLD_phone_720p.mp4` phone copy
- `release/SOLD_thumbnail_1280x720.png`, `packaging/PUBLISHING_PACKAGE.md`
- `release/FINAL_CONTACT_SHEET.png` frames pulled from the finished mp4

Rebuild (from this folder, with the toolkit venv and KOKORO_DIR set):
`python make_voices.py && python sound_build.py && python check.py contact && python render_film.py`
