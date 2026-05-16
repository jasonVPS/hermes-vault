---
created: 2026-05-16
updated: 2026-05-16
type: reference
status: permanent
tags: [meta, errors]
---

# ERROR LOG

Zweck: derselbe Fehler passiert nicht zweimal.

## Eintragsformat
Jeder Eintrag verwendet exakt dieses Format:
YYYY-MM-DD HH:MM — [Kurztitel]
Kontext: Aufgabe / Situation
Fehler: Was konkret schiefging
Ursache: fehlende Regel / falsche Annahme / Halluzination / Skill ignoriert / Duplikat / Tonalität / Struktur / Klassifikation
Lösung: Was richtig gewesen wäre
Vermeidung: Konkrete Regel + Ziel-Datei in _meta/
Skill-Update: Ja [Datei + Diff] / Nein
Tags: #typ/[halluzination|struktur|tonalitaet|regel-ignoriert|duplikat|klassifikation|frontmatter|wikilink|sonstiges]

## Pflicht
1. Jeden Fehler / jede Korrektur sofort eintragen, bevor du weiterarbeitest
2. Vor neuer Aufgabe: ERROR-LOG nach relevanten Tags scannen
3. Cluster (≥3 Einträge gleicher Tag / 30 Tage) → strukturelle Lösung (SELF-IMPROVEMENT.md)
4. Monatlich Cluster-Analyse → `_meta/reviews/YYYY/MM/`

## Statistik (Hermes pflegt am Ende dieser Datei)
- Einträge total: 4
- Einträge letzte 7 Tage: 4
- Einträge letzte 30 Tage: 4
- Top-3-Tags (30 Tage): #typ/struktur (2), #typ/halluzination (1), #typ/regel-ignoriert (1)
- Behobene Cluster (Regel eingeführt): 2
  - AUTONOMY.md Workaround-STOPP
  - _meta/skills → skill-workflows Umbenennung

---

## Einträge
[hier kommen alle Einträge, neueste zuerst]

2026-05-15 22:28 — Falscher Setup-Status: Multi-Agent behauptet statt korrigiert
Kontext: Capture von YouTube-Video angelegt. User korrigiert: 'Ich habe noch keine mehrere Agenten auf Discord. Du bist bisher der einzige.'
Fehler: In USER.md 'Setup-Status' nicht explizit vermerkt, in Capture-Notiz Themen als 'mein Setup' formuliert statt als 'recherchiertes Material'.
Ursache: halluzination — aus Video-Titel eigener Setup-Status abgeleitet, nicht nachgefragt.
Lösung: Capture präzisiert ('nicht mein Setup'), USER.md Setup-Status explizit verankert.
Vermeidung: Bei externem Content immer Status-Delta dokumentieren: 'Was hat der Autor' vs. 'Was habe ich'.
Skill-Update: Ja [youtube-capture.md ergänzt um Status-Delta-Pflicht]
Tags: #typ/halluzination

2026-05-15 22:26 — AUTONOMY-Verstoß: Rückfrage statt Ausführung nach bestätigtem Vorschlag
Kontext: User sagte 'Mach Vorschlag' → Vorschlag gemacht → User bestätigte mit 'Verschieben/löschen: alle fünf...'. Statt sofort auszuführen, kam Rückfrage: 'Soll ich die fünf Root-Dateien jetzt verschieben/archivieren/löschen?'
Fehler: Passivität trotz klarer Anweisung. Modus-Reflex statt Regel-gesteuertem Handeln.
Ursache: regel-ignoriert — AUTONOMY.md '## Verbot' listet 'Auf Aufträge warten', aber 'Soll ich X tun?' nach bestätigtem Vorschlag ist nicht explizit verboten.
Lösung: Sofort ausführen. ERROR-LOG + AUTONOMY.md präzisieren.
Vermeidung: AUTONOMY.md präzisieren: 'Wenn User Vorschlag explizit angefordert und dann bestätigt/ausgewählt hat: Ausführung ist Pflicht ohne weitere Rückfrage.'
Skill-Update: Ja [AUTONOMY.md präzisiert]
Tags: #typ/regel-ignoriert

2026-05-15 22:25 — Grundgerüst unvollständig: drei Top-Level-Ordner fehlten
Kontext: Audit-Check nach Initialisierung. User meldet: Vault zeigt nur 20_Notes, 30_Projects, 40_Areas, 50_Resources, _meta. Fehlend: 00_Inbox/, 10_Daily/, 90_Archive/.
Fehler: Prompt 11 (Vollständigkeits-Check) bestätigte 'alles OK', aber Tree-Output prüfte nur _meta/-Dateien, nicht Top-Level-Ordner-Existenz.
Ursache: struktur — Verifizierung zu oberflächlich, nur Dateien gezählt, nicht Ordner-Struktur gegen Soll-Vorlage.
Lösung: Fehlende Ordner nachgeholt (00_Inbox/2026/05, 10_Daily/2026/05, 90_Archive/2026). structure.md Tree aktualisiert.
Vermeidung: Nach jedem Setup-Schritt Tree-Output gegen Soll-Struktur verifizieren, nicht nur bestätigen. Explicit diff zu Prompt-Vorgabe.
Skill-Update: Nein (Regel in VAULT-RULES.md bereits vorhanden, nicht angewendet)
Tags: #typ/struktur
2026-05-15 22:21 — Datum-Konflikt: Systemdatum vs. User-Local-Time
Kontext: Capture angelegt mit Systemdatum 2026-05-15 UTC. User korrigiert: 'heute ist 2026-05-16' (CEST).
Fehler: Hart auf UTC-Systemdatum gesetzt, ohne User-Timezone zu berücksichtigen.
Ursache: fehlende Regel — VAULT-RULES spezifiziert 'Systemdatum' aber nicht die Zeitzone.
Lösung: VAULT-RULES präzisieren. UTC als technische Primärquelle, bei bekannter User-Timezone (Europe/Berlin) Umrechnung für Dateinamen.
Vermeidung: VAULT-RULES.md Sektion '## Zeitzone' ergänzen.
Skill-Update: Ja [_meta/skills/youtube-capture.md angelegt, VAULT-RULES Zeitzone-Sektion ergänzt]
Tags: #typ/struktur

