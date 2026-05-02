# PHB 2024 Spell Review Plan

**Goal:** Systematically compare every PHB 2024 spell in `_spells/` against the
canonical source in `PHB24/spell-descriptions-...d-d-beyond.md`, correcting any
inaccuracies in prose, numbers, tables, or formatting.

**Scope:** 391 PHB 2024 spells + 30 non-PHB spells = 421 total (all tracked in `spell-review-tracker.md`).

### Non-PHB Source Breakdown

| Source tag | Count | Canonical source file |
|---|---|---|
| Heroes of Faerun 2024 | 19 | `ForgottenRealmsHeroesOfFaerun24/chapter-5-magic-of-faer-n-...d-d-beyond.md` |
| Exploring Eberron 2024 | 3 | `CleanedFiles/EberronSpells24.md` — "Exploring Eberron Spells" section |
| Frontiers 2024 | 6 | `CleanedFiles/EberronSpells24.md` — "New and Reprinted Spells Frontiers of Eberron" section |
| Forge 2024 | 1 | `CleanedFiles/EberronSpells24.md` — "Forge of Artificer Spells" section |

**Duplicate flag:** *Magecraft* is tagged `Exploring Eberron 2024` in the spellbook but appears in **both** the Exploring Eberron and Frontiers sections of `EberronSpells24.md`. Verify during Batch 11 whether the two entries differ and which version the spellbook uses.

---

## Source Files

| Role | Path |
|------|------|
| Canonical PHB text | `G:\GitRepos\eberronAdvancedMdBook\sourcebooks\BeyondChunks\PHB24\spell-descriptions-player-s-handbook-dungeons-dragons-sources-d-d-beyond.md` |
| Overflow (if a spell is missing from above) | `G:\GitRepos\eberronAdvancedMdBook\sourcebooks\BeyondChunks\PHB24\spell-descriptions-player-s-handbook-dungeons-dragons-sources-d-d-beyond (1).md` |
| Spellbook files | `G:\GitRepos\year1-spellbook\_spells\*.markdown` |

---

## What to Check Per Spell

For each spell, compare the spellbook file against the PHB source and verify:

1. **Header stats** — Level, school, casting time, range, components, duration all match.
2. **Body text** — Prose description matches. Flag any added/missing sentences or wrong numbers.
3. **Damage / healing dice** — Every die expression (e.g. 3d6, 12d6) is correct.
4. **Saving throws & checks** — Correct ability (Str/Dex/Con/Int/Wis/Cha) named.
5. **Conditions** — All conditions named correctly (Blinded, Prone, Grappled, etc.).
6. **Tables** — Any embedded tables (Confusion, Prismatic Spray, etc.) match the source.
7. **Higher-level scaling** — "Using a Higher-Level Spell Slot" text is accurate.
8. **Formatting** — No merged sentences, no orphaned tokens, no HTML artifacts.

**Do NOT change:**
- Tags / subtags frontmatter (these are spellbook-specific metadata, not PHB text).
- Sources frontmatter.
- Intentional prose simplifications made for the static site (e.g. hyperlinks stripped).

---

## Status Key (used in tracker)

| Symbol | Meaning |
|--------|---------|
| ` ` (blank) | Not yet reviewed |
| `~` | Reviewed, no changes needed |
| `*` | Reviewed, changes made |
| `!` | Reviewed, issue found — needs manual decision |

---

## Workflow Per Session

1. Open `spell-review-tracker.md` — find the first unreviewed batch.
2. For each spell in the batch:
   a. Grep for the spell heading (`### Spell Name`) in the PHB source.
   b. Read the PHB section.
   c. Read the spellbook file.
   d. Compare on the 8 points above.
   e. Apply fixes directly; mark status in tracker.
3. After each batch, commit progress.

---

## Batches

| Batch | Range | Source | Count | Status |
|-------|-------|--------|-------|--------|
| 1 | Acid Splash → Augury | PHB 2024 | 20 | Complete |
| 2 | Bane → Burning Hands | PHB 2024 | 18 | Complete |
| 3 | Call Lightning → Cure Wounds | PHB 2024 | 39 | Complete |
| 4 | Dancing Lights → Friends | PHB 2024 | 69 (22 F-spells added) | Complete |
| 5 | Gaseous Form → Hypnotic Pattern | PHB 2024 | 36 | Not started |
| 6 | Ice Knife → Mislead | PHB 2024 | 49 | Not started |
| 7 | Misty Step → Purify Food and Drink | PHB 2024 | 39 | Not started |
| 8 | Raise Dead → Symbol | PHB 2024 | 57 | Not started |
| 9 | Summon Dragon → Zone of Truth | PHB 2024 | 46 | Not started |
| 10 | Alustriel's Mooncloak → Wardaway | Heroes of Faerun 2024 | 19 | Not started |
| 11 | Homunculus Servant → Orien Step | Eberron 2024 | 11 | Not started |
| **Total** | | | **421** | |

---

## Known Issues Already Fixed (Pre-Review)

These spells had Foundry VTT artifacts removed and/or content corrected
before the systematic review began:

- `bigbys-hand.markdown` — @Embed tokens replaced with verified PHB text
- `confusion.markdown` — @Embed table replaced with PHB-accurate d10 table
- `prismatic-spray.markdown` — @Embed table replaced with PHB-accurate d8 table (12d6)
- `reincarnate.markdown` — @Embed table replaced with d10 species table
- `teleport.markdown` — table and familiarity paragraphs restored from raw Foundry data
- `magic-circle.markdown` — missed &reference token fixed; merged sentences split
- `mordenkainens-private-sanctum.markdown` — merged bullet list split
- `bestow-curse.markdown` — merged bullet list split
- `calm-emotions.markdown` — merged bullet list split
- All 391 PHB files — Heavilyobscured/Difficultterrain/Lightlyobscured corrected
- All 421 files — @UUID links replaced with display text
