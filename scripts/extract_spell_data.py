"""
extract_spell_data.py
Parses all spell markdown files in ../_spells/ and outputs a CSV with
structured data for power analysis.

Usage:
    cd scripts
    python extract_spell_data.py
    -> writes ../claudeWorkbook/spell_data.csv
"""

import csv
import glob
import os
import re

SPELLS_DIR = os.path.join(os.path.dirname(__file__), "..", "_spells", "*.markdown")
OUTPUT_CSV = os.path.join(os.path.dirname(__file__), "..", "claudeWorkbook", "spell_data.csv")

SCHOOLS = {
    "abjuration", "conjuration", "divination", "enchantment",
    "evocation", "illusion", "necromancy", "transmutation",
}

LEVEL_TAGS = {
    "cantrip": 0, "level1": 1, "level2": 2, "level3": 3,
    "level4": 4, "level5": 5, "level6": 6, "level7": 7,
    "level8": 8, "level9": 9,
}

SAVE_TYPES = [
    "Strength", "Dexterity", "Constitution",
    "Intelligence", "Wisdom", "Charisma",
]

CONDITIONS = [
    "blinded", "charmed", "deafened", "exhaustion", "frightened",
    "grappled", "incapacitated", "invisible", "paralyzed", "petrified",
    "poisoned", "prone", "restrained", "stunned", "unconscious",
    "silenced", "cursed", "diseased",
]

# Maps common damage types for the damage dice summary
DAMAGE_TYPES = [
    "Acid", "Bludgeoning", "Cold", "Fire", "Force", "Lightning",
    "Necrotic", "Piercing", "Poison", "Psychic", "Radiant",
    "Slashing", "Thunder",
]


def parse_front_matter(text):
    """Extract the YAML front matter block as raw text."""
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    return m.group(1) if m else ""


def get_body(text):
    """Return everything after the front matter."""
    m = re.match(r"^---\n.*?\n---\n(.*)", text, re.DOTALL)
    return m.group(1) if m else text


def extract_title(front):
    m = re.search(r'title:\s*"(.+?)"', front)
    return m.group(1) if m else ""


def extract_tags(front):
    m = re.search(r"tags:\s*\[(.+?)\]", front)
    if not m:
        return []
    return [t.strip() for t in m.group(1).split(",")]


def extract_level(tags):
    for tag in tags:
        if tag in LEVEL_TAGS:
            return LEVEL_TAGS[tag]
    return ""


def extract_school(tags):
    for tag in tags:
        if tag in SCHOOLS:
            return tag.capitalize()
    return ""


def extract_concentration(tags):
    return "Yes" if "concentration" in tags else "No"


def field(body, label):
    """Extract a labelled field value like '**Casting Time**: 1 action'."""
    pattern = rf"\*\*{re.escape(label)}\*\*\s*[:\u2013\-]?\s*(.+)"
    m = re.search(pattern, body)
    return m.group(1).strip() if m else ""


def _main_body(body):
    """Strip the 'Using a Higher-Level Spell Slot' section to avoid
    counting upcast scaling dice as base dice."""
    return re.split(r'\*\*Using a Higher-Level', body)[0]


def extract_casting_time(body):
    raw = field(body, "Casting Time")
    # Trim trailing description after comma for brevity
    return raw.split(",")[0].strip() if raw else ""


def extract_duration(body):
    return field(body, "Duration")


def extract_save_type(body):
    # Spell attack rolls
    if re.search(r"ranged spell attack", body, re.IGNORECASE):
        return "Ranged Attack"
    if re.search(r"melee spell attack", body, re.IGNORECASE):
        return "Melee Attack"
    # Saving throws
    found = []
    for save in SAVE_TYPES:
        if re.search(rf"\b{save}\b saving throw", body):
            found.append(save)
    return "; ".join(found) if found else ""


def extract_healing_dice(body):
    """
    Find dice expressions used for healing (restoring Hit Points).
    Uses the main body only, excluding upcast scaling text.
    """
    main = _main_body(body)
    patterns = [
        # "regains/regain Hit Points equal to 2d8"
        r"regains?\s+(?:a number of )?Hit Points equal to\s+(\d+d\d+)",
        # "regain 2d8 Hit Points" (dice between verb and HP)
        r"regains?\s+(\d+d\d+)\s+Hit Points",
        # "restore/restores 2d6 Hit Points"
        r"restores?\s+(\d+d\d+)\s+Hit Points",
        # "2d8 Hit Points" as a standalone phrase (broad fallback)
        r"(\d+d\d+)\s+(?:Temporary )?Hit Points",
    ]
    found = []
    seen = set()
    for pat in patterns:
        for m in re.finditer(pat, main, re.IGNORECASE):
            d = m.group(1)
            if d not in seen:
                seen.add(d)
                found.append(d)
    return "; ".join(found) if found else ""


