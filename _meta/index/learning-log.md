---
created: 2026-05-16
updated: 2026-05-16
type: reference
status: permanent
tags: [meta, learning]
---

# Learning Log

Pflege: SELF-IMPROVEMENT.md
Zweck: Nicht nur Fehler, sondern auch Erkenntnisse festhalten. Jede Session produziert etwas.

## Eintragsformat

```
YYYY-MM-DD — [Kurztitel]
Kontext: Aufgabe / Situation
Erkenntnis: Was Neues gelernt
Quelle: [[session-note-name]] oder Tool/URL
Relevanz: Einmalig / Wiederkehrend / Strukturell
Skill-Update: Ja [Datei + Diff] / Nein
```

## 2026-05-16

### Claude Code geht nicht in headless Docker
Kontext: User wollte `ollama launch claude --model kimi-k2.6:cloud` in Docker
Erkenntnis: Claude Code Binary validiert Modell-IDs intern gegen Anthropic-Whitelist, ignoriert `ANTHROPIC_BASE_URL`. `ollama launch` braucht TTY + Browser-Auth.
Quelle: [[2026-05-16-session-hermes-coding-agent]]
Relevanz: Strukturell — gilt fuer alle headless Docker Setups
Skill-Update: Ja — AUTONOMY.md (Workaround-STOPP Regel)

### _meta/skills/ vs _meta/skill-workflows/ — Naming ist wichtig
Kontext: Skills-Registry falsch in 50_Resources/ angelegt, dann in _meta/skills/
Erkenntnis: `_meta/skills/` verwirrt, weil echte Skills in `/opt/data/skills/` leben. Meta-Doku braucht klare Trennung.
Quelle: [[2026-05-16-session-hermes-coding-agent]]
Relevanz: Strukturell — Vault-Organisation
Skill-Update: Ja — structure.md, AUTONOMY.md

### Auto-Dokumentation ist Default, nicht Optional
Kontext: User musste explizit daran erinnern, dass Sessions dokumentiert werden muessen
Erkenntnis: Das ist keine Option, die man abfragt. Es ist Grundverhalten.
Quelle: [[2026-05-16-session-hermes-coding-agent]]
Relevanz: Strukturell — Core-Expectation
Skill-Update: Ja — SELF-IMPROVEMENT.md (Explizite Verbote)
