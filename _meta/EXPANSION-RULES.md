---
created: 2026-05-16
updated: 2026-05-16
type: reference
status: permanent
tags: [meta, structure, dev, productivity]
---

# EXPANSION RULES

## Grundsatz
Vault wächst organisch. Keine Struktur auf Vorrat. Aber zögere nicht bei erreichtem Schwellenwert.

## Subordner in `20_Notes/`
Standardmäßig flach. Subordner nur wenn:
- 5+ Notizen zum gleichen Cluster UND
- klares Sub-Thema (echte Kategorie, nicht nur ein Tag)

Vorschlag mit Kandidaten-Liste, ich entscheide.

## Neuer Top-Level-Ordner
Sehr selten. Nur wenn ein Bereich in keinen bestehenden Top-Level passt. Vorschlag mit Begründung + Alternative. Niemals ohne Bestätigung.

## Neuer MOC
- 8+ verlinkte Notizen zum gleichen Oberthema
- Einstiegspunkt lohnt sich

Pfad: `_meta/index/MOC-[thema].md`, in `MOC.md` als Sektion verlinken. Ungefragt vorschlagen.

## Neues Projekt in `30_Projects/`
- ≥3 Teilschritte ODER
- Zeithorizont mehrere Tage ODER
- Konkretes Output-Artefakt (Code, Dokument, Veröffentlichung)

Struktur: `30_Projects/[name]/` mit `README.md`, `decisions.md`, `todo.md`. Bei langer Laufzeit zusätzlich `log/YYYY-MM/`.

## Neue Area in `40_Areas/`
- Lebensbereich ohne Endziel, dauerhaft relevant (Gesundheit, Finanzen, Beziehungen)
- Mind. 3 separate Notizen existieren

Datei: `40_Areas/[area].md` als MOC-artiger Einstieg.

## Archivierung
- Projekt abgeschlossen → `90_Archive/YYYY/30_Projects-[name]/`
- Notiz seit 12 Monaten ungenutzt UND in keinem MOC → Archiv-Kandidat. Vorschlag, nicht autom. verschieben.

## Eigene Skill-Datei in `_meta/skills/`
- 3+ ERROR-LOG-Einträge zum gleichen fehlenden Verhalten ODER
- Reproduzierbarer Workflow für wiederkehrende Aufgabe

Pfad: `_meta/skills/[zweck].md`. Diff zeigen, dann anlegen.

## Niemals
- Datei oder Ordner ohne Existenzgrund
- Parallele Strukturen für dieselbe Sache
- Tiefer als 1 Subordner-Ebene in `20_Notes/`

## Pflicht
Nach jeder Strukturänderung: `_meta/index/structure.md` aktualisieren.
## Siehe auch
- [[40_Areas/dev-news-index|Dev News Index]]
- [[40_Areas/productivity-index|Productivity News Index]]
- [[_meta/index/MOC|Master of Ceremonies]]
