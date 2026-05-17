#!/usr/bin/env python3
"""Cron: Scan feeds, create Obsidian notes, mark articles read."""
import os, re, subprocess, sys
from datetime import datetime

VAULT = "/opt/data/home/hermes-vault"
NOTE_DIR = os.path.join(VAULT, "20_Notes", "RSS")

def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def slugify(s):
    return re.sub(r'[^\w\s-]', '', s).strip().replace(' ', '_')[:80]

def main():
    # Scan feeds
    scan = run("blogwatcher-cli scan")
    if scan.returncode != 0:
        print("Scan failed:", scan.stderr, file=sys.stderr)
        sys.exit(1)

    # Get unread articles
    articles = run("blogwatcher-cli articles")
    if articles.returncode != 0:
        print("Articles fetch failed:", articles.stderr, file=sys.stderr)
        sys.exit(1)

    # Parse article lines
    lines = articles.stdout.strip().split('\n')
    articles_list = []
    current = {}
    for line in lines:
        line = line.strip()
        if line.startswith('[') and '] [new]' in line:
            if current: articles_list.append(current)
            # Extract ID and title: [NN] [new] Title...
            match = re.match(r'\[(\d+)\]\s+\[new\]\s+(.+)', line)
            if match:
                current = {"id": int(match.group(1)), "title": match.group(2).strip()}
        elif line.startswith('Blog:'):
            current["blog"] = line.split(':', 1)[1].strip()
        elif line.startswith('URL:'):
            current["url"] = line.split(':', 1)[1].strip()
        elif line.startswith('Published:'):
            current["published"] = line.split(':', 1)[1].strip()
    if current: articles_list.append(current)

    if not articles_list:
        print("No new articles.")
        return

    # Create notes
    today = datetime.now().strftime("%Y-%m-%d")
    daily_dir = os.path.join(NOTE_DIR, today)
    os.makedirs(daily_dir, exist_ok=True)

    read_ids = []
    for art in articles_list:
        title = art.get("title", "Untitled")
        blog = art.get("blog", "Unknown")
        url = art.get("url", "")
        published = art.get("published", today)
        art_id = art.get("id")

        # Skip if note already exists
        safe_title = slugify(title)
        filepath = os.path.join(daily_dir, f"{safe_title}.md")
        if os.path.exists(filepath):
            # Mark read anyway
            read_ids.append(art_id)
            continue

        # Detect content type from title
        clean_title = title.strip()
        lower_title = clean_title.lower()

        # "Quoting Author" format → quote note
        if lower_title.startswith("quoting ") or lower_title.startswith("quoted "):
            note_type = "quote"
            body = f"> {clean_title}\n\n— [{blog}]({url}), {published}\n"
        # "Webinar" → event note
        elif lower_title.startswith("webinar"):
            note_type = "event"
            body = f"## Zusammenfassung\n\n{clean_title}\n\n## Notizen\n\n-"
        # "AINews" prefix → AI news
        elif lower_title.startswith("ainews"):
            note_type = "ai-news"
            body = f"## Zusammenfassung\n\n{clean_title}\n\n## Notizen\n\n-"
        else:
            note_type = "capture"
            body = f"## Zusammenfassung\n\n{clean_title}\n\n## Notizen\n\n-"

        # Determine area tags from title (REGARDLESS of note_type)
        area_tags = set()
        lt = lower_title
        if any(k in lt for k in ["ai", "llm", "gpt", "claude", "gemini", "deepseek", "anthropic", "openai", "neural", "transformer", "model", "training", "finetune"]):
            area_tags.add("ai")
        if any(k in lt for k in ["security", "vulnerability", "exploit", "malware", "breach", "ransomware", "cve", "zero-day", "patch", "hack", "phishing", "backdoor", "trojan", "xss", "sql injection", "rce"]):
            area_tags.add("security")
        if any(k in lt for k in ["dev", "code", "programming", "github", "software", "api", "framework", "language", "rust", "python", "javascript", "docker", "nginx", "linux", "gem", "ruby", "npm", "script", "openclaw"]):
            area_tags.add("dev")
        if any(k in lt for k in ["productivity", "workflow", "habit", "time", "focus", "tool", "automation"]):
            area_tags.add("productivity")
        if any(k in lt for k in ["health", "medical", "fitness", "sleep", "diet", "mental"]):
            area_tags.add("health")
        if any(k in lt for k in ["finance", "money", "invest", "crypto", "stock", "market", "economy", "bitcoin", "ethereum"]):
            area_tags.add("finance")
        if any(k in lt for k in ["learning", "education", "study", "course", "book", "tutorial", "research", "knowledge"]):
            area_tags.add("learning")

        # Default to tech if no area detected
        if not area_tags:
            area_tags.add("tech")

        area_tag_list = sorted(area_tags)
        all_tags = ["rss", slugify(blog).lower(), note_type] + area_tag_list

        # Determine home link based on PRIMARY area
        home_link = "_meta/index/MOC"
        if "ai" in area_tags:
            home_link = "40_Areas/ai-news-index"
        elif "security" in area_tags:
            home_link = "40_Areas/security-news-index"
        elif "dev" in area_tags:
            home_link = "40_Areas/dev-news-index"
        elif "productivity" in area_tags:
            home_link = "40_Areas/productivity-index"
        elif "health" in area_tags:
            home_link = "40_Areas/health-index"
        elif "finance" in area_tags:
            home_link = "40_Areas/finance-index"
        elif "learning" in area_tags:
            home_link = "40_Areas/learning-index"

        see_also_lines = []

        # Auto-detected primary area
        area_index_map = {
            "ai": "40_Areas/ai-news-index",
            "security": "40_Areas/security-news-index",
            "dev": "40_Areas/dev-news-index",
            "productivity": "40_Areas/productivity-index",
            "health": "40_Areas/health-index",
            "finance": "40_Areas/finance-index",
            "learning": "40_Areas/learning-index",
            "tech": "40_Areas/tech-index",
        }
        for atag in area_tag_list:
            idx = area_index_map.get(atag)
            if idx:
                see_also_lines.append(f"- [[{idx}|{atag.title()} News Index]]")

        see_also_lines.append("- [[_meta/index/MOC|Master of Ceremonies]]")

        # Write Obsidian note with frontmatter
        note = f"""---
title: "{clean_title}"
source: "{blog}"
url: "{url}"
published: "{published}"
scanned: "{today}"
tags: [{', '.join(all_tags)}]
type: {note_type}
---

# {clean_title}

**Quelle:** [{blog}]({url})
**Veröffentlicht:** {published}
**Gescannt:** {today}

---

{body}

## Siehe auch
{chr(10).join(see_also_lines)}
"""
        with open(filepath, "w") as f:
            f.write(note)
            print(f"Created: {filepath}")

        read_ids.append(art_id)

    # Mark articles as read
    for art_id in read_ids:
        run(f"blogwatcher-cli read {art_id}")
        print(f"Marked read: ID {art_id}")

    # Git commit the new notes
    if read_ids:
        os.chdir(VAULT)
        run("git add -A")
        run(f'git commit -m "RSS: auto-import {len(read_ids)} articles from {today}"')
        run("git push")
        print(f"Pushed {len(read_ids)} articles to vault.")

    print(f"Done. Processed {len(read_ids)} articles.")

if __name__ == "__main__":
    main()
