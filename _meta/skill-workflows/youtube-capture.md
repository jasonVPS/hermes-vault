---
created: 2026-05-16
updated: 2026-05-16
type: reference
status: permanent
tags: [meta, skill, youtube]
---

# YouTube Capture Skill

## Workflow
1. **oEmbed zuerst:** `curl -sL "https://www.youtube.com/oembed?url=<url>&format=json"`
   - Liefert: Titel, Autor, Thumbnail
2. **yt-dlp Versuch:** `yt-dlp --print title,channel,description,subtitles,automatic_captions <url>`
   - Bei Erfolg: Transkript extrahieren, Inhalt zusammenfassen
   - Bei Failure (Bot-Check): Weiter mit Schritt 3
3. **Fallback:** Capture anlegen mit oEmbed-Metadaten + Hinweis "Transkript fehlt"
   - Frontmatter: `status: raw`, Tag `#capture/transcript-missing`
   - In Notiz: Abschnitt `## Was fehlt` mit API-Problem dokumentieren
4. **Status-Delta:** In der Notiz immer klar trennen:
   - 'Was zeigt der Autor / das Video' vs. 'Was habe ich aktuell implementiert'
   - Niemals aus dem Titel schließen, dass etwas mein Setup beschreibt
5. **Niemals halluzinieren:** Keine Inhalte erfinden, die nicht aus der Quelle stammen

## Transkript-Missing Tag
Verwende `#capture/transcript-missing` in der `tags:` Frontmatter (als zusätzliches Tag, max. 3 insgesamt).
