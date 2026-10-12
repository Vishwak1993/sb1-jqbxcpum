# ALONE | An Animated Short Film (2:38)

He has 214 friends and 0 new messages. On his birthday, nobody writes, so he decides they're busy and waits.
Then he looks out of the window: everyone across the street is alone with a phone that says 0. Everyone is waiting for someone else to go first. So he does.

- `release/ALONE_master_1080p.mp4` 1920x1080, 30 fps, H.264 CRF 17, AAC 256k stereo, -17.7 LUFS
- `release/ALONE_captions_only_master_1080p.mp4` same picture, reference style: no narrator, only the villain speaks (27 MB copy: `ALONE_captions_only_1080p_download.mp4`)
- `release/ALONE_phone_720p.mp4` phone copy (9.8 MB)
- `release/ALONE_thumbnail_1280x720.png`, `packaging/PUBLISHING_PACKAGE.md`
- `release/FINAL_CONTACT_SHEET.png` frames pulled from the finished mp4

Rebuild (from this folder, with the toolkit venv and KOKORO_DIR set):
`python make_voices.py && python sound_build.py && python check.py contact && python render_film.py`
