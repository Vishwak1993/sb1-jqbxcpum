# LATER. | An Animated Short Film (3:00)

His dad calls every Sunday, and every Sunday he says next week. Then he does the sum: Dad is 71, maybe 15 more years, 780 Sundays. A jar of marbles on his shelf, one for every Sunday left, and one falls out each week whether he goes or not.

Captions only, in the reference films' style: no narrator, the villain whispers "later.", the music carries the feeling.

- `release/LATER_master_1080p.mp4` master, 1920x1080, 30 fps, H.264 CRF 18, AAC 256k stereo, -18.0 LUFS, 81 MB
- `release/LATER_1080p_download.mp4` 19 MB download copy; `release/LATER_phone_720p.mp4` phone copy (13 MB)
- `release/LATER_thumbnail_1280x720.png`, `packaging/PUBLISHING_PACKAGE.md`
- `release/FINAL_CONTACT_SHEET.png` frames pulled from the finished mp4

Rebuild (from this folder, with the toolkit venv and KOKORO_DIR set):
`python make_voices.py && python sound_build.py && python check.py contact && python render_film.py`
