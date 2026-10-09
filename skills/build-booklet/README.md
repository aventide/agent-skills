# build-booklet

Turns coding work into an instruction booklet you build yourself, structured like a LEGO manual:

- a **preview** of the finished thing
- numbered **sections** sized for one sitting, each made of 10–20 minute **steps**
- every step says what to build, where it goes, and how to check it worked
- a **hint ladder** (nudge → approach → key code) instead of answers
- a **recap** after each section, written from your actual code

Then it coaches you while you build. Paste these into your coding agent:

| Command | What happens |
| --- | --- |
| `next` | Shows your next step. |
| `hint 1.2` | Gives the next hint for a step. |
| `check section 1` | Reviews every step in the section, lists anything that's off as pointers rather than fixes, ticks the steps that pass, and writes the recap. |
| `check 1.2` | Optional spot check on one step. |

**Works with:** Claude Code (tested). It should also work with other agents that load `SKILL.md` skills and can run shell commands, such as Codex CLI, but that's untested. The booklet format and renderer are plain Markdown and Python, and the note that keeps new sessions in booklet mode goes into `CLAUDE.md`, `AGENTS.md`, or both.

Say "stop using the booklet" to remove that note. The `booklet/` folder stays, so you can pick it back up later or delete it yourself.

## Why

When I work with an AI agent, it likely knows *exactly* what needs to be built. But sometimes I don't want it to just build it. I want to build it myself, in digestible steps, and enjoy the process. This skill comes from two ideas.

**LEGO instruction booklets.** They don't just show you how to snap bricks together. They start with a preview of what you're building, and after each part there's a review of what you just built, a piece of the whole you'll combine with the other pieces. I wanted that for code: always knowing what I'm making and what comes next, without getting lost.

**The joy of building your own furniture.** People get real satisfaction from putting together their own IKEA furniture, even though it's less convenient than having it built for them. There's a bit of struggle and some learning along the way, and you have the tools you need to do the job. But the struggle can't be so much that you give up. That's why there's a hint ladder for when I'm stuck, and why the tedious parts come done for me.

What I'm after is a flow state: enough challenge to stay engaged, small enough steps that I never feel overwhelmed.

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
