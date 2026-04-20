"""
Generate _spells/ markdown files from 2024 JSON data + class spell list.

Usage: py scripts/generate_spells.py
Run from the repo root.
"""

import json
import os
import re

# ── Short-name duplicates to skip (possessive form already exists in JSON) ──────
SKIP_NAMES = {
    "Acid Arrow", "Arcane Hand", "Arcane Sword", "Arcanist's Magic Aura",
    "Black Tentacles", "Faithful Hound", "Floating Disk", "Freezing Sphere",
    "Hideous Laughter", "Instant Summons", "Irresistible Dance",
    "Magnificent Mansion", "Private Sanctum", "Resilient Sphere",
    "Secret Chest", "Telepathic Bond", "Tiny Hut",
}

SCHOOL_MAP = {
    "abj": "abjuration",
    "con": "conjuration",
    "div": "divination",
    "enc": "enchantment",
    "evo": "evocation",
    "ill": "illusion",
    "nec": "necromancy",
    "trs": "transmutation",
}

LEVEL_ORDINAL = {
    1: "1st", 2: "2nd", 3: "3rd",
    4: "4th", 5: "5th", 6: "6th",
    7: "7th", 8: "8th", 9: "9th",
}


def spell_to_filename(title):
    name = title.lower()
    name = name.replace("'", "").replace("'", "")
    name = re.sub(r"[^a-z0-9]+", "-", name)
    return name.strip("-") + ".markdown"


def format_activation(activation):
    t = activation.get("type", "")
    v = activation.get("value")
    if t == "action":
        return "1 action"
    if t == "bonus":
        return "1 bonus action"
    if t == "reaction":
        cond = activation.get("condition", "")
        return f"1 reaction{', ' + cond if cond else ''}"
    if t == "minute":
        n = v or 1
        return f"{n} minute" if n == 1 else f"{n} minutes"
    if t == "hour":
        n = v or 1
        return f"{n} hour" if n == 1 else f"{n} hours"
    return t


def format_duration(duration, is_concentration):
    units = duration.get("units", "")
    value = duration.get("value", "")
    if units == "inst":
        return "Instantaneous"
    if units in ("disp", "perm"):
        return "Until dispelled"
    if units == "dstr":
        return "Until dispelled or triggered"
    if units in ("spec", "special"):
        return "Special"
    if units == "round":
        return "1 round"
    def safe_int(v):
        try:
            return int(v)
        except (ValueError, TypeError):
            return None

    if units == "minute":
        n = safe_int(value) or 1
        base = f"{n} minute" if n == 1 else f"{n} minutes"
    elif units == "hour":
        n = safe_int(value)
        if n is None:
            return "Special"
        base = f"{n} hour" if n == 1 else f"{n} hours"
    elif units == "day":
        n = safe_int(value) or 1
        base = f"{n} day" if n == 1 else f"{n} days"
    else:
        base = f"{value} {units}".strip()
    return f"Concentration, up to {base}" if is_concentration else base


def format_range(rng):
    units = rng.get("units", "")
    value = rng.get("value", "")
    if units == "ft":
        return f"{value} feet"
    if units == "self":
        return "Self"
    if units == "touch":
        return "Touch"
    if units == "special":
        return "Special"
    if units == "unlimited":
        return "Unlimited"
    if units == "sight":
        return "Sight"
    return f"{value} {units}".strip()


def format_components(components, material_text):
    parts = []
    if "vocal" in components:
        parts.append("V")
    if "somatic" in components:
        parts.append("S")
    if "material" in components:
        if material_text:
            parts.append(f"M ({material_text})")
        else:
            parts.append("M")
    return ", ".join(parts)


def html_to_markdown(html):
    # Strip Foundry-specific <section class="secret"> blocks entirely
    html = re.sub(r'<section class="secret"[^>]*>.*?</section>', "", html, flags=re.DOTALL)
    # Deduplicate: if the description is doubled, keep only the first half
    mid = len(html) // 2
    if html[:mid].strip() == html[mid:].strip():
        html = html[:mid]
    # Convert <strong> and <em>
    text = re.sub(r"<strong>(.*?)</strong>", r"**\1**", html, flags=re.DOTALL)
    text = re.sub(r"<em>(.*?)</em>", r"*\1*", text, flags=re.DOTALL)
    # Split on <p> tags into paragraphs
    text = re.sub(r"</?p>", "\n", text)
    # Remove any remaining tags
    text = re.sub(r"<[^>]+>", "", text)
    # Normalize whitespace between paragraphs
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    return "\n\n".join(paragraphs)


def format_level_school_line(level, school_full):
    if level == 0:
        return f"**{school_full.capitalize()} cantrip**"
    ordinal = LEVEL_ORDINAL.get(level, f"{level}th")
    return f"**{ordinal}-level {school_full}**"


def casting_time_tag(activation):
    t = activation.get("type", "")
    if t == "action":
        return "action"
    if t == "bonus":
        return "bonus"
    if t == "reaction":
        return "reaction"
    return "long"


