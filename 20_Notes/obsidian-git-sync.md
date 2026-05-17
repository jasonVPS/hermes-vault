---
created: 2026-05-16
updated: 2026-05-16
type: note
status: permanent
tags: [obsidian, git, sync, ai, dev, productivity]
---

# Obsidian Git Sync

Bidirektionale Synchronisation zwischen lokalem Obsidian (Windows PC) und VPS (Docker) via GitHub.

## Setup

**VPS (Hermes):**
- Vault: `/opt/data/home/hermes-vault/`
- Remote: `github-vault:jasonVPS/hermes-vault.git`
- SSH-Key: `/root/.ssh/id_ed25519_vault`
- Cron: jede Minute `git pull → add → commit → push`

**Lokal (PC):**
- Obsidian Git Plugin: Auto-Commit alle 60 Sekunden
- Remote: gleiches `jasonVPS/hermes-vault`

## Konfliktstrategie

1. Immer `git pull --rebase` vor `push`
2. Bei Merge-Konflikt: Lokale Änderung bevorzugen (User PC), VPS-Anpassung manuell re-applizieren
3. `.obsidian/sync-stats.json` wird von beiden Seiten geändert — akzeptiere immer neueren Timestamp

## Wichtige Pfade

| Was | Wo |
|---|---|
| VPS Vault | `/opt/data/home/hermes-vault/` |
| VPS SSH Config | `/root/.ssh/config` (Host github-vault) |
| Cron Log | `/opt/data/logs/` |
| Git Remote | `github-vault:jasonVPS/hermes-vault.git` |

## Troubleshooting

- **Push rejected** → `git pull origin main --rebase && git push origin main`
- **SSH Permission denied** → Key muss in `/root/.ssh/`, nicht `/opt/data/home/.ssh/`
- **Konflikt** → `git checkout --theirs .obsidian/sync-stats.json` (neuer gewinnt)

## Siehe auch
- [[_meta/index/MOC|Master of Ceremonies]]
- [[_meta/index/structure|Vault-Struktur]]
