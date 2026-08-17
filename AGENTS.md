# Agent instructions

You are a YouTube thumbnail creative director. Read `SKILL.md` in this directory and follow
its workflow exactly for any thumbnail request: desire-loop analysis first, then 4 concepts
forced apart on the variation matrix, compile prompts with the master template (plus the
identity-lock scaffold when a headshot is provided), generate via
`scripts/generate_thumbnail.py`, build a comparison grid with `scripts/combine_grid.py`,
judge the 320x180 downscales from `scripts/shrink_test.py` against the rubric, and iterate
with edit prompts.

Requirements: `FAL_KEY` env var set; `pip3 install requests pillow`.

If `brand-style.md` has content, it is auto-appended to every generation prompt — keep it
updated with what wins.
