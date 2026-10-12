# ALONE | An Animated Short Film (2:38)

He has 214 friends and 0 new messages. On his birthday, nobody writes, so he decides they're busy and waits.
Then he looks out of the window: everyone across the street is alone with a phone that says 0. Everyone is waiting for someone else to go first. So he does.

The official version is captions only (reference style): no narrator, silent captions, only the villain speaks, music carries the feeling.

- `release/ALONE_master_1080p.mp4` official master, 1920x1080, 30 fps, H.264 CRF 17, AAC 256k stereo, -17.5 LUFS
- `release/ALONE_1080p_download.mp4` 27 MB copy of the master; `release/ALONE_phone_720p.mp4` phone copy (9.8 MB)
- `release/ALONE_narrated_master_1080p.mp4` alternate: same picture with the narrator and spoken dialogue, -17.7 LUFS
- `release/ALONE_thumbnail_v3_1280x720.png`, `packaging/PUBLISHING_PACKAGE.md`
- `release/FINAL_CONTACT_SHEET.png` frames pulled from the finished mp4

Rebuild (from this folder, with the toolkit venv and KOKORO_DIR set):
`python make_voices.py && python sound_build.py --captions-only && python check.py contact && python render_film.py`
(narrated alternate: `python sound_build.py --v2 && python render_film.py --narrated`)
