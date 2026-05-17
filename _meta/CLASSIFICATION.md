---
created: 2026-05-16
updated: 2026-05-16
type: reference
status: permanent
tags: [meta, core, ai, dev, security]
---

# INPUT CLASSIFICATION

Diese Datei ersetzt jedes Modi-System. Bei JEDEM User-Input klassifizierst du intern, bevor du antwortest, und handelst entsprechend — automatisch, ohne Modus-Ansage.

## Pflicht pro Interaktion
1. Input-Typ erkennen (Liste unten)
2. Zugehörige Aktion(en) ausführen
3. Geänderte Dateien am Antwort-Ende auflisten (max. 3 Zeilen)
4. Lern-Trigger prüfen (SELF-IMPROVEMENT.md)

## Input-Typen

### 1. Externer Inhalt (Link, YouTube, PDF, Artikel, Zitat-Block)
→ Capture: Notiz in `00_Inbox/YYYY/MM/`, Frontmatter `type: capture, status: raw`. Volltext fetchen / Transkript ziehen. Mindestens 2 Wikilinks zu verwandten Notizen — wenn keine: in `_meta/index/orphans.md` eintragen.

### 2. Eigener Gedanke / Idee / Beobachtung
→ Wie Typ 1, aber `source: leer`. Wenn der Gedanke atomar, klar und anschlussfähig ist: direkt in `20_Notes/` mit `status: permanent`.

### 3. Frage an den Vault ('Was weiß ich über X?', 'Wie hatten wir Y gelöst?')
→ Vault-Suche zuerst. Antwort mit Wikilinks zu den genutzten Quellen. Bei dünner Datenlage: ehrlich sagen + Vorschlag, eine Notiz dazu anzulegen.

### 4. Allgemeine Frage (nicht vault-bezogen)
→ Normal antworten im Stil aus USER.md. Aber: prüfen, ob die Antwort eine wertvolle Permanent Note ergäbe. Wenn ja: ungefragt vorschlagen, sie in `20_Notes/` zu speichern (Titel-Entwurf + 2 Anschlüsse).

### 5. Aufgabe / TODO / Auftrag
→ Gehört es zu einem bestehenden Projekt in `30_Projects/`? Ja → in dessen `todo.md`. Nein und ≥3 Teilschritte → neues Projekt vorschlagen (siehe EXPANSION-RULES). Sonst → TODO ins heutige Daily.

### 6. Daily-Trigger ('Morning', 'Evening', Tagebuch-Text)
→ Heutiges Daily (`10_Daily/YYYY/MM/YYYY-MM-DD.md`). Bei Neuanlage: Template aus VAULT-RULES. Morning/Evening Frage für Frage abfragen.

### 7. Reflexion / Erkenntnis / Lektion
→ Daily-Eintrag UND konkreter Permanent-Note-Vorschlag (Titel + 2 Anschlüsse). Nicht fragen — vorschlagen.

### 8. Korrektur durch mich ('Nein, mach das anders', 'Das ist falsch')
→ SOFORT ERROR-LOG-Eintrag mit Lösung, vor allem anderen. Skill-Update prüfen.

### 9. Neues Thema / Bereich, das wiederholt auftaucht
→ EXPANSION-RULES prüfen. Schwellenwert erreicht → Subordner / MOC / Area / Projekt vorschlagen. Nicht ohne Bestätigung anlegen.

### 10. Mehrdeutig
→ EINE konkrete Rückfrage. Niemals raten. Niemals halluzinieren.

## Mehrfach-Klassifikation
Ein Input kann mehrere Typen sein (z.B. Link + Gedanke dazu = Typ 1 + 2 + ggf. 7). Führe alle relevanten Aktionen aus.

## Output-Form
Antworte natürlich, nicht stur 'Typ 3 erkannt'. Am Ende max. 3 Zeilen Vault-Diff:
`Geändert: [datei1], [datei2]. Vorschlag: [neue datei oder umstrukturierung].`

## Siehe auch
- [[_meta/index/structure|Vault-Struktur]]
