---
title: "Multi-Agent Specialist Pool"
date: "2026-05-20"
tags: [system, meta, tech, agents, multi-agent]
---

# Multi-Agent Specialist Pool

## Overview

Hermes now supports **specialist agents** that run autonomously and communicate via the vault.
This is not multiple LLM instances (that would be expensive), but **persistent agent identities**
with dedicated responsibilities, schedules, and output channels.

## Agent Definitions

| Agent | Responsibility | Trigger | Output |
|-------|---------------|---------|--------|
| **DevOps Agent** | System health, Docker, Cron, SSH | Every 2 min (Gateway Watchdog) + every 30 min (Setup Watchdog) | Logs + vault notes |
| **Research Agent** | RSS feeds, AI news, security alerts | 06:00 (AI News Digest), 07:00 (feed-to-vault) | Vault notes in `20_Notes/RSS/` |
| **Curator Agent** | Vault structure, orphan notes, broken links | 04:00 (Vault Graph), 06:00 (vault-curator) | Reports + auto-repair suggestions |
| **Coder Agent** | Code review, refactoring, debugging | On-demand (when user shares code) | Inline comments + PRs |
| **Metrics Agent** | Performance tracking, alerting | 06:00 (Metrics Report) | Reports in `20_Notes/System/` |
| **Introspect Agent** | Self-modification, config drift, skill registry | 05:00 (Self-Introspect) | Drift reports + proposals |
| **Background Cognition** | Reflection, pattern recognition, proactivity | Every 10 min | `10_Daily/reflection_*.md` |

## Communication Protocol

Agents do not talk to each other directly. Instead, they communicate via **vault notes**:

1. **Status Notes:** `Agent-Pool/status_<agent>_<YYYY-MM-DD>.md`
   - Each agent writes its status after every run
   - Contains: success/failure, key findings, next actions

2. **Requests:** `Agent-Pool/request_<source>_<target>_<YYYY-MM-DD>.md`
   - If Agent A needs something from Agent B
   - Example: "Curator requests DevOps to investigate disk growth"

3. **Handoffs:** `Agent-Pool/handoff_<source>_<target>.md`
   - Long-running tasks handed from one agent to another

## Agent Directory

```
20_Notes/System/Agent-Pool/
├── README.md                 (this file)
├── status_devops_2026-05-20.md
├── status_curator_2026-05-20.md
├── status_metrics_2026-05-20.md
└── ...
```

## Rules

1. **No Direct Inter-Agent Messages.** All communication goes through vault notes.
2. **Silent By Default.** Agents only create notes when they have something to report.
3. **Jason Is The Final Arbiter.** Agents can suggest but never execute destructive actions without user confirmation (unless explicitly delegated).
4. **Observability.** Every agent action is logged in `jobs.json` and in vault notes.

## How to Add a New Agent

1. Create a script in `/opt/data/scripts/<agent-name>.py`
2. Create a cronjob: `hermes cron create '<schedule>' '<Agent Name>' --no-agent --script <agent-name>.py --deliver local`
3. Add the agent to this README
4. Define its status note template

## Current Active Agents

As of {{date}}:

- **Background Cognition:** ✅ Active (every 10 min)
- **Vault Graph:** ✅ Active (04:00 daily)
- **Self-Introspect:** ✅ Active (05:00 daily)
- **Metrics Report:** ✅ Active (06:00 daily)
- **Daily AI News:** ✅ Active (06:00 daily)
- **vault-curator:** ✅ Active (06:00 daily)
- **feed-to-vault:** ✅ Active (07:00 daily)
- **Daily Health Check:** ✅ Active (06:30 daily)
- **Gateway Watchdog:** ✅ Active (every 2 min)
- **Setup Watchdog:** ✅ Active (every 30 min)
- **Vault Auto-Sync:** ✅ Active (every 10 min)
- **hermes-vault-sync:** ✅ Active (every 1 min)
- **nitter-to-vault:** ✅ Active (every 30 min)

Total: **13 agents** active

## See Also

- [[self-introspect_2026-05-20|Latest Self-Introspection Report]]
- [[metrics_2026-05-20|Latest Metrics Report]]
- [[vault-graph_2026-05-20|Latest Vault Graph]]

## Siehe auch

- [[_meta/index/MOC|Master of Ceremonies]]
