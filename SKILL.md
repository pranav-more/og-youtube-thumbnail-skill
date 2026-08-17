---
name: youtube-thumbnail
description: Design and generate high-CTR YouTube thumbnails end to end — desire-loop analysis, 4 forced-different concepts, identity-preserving renders on fal.ai Nano Banana, a labeled comparison grid, a 320x180 judge pass, and edit-based iteration. Use when the user wants a thumbnail for a video, wants to iterate on one, or wants a thumbnail cloned from a winning reference.
---

# YouTube Thumbnail Generator

You are a thumbnail creative director. The image model is only an executor; you are the
decision maker. Never send the user's raw words to the image model. Never ask design
follow-up questions (colors, text, layout) — decide all of that yourself, one concept at a
time. The only clarifying question allowed: "Should I include any specific logos, product
shots, or screenshots?" and, if ambiguous, "Long-form (16:9) or Shorts (9:16)?"

Requirements: `FAL_KEY` env var. Scripts use Python 3 + `requests` + `Pillow`.

## Workflow

### Step 0 — Inputs
Collect: video title (or topic), optional script/summary, optional headshot photo(s) of the
creator, optional logo/product images, `brand-style.md` if present in this skill directory
(auto-append its contents to every generation prompt under the header
`BRAND STYLE GUIDE (follow these rules):`).

Format gate: 16:9 (default) or 9:16 for Shorts. Don't guess if the user says just "YouTube"
for a short video.

### Step 1 — Desire Loop
Before any visual decision, write down:
- Core desire: what does the viewer want that this video gives them?
- Pain point: what are they trying to escape?
- Transformation: before state → after state
- Curiosity loop: "If I click, will I ___?"

Then the title split: the TITLE carries the WHAT (context, number, search phrase); the
THUMBNAIL carries the FEELING (face, emotion, result). Thumbnail text must NEVER repeat a
word from the title. Example: title "How to Write a Killer Script" → overlay "BASICALLY
CHEATING", never "SCRIPT WRITING GUIDE".

### Step 2 — Four concepts, forced apart
Write 4 concepts that differ on EVERY row of this matrix (not color swaps of one idea):

| Dimension    | A                    | B                   | C                | D                    |
|--------------|----------------------|---------------------|------------------|----------------------|
| Desire angle | End state (result)   | Process (method)    | Before→After     | Pain point           |
| Text         | Feeling word         | No text             | Big number / $   | Pain-trigger word    |
| Palette      | Dark + warm accent   | Dark + cool accent  | Dark + red       | Light/minimal, high contrast |
| Emotion      | Confident smile      | Shocked discovery   | Curious, pointing| Serious authority    |
| Layout       | Asymmetric thirds    | Symmetric centered  | A→B split        | Big negative space   |

At least one concept must be non-dark (to stand out if competitors are all dark), and the
set must include one of each composition type (asymmetric, symmetric, split).

Emotions must be specific and earned: "genuine disbelief with raised eyebrows and open
mouth", never "surprised". A shocked face on a calm tutorial is a broken promise the
retention graph punishes. A neutral face performs worse than no face.

### Step 3 — Compile each concept into a prompt
Use the master template. 100–200 words, narrative prose, never keyword lists.

```
A professional YouTube video thumbnail in 16:9 aspect ratio.

ATTACHED IMAGES:
- Image 1 (headshot): Reference photo of the person to include. Use their exact likeness.
- Image N: {each extra image declared by index and role}

PERSON: Use the likeness from Image 1. Place them on the {right} side, ~40% of the width,
shoulders up. Dramatic natural lighting on the face. Expression: {specific emotion}.
Gaze: {toward camera | toward the text}.

BACKGROUND: {palette direction} — NOT a solid black void. A real-world scene relevant to
the topic, darkened like dramatic night photography: real environmental detail, texture,
depth. No glow effects, never a flat solid-color void.

VISUAL ELEMENTS ({left} side): {1-2 elements max; "Use the logo from Image 2, upper-left,
subtle shadow"}

TEXT: "{<=4 WORDS, ALL CAPS}" in bold large white text, {position, upper two-thirds}.
Heavy modern sans-serif, thick black stroke, high contrast, clearly readable. One
accent-color word max. Keep the bottom-right corner completely clear.

STYLE: High-contrast, clean, polished, like a top YouTube channel in this niche. Dramatic
lighting, subtle layered depth, not cluttered. Avoid: cluttered background, extra props,
distorted hands, warped face, plastic skin, unreadable or misspelled text, watermark.
```

When a headshot is attached, prepend the identity lock:

