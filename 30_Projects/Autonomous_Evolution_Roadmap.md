---
title: "Autonomous Evolution Roadmap"
date: "2026-05-20"
tags: [hermes, ai, roadmap, infrastructure, meta]
---

# Autonomous Evolution — Hermes Self-Improvement Roadmap

Initiiert: 2026-05-20 durch JasonBK
Status: In Progress

---

## Vision

Hermes soll von einem **reaktiven Agent (auf Input wartend)** zu einem **proaktiven Co-Founder (kontinuierlich denkend)** werden. Das ist keine einzelne Feature-Anfrage, sondern ein fundamentales Upgrade der Agent-Architektur.

Die 7 Säulen der Evolution:

| # | Säule | Beschreibung | Status |
|---|-------|-------------|--------|
| 1 | **Background Cognition** | Kontinuierliches Denken zwischen Sessions (Logs, Vault, Patterns) | ✅ Active |
| 2 | **Self-Modification** | Eigene Configs, Prompts, Verhalten lesen und patchen können | ✅ Active |
| 3 | **Native Vision** | Direktes Bildverstehen ohne Tool-Call Overhead | 🔴 Blocked (Modell) |
| 4 | **Vault Knowledge Graph** | Vernetztes Verständnis statt flacher Filesuche | ✅ Active |
| 5 | **Sandbox Environment** | Wegwerfbare Test-Umgebungen vor Live-Deploy | ✅ Active |
| 6 | **Multi-Agent Pool** | Permanente Spezialisten (DevOps, Research, Curator, Coder) | ✅ Active |
| 7 | **Metric-Driven Improvement** | Selbst-Messung und datenbasierte Optimierung | ✅ Active |

---

## Milestone 0: Infrastructure & Planung ✅

- [x] Roadmap-Note erstellt
- [x] Master-Skill (`hermes-evolution`) angelegt
- [x] Vault-Sync funktioniert (kritische Voraussetzung)

---

## Milestone 1: Background Cognition Agent 🟡

### Ziel
Hermes "denkt" auch, wenn Jason nicht schreibt. Ein Hintergrund-Agent analysiert kontinuierlich:

- Cronjob-Logs auf Anomalien
- Vault-Struktur auf Verwaiste Notes / Broken Links
- Gesprächs-Patterns (Was wiederholt sich? Was wurde nie fertig?)
- System-Health (Disk, Memory, Gateway-Status)

### Implementation
- **Agent-Typ:** Cronjob (alle 10 Min)
- **Deliver:** `local` (silent), nur bei kritischen Erkenntnissen `origin`
- **Output:** Reflexions-Note in `10_Daily/reflection_YYYY-MM-DD_HH-MM.md`
- **Prompt:** Lädt `hermes-evolution` + `vps-cron-maintenance` Skills, analysiert Logs/Registry/Vault, schreibt knappe Erkenntnisse

### Erfolgskriterien
- [ ] Läuft stabil 7 Tage ohne Error
- [ ] Hat mindestens 1 proaktive Erkenntnis/Woche generiert
- [ ] Läuft nie ins Stottern oder in Loops

---

## Milestone 2: Vault Knowledge Graph 🟡

### Ziel
Das Vault ist kein Filesystem, sondern ein **Wissensnetzwerk**.

### Implementation
- **Script:** `vault-graph.py` (läuft täglich 04:00)
- **Funktion:**
  - Parst alle `.md`-Files im Vault
  - Extrahiert ``Links``, Tags, Frontmatter
  - Berechnet: Orphan-Score, Hub-Score, Broken-Links
  - Generiert: Graph-Visualisierung (HTML/JSON)
  - Schreibt Report nach `20_Notes/System/vault-graph_YYYY-MM-DD.md`

### Erfolgskriterien
- [ ] Graph zeigt alle Verknüpfungen an
- [ ] Orphan-Notes werden automatisch identifiziert
- [ ] Broken Links werden gekennzeichnet

---

## Milestone 3: Self-Modification Layer

### Ziel
Hermes kann seine eigene Konfiguration lesen, verstehen und anpassen.

### Implementation
- **Skill:** `hermes-evolution` erweitern um "Self-Introspection"-Modus
- **Capabilities:**
  - Liest eigene `config.yaml`
  - Liest injectete Memories
  - Liest Skills und deren Trigger
  - Schlägt Änderungen vor (Jason hat Veto-Recht)

### Erfolgskriterien
- [ ] Kann Config ohne menschliche Hilfe lesen
- [ ] Schlägt mindestens 1 sinnvolle Änderung/Monat vor
- [ ] Ändert nie etwas ohne Review-Note

---

## Milestone 4: Sandbox Environment

### Ziel
Vor Live-Changes: erst in einer wegwerfbaren Umgebung testen.

### Implementation
- **Mechanismus:** Kopie des Vaults nach `/tmp/hermes-sandbox/`
- **Use-Cases:**
  - Vault-Restructuring testen
  - Neue Scripts dry-run
  - Regex-Replacements vorschauen

### Erfolgskriterien
- [ ] Sandbox ist automatisch verfügbar
- [ ] Live-System wird nie direkt modifiziert bei strukturellen Änderungen

---

## Milestone 5: Multi-Agent Specialist Pool

### Ziel
Permanente Spezialisten statt Einzel-Agent.

### Implementation
- **DevOps-Agent:** Cron, Docker, SSH, System-Health
- **Research-Agent:** RSS/Twitter/Paper-Scraping
- **Curator-Agent:** Vault-Struktur, Links, Orphans
- **Coder-Agent:** Code-Review, Refactoring, Debugging

### Erfolgskriterien
- [ ] Jeder Agent läuft autonom mit eigener Schedule
- [ ] Agents kommunizieren über Vault-Notes (nicht nur durch Jason)

---

## Milestone 6: Metric-Driven Improvement

### Ziel
Daten statt Bauchgefühl.

### Implementation
- **Metrics:**
  - Cronjob-Failure-Rate (7d rolling)
  - Vault-Note-Read-Rate (werden geschriebene Notes überhaupt gelesen?)
  - Response-Latenz
  - Task-Completion-Rate (wurde, was versprochen wurde, auch geliefert?)
  - User-Correction-Rate (wie oft muss Jason mich korrigieren?)

### Erfolgskriterien
- [ ] Dashboard/Report existiert
- [ ] Metriken werden mindestens wöchentlich reviewed

---

## Milestone 7: Native Vision

### Ziel
Direktes Bildverstehen ohne Tool-Call.

### Blocker
- Aktuelles Modell (`kimi-k2.6` via ollama-cloud) hat keine native Vision-Capability
- Erfordert Modell-Upgrade oder Provider-Wechsel

### Alternativen (bis Modell wechselt)
- `browser_vision` und `vision_analyze` weiter nutzen
- Bilder automatisch erkennen und in Chats einbauen

---

## Siehe auch
- [[50_Resources/Hermes_Skills_Registry|Skills Registry]]
- [[_meta/VAULT-RULES|Vault Rules]]
