# Style bible

World
- Near-black rooms drawn as a side slice: one floor line, a back wall, a few objects against it. Light only comes from lamps, windows, screens and the candle. The thing that matters is the thing that is lit.
- Finish on every frame: line boil (outlines redrawn every 3 frames), ~4.5% grain, soft vignette, thin letterbox bars. All text stays inside the bars.

Colour (absolute rules)
- Red = the villain and failure only (villain glow, villain whispers, a failed counter, the title underline, and anything the villain controls, like NO.'s puppet strings).
- Gold = connection and truth. It does not appear until the payoff. Screens are muted blue (a phone's charging green is the one exception, used in 1%.).
- Everything else is muted grey/blue. If a colour isn't in this list, it isn't in the film.

Character
- Pale, round head, tube limbs, no hair, no nose, no clothes. One defining detail per side character (Sam: mustard beanie).
- Staged in profile, facing right means moving forward. Raise the far arm, never the one in front of the face. Props at hip or chest height, below the chin.
- Eyebrows carry the acting: inner end up = sad/worried, inner end down = determined/angry. Check them on every emotional shot. One tear per film.
- Frame people big enough to read a face on a phone: kitchen-scale shots use ~1.3-1.5x zoom, never the full wide set.

Story shape learned from the reference films (details in `references/REFERENCE_FILMS.md`)
- The device measures the pain on screen from the first minute and changes meaning at the turn.
- Draw the lesson (a graph, a circle, a map, a quote with its author) instead of saying it.
- Set up 3-5 places in act 1 and replay them changed in act 3.
- End on a mirror (someone younger gets the lesson) or on the opening shot replayed changed.
- After the turn the world may warm up: sunrise, warm exteriors. Before it, stay dark and muted.
- Heavy topics (addiction, self-harm, grief) end with a helpline card.

Villain
- A dark person-shaped silhouette with a red glow and a red grin, always born from something already on screen (a phone's glow).
- It only whispers short lower-case lines in red text that drift up and tremble. Its text never sits on its own head or on anything busy.

Text
- Patrick Hand for captions (white, sentence case, full stop, centred near the top), Luckiest Guy for numbers and the title.
- About ten captions per film. They name the feeling, never describe the picture.
- Ending: title in caps with a red underline, then a caption pair: quiet truth in white, the punch in gold. (The reference films put the punch in red, a 2-3 word command: "Start anyway." "Go find out." Ours stays gold because gold is our connection colour; keep it a command.)

How the reference films use voice (from the transcripts of DISCIPLINE, DOPAMINE, ROOTS, Motivation Will Fail You)
- No narrator. The story is told by silent on-screen captions plus music; the only voice is the villain whispering short lines ("Nobody cares." "Just one more." "It's too hard. You deserve a break." "You're not smart."). Occasional non-verbal sounds (a snort, "woo!"). ("Heat. Heat." in auto-transcripts is music misheard.)
- Default for our films: the same. Silent captions, villain whispers, music carrying the feeling. A narrator reading the captions is an option only if the user asks for it for that film. ALONE has both versions; the user chose captions only.
- Without a narrator the music must carry the quiet openings and caption cards: check those scenes first in the phone-level table.

Sound and voices (local, free: Kokoro neural TTS)
- Narrator: `af_heart`, speed 0.88, light room reverb. Calm and intimate.
- Protagonist: `am_michael`, speed 0.92. Phone voices: `af_bella` through a 350-3200 Hz phone band.
- Villain: `am_onyx` whispered: pitched down to 0.84, breath noise that follows the voice, a lower double, a little reverb.
- One 4-chord theme per film that changes role with the story. Every visible action gets a sound on its exact frame. Every low sound gets a mid-range layer so phones play it. 1-2 s near-silence (heartbeat only) before the biggest hit.

Thumbnails (study `references/thumbnails/`; learn from them, never copy a composition, pose, prop or wording)
- Reference set: Day One Films channel (DAY 1., DOPAMINE., DISCIPLINE., WHAT IF?, JUST SHOW UP., WAKE UP., ONE LAST TIME., READ THIS.). Use them for principles only; our own films keep our own character, devices and words.
- What they do: 1-3 words in huge, thick, rounded white caps with a full stop or question mark, across the top. One face, close up, filling about half the frame, with one pushed emotion (bloodshot eyes, sweat drops, heavy brows). One story object carries the colour (red 5:00, glowing phone, red F). One light source on the face. Dark background.
- They are more rendered than the films: soft shading, texture and detail on the face and object. A thumbnail may push detail beyond the film's flat look, as long as it is still the same character.
- Ours: built from the film's own character code, then pushed. The hook word in white, the story number or object in our accent colour. Never show the payoff. Always check at 320x180 next to the reference row before shipping.
- Vary the layout from film to film. ALONE and NO. were both a big face on the right with one word on the left; the user found a third one too familiar. Other layouts: a split frame (two people, two colours, as LATER. v2), the device as the whole picture on a bright background (1%.), a wide low-angle scene with the word on the ground (HEAVY.), a full-bleed pattern of the device with the word as a stamp across it (SOLD.), a frame within the frame with words that contradict the picture (FRAUD.: "FIRST DAY." over a mirror whose badge says FRAUD), an absurd picture that reads without words (RAIN.: friends holding umbrellas at a dinner table under his cloud), a reveal split across one face (FINE.: the smiling mask pulled off half his face, the crying half showing; B: a costume party where his is the one mask that isn't a costume).
- Make two thumbnails per film: one with the title word, one with the villain's line or the hero's question as the words (Monk Mode Films swapped SEEN. for TEXT HER. and DELETE CHANNEL? for WHY NOT ME? after publishing). Use YouTube's thumbnail test, or swap after 48 hours if views stall. The user found the villain-whisper B thumbnails too alike once there were six of them (October 18): from RAIN. on, B gets its own new layout too, never the same template twice in a row. The earlier films' B versions were redone in their own layouts by `thumbnails_b2.py` (a dialog box, a calendar, a giant laptop, a paper diagram, a receipt, a spotlight); the old villain-whisper family from `thumbnails_b.py` (the villain whispering in his ear, its line as the words, one word red, the villain side alternating per film); the A versions keep a new layout every film.
- Stay distinct from the channels we study: Last Soul (silhouettes, 133K views) out-performs NOT TODAY (a repeated template, under 1K) by being different. Each of our films gets a new device, a new main location and a new thumbnail layout.
- Every thumbnail has a big, readable face from October 18 on (the channel's small-figure thumbnails got about 2% click-through and zero clicks from Suggested). Vary the layout around the face, not instead of it. Never put text or the key object in the bottom-right corner, where YouTube puts the time badge.
- Every film opens on a moving picture with the device in frame 1 and the first caption over it. No black card at the start.
- The four films already on the channel (NO., LATER., 1%., HEAVY.) were re-rendered with a picture opening and given big-face thumbnails (`thumbnails_face.py`) on October 18. ALONE. stays shelved (unlist it): its v3 thumbnail is already a big face, but the film is too close to Day One's LONELINESS.
