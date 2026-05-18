---
title: "For years, voice AI has been stuck in a rigid loop: think, then speak. But real human conversation is messy, overlapping, and asynchronous.

In our new #ICASSP2026 work, we built a tandem architecture that shifts the paradigm to “speak while thinking.” A fast speech model starts replying instantly, while a backend LLM runs in parallel to inject deep knowledge on the fly.

It’s a completely different way to approach conversational AI, making it feel remarkably more alive.

Blog: https://pub.sakana.ai/kame/ 🐢"
source: "X - David Ha"
author: "David Ha"
url: "http://nitter.perennialte.ch/hardmaru/status/2049545060681933002#m"
published: "Wed, 29 Apr 2026 17:43:15 GMT"
scanned: "2026-05-18"
tags: [rss, x_-_david_ha, twitter, x, social, ai, ai]
type: social
---

# For years, voice AI has been stuck in a rigid loop: think, then speak. But real human conversation is messy, overlapping, and asynchronous.

In our new #ICASSP2026 work, we built a tandem architecture that shifts the paradigm to “speak while thinking.” A fast speech model starts replying instantly, while a backend LLM runs in parallel to inject deep knowledge on the fly.

It’s a completely different way to approach conversational AI, making it feel remarkably more alive.

Blog: https://pub.sakana.ai/kame/ 🐢

**Quelle:** [X - David Ha](http://nitter.perennialte.ch/hardmaru/status/2049545060681933002#m)  
**Autor:** David Ha  
**Veröffentlicht:** Wed, 29 Apr 2026 17:43:15 GMT  
**Gescannt:** 2026-05-18

---

## Inhalt

For years, voice AI has been stuck in a rigid loop: think, then speak. But real human conversation is messy, overlapping, and asynchronous. In our new #ICASSP2026 work, we built a tandem architecture that shifts the paradigm to “speak while thinking.” A fast speech model starts replying instantly, while a backend LLM runs in parallel to inject deep knowledge on the fly. It’s a completely different way to approach conversational AI, making it feel remarkably more alive. Blog: pub.sakana.ai/kame/ 🐢 Sakana AI (@SakanaAILabs) We’re excited to introduce KAME: Tandem Architecture for Enhancing Knowledge in Real-Time Speech-to-Speech Conversational AI, accepted at #ICASSP2026 ! 🐢 Blog pub.sakana.ai/kame/ Paper arxiv.org/abs/2510.02327 Can a speech AI think deeply without pausing to process? In real conversation, we don’t wait until we’ve fully worked out what we want to say—we start talking, and our thoughts catch up as the sentence unfolds. Fast speech-to-speech models achieve this, but their reasoning tends to stay shallow. Cascaded pipelines that route through a knowledgeable LLM are smarter, but the added latency breaks the flow—they fall back to "think, then speak." In our new paper, we propose a way to break this trade-off. We call it KAME (Turtle in Japanese). A speech-to-speech model handles the fast response loop and starts replying immediately. In parallel, a backend LLM runs asynchronously, generating response candidates that are continuously injected as "oracle" signals in real time. This shifts the AI paradigm from "think, then speak" to "speak while thinking." The backend LLM is completely swappable. You can plug in GPT-4.1, Claude Opus, or Gemini 2.5 Flash depending on the task without changing the frontend. In our experiments, Claude tended to score higher on reasoning, while GPT did better on humanities questions. Try the model yourself here: huggingface.co/SakanaAI/kame Video — http://nitter.perennialte.ch/SakanaAILabs/status/2049544945233764755#m

## Siehe auch
- [[40_Areas/ai-news-index|Ai News Index]]
- [[_meta/index/MOC|Master of Ceremonies]]
