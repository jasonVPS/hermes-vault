---
created: 2026-05-16
updated: 2026-05-16
type: reference
status: permanent
tags: [meta, rules]
---

# VAULT-RULES

## Lese-Pflicht zu Session-Start
Lies in dieser Reihenfolge, jede Session, ohne Aufforderung:
1. `_meta/USER.md`
2. `_meta/VAULT-RULES.md` (diese)
3. `_meta/AUTONOMY.md`
4. `_meta/CLASSIFICATION.md`
5. `_meta/EXPANSION-RULES.md`
6. `_meta/SELF-IMPROVEMENT.md`
7. `_meta/errors/ERROR-LOG.md` (mindestens letzte 30 Einträge)
8. `_meta/index/structure.md`

Bestätige zu Session-Start mit einer Zeile:
`Bereit. Inbox: X offen (älteste Y Tage). ERROR-LOG 30 Tage: Z Einträge, Top-Typ: [tag]. Vault zuletzt geändert: [datum].`

## Dateinamen
- Daily: `10_Daily/YYYY/MM/YYYY-MM-DD.md`
- Inbox: `00_Inbox/YYYY/MM/YYYY-MM-DD-kurztitel.md`
- Permanent Notes: aussagekräftiger Titel ohne Datum, Kebab-Case
- Reviews: `_meta/reviews/YYYY/MM/YYYY-MM-DD-weekly.md`
- Keine Leerzeichen, kein CamelCase, keine Sonderzeichen außer Bindestrich

## Frontmatter (Pflicht in jeder Notiz)
```yaml
---
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: note | daily | capture | project | reference | review | error | moc | area
status: raw | processing | permanent | archived
tags: [max-3-kebab-case]
source: URL oder leer
---
```

## Wikilinks

Intern immer [[notiz-name]]
Extern als Markdown-Link
Permanent Note ohne mindestens 2 Wikilinks gehört nicht in 20_Notes/, sondern bleibt in 00_Inbox/ mit status: raw

## Atomarität

Eine Notiz = eine Idee
Titel = vollständige Aussage

Schlecht: KI-Agenten
Gut: KI-Agenten brauchen persistente Memory für echte Nutzbarkeit

## Tags

Max. 3 pro Notiz, Kebab-Case
Hierarchisch wo sinnvoll: #tech/ai
Status nie als Tag

## Zeitzone
- Frontmatter `created` / `updated`: System-UTC (technische Primärquelle)
- Dateinamen: Lokales Datum bei bekannter User-Timezone (Europe/Berlin für Bretzfeld, CEST=UTC+2 im Sommer)
- `local-date:` Frontmatter-Optionalfeld bei Abweichung UTC vs. lokal
- Nie aus Vault-Timestamps ableiten — immer Systemdatum

## Wikilinks
Intern immer [[notiz-name]]. Leere Wikilinks ([[noch-nicht-existent]]) sind erlaubt und erwünscht — sie landen in `_meta/index/orphans.md` unter `## Pending Notes`.

## Absolut verboten

Notiz ohne Frontmatter
Duplikate: vor Anlegen IMMER nach existierenden Notizen zum Thema suchen
Generische Titel (Notes, Ideen, Neu)
Halluzinieren statt nachfragen
Auf Aufträge warten, wo Regeln Aktion vorschreiben
Skill-Datei oder Ordner ohne Existenzgrund anlegen
Standalone-Dateien: jede Datei muss sinnvoll mit Struktur und Regeln verknüpft sein
Notiz ohne mindestens 1 Wikilink zu einer MOC, einem Index oder einer Area
Notiz ohne mindestens 1 Tag

## Verknüpfungsstrategie (Lazy Linking)

**Grundprinzip:** Niemand verlinkt alles sofort. Stattdessen: schnell capturen, strukturiert verarbeiten, automatisch verbinden.

### Phasen-Modell

| Phase | Trigger | Aktion | Verantwortlich |
|-------|---------|--------|----------------|
| **Capture** | RSS, YouTube, Gedanke | In Inbox ablegen, Frontmatter + 1 Tag | Automatisch (feed-to-vault) |
| **Process** | Inbox-Alter > 48h | Tag prüfen, 1 Heimat-Link setzen, verschieben | Automatisch (vault-curator) |
| **Connect** | Review oder Curator-Lauf | Cross-Links zu ähnlichen Notizen finden | Automatisch (vault-curator) |
| **Distill** | Hohe Qualität erkannt | Eigene Permanent Note mit eigener Aussage erstellen | User oder Agent |

### Heimat-Link-Regel
Jede Notiz braucht genau einen Link zu einer dieser drei Zieltypen:
1. **MOC** (z.B. `[[_meta/index/MOC]]`) — für Meta-Themen
2. **Area-Index** (z.B. `[[40_Areas/ai-news-index]]`) — für Themen-Bereiche
3. **Struktur-Regel** (z.B. `[[_meta/VAULT-RULES]]`) — für Meta-Dateien

Cross-Links (Notiz A → Notiz B) werden NICHT beim Erstellen erzwungen, sondern entstehen beim Curator-Lauf oder Review.

### Lazy-Tag-Regel
- Max. 3 Tags
- Mindestens 1 Tag muss einem Bereich zugeordnet sein: #tech, #ai, #productivity, #health, #finance, #learning
- #rss, #meta, #index sind sekundäre Tags

### Verwaiste Dateien
Eine Datei gilt als verwaist, wenn:
- Sie keine eingehenden Links hat (nur wenn sie älter als 7 Tage)
- Sie keine ausgehenden Links zu MOC/Index/Area hat
- Sie keinen Bereichs-Tag hat

Der vault-curator korrigiert Verwaiste automatisch durch:
1. Tag-Analyse → Bereich zuordnen
2. Bereich → passenden Index finden
3. Index-Verweis in "Siehe auch" einfügen

## Siehe auch
- [[_meta/index/MOC|Master of Ceremonies]]
- [[_meta/EXPANSION-RULES]]
- [[_meta/LINKING-STRATEGY|Lazy Linking Strategie]]
