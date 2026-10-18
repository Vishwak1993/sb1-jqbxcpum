# FRAUD. | An Animated Short Film (2:48)

He got the job and was sure it was a mistake. Only he could see his badge flicker red: FRAUD. He counted down to his probation review, said nothing in meetings, hid what he didn't know, and typed a resignation letter the night before. In the lift on review day, every badge flickered the same word.

Captions only, in the reference films' style: no narrator, the villain whispers "they'll find out.", the music carries the feeling.

- `release/FRAUD_master_1080p.mp4` master, 1920x1080, 30 fps, H.264 CRF 18, AAC 256k stereo
- `release/FRAUD_1080p_download.mp4` download copy; `release/FRAUD_phone_720p.mp4` phone copy
- `release/FRAUD_thumbnail_1280x720.png` (A) and `packaging/FRAUD_thumbnail_B_1280x720.png` (B), `packaging/PUBLISHING_PACKAGE.md`
- `release/FINAL_CONTACT_SHEET.png` frames pulled from the finished mp4

Rebuild (from this folder, with the toolkit venv and KOKORO_DIR set):
`python make_voices.py && python sound_build.py && python check.py contact && python render_film.py`
