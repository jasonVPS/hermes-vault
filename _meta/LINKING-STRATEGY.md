---
created: 2026-05-17
updated: 2026-05-17
type: reference
status: permanent
tags: [meta, linking, strategy]
---

# Lazy Linking Strategie

> **Prinzip:** Niemand verlinkt alles sofort. Stattdessen: schnell capturen, strukturiert verarbeiten, automatisch verbinden.

## Warum Lazy?

| Ansatz | Problem |
|--------|---------|
| Sofort alles verlinken | Führt zu Überanstrengung, Vault wird nicht genutzt |
| Gar nicht verlinken | Vault wird zum Dateifriedhof, kein 2. Gehirn |
| **Lazy** | Balance: schnell capturen, langsam verknüpfen, System übernimmt Routine |

## Das 4-Phasen-Modell

### Phase 1: Capture (Input)
**Trigger:** RSS, YouTube, Gedanke, Artikel
**Aktion:**
- In `00_Inbox/` ablegen
- Frontmatter mit `type: capture`, `status: raw`, 1-2 Tags
- KEINE Links gesetzt außer automatisch zum MOC

**Zuständig:** `feed-to-vault` Cronjob

### Phase 2: Process (Strukturieren)
**Trigger:** Inbox-Alter > 48h
**Aktion:**
- Tags prüfen und ggf. ergänzen (mindestens 1 Bereichs-Tag)
- 1 Heimat-Link setzen (zu Area-Index oder MOC)
- Verschieben in passenden Ordner (`20_Notes/`, `30_Projects/`, `40_Areas/`)
- Status auf `processing` setzen

**Zuständig:** `vault-curator` Cronjob

### Phase 3: Connect (Vernetzten)
**Trigger:** Wöchentlicher Curator-Lauf
**Aktion:**
- Ähnliche Notizen finden (gleiche Tags, ähnliche Titel)
- Cross-Links in "Siehe auch" einfügen
- Verwaiste Notizen verlinken

**Zuständig:** `vault-curator` Cronjob

### Phase 4: Distill (Verdichten)
**Trigger:** Hohe Qualität erkannt, wiederholt referenziert
**Aktion:**
- Eigene Permanent Note mit eigener Aussage erstellen
- Alle relevanten Quellen verlinken
- Status auf `permanent` setzen

**Zuständig:** User oder Agent bei Review

## Heimat-Link-Regel

Jede Notiz braucht **genau einen** Link zu einer dieser drei Zieltypen:

| Zieltyp | Beispiel | Wann |
|---------|----------|------|
| **MOC** | `[[_meta/index/MOC]]` | Meta-Themen, System-Notizen |
| **Area-Index** | `[[40_Areas/ai-news-index]]` | Themen-Bereiche |
| **Struktur** | `[[_meta/VAULT-RULES]]` | Meta-Regeln |

Cross-Links (Notiz A → Notiz B) werden NICHT beim Erstellen erzwungen. Die entstehen automatisch in Phase 3.

## Verwaiste Dateien — Definition

Eine Datei ist verwaist, wenn sie ALLE drei Kriterien erfüllt:
1. Keine eingehenden Links hat (und älter als 7 Tage)
2. Keinen Heimat-Link zu MOC/Index/Area hat
3. Keinen Bereichs-Tag hat (#tech, #ai, #productivity, etc.)

Korrektur durch vault-curator:
1. Tag-Analyse → Bereich zuordnen
2. Bereich → passenden Index finden
3. Index-Verweis in "Siehe auch" einfügen

## Lazy-Tag-Regel

- Max. 3 Tags
- Mindestens 1 Bereichs-Tag: #tech, #ai, #productivity, #health, #finance, #learning, #dev, #security, #news
- Sekundäre Tags: #rss, #meta, #index, #quote, #capture

## Indikatoren für gute Vernetzung

| Metrik | Zielwert | Überprüfung |
|--------|----------|-------------|
| Orphan-Ratio | < 10% | vault-curator Report |
| Durchschnittliche Links pro Notiz | > 2 | vault-curator Report |
| Notes mit Heimat-Link | 100% | vault-curator Report |
| Inbox-Alter (älteste) | < 7 Tage | vault-curator Report |

## Siehe auch
- [[_meta/VAULT-RULES]]
- [[_meta/EXPANSION-RULES]]
- [[_meta/index/MOC]]
