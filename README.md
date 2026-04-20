# Year1 Spellbook

The Year1 Spellbook is a mobile-friendly spellbook for Year1 homebrew campaign content that organizes spell lists by class and level.

See the latest compiled build here: [https://typewritergoblin.github.io/year1-spellbook/](https://typewritergoblin.github.io/year1-spellbook/)

The Spellbook is adapted from [Typewritergoblin/icara-spellbook](https://github.com/Typewritergoblin/icara-spellbook/), which itself is forked from [thebombzen/grimoire](https://github.com/thebombzen/grimoire/). This content is NOT official content — spells are adapted for the Year1 homebrew setting using the 2024 D&D rules.

## Structure
Spells can be found inside `_spells/`. Each spell gets its own file, written and stored as a [Markdown](https://daringfireball.net/projects/markdown/basics) file. Files are named by spell name only (e.g. `acid-splash.markdown`) — no date prefix is needed or used.

Spell files use Jekyll [Collections](https://jekyllrb.com/docs/collections/) rather than posts, which is why no date is required in the filename.

If you'd like to add a new spell:

1. Make a new file inside `_spells/` named after the spell (lowercase, hyphens, `.markdown` extension).
2. Copy the frontmatter and formatting from an existing spell.
3. Submit a pull request when you're finished.

## Build Instructions
This site builds via a GitHub Action to GitHub Pages. Review the documentation for basic instructions: (https://jekyllrb.com/docs/continuous-integration/github-actions/)