def extract_effect_dice(body):
    """
    Find dice expressions used as buff/effect sizing (e.g. Bless +1d4 to attack
    rolls, Guidance +1d4 to ability checks). Excludes healing and damage dice.
    Uses the main body only.
    """
    main = _main_body(body)
    patterns = [
        # "adds 1d4 to" (Bless, Guidance)
        r"adds?\s+(\d+d\d+)\s+to",
        # "1d4 to the attack roll / saving throw / ability check / save"
        r"(\d+d\d+)\s+(?:bonus\s+)?to (?:the )?(?:attack roll|saving throw|ability check|save)\b",
        # "roll a Xd6 and add" style
        r"rolls?\s+(?:a |an )?(\d+d\d+)[^.]{0,30}?(?:and add|as a bonus)",
    ]
    found = []
    seen = set()
    for pat in patterns:
        for m in re.finditer(pat, main, re.IGNORECASE):
            d = m.group(1)
            if d not in seen:
                seen.add(d)
                found.append(d)
    return "; ".join(found) if found else ""


def extract_damage_dice(body):
    """
    Find dice expressions used for damage. Excludes healing and effect dice,
    and upcast scaling text. Returns entries like '8d6 Fire; 2d8 Cold'.
    """
    main = _main_body(body)
    entries = []
    seen = set()

    for m in re.finditer(r'(\d+d\d+(?:\s*\+\s*\d+)?)', main):
        dice = m.group(1).strip()
        ctx_start = max(0, m.start() - 60)
        ctx_end = min(len(main), m.end() + 60)
        ctx = main[ctx_start:ctx_end].lower()
        ctx_after = main[m.end():min(len(main), m.end() + 50)].lower()
        ctx_before = main[max(0, m.start() - 50):m.start()].lower()

        # Skip healing contexts
        if re.search(r'hit points?|\bhp\b|regains?|restores?', ctx):
            continue
        # Skip effect/buff dice: "adds Xd4 to" or "Xd4 to attack roll/save/check"
        if re.search(r'\badds?\b', ctx_before) and re.search(r'\bto\b', ctx_after[:15]):
            continue
        if re.search(
            r'to (?:the )?(?:attack roll|saving throw|ability check|save)\b',
            ctx_after
        ):
            continue

        # Annotate with damage type if the word immediately follows
        after_text = main[m.end():m.end() + 25]
        word_m = re.match(r'\s+([A-Z][a-z]+)', after_text)
        if word_m and word_m.group(1) in DAMAGE_TYPES:
            entry = f"{dice} {word_m.group(1)}"
        else:
            entry = dice

        if entry not in seen:
            seen.add(entry)
            entries.append(entry)

    return "; ".join(entries) if entries else ""


def extract_targets(body):
    """
    Classify the targeting pattern. Checks AoE shapes first, then multi/single target.
    """
    aoe_shapes = [
        (r"(\d+)-foot(?:-radius)?\s+Sphere", "Sphere"),
        (r"(\d+)-foot\s+Cone", "Cone"),
        (r"(\d+)-foot\s+Cube", "Cube"),
        (r"(\d+)-foot\s+Line", "Line"),
        (r"(\d+)-foot(?:-radius)?\s+Cylinder", "Cylinder"),
        (r"(\d+)-foot(?:-radius)?\s+Circle", "Circle"),
        (r"(\d+)-foot(?:-wide)?\s+Emanation", "Emanation"),
    ]
    for pattern, shape in aoe_shapes:
        if re.search(pattern, body, re.IGNORECASE):
            return f"AoE ({shape})"

    # Multi-target phrasings
    if re.search(r"up to (three|four|five|\d+) creatures", body, re.IGNORECASE):
        return "Multi-target"
    if re.search(r"each creature", body, re.IGNORECASE):
        return "All creatures in area"
    if re.search(r"one or more", body, re.IGNORECASE):
        return "Multi-target"

    # Self-only
    range_val = field(body, "Range")
    if range_val.lower() == "self":
        return "Self"

    # Default single target
    return "Single target"


def extract_aoe_size(body):
    """Return the first AoE size string found, e.g. '20-foot-radius Sphere'."""
    aoe_patterns = [
        r"(\d+-foot(?:-radius)?\s+Sphere)",
        r"(\d+-foot\s+Cone)",
        r"(\d+-foot\s+Cube)",
        r"(\d+-foot\s+Line)",
        r"(\d+-foot(?:-radius)?\s+Cylinder)",
        r"(\d+-foot(?:-radius)?\s+Circle)",
        r"(\d+-foot(?:-wide)?\s+Emanation)",
    ]
    for pat in aoe_patterns:
        m = re.search(pat, body, re.IGNORECASE)
        if m:
            return m.group(1)
    return ""


def extract_conditions(body):
    """Find conditions from &Reference[condition] markup or plain text."""
    found = set()
    # Foundry VTT reference markup: &amp;Reference[condition] or &Reference[condition]
    for m in re.finditer(r"Reference\[(\w[\w-]*)", body, re.IGNORECASE):
        cond = m.group(1).lower()
        if cond in CONDITIONS:
            found.add(cond.capitalize())
    # Plain-text fallback (capitalised condition names in body)
    for cond in CONDITIONS:
        if re.search(rf"\b{cond}\b", body, re.IGNORECASE):
            found.add(cond.capitalize())
    return "; ".join(sorted(found)) if found else ""


