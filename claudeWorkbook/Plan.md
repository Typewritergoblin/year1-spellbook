# Spellbook 2024 Update Plan

**Goal:** Migrate The Grimoire from 2014 D&D 5e spells to 2024 D&D 5e spells, choosing the best data format and rebuilding the site accordingly.

---

## Phase 1: Understand the Current Project (Complete)

### Current Stack
- **Site generator:** Jekyll (static site generator)
- **Source:** Markdown posts (not in repo — only the generated HTML output is tracked)
- **Parser:** `scripts/parse_spells.py` (Python 2) — extracted structured data from markdown
- **Search:** Jets.js (full-text, no backend) + custom `tagsearch.js` (tag/class filtering)
- **CSS:** Hand-written responsive CSS
- **Pages:** 489 spell HTML pages + tag index pages

### Current Data Model (per spell)
Each spell has:
- Name, level/school, casting time, range, components, duration
- Description (prose paragraphs, with cross-spell hyperlinks)
- Source book references (e.g. PHB.211, SRD.114)
- Tags: race tags → class tags → level tag → ritual tag → school tag

### Key Problem: Source Files Missing
The original Jekyll markdown source (`_posts/*.md`) is not in the tracked repo — only the generated HTML output. The `_config.yml`, `Gemfile`, `_posts/` directory are all absent. The current workflow cannot be reproduced from the repo as-is.

---

## Phase 2: Format Analysis & Decision

### Option A — Keep Markdown Per-Spell (2014 format)
Each spell is its own `.md` file following `style-guidelines.md`.

**Pros:**
- Human-readable and hand-editable
- Works with existing Jekyll pipeline
- Easy to add tags, notes, cross-references per spell

**Cons:**
- 300+ spells to write/edit individually
- No automated import from the 2024 JSON
- Missing Jekyll source means we'd be starting fresh anyway
- Python 2 parser is dead tech

### Option B — Single JSON (like the 2024 condensed file)
One `spells.json` file, site reads it at build time or runtime.

**Pros:**
- All spells in one place, easy to diff and update
- Can auto-import from `dnd2024-spells-condensed.json` as a starting point
- Works well with modern JS-first site generators (Astro, Eleventy, Next.js)
- Easy to add/extend fields (class tags, source books, etc.)

**Cons:**
- Less human-readable for individual spell editing
- Descriptions already in HTML — need care to sanitize/render safely
- Class tags are MISSING from the 2024 JSON — must be sourced separately

### Option C — Hybrid: JSON data + generated Markdown/HTML
Build script reads JSON → generates per-spell markdown/HTML at build time.

**Pros:**
- Clean separation of data and presentation
- Best of both worlds

**Cons:**
- More tooling complexity

### Critical Gap: Class Tags Are Missing
Neither `dnd2024-spells-condensed.json` nor `dnd2024-spells-full.json` includes which classes can cast each spell. This is the most important metadata for the site's filtering. This data must be sourced separately (e.g., manually curated, scraped from SRD, or found in another dataset).

### Recommendation: Option B — JSON with a Modern Static Site
**Use `dnd2024-spells-condensed.json` as the base data source**, enriched with class tags. Build the site with a modern static site generator (Astro or Eleventy recommended) that reads the JSON at build time and generates static HTML. This gives:
- Easy data editing (one JSON file)
- Fast static site output
- No Python 2 or Jekyll dependency
- Preserves the no-backend, no-database, fully static approach

**Decision to confirm with user before proceeding.**

---

## Phase 3: Data Migration

### 3a. Enrich the 2024 JSON with Missing Data
The condensed JSON needs these fields added per spell:
- `classes` — array of class names (and subclasses) that can cast the spell
- `source` — page reference in the 2024 PHB
- `ritual` — boolean (some spells are rituals)
- `tags` — derived from above, ordered per style-guidelines.md

Strategy options:
1. Find a pre-curated 2024 class spell list dataset online
2. Use the `dnd2024-spells-full.json` (Foundry format) — check if it has class data
3. Manual entry (time-intensive but authoritative)

### 3b. Normalize School Abbreviations
The condensed JSON uses abbreviations (`"evo"`, `"abj"`, `"div"`, etc.) — need mapping to full school names for tags and display.

| Abbr | School |
|------|--------|
| abj | abjuration |
| con | conjuration |
| div | divination |
| enc | enchantment |
| evo | evocation |
| ill | illusion |
| nec | necromancy |
| trs | transmutation |

### 3c. Confirm Spell List Scope
The 2024 PHB has a different spell list than 2014. Some spells were removed, renamed, or revised. Confirm what the target list is (PHB 2024 only? Include UA? Setting-specific spells?).

---

## Phase 4: Rebuild the Website

### 4a. Choose Framework
**Recommendation: Eleventy (11ty)** — lightweight, zero-JS-by-default, supports JSON data files natively, generates static HTML, easy to customize.

Alternative: Astro — more modern, component-based, also excellent for static sites.

### 4b. Site Structure
```
_data/
  spells.json          ← enriched 2024 spell data
  tags.json            ← tag index metadata
src/
  spells/
    [slug].html        ← per-spell template (generated)
  tags/
    [tag].html         ← per-tag template (generated)
  index.html           ← spell list with search/filter
  about/index.html
  css/
  js/
    search.js          ← Jets.js or similar
```

### 4c. Preserve Site Features
- Tag-based filtering (class, school, level, ritual)
- Full-text search (Jets.js or Pagefind)
- Cross-spell hyperlinks in descriptions
- Responsive design
- RSS feed

### 4d. New Style Guidelines Considerations
- 2024 descriptions are already in HTML — may need sanitization and prose reformatting
- Cross-spell hyperlinks need to be re-inserted (not in the JSON)
- Smart quotes, em-dashes per style-guidelines.md

---

## Phase 5: Publish

- **Current hosting:** thebombzen.com/grimoire (external host, not GitHub Pages)
- Confirm deployment method (rsync? FTP? SSH? CI/CD?)
- Build output goes to `_site/` (standard for Jekyll/Eleventy)
- Update DNS or upload built files to host

---

## Open Questions (Need User Input)

1. **Format decision:** Confirm Option B (JSON + modern static site generator)?
2. **Framework choice:** Eleventy vs Astro vs something else?
3. **Class tags source:** Do you have a dataset for 2024 class spell lists, or do we need to build one?
4. **Scope:** PHB 2024 only, or include other 2024 sourcebooks?
5. **Hosting:** How is the current site deployed — SSH/rsync, FTP, CI/CD?
6. **Style guidelines:** Do the 2024 entries need to follow the same prose style (smart quotes, cross-spell hyperlinks), or is that a later concern?
7. **Visual design:** Keep the same look, or redesign while you're at it?

---

## Immediate Next Steps (after decisions)

- [ ] Confirm format and framework choice
- [ ] Source or build class-tag data for 2024 spells
- [ ] Write enrichment script to add class tags to condensed JSON
- [ ] Initialize new site framework (Eleventy or Astro)
- [ ] Build spell page template
- [ ] Build tag index template
- [ ] Build search/filter functionality
- [ ] Migrate and verify all spells
- [ ] Test on local
- [ ] Deploy to production
