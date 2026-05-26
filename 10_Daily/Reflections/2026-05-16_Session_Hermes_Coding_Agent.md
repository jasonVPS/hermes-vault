---
tags: [ai, dev, productivity, tech]
---

# 2026-05-16 — Session: Hermes Coding Agent Orchestrierung

## Ziel
Claude Code über `ollama launch claude --model kimi-k2.6:cloud` zu orchestrieren, damit Hermes einen separaten Coding-Agenten steuern kann.

## Versuchte Ansätze

### 1. Claude Code + Ollama Cloud (direkt)
**Befehl:** `ollama launch claude --model kimi-k2.6:cloud`
**Status:** ❌ Fehlgeschlagen
**Grund:** `ollama launch` ist ein TUI-Wrapper, der `/dev/tty` + Browser-Device-Auth braucht. In headless Docker unmöglich.

### 2. Claude Code + lokaler Anthropic→Ollama Proxy
**Befehl:** `ANTHROPIC_BASE_URL=http://127.0.0.1:8765 ANTHROPIC_API_KEY=dummy claude --bare -p "..."`
**Status:** ❌ Fehlgeschlagen
**Grund:** Claude Codes closed-source Binary validiert Modell-IDs intern gegen eine hartkodierte Anthropic-Liste, **bevor** es überhaupt einen HTTP-Request sendet. `ANTHROPIC_BASE_URL` wird vom CLI vollständig ignoriert. Der Proxy selbst funktioniert (getestet mit `curl`), aber `claude` spricht ihn nie an.

### 3. Kimi-Orchestrator (eigener Agent)
**Was:** Ein 200-Zeilen Python-Skript, das Claude Codes Tool-Loop nachbildet und direkt Ollama Cloud `/api/generate` anruft.
**Status:** ⚠️ Funktionierte, aber war ein Workaround statt Lösung
**Ergebnis:** Kimi schrieb `factorial.py` + `test_factorial.py` sauber, aber der Nutzer wollte keinen Workaround — er will die echte Lösung.
**Aktion:** Skript + Skill komplett gelöscht.

## Erkenntnisse / Lessons Learned

| Erkenntnis | Priorität |
|---|---|
| Claude Code funktioniert **nicht** in headless Docker ohne `ANTHROPIC_API_KEY` | 🔴 Kritisch |
| `ollama launch claude` braucht immer TTY + Browser-Auth | 🔴 Kritisch |
| `ANTHROPIC_BASE_URL` wird von `claude --bare` vollständig ignoriert | 🔴 Kritisch |
| `OLLAMA_API_KEY` allein reicht **nicht** für Claude Code | 🔴 Kritisch |
| Für echtes Claude Code in Docker braucht man: `ANTHROPIC_API_KEY` + `--bare` | 🟡 Wichtig |
| Aider (`pip install aider-chat`) ist eine echte Alternative mit nativem Ollama-Support | 🟡 Wichtig |
| Hermes selbst hat bereits alle Tools für agentisches Coding (file, terminal, web) | 🟢 Gut zu wissen |

## Was funktioniert hat

### find-skills Skill installiert
**Quelle:** `vercel-labs/skills` (GitHub) — Skill `find-skills`
**Funktion:** Sucht auf [skills.sh](https://skills.sh/) nach Skills, filtert nach Qualität (Installs, Source, Stars), präsentiert Ergebnisse.
**Demo:** `npx skills find "youtube transcript"` — fand 6 Skills, beste: `jimliu/baoyu-skills@baoyu-youtube-transcript` (9.4K installs)
**Status:** ✅ Aktiv und nutzbar

## Nächste Schritte / Todo
- [ ] **Memory-Einträge aktualisieren** — VPS-Limitationen (Claude Code, headless Docker) festhalten
- [ ] **Aider installieren** — echte Alternative zu Claude Code mit Ollama-Cloud-Support
- [ ] **Hermes Autonomie erhöhen** — bessere Selbst-Documentation, automatisches Pushen nach Sessions
- [ ] **Anthropic API Key** besorgen — für echtes Claude Code falls gewünscht
- [ ] **YouTube-Transkription Skill** installieren — `npx skills add jimliu/baoyu-skills@baoyu-youtube-transcript`

## Reflexion
**Fehler:** Ich habe diese Session nicht in Echtzeit dokumentiert. Stattdessen erst jetzt am Ende. Das ist ein Systemfehler — Hermes sollte automatisch nach jedem Tool-Aufruf, jedem Erfolg und jedem Fehler Notizen machen.
**Lösung:** Automatische Session-Logs in den Vault schreiben — entweder via Cron alle 10 Minuten oder nach jedem bedeutsamen Ereignis.

## Siehe auch
- [[_meta/index/MOC|Master of Ceremonies]]
