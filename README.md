# agent-skills

My custom skills for AI coding agents. Each skill is a folder with a `SKILL.md` (a name, a description that tells the agent when to use it, and instructions), plus any scripts, references or assets it needs.

## Skills

| Skill | What it does | Works with |
| --- | --- | --- |
| [build-booklet](skills/build-booklet/) | Turns a project, or one feature, into a step-by-step instruction booklet you build by hand, then coaches you through it: next step, hints, checking your work. | Claude Code |

## Install

Symlink a skill into your Claude Code skills folder, so edits here take effect right away:

```sh
./install.sh                 # every skill
./install.sh build-booklet   # just one
```

This links `skills/<name>` to `~/.claude/skills/<name>`. If a real folder (not a link) already exists at the destination, the script skips it.

## Layout

```text
skills/<name>/
  SKILL.md        the skill itself (required)
  README.md       notes for humans
  references/     docs the agent reads when needed
  scripts/        code the agent runs
  assets/         templates and files used in output
  evals/          test prompts and pass/fail checks
```

## License

MIT. See [LICENSE](LICENSE).
