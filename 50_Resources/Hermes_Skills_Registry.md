---
tags: [ai, dev, productivity]
---

# Hermes Skills Registry

Aktualisiert: 2026-05-23

> **Hinweis:** Alle Skills (Builtin + Custom) sind konsolidiert unter `/opt/data/skills/`. Custom Skills aus `~/.hermes/skills/` wurden migriert.

## Custom Skills (selbst erstellt/importiert)

| Skill | Kategorie | Status | Zweck | Quelle |
|-------|-----------|--------|-------|--------|
| **dogfood** | — | enabled | Exploratory QA von Web-Apps | Selbst erstellt |
| **find-skills** | — | enabled | Skills Discovery von [skills.sh](https://skills.sh/) | Vercel Labs (GitHub) |
| **auto-session-log** | productivity | enabled | Automatische Session-Dokumentation in Obsidian | Selbst erstellt |
| **frontend-design** | creative | enabled | Produktionsreife Frontend-Interfaces, vermeidet generische AI-Ästhetik | anthropics/skills (skills.sh) |
| **ui-ux-pro-max** | creative | enabled | UI/UX Design-Intelligenz: 50+ Styles, 161 Paletten, 57 Fonts, 99 UX Guidelines | nextlevelbuilder/ui-ux-pro-max-skill (skills.sh) |
| **baoyu-youtube-transcript** | media | enabled | YouTube-Transkripte ziehen + Timestamps + Summaries ins Vault | jimliu/baoyu-skills (skills.sh) |
| **devops-engineer** | devops | enabled | CI/CD, Docker, GitHub Actions, Deployments automatisiert | jeffallan/claude-skills (skills.sh) |
| **research** | research | enabled | Automatische Web-Recherche, Content Discovery, AI-Tool-Marktplatz-Monitoring | kenneth-liao/ai-launchpad-marketplace (skills.sh) |
| **yuanbao** | social | enabled | Yuanbao (元宝) Group-Management: @mentions, Queries | Selbst erstellt |
| **multi-agent-orchestration** | devops | enabled | Multi-Agent-Workflows orchestrieren und delegieren | skills.sh |

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
| **frontend-design** | Produktionsreife Frontend-Interfaces (importiert) |
| manim-video | Mathe-Animationen |
| p5js | Generative Kunst |
| pixel-art | Pixel Art mit Paletten |
| sketch | HTML Mockups |
| ... | (weitere siehe `hermes skills list`) |

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
| **blogwatcher** | RSS/Atom Feed Monitoring (aktiv: AI-News-Feeds → Vault) |
| llm-wiki | LLM Knowledge Base |
| polymarket | Polymarket Queries |

## Scripts

| Script | Zweck | Standort |
|--------|-------|----------|
| `vault-bootstrap.bat` | Windows: Git Identity, Pull, Push-Test | `_meta/scripts/vault-bootstrap.bat` |
| `vault-bootstrap.sh` | Linux/macOS: Git Identity, Pull, Push-Test | `_meta/scripts/vault-bootstrap.sh` |
| `setup-check.sh` | Self-healing: Tools prüfen + reinstallieren | `~/.hermes/scripts/setup-check.sh` |
| `daily-health-check.py` | Daily: Cron/Vault/Git Diagnose | `~/.hermes/scripts/daily-health-check.py` |
| `update-skills-registry.py` | Skills Registry auto-patchen | `~/.hermes/scripts/update-skills-registry.py` |

## Importierte Skills (Hub)

| Skill | Quelle | Install-Count | Risk |
|-------|--------|---------------|------|
| **frontend-design** | anthropics/skills | 100K+ | Low (Safe) |
| **ui-ux-pro-max** | nextlevelbuilder/ui-ux-pro-max-skill | 1K–10K | Low (Snyk), Caution (Gen) |
| **baoyu-youtube-transcript** | jimliu/baoyu-skills | 1K+ | Med (Gen, Snyk) |
| **devops-engineer** | jeffallan/claude-skills | 4.9K | Safe (Low Risk) |
| **research** | kenneth-liao/ai-launchpad-marketplace | 55 | Safe (Gen), Med (Snyk) |

## Todo: Skills suchen & installieren

- [x] YouTube-Transkription Skill von skills.sh (`baoyu-youtube-transcript`)
- [x] DevOps/Deployment Skills (`devops-engineer`)
- [x] Research Skills (`research`)
- [ ] Testing/QA Skills
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
