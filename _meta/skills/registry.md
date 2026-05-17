---
created: 2026-05-16
updated: 2026-05-16
type: reference
status: permanent
tags: [meta, skills, registry]
---

# Skills Registry

## Custom Skills (selbst erstellt/importiert)

| Skill | Kategorie | Status | Zweck | Quelle |
|-------|-----------|--------|-------|--------|
| **find-skills** | — | ✅ enabled | Skills Discovery von [skills.sh](https://skills.sh/) | Vercel Labs (GitHub) |
| **auto-session-log** | productivity | ✅ enabled | Automatische Session-Dokumentation in Obsidian | Selbst erstellt |

## Builtin Skills (vorinstalliert)

### Autonomous AI Agents
| Skill | Zweck |
|-------|-------|
| claude-code | Claude Code CLI Delegation |
| codex | OpenAI Codex CLI Delegation |
| hermes-agent | Hermes Config/Setup/Development |
| opencode | OpenCode CLI Delegation |

### Creative
| Skill | Zweck |
|-------|-------|
| architecture-diagram | SVG Architekturdiagramme |
| ascii-art | ASCII Art Generator |
| comfyui | Bild/Video Generierung |
| excalidraw | Handgezeichnete Diagramme |
| manim-video | Mathe-Animationen |
| p5js | Generative Kunst |
| pixel-art | Pixel Art mit Paletten |
| sketch | HTML Mockups |

### Data Science
| Skill | Zweck |
|-------|-------|
| jupyter-live-kernel | Live Jupyter Kernel |

### DevOps
| Skill | Zweck |
|-------|-------|
| kanban-orchestrator | Multi-Agent Task Board |
| kanban-worker | Kanban Worker |
| webhook-subscriptions | Event-Driven Webhooks |

### GitHub
| Skill | Zweck |
|-------|-------|
| github-auth | GitHub Auth Setup |
| github-code-review | PR Reviews |
| github-pr-workflow | PR Lifecycle |
| github-issues | Issue Management |
| github-repo-management | Repo Management |

### Media
| Skill | Zweck | Notiz |
|-------|-------|-------|
| **youtube-content** | YouTube Transkripte, Summaries | Nutzt ursprünglich `youtube-transcript-api` |
| gif-search | Tenor GIF Suche |
| spotify | Spotify Playback |
| songsee | Audio Analyse |

### Note-Taking
| Skill | Zweck |
|-------|-------|
| obsidian | Obsidian Vault Management |
| obsidian-vault-sync | Git-Sync für Obsidian |
| vault-curation | Autonome Vault Curation |

### Productivity
| Skill | Zweck |
|-------|-------|
| **auto-session-log** | Automatische Session Logs |
| **vault-curation** | Zettelkasten Curation |
| google-workspace | Gmail, Calendar, Drive |
| notion | Notion API |
| linear | Linear Issue Tracking |
| powerpoint | .pptx Erstellung |

### Research
| Skill | Zweck |
|-------|-------|
| arxiv | arXiv Paper Suche |
| blogwatcher | RSS/Atom Feed Monitoring |
| llm-wiki | LLM Knowledge Base |
| polymarket | Polymarket Queries |

## Importierte Skills (Hub)

Keine aktuell — alle Skills sind entweder builtin oder manuell erstellt.

## Todo: Skills suchen & installieren

- [ ] YouTube-Transkription Skill von skills.sh (`npx skills add jimliu/baoyu-skills@baoyu-youtube-transcript`)
- [ ] Testing/QA Skills
- [ ] DevOps/Deployment Skills
- [ ] Weitere Productivity Skills

## Skill-Verwaltung

```bash
# Alle Skills anzeigen
hermes skills list

# Skill aktivieren/deaktivieren
hermes skills config

# Skill vom Hub installieren
hermes skills install <id>

# Skills updaten
hermes skills update
```

## Siehe auch
- [[_meta/index/MOC|Master of Ceremonies]]
- [[_meta/index/structure|Vault-Struktur]]
