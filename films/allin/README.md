# ALL IN. | An Animated Short Film (3:02)

It started with ₹500 and a lucky six. The next night he lost ₹2,000, and his WINNINGS counter flipped to TO GET EVEN. Every bet to get even made the number bigger, until he bet his Goa money, then his best friend's money. The app made him a VIP. Then Kabir knocked on the door and asked what was going on.

Captions only, in the reference films' style: no narrator, the villain whispers "win it back.", the music carries the feeling. Ends with a helpline card (Tele-MANAS 14416, findahelpline.com).

- `release/ALL_IN_master_1080p.mp4` master, 1920x1080, 30 fps, H.264 CRF 18, AAC 256k stereo
- `release/ALL_IN_1080p_download.mp4` download copy; `release/ALL_IN_phone_720p.mp4` phone copy
- `release/ALL_IN_thumbnail_1280x720.png` (A) and `packaging/ALL_IN_thumbnail_B_1280x720.png` (B), `packaging/PUBLISHING_PACKAGE.md`
- `release/FINAL_CONTACT_SHEET.png` frames pulled from the finished mp4

Rebuild (from this folder, with the toolkit venv and KOKORO_DIR set):
`python make_voices.py && python sound_build.py && python check.py contact && python render_film.py`
