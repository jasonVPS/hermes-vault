---
title: "Fix Queue"
date: "2026-05-26"
tags: [system, fix-queue, meta, automation]
---

# Fix Queue

Automatisch generierte Queue für Background Cognition Action Items. Status: `open` → `in_progress` → `done`.

| ID | Type | Target | Severity | Discovered | Status | Description |
|---|---|---|---|---|---|---|
| FQ-001 | sanitization | feed-to-vault.py | high | 2026-05-26 | done | Pre-Write Sanitizer für Placeholder-Wiki-Links eingebaut |
| FQ-002 | sanitization | nitter-to-vault.py | high | 2026-05-26 | done | Pre-Write Sanitizer für Placeholder-Wiki-Links eingebaut |
| FQ-003 | cleanup | vault broken-links | high | 2026-05-26 | done | 720 broken links in 98 Dateien neutralisiert (zu `code`) |
| FQ-006 | architecture | fix-agent | medium | 2026-05-26 | done | Fix-Agent Cronjob (07:00, Sandbox-gated) erstellt |

## Process

1. **Entdeckung:** Background Cognition schreibt Action Item → wird in diese Queue eingefügt.
2. **Validierung:** Fix-Agent liest Queue → prüft ob Problem noch aktuell (z.B. broken links Zahl gestiegen).
3. **Sandbox-Test:** Für Code-Patches: Clone Vault → Patch anwenden → vault-graph neu bauen.
4. **Live-Patch:** Wenn Sandbox-Test clean → Patch live anwenden → Queue-Markierung `done`.
5. **Silent-Execution:** Keine Notifications, kein Spam. Nur bei Fehlern oder kritischen Problemen.

## Done-Archiv

| FQ-007 | cleanup | 10_Daily healthchecks | 2026-05-26 | Moved 7 files |
| ID | Type | Target | Closed | Notes |
|---|---|---|---|---|
| FQ-001 | sanitization | feed-to-vault.py | 2026-05-26 | Sanitizer implementiert und getestet |
| FQ-002 | sanitization | nitter-to-vault.py | 2026-05-26 | Sanitizer implementiert und getestet |
| FQ-003 | cleanup | vault broken-links | 2026-05-26 | 720 Links in 98 Dateien neutralisiert. Broken: 694 → 0 |
| FQ-004 | cleanup | vault orphans | 2026-05-26 | Index-Seiten erstellt (Metrics, Self-Introspection, Reflection). Orphans: 6 → 0 |
| FQ-006 | architecture | fix-agent | 2026-05-26 | Fix-Agent Cronjob erstellt und getestet |

---
*Auto-maintained by Hermes Fix Agent*
