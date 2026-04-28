# Foundry VTT Reference Cleanup Plan

**Goal:** Remove all Foundry VTT inline reference syntax from `_spells/*.markdown` files
and replace it with clean, human-readable plain text.

**Scope:** 148 files affected (identified via grep).

---

## Why "Replace with Plain Text" (not a new database)

This is a static Jekyll site. The references are Foundry VTT-specific syntax that
points to a live compendium database at runtime. There is no reasonable lightweight
equivalent to recreate that on a static site — conditions like "Blinded" or "Prone"
are one or two words of plain text, and saving throw calls are already described in
the surrounding prose. Creating a database would add infrastructure complexity for
zero user-visible benefit. Replace everything with plain text.

---

## Pattern Catalogue

Below is every reference type found in the spell files, with its replacement rule.

### 1. Saving Throw Buttons — `[[/save ...]]`

```
[[/save ability=wis dc=@attributes.spell.dc format=long]]
[[/save ability=con dc=@attributes.spell.dc]]
```

**Replace with:** `[Ability] saving throw`

Ability abbreviation map:
| Code | Full Name  |
|------|------------|
| str  | Strength   |
| dex  | Dexterity  |
| con  | Constitution |
| int  | Intelligence |
| wis  | Wisdom     |
| cha  | Charisma   |

Context example:
> "makes a [[/save ability=con dc=@attributes.spell.dc format=long]], ending the spell"
> → "makes a Constitution saving throw, ending the spell"

---

### 2. Ability Check Buttons — `[[/check ...]]`

```
[[/check ability=str skill=ath dc=@attributes.spell.dc]]
[[/check ability=wis skill=prc]]
```

**Replace with:** `[Ability] ([Skill]) check`

Skill abbreviation map:
| Code | Full Name        |
|------|------------------|
| ath  | Athletics        |
| acr  | Acrobatics       |
| arc  | Arcana           |
| dec  | Deception        |
| his  | History          |
| ins  | Insight          |
| itm  | Intimidation     |
| inv  | Investigation    |
| med  | Medicine         |
| nat  | Nature           |
| prc  | Perception       |
| prf  | Performance      |
| per  | Persuasion       |
| rel  | Religion         |
| slt  | Sleight of Hand  |
| ste  | Stealth          |
| sur  | Survival         |
| ani  | Animal Handling  |

Context example:
> "make a [[/check ability=str skill=ath dc=@attributes.spell.dc]] check against your spell save DC"
> → "make a Strength (Athletics) check against your spell save DC"

**Edge case — standalone check blocks:** Some files (e.g., `grasping-vine.markdown`) have
bare `[[/check...]]` lines as extra Foundry-only GM shortcuts **not in the original spell
text**. These appear under headings like "Escape Tests" and should be **removed entirely**
along with their heading. See §Foundry-Only Sections below.

---

### 3. Damage Roll Buttons — `[[/damage ...]]`

#### 3a. With explicit dice and type, no display text:
```
[[/damage 2d8 type=fire]]
[[/damage 50 type=force]]
```
**Replace with:** `[dice] [Type]` (capitalize damage type)
> `[[/damage 2d8 type=fire]]` → `2d8 Fire`
> `[[/damage 50 type=bludgeoning]]` → `50 Bludgeoning`

#### 3b. With display text `{...}` after the bracket:
```
[[/damage (@item.level + 2)d8 type=acid]]{Acid}
[[/damage 2d8 type=fire]]{warm}
```
**Replace with:** just the display text (strip the entire `[[...]]` part)
> `[[/damage (@item.level + 2)d8 type=acid]]{Acid}` → `Acid`

#### 3c. Empty `[[/damage]]` with no args:
Appears in Hunter's Mark where damage is context-dependent.
**Replace with:** *(nothing — delete the tag, surrounding text already describes it)*

---

### 4. Healing Buttons — `[[/healing ...]]`

#### 4a. Inline in prose:
```
[[/healing 1 type=healing]]{1 Hit Point}
```
Has display text → **use the display text**.

#### 4b. Standalone shortcut blocks (e.g., Power Word Fortify's "Temporary HP Shortcuts"):
These entire sections are Foundry-only UI shortcuts with no equivalent in the spell text.
**Remove the heading and all `[[/healing ...]]` lines.** See §Foundry-Only Sections.

---

