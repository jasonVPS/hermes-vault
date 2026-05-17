#!/usr/bin/env python3
import re
from pathlib import Path
from datetime import datetime

VAULT = "/opt/data/home/hermes-vault"

AREA_MAP = {
    "ai-news-index.md": {"tags": ["ai"], "title": "AI News Index"},
    "security-news-index.md": {"tags": ["security"], "title": "Security News Index"},
    "dev-news-index.md": {"tags": ["dev"], "title": "Developer News Index"},
    "productivity-index.md": {"tags": ["productivity"], "title": "Productivity Index"},
    "health-index.md": {"tags": ["health"], "title": "Health Index"},
    "finance-index.md": {"tags": ["finance"], "title": "Finance Index"},
    "learning-index.md": {"tags": ["learning"], "title": "Learning Index"},
    "tech-index.md": {"tags": ["tech"], "title": "Tech Index"},
}

def parse_frontmatter(filepath):
    """Extract frontmatter dict from a note (lightweight, no yaml dep)."""
    content = filepath.read_text(errors="ignore")
    m = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).split('\n'):
        if ':' not in line:
            continue
        key, val = line.split(':', 1)
        key = key.strip()
        val = val.strip().strip('"')
        if key == 'tags':
            val = re.findall(r'[\w/-]+', val)
        fm[key] = val
    return fm

def update_index(filename, cfg):
    idx_path = Path(VAULT) / "40_Areas" / filename
    today_str = datetime.now().strftime("%Y-%m-%d")

    if not idx_path.exists():
        idx_path.write_text(f"""---
created: {today_str}
updated: {today_str}
type: index
status: permanent
tags: [index, area]
---

# {cfg['title']}

> Auto-generated index. Updated: {datetime.now():%Y-%m-%d %H:%M}

## Einträge

## Siehe auch
- [[_meta/index/MOC|Master of Ceremonies]]
- [[_meta/LINKING-STRATEGY|Lazy Linking Strategie]]
""")

    # Gather matching notes
    matching = []
    target_tags = set(cfg["tags"])
    for f in Path(VAULT).rglob("*.md"):
        if f.name == filename:
            continue
        fm = parse_frontmatter(f)
        note_tags = fm.get("tags", [])
        if not isinstance(note_tags, list):
            continue
        if any(t in target_tags for t in note_tags):
            title = fm.get("title") or f.stem
            rel = str(f.relative_to(VAULT))
            # Sort key: prefer published/scanned/created date
            date_key = (
                str(fm.get("published", ""))
                or str(fm.get("scanned", ""))
                or str(fm.get("created", ""))
            )
            matching.append((date_key, rel, title))

    # Sort newest first
    matching.sort(key=lambda x: x[0], reverse=True)

    # Build entries block
    entries = "## Einträge\n\n"
    if matching:
        entries += "\n".join(f"- [[{rel}|{title}]]" for _, rel, title in matching) + "\n"
    else:
        entries += "_Keine Einträge aktuell_\n"

    content = idx_path.read_text(errors="ignore")

    # Replace existing entries block
    new_content = re.sub(
        r"## Einträge\n.*?\n(?=## |\Z)",
        entries,
        content,
        count=1,
        flags=re.DOTALL
    )

    # Update frontmatter 'updated'
    new_content = re.sub(
        r'updated:\s*\d{4}-\d{2}-\d{2}',
        f'updated: {today_str}',
        new_content
    )

    # Update auto-generated line
    new_content = re.sub(
        r'\u003e Auto-generated index\. Updated: .+',
        f'\u003e Auto-generated index. Updated: {datetime.now():%Y-%m-%d %H:%M}',
        new_content
    )

    if new_content != content:
        idx_path.write_text(new_content)
        print(f"Updated: {filename} ({len(matching)} Einträge)")
    else:
        print(f"Unchanged: {filename} ({len(matching)} Einträge)")

if __name__ == "__main__":
    for fname, config in AREA_MAP.items():
        update_index(fname, config)
    print("Done updating indices.")
