# NO. | An Animated Short Film (2:40)

He never said no. Every yes ties another red string to him, until he moves like a puppet and the one day he kept for himself is gone too. Then he tugs a string and finds out nobody was holding it. Only his fear was.

Captions only, in the reference films' style: no narrator, the villain whispers, the music carries the feeling.

- `release/NO_master_1080p.mp4` master, 1920x1080, 30 fps, H.264 CRF 17, AAC 256k stereo, -18.0 LUFS
- `release/NO_1080p_download.mp4` 21 MB copy of the master; `release/NO_phone_720p.mp4` phone copy (14 MB)
- `release/NO_thumbnail_1280x720.png`, `packaging/PUBLISHING_PACKAGE.md`
- `release/FINAL_CONTACT_SHEET.png` frames pulled from the finished mp4

Rebuild (from this folder, with the toolkit venv and KOKORO_DIR set):
`python make_voices.py && python sound_build.py && python check.py contact && python render_film.py`
