"""
clean_references.py — Strip Foundry VTT inline reference syntax from _spells/*.markdown.

Replaces all [[/save ...]], [[/check ...]], [[/damage ...]], [[/r ...]], [[/gmr ...]],
[[/healing ...]], &amp;Reference[...], and [[@item.level ...]] patterns with plain text.
Removes Foundry-only shortcut sections that have no equivalent in official spell text.

Run from the repo root:
    python scripts/clean_references.py
"""

import re
import sys
from pathlib import Path

SPELLS_DIR = Path(__file__).parent.parent / "_spells"

ABILITY_NAMES = {
    "str": "Strength",
    "dex": "Dexterity",
    "con": "Constitution",
    "int": "Intelligence",
    "wis": "Wisdom",
    "cha": "Charisma",
}

SKILL_NAMES = {
    "ath": "Athletics",
    "acr": "Acrobatics",
    "arc": "Arcana",
    "dec": "Deception",
    "his": "History",
    "ins": "Insight",
    "itm": "Intimidation",
    "inv": "Investigation",
    "med": "Medicine",
    "nat": "Nature",
    "prc": "Perception",
    "prf": "Performance",
    "per": "Persuasion",
    "rel": "Religion",
    "slt": "Sleight of Hand",
    "ste": "Stealth",
    "sur": "Survival",
    "ani": "Animal Handling",
}

# Patterns that must run first: [[...]] tokens with a {display text} suffix.
# The display text is always the human-readable version — keep it, drop the [[...]].
RE_BRACKET_WITH_DISPLAY = re.compile(
    r'\[\[/[^\]]*(?:\][^\]]*)*\]\]\{([^}]+)\}'
)

# [[/save ability=X dc=... (format=long)?]]
RE_SAVE = re.compile(
    r'\[\[/save\s+ability=(\w+)[^\]]*\]\]'
)

# [[/check ability=X skill=Y dc=... ]]
RE_CHECK = re.compile(
    r'\[\[/check\s+ability=(\w+)\s+skill=(\w+)[^\]]*\]\]'
)

# [[/damage NdN type=word]] — explicit dice/number with a type
RE_DAMAGE_EXPLICIT = re.compile(
    r'\[\[/damage\s+([\dd]+(?:\.\d+)?)\s+type=(\w+)[^\]]*\]\]'
)

# [[/damage ...]] — any remaining (e.g. bare [[/damage]] or complex expressions)
RE_DAMAGE_ANY = re.compile(r'\[\[/damage[^\]]*\]\]')

# [[/healing N type=...]]
RE_HEALING = re.compile(r'\[\[/healing\s+(\d+)\s+type=\w+\]\]')

# [[/r NdN]] or [[/r N]] — simple expressions only
RE_ROLL_SIMPLE = re.compile(r'\[\[/r\s+(\d+(?:d\d+)?)\]\]')

# [[/r ...]] — any remaining complex rolls (without display text, which was handled first)
RE_ROLL_ANY = re.compile(r'\[\[/r[^\]]*\]\]')

# [[/gmr NdN]] or [[/gmr N]]
RE_GMR = re.compile(r'\[\[/gmr\s+(\d+(?:d\d+)?)\]\]')

# [[@item.level +/- N]] or [[@item.level]]
RE_ITEM_LEVEL = re.compile(r'\[\[@item\.level\s*([+-])\s*(\d+)\]\]')
RE_ITEM_LEVEL_BARE = re.compile(r'\[\[@item\.level\]\]')

# &amp;Reference[X]{display} or &Reference[X]{display}
RE_REF_DISPLAY = re.compile(
    r'&(?:amp;)?Reference\[[^\]]+\]\{([^}]+)\}'
)

# &amp;Reference[X apply=false] or &Reference[X apply=false]
RE_REF_APPLY_FALSE = re.compile(
    r'&(?:amp;)?Reference\[(\w+(?:\s+\w+)*?)\s+apply=false\]'
)

# &amp;Reference[X] — catch-all (senses, features, bare conditions)
RE_REF_ANY = re.compile(r'&(?:amp;)?Reference\[([^\]]+)\]')

# Any remaining [[ ... ]] tokens not matched above
RE_LEFTOVER = re.compile(r'\[\[[^\]]*(?:\][^\]]*)*\]\]')


def expand_ability(code: str) -> str:
    return ABILITY_NAMES.get(code.lower(), code.title())


def expand_skill(code: str) -> str:
    return SKILL_NAMES.get(code.lower(), code.title())


def capitalize_condition(raw: str) -> str:
    return raw.strip().title()


def sub_save(m: re.Match) -> str:
    ability = expand_ability(m.group(1))
    return f"{ability} saving throw"


def sub_check(m: re.Match) -> str:
    ability = expand_ability(m.group(1))
    skill = expand_skill(m.group(2))
    return f"{ability} ({skill}) check"


def sub_damage_explicit(m: re.Match) -> str:
    dice = m.group(1)
    damage_type = m.group(2).title()
    return f"{dice} {damage_type}"


def sub_item_level(m: re.Match) -> str:
    op = m.group(1)
    n = m.group(2)
    op_word = "+" if op == "+" else "−"
    return f"(spell slot level {op_word} {n})"


