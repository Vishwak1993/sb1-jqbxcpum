# ONE MORE MATCH. | An Animated Short Film (2:45)

Every night was one more match. His rank climbed from Silver to Diamond while his keeper gloves gathered dust on the shelf. He made Diamond at 3:52 AM on the night before his team's final, slept through it, and they lost 2-1 without a keeper. Three days later the season ended and every rank reset to zero.

Captions only, in the reference films' style: no narrator, the villain whispers "one more match.", the music carries the feeling.

- `release/ONE_MORE_MATCH_master_1080p.mp4` master, 1920x1080, 30 fps, H.264 CRF 18, AAC 256k stereo
- `release/ONE_MORE_MATCH_1080p_download.mp4` download copy; `release/ONE_MORE_MATCH_phone_720p.mp4` phone copy
- `release/ONE_MORE_MATCH_thumbnail_1280x720.png` (A) and `packaging/ONE_MORE_MATCH_thumbnail_B_1280x720.png` (B), `packaging/PUBLISHING_PACKAGE.md`
- `release/FINAL_CONTACT_SHEET.png` frames pulled from the finished mp4

Rebuild (from this folder, with the toolkit venv and KOKORO_DIR set):
`python make_voices.py && python sound_build.py && python check.py contact && python render_film.py`
