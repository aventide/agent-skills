#!/usr/bin/env bash
# Symlink skills from this repo into ~/.claude/skills.
# Usage: ./install.sh [skill-name ...]   (no arguments = every skill)
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dest="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
mkdir -p "$dest"

if [ "$#" -eq 0 ]; then
	set -- $(ls "$repo/skills")
fi

for name in "$@"; do
	src="$repo/skills/$name"
	target="$dest/$name"
	if [ ! -f "$src/SKILL.md" ]; then
		echo "skip $name: no skills/$name/SKILL.md" >&2
		continue
	fi
	if [ -L "$target" ]; then
		ln -sfn "$src" "$target"
		echo "linked $name (updated)"
	elif [ -e "$target" ]; then
		echo "skip $name: $target exists and isn't a symlink" >&2
	else
		ln -s "$src" "$target"
		echo "linked $name"
	fi
done