def build_tags(classes, level, is_ritual, is_concentration, activation, school_full):
    tags = sorted(c.lower() for c in classes)
    tags.append("cantrip" if level == 0 else f"level{level}")
    if is_ritual:
        tags.append("ritual")
    if is_concentration:
        tags.append("concentration")
    tags.append(casting_time_tag(activation))
    tags.append(school_full)
    return tags


def parse_subclass_tag(tag):
    """Returns (parent_class, subtag_value) from a subclass tag string.
    For ranger-/sorc-/artificer- prefixes the class is already in the tag,
    so strip the prefix to avoid redundant URLs like ranger-ranger-bloodhound."""
    if tag.startswith("domain-"):
        return ("cleric", tag)
    if tag.startswith("circle-"):
        return ("druid", tag)
    if tag.startswith("oath-"):
        return ("paladin", tag)
    if tag.startswith("patron-"):
        return ("warlock", tag)
    if tag.startswith("ranger-"):
        return ("ranger", tag[len("ranger-"):])
    if tag.startswith("sorc-"):
        return ("sorcerer", tag[len("sorc-"):])
    if tag.startswith("artificer-"):
        return ("artificer", tag[len("artificer-"):])
    return (None, tag)


def parse_class_list(path):
    """Returns dict: spell_name → (classes list, subtags list of {class: subtag} dicts)."""
    class_map = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("|") or line.startswith("| Spell") or line.startswith("| ---"):
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 4 or not parts[1]:
                continue
            name = parts[1]
            classes = [c.strip() for c in parts[3].split(",") if c.strip()]
            subclass_tags = []
            if len(parts) >= 5 and parts[4]:
                for raw in parts[4].split(","):
                    raw = raw.strip()
                    if raw:
                        parent, subtag = parse_subclass_tag(raw)
                        if parent:
                            subclass_tags.append({parent: subtag})
            class_map[name] = (classes, subclass_tags)
    return class_map


def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    condensed_path = os.path.join(repo_root, "2024spells", "dnd2024-spells-condensed.json")
    full_path      = os.path.join(repo_root, "2024spells", "dnd2024-spells-full.json")
    class_list_path = os.path.join(repo_root, "claudeWorkbook", "classSpellLists.md")
    output_dir     = os.path.join(repo_root, "_spells")

    with open(condensed_path, "r", encoding="utf-8") as f:
        condensed = json.load(f)
    with open(full_path, "r", encoding="utf-8") as f:
        full = json.load(f)

    # Build material lookup from full JSON (skip duplicate short-name entries)
    material_map = {}
    for s in full:
        raw_name = s.get("name", "")
        if raw_name in SKIP_NAMES:
            continue
        mat = s.get("system", {}).get("materials", {}).get("value", "")
        if mat:
            material_map[raw_name] = mat

    class_map = parse_class_list(class_list_path)

    skipped = []
    written = []
    no_classes = []

    for spell in condensed:
        raw_name = spell["name"]
        if raw_name in SKIP_NAMES:
            continue
        title = raw_name
        level = spell.get("level", 0)
        school_abbr = spell.get("school", "")
        school_full = SCHOOL_MAP.get(school_abbr, school_abbr)
        components = spell.get("components", [])
        is_ritual = "ritual" in components
        is_concentration = "concentration" in components
        material_text = material_map.get(title, "")
        activation = spell.get("activation", {})
        duration = spell.get("duration", {})
        rng = spell.get("range", {})
        description_html = spell.get("description", "")

        classes, subclass_tags = class_map.get(title, ([], []))
        if not classes:
            no_classes.append(title)

        tags = build_tags(classes, level, is_ritual, is_concentration, activation, school_full)
        tags_yaml = "[" + ", ".join(tags) + "]"
        sources_yaml = "[PHB 2024]"

        subtags_yaml = ""
        if subclass_tags:
            items = ", ".join(
                "{" + f"{list(d.keys())[0]}: {list(d.values())[0]}" + "}"
                for d in subclass_tags
            )
            subtags_yaml = f"subtags: [{items}]\n"

        casting_time = format_activation(activation)
        duration_str = format_duration(duration, is_concentration)
        range_str = format_range(rng)
        components_str = format_components(components, material_text)
        level_school_line = format_level_school_line(level, school_full)
        body = html_to_markdown(description_html)

        filename = spell_to_filename(title)
        filepath = os.path.join(output_dir, filename)

        content = f"""---
layout: post
title:  "{title}"
sources: {sources_yaml}
tags: {tags_yaml}
{subtags_yaml}---

{level_school_line}

**Casting Time**: {casting_time}

**Range**: {range_str}

**Components**: {components_str}

**Duration**: {duration_str}

{body}
"""
        with open(filepath, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        written.append(filename)

    print(f"Written: {len(written)} spell files")
    if no_classes:
        print(f"\nSpells with no class tags ({len(no_classes)}) — supplement spells or unmatched names:")
        for name in sorted(no_classes):
            print(f"  {name}")
    if skipped:
        print(f"\nSkipped ({len(skipped)}):")
        for name in sorted(skipped):
            print(f"  {name}")


if __name__ == "__main__":
    main()
