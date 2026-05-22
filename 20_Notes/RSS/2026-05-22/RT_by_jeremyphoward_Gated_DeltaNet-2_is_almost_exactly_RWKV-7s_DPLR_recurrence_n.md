---
title: "RT by @jeremyphoward: Gated DeltaNet-2 is almost exactly RWKV-7's DPLR recurrence, not acknowledging the elephant in the room 🙂"
source: "X - Jeremy Howard"
author: "Jeremy Howard"
url: "http://nitter.perennialte.ch/BlinkDL_AI/status/2057693097845493992#m"
published: "Fri, 22 May 2026 05:20:39 GMT"
scanned: "2026-05-22"
tags: [rss, x_-_jeremy_howard, twitter, x, social, ai, ai, dev]
type: social
---

# RT by @jeremyphoward: Gated DeltaNet-2 is almost exactly RWKV-7's DPLR recurrence, not acknowledging the elephant in the room 🙂

**Quelle:** [X - Jeremy Howard](http://nitter.perennialte.ch/BlinkDL_AI/status/2057693097845493992#m)  
**Autor:** Jeremy Howard  
**Veröffentlicht:** Fri, 22 May 2026 05:20:39 GMT  
**Gescannt:** 2026-05-22

---

## Inhalt

Gated DeltaNet-2 is almost exactly RWKV-7's DPLR recurrence, not acknowledging the elephant in the room 🙂 Ali Hatamizadeh (@ahatamiz1) Gated DeltaNet-2 is here. 🚀 🔥 New paper: Gated DeltaNet-2: Decoupling Erase and Write in Linear Attention Gated DeltaNet-2 outperforms KDA and Mamba-3, the latest and best recurrent architectures, head to head at 1.3B. 🏆 💡 Here's the idea behind it: Linear attention squeezes an unbounded KV cache into a fixed-size recurrent state. The hard part isn't just what to forget, it's how to edit that memory without scrambling the associations already in it. Prior delta-rule models like Gated DeltaNet and KDA use one scalar gate to do two jobs at once: erasing old content and writing new content. But these two decisions act on different axes of the state, so tying them together is a real limitation. Gated DeltaNet-2 decouples them. ✂️ a channel-wise erase gate b_t picks which key-side coordinates to read and remove ✍️ a channel-wise write gate w_t picks which value-side coordinates to commit 🔁 recovers KDA when both gates collapse to a scalar, and Gated DeltaNet when the decay collapses too ⚡ still trains fast: chunkwise WY algorithm with gate-aware backward, fused in Triton 📊 Results: We train 1.3B models on 100B tokens of FineWeb-Edu, matched in recurrent state size, against Mamba-2, Gated DeltaNet, KDA, and Mamba-3. Best average on language modeling + commonsense reasoning, in both recurrent and hybrid settings Biggest gains on long-context RULER retrieval. S-NIAH-3 jumps from 63 to 90 over KDA, and multi-key needle retrieval climbs from 28 to 38 Joint work with @YejinChoinka and @jankautz . 📄 Paper: shorturl.at/AAlVb 💻 Code: github.com/NVlabs/GatedDelta… #LinearAttention #StateSpaceModels #Mamba #LLM — http://nitter.perennialte.ch/ahatamiz1/status/2057586630450610673#m

## Siehe auch
- [[40_Areas/ai-news-index|Ai News Index]]
- [[40_Areas/dev-news-index|Dev News Index]]
- [[_meta/index/MOC|Master of Ceremonies]]
