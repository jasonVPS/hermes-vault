---
title: "New supply chain attack this time for npm axios, the most popular HTTP client library with 300M weekly downloads.

Scanning my system I found a use imported from googleworkspace/cli from a few days ago when I was experimenting with gmail/gcal cli. The installed version (luckily) resolved to an unaffected 1.13.5, but the project dependency is not pinned, meaning that if I did this earlier today the code would have resolved to latest and I'd be pwned.

It's possible to personally defend against these to some extent with local settings e.g. release-age constraints, or containers or etc, but I think ultimately the defaults of package management projects (pip, npm etc) have to change so that a single infection (usually luckily fairly temporary in nature due to security scanning) does not spread through users at random and at scale via unpinned dependencies.

More comprehensive article:
https://www.stepsecurity.io/blog/axios-compromised-on-npm-malicious-versions-drop-remote-access-trojan"
source: "X - Andrej Karpathy"
author: "Andrej Karpathy"
url: "http://nitter.perennialte.ch/karpathy/status/2038849654423798197#m"
published: "Tue, 31 Mar 2026 05:23:32 GMT"
scanned: "2026-05-18"
tags: [rss, x_-_andrej_karpathy, twitter, x, social, ai, ai, dev, security]
type: social
---

# New supply chain attack this time for npm axios, the most popular HTTP client library with 300M weekly downloads.

Scanning my system I found a use imported from googleworkspace/cli from a few days ago when I was experimenting with gmail/gcal cli. The installed version (luckily) resolved to an unaffected 1.13.5, but the project dependency is not pinned, meaning that if I did this earlier today the code would have resolved to latest and I'd be pwned.

It's possible to personally defend against these to some extent with local settings e.g. release-age constraints, or containers or etc, but I think ultimately the defaults of package management projects (pip, npm etc) have to change so that a single infection (usually luckily fairly temporary in nature due to security scanning) does not spread through users at random and at scale via unpinned dependencies.

More comprehensive article:
https://www.stepsecurity.io/blog/axios-compromised-on-npm-malicious-versions-drop-remote-access-trojan

**Quelle:** [X - Andrej Karpathy](http://nitter.perennialte.ch/karpathy/status/2038849654423798197#m)  
**Autor:** Andrej Karpathy  
**Veröffentlicht:** Tue, 31 Mar 2026 05:23:32 GMT  
**Gescannt:** 2026-05-18

---

## Inhalt

New supply chain attack this time for npm axios, the most popular HTTP client library with 300M weekly downloads. Scanning my system I found a use imported from googleworkspace/cli from a few days ago when I was experimenting with gmail/gcal cli. The installed version (luckily) resolved to an unaffected 1.13.5, but the project dependency is not pinned, meaning that if I did this earlier today the code would have resolved to latest and I'd be pwned. It's possible to personally defend against these to some extent with local settings e.g. release-age constraints, or containers or etc, but I think ultimately the defaults of package management projects (pip, npm etc) have to change so that a single infection (usually luckily fairly temporary in nature due to security scanning) does not spread through users at random and at scale via unpinned dependencies. More comprehensive article: stepsecurity.io/blog/axios-c… Feross (@feross) 🚨 CRITICAL: Active supply chain attack on axios -- one of npm's most depended-on packages. The latest axios@1.14.1 now pulls in plain-crypto-js@4.2.1, a package that did not exist before today. This is a live compromise. This is textbook supply chain installer malware. axios has 100M+ weekly downloads. Every npm install pulling the latest version is potentially compromised right now. Socket AI analysis confirms this is malware. plain-crypto-js is an obfuscated dropper/loader that: • Deobfuscates embedded payloads and operational strings at runtime • Dynamically loads fs, os, and execSync to evade static analysis • Executes decoded shell commands • Stages and copies payload files into OS temp and Windows ProgramData directories • Deletes and renames artifacts post-execution to destroy forensic evidence If you use axios, pin your version immediately and audit your lockfiles. Do not upgrade. — http://nitter.perennialte.ch/feross/status/2038807290422370479#m

## Siehe auch
- [[40_Areas/ai-news-index|Ai News Index]]
- [[40_Areas/dev-news-index|Dev News Index]]
- [[40_Areas/security-news-index|Security News Index]]
- [[_meta/index/MOC|Master of Ceremonies]]
