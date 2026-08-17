# og-youtube-thumbnail-skill

An agent skill that designs and generates high-CTR YouTube thumbnails end to end: desire-loop
analysis, 4 forced-different concepts, identity-preserving renders on fal.ai Nano Banana,
a labeled comparison grid, a 320x180 judge pass, and edit-based iteration. Works with
Claude Code and Codex.

## Setup (both tools)

```bash
pip3 install requests pillow
export FAL_KEY="your-fal-ai-key"   # add to your shell profile
```

## Use with Claude Code

Install as a personal skill:

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/pranav-more/og-youtube-thumbnail-skill.git ~/.claude/skills/youtube-thumbnail
```

Then in any session: "make a thumbnail for my video about X" (or `/youtube-thumbnail`).

## Use with Codex

Codex reads `AGENTS.md` from the working directory, which routes it into the same workflow:

```bash
git clone https://github.com/pranav-more/og-youtube-thumbnail-skill.git
cd og-youtube-thumbnail-skill
codex "make a thumbnail for my video about X — my headshot is at ~/photos/me.jpg"
```

## What's inside

- `SKILL.md` — the full creative-direction workflow: concept variation matrix, master
  prompt template, identity-lock scaffold, judge rubric, 16:9 and 9:16 safe zones,
  template-clone + face-swap mode, YouTube Test & Compare guidance
- `AGENTS.md` — entry point for Codex and other AGENTS.md-compatible tools
- `scripts/generate_thumbnail.py` — fal.ai queue client (nano-banana-2 default,
  `--model pro` for finals), reference-image support, exact 1280x720 output
- `scripts/combine_grid.py` — labeled A/B/C/D comparison grid
- `scripts/shrink_test.py` — 320x180 downscales for the judge pass
- `brand-style.md` — your channel's style memory, auto-appended to every prompt

Costs: ~$0.08/image (nano-banana-2), ~$0.15/image (nano-banana-pro).
