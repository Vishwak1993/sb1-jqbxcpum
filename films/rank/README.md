# RANK. | An Animated Short Film (3:02)

He was seventeen and preparing for JEE, and his mock-test rank floated over his head in red, the first thing anyone at home saw. Every test he studied longer and slept less, and the number grew. In the exam hall his mind went blank. That night his dad sat with him on the front step and showed him his own old rank card.

Captions only, in the reference films' style: no narrator, the villain whispers "you are your rank.", the music carries the feeling. Ends with a helpline card (Tele-MANAS 14416, findahelpline.com).

- `release/RANK_master_1080p.mp4` master, 1920x1080, 30 fps, H.264 CRF 18, AAC 256k stereo
- `release/RANK_1080p_download.mp4` download copy; `release/RANK_phone_720p.mp4` phone copy
- `release/RANK_thumbnail_1280x720.png` (A) and `packaging/RANK_thumbnail_B_1280x720.png` (B), `packaging/PUBLISHING_PACKAGE.md`
- `release/FINAL_CONTACT_SHEET.png` frames pulled from the finished mp4

Rebuild (from this folder, with the toolkit venv and KOKORO_DIR set):
`python make_voices.py && python sound_build.py && python check.py contact && python render_film.py`