### 5. Roll Buttons — `[[/r ...]]`

#### 5a. With display text:
```
[[/r 1d100cs&lt;26#Vehicle is capsized]]{25 percent}
[[/r (@flags.dnd-players-handbook.mirrorImages)d6kh1cs&gt;2#Duplicate destroyed]]{d6 for each}
[[/r 1d100cs&gt;25#Spell cast successfully on 1]]{25 percent}
```
**Replace with:** just the display text (strip the entire `[[...]]` part)
> `[[/r 1d100cs&lt;26#...]]{25 percent}` → `25 percent`
> `[[/r (@flags...)d6kh1cs&gt;2#...]]{d6 for each}` → `d6 for each`

#### 5b. Without display text — simple die expressions:
```
[[/r 1d6]]
[[/r 2d12]]
[[/r 1d8]]
```
**Replace with:** just the die expression
> `[[/r 1d6]]` → `1d6`

#### 5c. Without display text — complex expressions:
```
[[/r (@flags.dnd-players-handbook.mirrorImages)d6kh1cs>2#Duplicate destroyed]]
```
These need manual review since the Foundry formula references internal flags.

---

### 6. GM Roll Buttons — `[[/gmr ...]]`

```
[[/gmr 1d100]]
```
**Replace with:** the die expression
> `[[/gmr 1d100]]` → `1d100`

---

### 7. Item-level Expressions — `[[@item.level ...]]`

```
[[@item.level - 3]]
```
These compute values based on spell slot level at cast time (Foundry runtime only).

**Replace with:** a human-readable equivalent describing the scaling:
> `[[@item.level - 3]]` → `(spell slot level − 3)`

Context note: In `grasping-vine.markdown` this appears in a Foundry-only footer section
("Total number creatures able to be Grappled: [[@item.level - 3]]") — remove the whole line.

---

### 8. Condition & Sense References — `&amp;Reference[...]` / `&Reference[...]`

Both the HTML-encoded (`&amp;`) and raw (`&`) forms appear in the files.

#### 8a. With `apply=false` (conditions):
```
&amp;Reference[blinded apply=false]
&amp;Reference[Restrained apply=false]
&amp;Reference[Stunned apply=false]
&amp;Reference[Prone apply=false]
&amp;Reference[Frightened apply=false]
&amp;Reference[Charmed apply=false]
&amp;Reference[Unconscious apply=false]
```
**Replace with:** the condition name, properly Title-Cased (strip `apply=false`).
The word is already used in context — no need to italicize or bold it.
> `&amp;Reference[blinded apply=false]` → `Blinded`

#### 8b. Without `apply=false` (senses, features):
```
&amp;Reference[blindsight]
&amp;Reference[truesight]
&amp;Reference[Grappled]
&amp;Reference[prone]
```
**Replace with:** the name, Title-Cased
> `&amp;Reference[blindsight]` → `Blindsight`

#### 8c. With display text `{...}`:
```
&amp;Reference[Study]{Study}
```
**Replace with:** just the display text
> `&amp;Reference[Study]{Study}` → `Study`

---

## Foundry-Only Sections to Remove Entirely

Some files have entire sections that exist only as Foundry UI helpers — they have no
equivalent in the official spell text. These should be deleted, not converted.

| File | Section to Remove |
|------|------------------|
| `power-word-fortify.markdown` | `**Temporary HP Shortcuts**` heading + all `[[/healing ...]]` lines below it |
| `grasping-vine.markdown` | `Total number creatures able to be Grappled: [[@item.level - 3]]` line + `Escape Tests` heading + both `[[/check ...]]` lines |

Check all other files for similar patterns (bare `[[/...]]` on its own line outside prose
paragraphs) and evaluate whether they belong to the original spell text.

---

## Implementation: Python Cleanup Script

Write `scripts/clean_references.py` to process all `_spells/*.markdown` files.

### Script logic (in order):

1. **`[[...]]` with display text `{...}`** — strip the `[[...]]` token, keep the `{...}` content.
   - Pattern: `\[\[/[^\]]+\]\]\{([^}]+)\}` → `\1`
   - Must run BEFORE other `[[...]]` rules to avoid partial matches.

2. **`[[/save ability=X dc=...]]`** — replace with "`[Ability] saving throw`"
   - Pattern: `\[\[/save ability=(\w+)[^\]]*\]\]` → expand ability code to full name

