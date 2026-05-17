#!/usr/bin/env python3
"""Collect vault statistics for the vault-curator LLM agent.

Metrics calculated according to Lazy Linking Strategy (_meta/LINKING-STRATEGY.md):
- orphan_notes: files with NO internal links AND no "Siehe auch" section (true orphans)
- notes_without_home_link: missing Heimat-Link to MOC/Index/Area
- notes_without_area_tag: missing Bereichs-Tag (e.g. #tech, #ai)
- true_orphans: no links AND older than 7 days AND no area-tag
- link_density_avg: average internal links per note
"""
import os, re, sys, json
from pathlib import Path
from datetime import datetime, timedelta

VAULT = "/opt/data/home/hermes-vault"

BEREICHS_TAGS = {"tech", "ai", "productivity", "health", "finance", "learning", "dev", "security", "news"}

def count_notes(path):
    return len(list(Path(path).rglob("*.md")))

def recent_notes(hours=24):
    cutoff = datetime.now() - timedelta(hours=hours)
    recent = []
    for f in Path(VAULT).rglob("*.md"):
        try:
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            if mtime > cutoff:
                recent.append(str(f.relative_to(VAULT)))
        except Exception:
            pass
    return recent

def get_links(content):
    """Return list of internal wikilinks found in content."""
    return re.findall(r'\[\[([^\]|]+)', content)

def has_home_link(content):
    """Check if note has a link to MOC, Index, or Area."""
    links = get_links(content)
    for link in links:
        l = link.lower()
        if any(x in l for x in ["moc", "index", "areas", "vault-rules", "linking-strategy"]):
            return True
    # Also check Siehe auch section for MOC/Index links
    if re.search(r'## Siehe auch.*?(?:_meta/index|MOC|index|40_Areas)', content, re.DOTALL):
        return True
    return False

def get_note_tags(content):
    """Extract tags from frontmatter."""
    tags = []
    for line in re.findall(r'(?m)^tags:\s*(.+)', content):
        tags.extend(re.findall(r'\b[\w/-]+\b', line))
    return tags

def has_area_tag(content):
    """Check if note has at least one Bereichs-Tag."""
    tags = get_note_tags(content)
    return any(t in BEREICHS_TAGS for t in tags)

def orphan_notes():
    orphans = []
    for f in Path(VAULT).rglob("*.md"):
        content = f.read_text(errors="ignore")
        # No internal links at all?
        if not re.search(r'\[\[.*?\]\]', content):
            orphans.append(str(f.relative_to(VAULT)))
    return orphans

def notes_without_home_link():
    failing = []
    for f in Path(VAULT).rglob("*.md"):
        content = f.read_text(errors="ignore")
        if not has_home_link(content):
            failing.append(str(f.relative_to(VAULT)))
    return failing

def notes_without_area_tag():
    failing = []
    for f in Path(VAULT).rglob("*.md"):
        content = f.read_text(errors="ignore")
        if not has_area_tag(content):
            failing.append(str(f.relative_to(VAULT)))
    return failing

def true_orphans():
    """Verwaist = no links AND older than 7 days AND no area-tag."""
    orphans = []
    cutoff = datetime.now() - timedelta(days=7)
    for f in Path(VAULT).rglob("*.md"):
        try:
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            if mtime > cutoff:
                continue  # too new
        except Exception:
            continue
        content = f.read_text(errors="ignore")
        has_links = bool(re.search(r'\[\[.*?\]\]', content))
        if not has_links and not has_area_tag(content):
            orphans.append(str(f.relative_to(VAULT)))
    return orphans

def link_density():
    total_links = 0
    total_notes = 0
    for f in Path(VAULT).rglob("*.md"):
        content = f.read_text(errors="ignore")
        links = len(re.findall(r'\[\[.*?\]\]', content))
        total_links += links
        total_notes += 1
    avg = round(total_links / total_notes, 2) if total_notes else 0
    return {"total_links": total_links, "total_notes": total_notes, "average": avg}

def get_tags():
    tag_counts = {}
    for f in Path(VAULT).rglob("*.md"):
        content = f.read_text(errors="ignore")
        for line in re.findall(r'(?m)^tags:\s*(.+)', content):
            for tag in re.findall(r'[\w/-]+', line):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
    return dict(sorted(tag_counts.items(), key=lambda x: -x[1])[:20])

if __name__ == "__main__":
    true_orphan_list = true_orphans()
    link_stats = link_density()
    stats = {
        "total_notes": count_notes(VAULT),
        "recent_24h": recent_notes(24),
        "orphans": orphan_notes(),
        "true_orphans": true_orphan_list,
        "true_orphan_count": len(true_orphan_list),
        "notes_without_home_link": notes_without_home_link(),
        "notes_without_area_tag": notes_without_area_tag(),
        "link_stats": link_stats,
        "untagged": [str(n.relative_to(VAULT)) for n in Path(VAULT).rglob("*.md") if not re.search(r'(?m)^tags:', n.read_text(errors="ignore"))],
        "top_tags": get_tags()
    }
    print(json.dumps(stats, indent=2))