def remove_foundry_only_sections(text: str, filename: str) -> tuple[str, list[str]]:
    """Remove entire sections that are Foundry-only UI helpers with no spell text equivalent."""
    removed = []

    if filename == "power-word-fortify.markdown":
        # Remove the "Temporary HP Shortcuts" heading and all [[/healing ...]] lines below it.
        pattern = re.compile(
            r'\n\*\*Temporary HP Shortcuts\*\*\n(?:\n?\[\[/healing[^\n]*\n)*',
            re.MULTILINE
        )
        new_text, n = pattern.subn("", text)
        if n:
            removed.append("Removed 'Temporary HP Shortcuts' section")
            text = new_text

    if filename == "grasping-vine.markdown":
        # Remove the scaling line and the Escape Tests section.
        patterns = [
            (re.compile(r'\nTotal number creatures able to be Grappled:[^\n]*\n'), "Removed grapple scaling line"),
            (re.compile(r'\nEscape Tests\n(?:\n?\[\[/check[^\n]*\n)*', re.MULTILINE), "Removed 'Escape Tests' section"),
        ]
        for pat, msg in patterns:
            new_text, n = pat.subn("", text)
            if n:
                removed.append(msg)
                text = new_text

    return text, removed


def clean_file(path: Path) -> dict:
    original = path.read_text(encoding="utf-8")
    text = original
    filename = path.name
    counts = {}
    review_needed = []

    # Step 0: Remove Foundry-only sections
    text, section_removals = remove_foundry_only_sections(text, filename)
    if section_removals:
        counts["sections_removed"] = section_removals

    # Step 1: [[...]] with display text — must run before other [[ rules
    def count_sub(pattern, repl, label):
        nonlocal text
        new_text, n = pattern.subn(repl, text)
        if n:
            counts[label] = counts.get(label, 0) + n
        text = new_text

    count_sub(RE_BRACKET_WITH_DISPLAY, lambda m: m.group(1), "bracket_display")

    # Step 2: Saving throws
    count_sub(RE_SAVE, sub_save, "save")

    # Step 3: Ability checks
    count_sub(RE_CHECK, sub_check, "check")

    # Step 4: Damage with explicit values
    count_sub(RE_DAMAGE_EXPLICIT, sub_damage_explicit, "damage_explicit")

    # Step 5: Any remaining [[/damage ...]]
    count_sub(RE_DAMAGE_ANY, "", "damage_other")

    # Step 6: Healing
    count_sub(RE_HEALING, lambda m: m.group(1), "healing")

    # Step 7: Simple rolls
    count_sub(RE_ROLL_SIMPLE, lambda m: m.group(1), "roll_simple")

    # Step 8: GM rolls
    count_sub(RE_GMR, lambda m: m.group(1), "gmr")

    # Step 9: Complex rolls without display text — flag for review, delete
    for m in RE_ROLL_ANY.finditer(text):
        review_needed.append(f"  Complex roll (deleted): {m.group(0)!r}")
    count_sub(RE_ROLL_ANY, "", "roll_complex")

    # Step 10: [[@item.level +/- N]]
    count_sub(RE_ITEM_LEVEL, sub_item_level, "item_level")
    count_sub(RE_ITEM_LEVEL_BARE, "(spell slot level)", "item_level_bare")

    # Step 11: &Reference with display text
    count_sub(RE_REF_DISPLAY, lambda m: m.group(1), "ref_display")

    # Step 12: &Reference[X apply=false] — condition links
    count_sub(RE_REF_APPLY_FALSE, lambda m: capitalize_condition(m.group(1)), "ref_condition")

    # Step 13: &Reference[X] catch-all
    count_sub(RE_REF_ANY, lambda m: capitalize_condition(m.group(1)), "ref_other")

    # Step 14: Catch any leftover [[ ]] tokens and flag them
    for m in RE_LEFTOVER.finditer(text):
        review_needed.append(f"  Unhandled token (left in place): {m.group(0)!r}")

    changed = text != original
    if changed:
        path.write_text(text, encoding="utf-8")

    return {
        "changed": changed,
        "counts": counts,
        "review": review_needed,
    }


def main():
    spell_files = sorted(SPELLS_DIR.glob("*.markdown"))
    if not spell_files:
        print(f"No .markdown files found in {SPELLS_DIR}", file=sys.stderr)
        sys.exit(1)

    total_changed = 0
    total_review = []
    pattern_totals = {}

    for path in spell_files:
        result = clean_file(path)
        if result["changed"]:
            total_changed += 1
            for k, v in result["counts"].items():
                if k == "sections_removed":
                    continue
                pattern_totals[k] = pattern_totals.get(k, 0) + (v if isinstance(v, int) else 1)
            if result["review"]:
                total_review.append((path.name, result["review"]))
            if result["counts"].get("sections_removed"):
                for msg in result["counts"]["sections_removed"]:
                    print(f"  [{path.name}] {msg}")

    print(f"\nDone. {total_changed}/{len(spell_files)} files modified.\n")

    if pattern_totals:
        print("Replacements by pattern type:")
        for k, v in sorted(pattern_totals.items(), key=lambda x: -x[1]):
            print(f"  {k:<20} {v}")

    if total_review:
        print("\n--- NEEDS REVIEW ---")
        for fname, items in total_review:
            print(f"\n{fname}:")
            for item in items:
                print(item)
    else:
        print("\nNo tokens need manual review.")

    # Final verification grep
    print("\nRunning verification checks...")
    import subprocess
    for check_pat, label in [
        (r'\[\[', "remaining [[ tokens"),
        (r'&(?:amp;)?Reference\[', "remaining &Reference tokens"),
        (r'@attributes|@item|@flags', "remaining @ expressions"),
    ]:
        result = subprocess.run(
            ["grep", "-rl", "--include=*.markdown", check_pat, str(SPELLS_DIR)],
            capture_output=True, text=True
        )
        if result.stdout.strip():
            files = result.stdout.strip().split("\n")
            print(f"  FAIL — {label} still found in {len(files)} file(s):")
            for f in files:
                print(f"    {f}")
        else:
            print(f"  PASS — no {label}")


if __name__ == "__main__":
    main()