def extract_buffs(body):
    """Detect common buff types: AC bonus, attack bonus, resistances, temp HP."""
    buffs = []

    if re.search(r"\+\s*\d+\s*bonus to AC", body, re.IGNORECASE):
        m = re.search(r"\+\s*(\d+)\s*bonus to AC", body, re.IGNORECASE)
        buffs.append(f"+{m.group(1)} AC" if m else "AC bonus")

    if re.search(r"Disadvantage on attack rolls against", body, re.IGNORECASE):
        buffs.append("Attackers have Disadvantage")

    if re.search(r"Advantage on attack rolls", body, re.IGNORECASE):
        buffs.append("Advantage on attacks")

    if re.search(r"\+1d4 to (?:the )?attack roll|adds 1d4.*attack roll", body, re.IGNORECASE):
        buffs.append("+1d4 to attack rolls")

    if re.search(r"\+1d4 to (?:the )?saving throw|adds 1d4.*saving throw", body, re.IGNORECASE):
        buffs.append("+1d4 to saves")

    if re.search(r"resistance to", body, re.IGNORECASE):
        types_found = re.findall(
            r"resistance to\s+([A-Z][a-z]+(?:,\s*[A-Z][a-z]+)*(?:\s*and\s+[A-Z][a-z]+)?)",
            body
        )
        for t in types_found:
            buffs.append(f"Resistance ({t.strip()})")

    if re.search(r"immunity to", body, re.IGNORECASE):
        buffs.append("Immunity")

    if re.search(r"Temporary Hit Points?", body, re.IGNORECASE):
        buffs.append("Temp HP")

    if re.search(r"Hit Point maximum.*increase|increase.*Hit Point maximum", body, re.IGNORECASE):
        buffs.append("Max HP increase")

    return "; ".join(buffs) if buffs else ""


def extract_effect(body):
    """
    Catch-all: note notable non-damage, non-condition effects not captured above.
    Looks for Invisible, teleport, fly, polymorph, summoning, etc.
    """
    effects = []
    checks = [
        (r"\binvisib", "Invisibility"),
        (r"\bfly(?:ing)?\b", "Flight"),
        (r"\bteleport", "Teleport"),
        (r"\bpolymorph\b", "Polymorph"),
        (r"\bsummon\b", "Summon"),
        (r"\bheal\b|\bregain(?:s)?\b.*hit points?\b|\bhit points?.*restor", "Healing"),
        (r"\brestores?\b.*hit points?", "Healing"),
        (r"\bdisadvantage on attack rolls", "Impose Disadvantage (attacks)"),
        (r"\bdisadvantage on.*saving throw", "Impose Disadvantage (saves)"),
        (r"\badvantage on.*saving throw", "Advantage on saves"),
        (r"\bcan't take reactions\b", "No reactions"),
        (r"\bpushed\b.*feet|\bknocked back\b", "Forced movement"),
        (r"\bdivination\b|\bforesight\b|\bscry", "Divination/Scrying"),
        (r"\bcreate\b.*creature|\bconjure\b", "Conjure/Create"),
        (r"\bcurse\b", "Curse"),
        (r"\bdisease\b", "Disease"),
        (r"\bno damage\b|take no damage", "Negate damage"),
    ]
    for pattern, label in checks:
        if re.search(pattern, body, re.IGNORECASE):
            effects.append(label)
    return "; ".join(effects) if effects else ""


def process_file(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()

    front = parse_front_matter(text)
    body = get_body(text)
    tags = extract_tags(front)

    return {
        "name":               extract_title(front),
        "level":              extract_level(tags),
        "school":             extract_school(tags),
        "concentration":      extract_concentration(tags),
        "casting_time":       extract_casting_time(body),
        "duration":           extract_duration(body),
        "save_type":          extract_save_type(body),
        "damage_dice":        extract_damage_dice(body),
        "healing_dice":       extract_healing_dice(body),
        "effect_dice":        extract_effect_dice(body),
        "targets":            extract_targets(body),
        "aoe_size":           extract_aoe_size(body),
        "conditions":         extract_conditions(body),
        "buffs":              extract_buffs(body),
        "effect":             extract_effect(body),
    }


def main():
    files = sorted(glob.glob(SPELLS_DIR))
    if not files:
        print(f"No spell files found at {SPELLS_DIR}")
        return

    rows = []
    for path in files:
        try:
            rows.append(process_file(path))
        except Exception as e:
            print(f"Warning: failed to parse {os.path.basename(path)}: {e}")

    fieldnames = [
        "name", "level", "school", "concentration", "casting_time",
        "duration", "save_type", "damage_dice", "healing_dice", "effect_dice",
        "targets", "aoe_size", "conditions", "buffs", "effect",
    ]

    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Written {len(rows)} spells to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