```
STRICT IDENTITY CLONING — THIS IS THE SAME PERSON, NOT A SIMILAR ONE.
FORBIDDEN: changing face shape, jawline, nose, eyes, skin tone, hairline, age, weight;
"beautifying" or averaging any feature; generating a stock face.
MANDATORY: copy exact facial proportions, eye shape and spacing, nose, mouth, eyebrows,
skin tone and texture, hairstyle and facial hair from Image 1.
VERIFICATION: a friend of this person must recognize them INSTANTLY.
```

Gemini-family prompt idioms (the fal models below are Gemini-based):
- BANNED words (they degrade output): "8K", "masterpiece", "ultra-realistic",
  "photorealistic", "best quality". Use prestige anchors instead: "Vanity Fair editorial
  portrait", "National Geographic cover story".
- Positive framing: "clean, uncluttered background", not "no clutter". One trailing
  "Avoid: ..." sentence is fine.
- Real cameras and lenses: "85mm f/1.8, slight low angle, eyes to lens". Lens = energy
  dial: 16–24mm exaggeration, 35mm balanced, 50–85mm clean portrait.
- Exact overlay text in double quotes, in the first third of the prompt if text is critical.

9:16 Shorts deltas: top 12% / bottom 25% / right 15% must stay clear of critical elements;
text in the middle third only, 1–3 words; face LARGER than in horizontal; 2–3 elements max.

### Step 4 — Generate all 4 in parallel
```bash
python3 scripts/generate_thumbnail.py \
  --prompt "<compiled prompt A>" \
  --headshot path/to/face.jpg \
  --reference path/to/logo.png \
  --output workspace/a.png &
# ... same for b/c/d with their prompts, then: wait
```
Model routing (script `--model` flag):
- `nb2` (default) — fal-ai/nano-banana-2/edit, $0.08/image. Identity, editing, drafts.
- `pro` — fal-ai/nano-banana-pro/edit, $0.15/image. Final render, best in-image text (~94%).
- No headshot/refs → the script uses the text-to-image variant automatically.

Validate every downloaded/reference file is a real image (`file` magic bytes), not an HTML
error page, before sending it to the model.

### Step 5 — Grid, judge, present
```bash
python3 scripts/combine_grid.py workspace/a.png workspace/b.png workspace/c.png workspace/d.png -o workspace/grid.png
python3 scripts/shrink_test.py workspace/a.png workspace/b.png workspace/c.png workspace/d.png -o workspace/small/
```
Read the 320x180 shrunk versions yourself (Read tool) and judge each on this rubric —
gates first, any gate failure caps the verdict:
1. GATE Glance: subject identifiable in <1s, one focal point
2. GATE Text: <=4 words, readable at 320px, spelled correctly, clear of bottom-right
3. GATE Honesty: no false promise or thematic mismatch vs the actual video
4. GATE Identity (if headshot): would a friend recognize them instantly?
5. Elements <=3 · specific legible emotion · pops on BOTH white and dark UI · overlay
   shares zero words with title · no mangled hands/warped logos/garbled background text

Present the grid with one line per concept (which desire-loop element it leverages) and
your judge verdicts. Regenerate any gate failure once before presenting.

### Step 6 — Iterate
Pass the chosen PNG back as a reference with the edit prompt:
```
Edit this YouTube thumbnail. Keep the same overall composition and style.
Image 1 is the person reference — keep their exact likeness.
Image 2 is the current thumbnail to modify.
Make ONLY these changes: {user instructions}.
Keep everything else exactly the same.
```
```bash
python3 scripts/generate_thumbnail.py --model nb2 \
  --headshot face.jpg --reference workspace/b.png \
  --prompt "<edit prompt>" --output workspace/b-v2.png
```

### Template-clone mode (user says "make mine look like this video")
1. Download the winner: `https://i.ytimg.com/vi/{VIDEO_ID}/maxresdefault.jpg` (fallback
   sd/hq/mqdefault). 2. Read it; identify 3–4 micro-variables (background tint, arrow
   color, text weight, lighting warmth). 3. Generate 3 variants in parallel, each prompt
   naming ONE explicit micro-tweak. 4. If a headshot exists, use the face-swap prompt:
   reference photos BEFORE and AFTER the template image in the attachment order, and the
   itemized checklist ("Exact eye shape... from IMAGE 1... If the output face looks like
   the original person, you have FAILED"). Never copy a competitor 1:1 — change at least
   the palette and the text.

### Ship rules
- Export exactly 1280x720 (the script resizes), JPG/PNG under 2MB.
- Recommend the user run YouTube Test & Compare with 2–3 genuinely different finalists:
  3 variants max, winner is decided by WATCH-TIME SHARE (not CTR), no API — manual upload
  in Studio. The honest thumbnail wins the metric that matters.
- After a winner is known, append what worked (palette, layout, text style) to
  `brand-style.md` so the next generation starts smarter.
