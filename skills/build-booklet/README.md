# build-booklet

Turns coding work into an instruction booklet you build yourself, structured like a LEGO manual:

- a **preview** of the finished thing
- numbered **sections** sized for one sitting, each made of 10–20 minute **steps**
- every step says what to build, where it goes, and how to check it worked
- a **hint ladder** (nudge → approach → key code) instead of answers
- a **recap** after each section, written from your actual code

Then it coaches you while you build. Paste these into Claude:

| Command | What happens |
| --- | --- |
| `next` | Shows your next step. |
| `hint 1.2` | Gives the next hint for a step. |
| `check section 1` | Reviews every step in the section, lists anything that's off as pointers rather than fixes, ticks the steps that pass, and writes the recap. |
| `check 1.2` | Optional spot check on one step. |

**Works with:** Claude Code. The booklet format and renderer are plain Markdown and Python. The Claude-specific parts are the `CLAUDE.md` offer and "Tell Claude" wording in the viewer.

## Use

```text
> /build-booklet I want to build a CLI habit tracker in Rust in ~/Dev/habits.
> /build-booklet pick back up on this project and plan what's next
> /build-booklet add a /blog section to this site, I'll build it myself
```

It writes `booklet/` in your repo (`booklet/features/<name>/` for a single feature) and renders `booklet/view.html`.

## Files

- `SKILL.md`: the workflow
- `references/booklet-format.md`: Markdown templates the renderer depends on
- `scripts/render_booklet.py`: renders `booklet/*.md` into `view.html` (no dependencies; the page loads marked and mermaid from a CDN)
- `assets/viewer.html`: the viewer template
- `evals/evals.json`: test prompts and pass/fail checks from development
