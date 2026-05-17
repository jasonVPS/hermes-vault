#!/usr/bin/env python3
"""Retrofit existing RSS notes with area tags and home links."""
import re
from pathlib import Path

VAULT = '/opt/data/home/hermes-vault'
BEREICHS_TAGS = {'tech', 'ai', 'security', 'dev', 'productivity', 'health', 'finance', 'learning'}
AREA_INDEX_MAP = {
    'ai': '40_Areas/ai-news-index',
    'security': '40_Areas/security-news-index',
    'dev': '40_Areas/dev-news-index',
    'productivity': '40_Areas/productivity-index',
    'health': '40_Areas/health-index',
    'finance': '40_Areas/finance-index',
    'learning': '40_Areas/learning-index',
    'tech': '40_Areas/tech-index',
}

def derive_area_tags(text_lower):
    area_tags = set()
    t = text_lower
    if any(k in t for k in ["ai", "llm", "gpt", "claude", "gemini", "deepseek", "anthropic", "openai", "neural", "transformer", "model", "training", "finetune"]):
        area_tags.add('ai')
    if any(k in t for k in ["security", "vulnerability", "exploit", "malware", "breach", "ransomware", "cve", "zero-day", "patch", "hack", "phishing", "backdoor", "trojan", "xss", "rce"]):
        area_tags.add('security')
    if any(k in t for k in ["dev", "code", "programming", "github", "software", "api", "framework", "language", "rust", "python", "javascript", "docker", "nginx", "linux", "gem", "ruby", "npm", "script", "openclaw"]):
        area_tags.add('dev')
    if any(k in t for k in ["productivity", "workflow", "habit", "time", "focus", "tool", "automation"]):
        area_tags.add('productivity')
    if any(k in t for k in ["health", "medical", "fitness", "sleep", "diet", "mental"]):
        area_tags.add('health')
    if any(k in t for k in ["finance", "money", "invest", "crypto", "stock", "market", "economy", "bitcoin", "ethereum"]):
        area_tags.add('finance')
    if any(k in t for k in ["learning", "education", "study", "course", "book", "tutorial", "research", "knowledge"]):
        area_tags.add('learning')
    if not area_tags:
        area_tags.add('tech')
    return area_tags

changed = 0
for f in sorted(Path(VAULT).rglob('*.md')):
    content = f.read_text(errors='ignore')
    # Skip if already has area tag
    m = re.search(r'^tags:\s*(.+)', content, re.M)
    if not m:
        continue
    existing = set(re.findall(r'\b[\w/-]+\b', m.group(1)))
    if existing & BEREICHS_TAGS:
        continue  # already has one

    # Derive area from title + content
    title_m = re.search(r'^title:\s*"?([^\"\n]+)"?', content, re.M)
    title = title_m.group(1) if title_m else f.stem
    search_text = (title + ' ' + content).lower()
    area_tags = derive_area_tags(search_text)

    # Update tags line
    old_tags = m.group(1)
    new_tags = old_tags.rstrip(']') + ', ' + ', '.join(sorted(area_tags)) + ']'
    new_content = content.replace(old_tags, new_tags, 1)

    # Add Siehe auch if missing entirely
    if '## Siehe auch' not in new_content:
        see_also = '\n## Siehe auch\n'
        for a in sorted(area_tags):
            idx = AREA_INDEX_MAP.get(a)
            see_also += f'- [[{idx}|{a.title()} News Index]]\n'
        see_also += '- [[_meta/index/MOC|Master of Ceremonies]]\n'
        new_content = new_content.rstrip() + see_also

    if new_content != content:
        f.write_text(new_content)
        changed += 1
        print(f.relative_to(VAULT))

print(f'\nGeaendert: {changed} Notizen')
