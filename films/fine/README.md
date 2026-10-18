# FINE. | An Animated Short Film (2:55)

Every time someone asked how he was, a smiling mask with a red grin snapped onto his face and said "fine." SAID FINE counted every one. Only the viewer saw his real face, at night, when the mask went back on its hook by the door. Then one night it wouldn't come off. At Jo's Halloween party he was the only one whose mask wasn't a costume, until Jo sat down next to him on the back step and asked twice.

Captions only, in the reference films' style: no narrator, the villain whispers "say you're fine.", the music carries the feeling. Ends with a helpline card.

- `release/FINE_master_1080p.mp4` master, 1920x1080, 30 fps, H.264 CRF 18, AAC 256k stereo
- `release/FINE_1080p_download.mp4` download copy; `release/FINE_phone_720p.mp4` phone copy
- `release/FINE_thumbnail_1280x720.png` (A) and `packaging/FINE_thumbnail_B_1280x720.png` (B), `packaging/PUBLISHING_PACKAGE.md`
- `release/FINAL_CONTACT_SHEET.png` frames pulled from the finished mp4

Rebuild (from this folder, with the toolkit venv and KOKORO_DIR set):
`python make_voices.py && python sound_build.py && python check.py contact && python render_film.py`