3. **`[[/check ability=X skill=Y ...]]`** — replace with "`[Ability] ([Skill]) check`"
   - Pattern: `\[\[/check ability=(\w+) skill=(\w+)[^\]]*\]\]` → expand both codes

4. **`[[/damage X type=Y]]`** (with explicit values) — replace with `X Y`
   - Pattern: `\[\[/damage ([\d]+(?:d[\d]+)?) type=(\w+)\]\]` → `\1 \2` (capitalize type)

5. **`[[/damage ...]]`** (any remaining — catch-all) — delete
   - Pattern: `\[\[/damage[^\]]*\]\]` → ``

6. **`[[/healing X type=...]]`** — keep only the number
   - Pattern: `\[\[/healing ([\d]+) type=\w+\]\]` → `\1`

7. **`[[/r X]]`** simple dice — keep die expression
   - Pattern: `\[\[/r ([\dd]+)\]\]` → `\1`

8. **`[[/gmr X]]`** — keep die expression
   - Pattern: `\[\[/gmr ([\dd]+)\]\]` → `\1`

9. **`[[/r ...]]`** catch-all (complex expressions without display text) — flag for manual review, log to console, leave in place as a `<!-- REVIEW: ... -->` comment.

10. **`[[@item.level...]]`** — replace with scaling text
    - Pattern: `\[\[@item\.level\s*([+-])\s*(\d+)\]\]` → `(spell slot level \1 \2)`
    - Bare `[[@item.level]]` → `(spell slot level)`

11. **`&amp;Reference[X]{display}` and `&Reference[X]{display}`** — keep display text
    - Pattern: `&(?:amp;)?Reference\[[^\]]+\]\{([^}]+)\}` → `\1`

12. **`&amp;Reference[X apply=false]` and `&Reference[X apply=false]`** — keep condition name
    - Pattern: `&(?:amp;)?Reference\[(\w+(?:\s+\w+)*?) apply=false\]` → Title-Case `\1`

13. **`&amp;Reference[X]`** catch-all (no apply=false, no display) — keep name
    - Pattern: `&(?:amp;)?Reference\[([^\]]+)\]` → Title-Case `\1`

14. **Foundry-only section removal** — manual pass after script runs, or add specific
    section-detection logic for known files.

### Script output:
- Modify files in place
- Print a report: file name + count of replacements per pattern type
- Print a "NEEDS REVIEW" list for any `[[...]]` tokens that weren't matched

---

## Validation

After running the script:

1. `grep -r '\[\[' _spells/` — should return zero results
2. `grep -r '&amp;Reference\|&Reference' _spells/` — should return zero results
3. `grep -r '@attributes\|@item\|@flags' _spells/` — should return zero results
4. Manual spot-check 10 files for prose quality
5. Build the site locally and verify affected spell pages render correctly

---

## Files Needing Manual Review After Script

These contain complex or ambiguous patterns:

- `mirror-image.markdown` — `[[/r (@flags.dnd-players-handbook.mirrorImages)d6kh1cs>2...]]{d6 for each}` — the display text handles it but verify surrounding prose makes sense
- `control-water.markdown` — `[[/r 1d100cs&lt;26#Vehicle is capsized]]{25 percent}` — verify plain text reads naturally
- `glyph-of-warding.markdown` — `[[/damage (@item.level + 2)d8 type=acid]]{Acid}` repeated five times — the surrounding "5d8" text is a Foundry-only hardcoded minimum; after cleanup this will read "A creature takes 5d8 Acid, Cold, Fire, Lightning, or Thunder damage" which is correct
- `slow.markdown` — `[[/r 1d100cs&gt;25#Spell cast successfully on 1]]{25 percent}` — verify surrounding prose
- `earthquake.markdown` — `[[/damage 50 type=bludgeoning]]` in structure damage line — verify it reads "50 Bludgeoning damage"
- `grasping-vine.markdown` — entire Foundry footer section must be removed manually
- `power-word-fortify.markdown` — "Temporary HP Shortcuts" section must be removed manually

---

## Estimated Effort

| Task | Effort |
|------|--------|
| Write cleanup script | 1–2 hours |
| Run script + review output | 30 min |
| Manual cleanup of Foundry-only sections | 30 min |
| Spot-check and validation | 30 min |
| **Total** | **~3 hours** |
