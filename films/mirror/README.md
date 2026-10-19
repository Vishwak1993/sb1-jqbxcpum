# MIRROR. | An Animated Short Film (3:02)

In every mirror his reflection was smaller than he was: grey, hunched, and shrinking a little more with every body he measured himself against. He trained harder, wore a hoodie at 38 degrees, stood at the back of every photo and kept telling his old swim friend "after i bulk." Then the big man he envied at the gym asked him to take his photo, needed 37 tries, deleted them all, and in the mirror his reflection was small too.

Captions only, in the reference films' style: no narrator, the villain whispers "not enough.", the music carries the feeling. Ends with a helpline card (Tele-MANAS 14416, findahelpline.com).

- `release/MIRROR_master_1080p.mp4` master, 1920x1080, 30 fps, H.264 CRF 18, AAC 256k stereo
- `release/MIRROR_1080p_download.mp4` download copy; `release/MIRROR_phone_720p.mp4` phone copy
- `release/MIRROR_thumbnail_1280x720.png` (A) and `packaging/MIRROR_thumbnail_B_1280x720.png` (B), `packaging/PUBLISHING_PACKAGE.md`
- `release/FINAL_CONTACT_SHEET.png` frames pulled from the finished mp4

Rebuild (from this folder, with the toolkit venv and KOKORO_DIR set):
`python make_voices.py && python sound_build.py && python check.py contact && python render_film.py`
