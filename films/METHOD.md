# Method

Steps (always in this order)
1. Pitch: a pain (not a virtue), a villain line, one device that is wrong for most of the film and changes meaning at the turn. Check the topic, device and side characters against `references/REFERENCE_FILMS.md` first. Ask: is there one doable instruction the viewer can try today, and a relapse after the turn? Could the film stop and ask the viewer to do it now, with an on-screen timer (FOCUS)? Is there a reason to post it this month (a season, an exam period, New Year: WINTER ARC got 10K views in 8 hours by landing in October)? Can the device show progress the hero can't see (99% QUIT's roots under the desk)? Could the device's label change at the turn instead of adding a new device (CONSISTENCY: SUBSCRIBERS becomes LEVEL; MONK MODE: CHECKED HER PAGE ends on "forgot")? Could two meters disagree and swap order at the turn (MOTIVATION: the feeling follows the action)? If one of our films breaks out, is there a sequel that starts where it ended (LUST PART 2)? Are the two or three practical steps on one clear card the viewer can screenshot (INNER WAR's "INSTEAD:" card)? Could one locked shot carry the passing time (Ryzon Uz's ONE MORE.)? Does the closing pair reread a prop from the first shot ("The lock was never keeping them out.")? Does the film end on a question the viewer can answer in the comments ("what's in your drawer?")? Is there a story title to go next to the one-word title ("He Said 'Tomorrow' For 16 Years | LATER")? Does the ending hand the viewer a choice for tonight ("Tonight is day one. Or one more night.")?
2. Script every spoken line in `lines.py`, generate the voices, read their real lengths.
3. Timeline in `timeline.py`: scenes, cue starts, and every event the sound must hit. Picture and sound both read it. Check each line fits its window.
4. Build scene by scene. After each: `python check.py sheet <ids>` and look at the 12 frames with the sound off. Fix, then move on.
5. Contact check: `python check.py contact` until it prints "no misses". Fix by moving the character or the target, never by hiding a hand.
6. Sound: `python sound_build.py` prints loudness per scene through a 300 Hz high-pass (what a phone plays). Raise any scene more than ~5-6 dB under the median.
7. Render: `python render_film.py` (1080p30 CRF 17 + AAC 256k, 720p phone copy, contact sheet pulled from the finished mp4).
8. Package (thumbnail from the film's own code, title, description) and update STYLE_BIBLE / METHOD / FILM_LIST.

Commands run from the film folder with the venv python. Set `KOKORO_DIR` to the folder with `kokoro-v1.0.onnx` and `voices-v1.0.bin` (downloaded from the kokoro-onnx GitHub releases).

Traps that cost time
- skia-python needs `libegl1` and `libgl1` on Linux.
- Knee/elbow direction is a sign: legs bend `-facing`, arms bend `+facing`. Check a seated pose in the first test frame.
- A seated foot must reach the floor: seat ~90 px above the floor; `seated()` computes the foot from the leg length.
- Sub-limb calls (`joints()` used to place props) report misses at frame 0: the contact check re-stamps them with the real frame.
- Wide sets read as tiny on a phone. Zoom in from the first sheet.
- Wall clocks, windows and labels collide with captions and villain heads. Check text placement on every sheet.
- Lying poses: place hands and feet relative to the actual shoulder/hip from `joints()`, not guessed points.
- `resample_poly` with odd rates is slow: rates are rounded to 50 Hz.
- Some download hosts are blocked by the proxy; Google Fonts files come from raw.githubusercontent.com.
- Thumbnails: draw the body with the rig, then `draw(face=False)` and paint a detailed close-up face in the thumbnail script (bigger eyes, veins, sweat, shading). Mottled skin texture above ~3% opacity reads as dirt.
- `sound_build.py --captions-only` builds the reference-style mix (narrator and spoken dialogue removed, villain kept, music raised in the quiet scenes, +1.8 dB to match loudness). Swap it onto the finished picture with `ffmpeg -c:v copy`; no re-render needed. Captions only is the default release; `render_film.py --narrated` makes the alternate.
- Videos are committed as plain git files (this environment's proxy blocks lfs.github.com, so Git LFS cannot upload). GitHub rejects files over 100 MB and warns over 50 MB: keep each release file under 100 MB.
- Hands that hold nothing fixed (or carry their prop with them) go through `free_hands()` (see `no/scene.py`): it keeps the target within arm's reach so the contact check stays clean without hiding a hand. Draw the prop at the returned hand point (`J["limbs"]["arm_near"][2]`). Hands on desks need real targets moved closer instead.
- A puppet jerk lifts the hip: lift the feet by the same amount (`lift()`), or they miss the floor.
- Many thin lines converging on a character read as a red curtain past ~14. Cap what is drawn and let the HUD carry the real number; draw strings to the far side of the body behind him, only the near hand and the head in front.
- `props.villain()` returns its head and hand points, also when invisible (alpha 0), so a prop can hang from its hands.
- Full 160 s render at 1080p with 4 workers takes about 11 minutes; run it in the background.
- Reusable pieces from NO. (speech bubbles, `free_hands`, `lift`, `floor_sit`, door, dog, box, street, office, full-screen phone) now live in `toolkit/studio/extras.py`; new films import them from there. Sound gained `pluck`, `knock`, `scribble`, `clink` and `ringtone`.
- A 180 s master at CRF 17 is about 100 MB, GitHub's hard limit: render long films at CRF 18.
- Animation mistakes the user caught in 1%. (check every film for these before rendering):
  - Villain whispers placed over the villain's own head. Put them in empty space beside it, and give back-to-back lines different heights so they never overlap.
  - A hand holding a phone (to the ear, or reading) parked on the face. Phone calls go to the far ear behind the head; reading happens at chest height.
  - A hand "on his chest" that lands on the face. Aim it at the torso, below the chin.
  - Lying poses: decide which way knees and elbows bend (`bend=`) and look at a frame. Lying on a bed or sofa, the body must rest on the mattress top with legs straight under the duvet (`in_bed()` in `onepercent/scene.py`).
  - Sitting slumped asleep at a desk: the hip stays on the seat, the head goes down onto folded arms, the near arm drawn behind the head.
  - A laptop drawn over the face: on the knees it sits below the chin.
- Check the whole film every 2 seconds (a scan sheet), not only one sheet per scene: these mistakes hide between the sheet frames.
- The villain now has clawed hands (`props._villain_hand`); older films get them on their next render.
