---
title: "RT by @jeremyphoward: Today we release Token Superposition Training (TST), a modification to the standard LLM pretraining loop that produces a 2-3× wall-clock speedup at matched FLOPs without changing the model architecture, optimizer, tokenizer, or training data.

During the first third of training, the model reads and predicts contiguous bags of tokens, averaging their embeddings on the input side and predicting the next bag with a modified cross-entropy on the output side. For the remainder of the run, it trains normally on next-token prediction. The inference-time model is identical to one produced by conventional pretraining.

Validated at 270M, 600M, and 3B dense scales, and at 10B-A1B MoE.

The work on TST was led by @bloc97_, @gigant_theo, and @theemozilla."
source: "X - Jeremy Howard"
author: "Jeremy Howard"
url: "http://nitter.perennialte.ch/NousResearch/status/2054610062836892054#m"
published: "Wed, 13 May 2026 17:09:46 GMT"
scanned: "2026-05-18"
tags: [rss, x_-_jeremy_howard, twitter, x, social, ai, ai]
type: social
---

# RT by @jeremyphoward: Today we release Token Superposition Training (TST), a modification to the standard LLM pretraining loop that produces a 2-3× wall-clock speedup at matched FLOPs without changing the model architecture, optimizer, tokenizer, or training data.

During the first third of training, the model reads and predicts contiguous bags of tokens, averaging their embeddings on the input side and predicting the next bag with a modified cross-entropy on the output side. For the remainder of the run, it trains normally on next-token prediction. The inference-time model is identical to one produced by conventional pretraining.

Validated at 270M, 600M, and 3B dense scales, and at 10B-A1B MoE.

The work on TST was led by @bloc97_, @gigant_theo, and @theemozilla.

**Quelle:** [X - Jeremy Howard](http://nitter.perennialte.ch/NousResearch/status/2054610062836892054#m)  
**Autor:** Jeremy Howard  
**Veröffentlicht:** Wed, 13 May 2026 17:09:46 GMT  
**Gescannt:** 2026-05-18

---

## Inhalt

RT by @jeremyphoward: Today we release Token Superposition Training (TST), a modification to the standard LLM pretraining loop that produces a 2-3× wall-clock speedup at matched FLOPs without changing the model architecture, optimizer, tokenizer, or training data.

During the first third of training, the model reads and predicts contiguous bags of tokens, averaging their embeddings on the input side and predicting the next bag with a modified cross-entropy on the output side. For the remainder of the run, it trains normally on next-token prediction. The inference-time model is identical to one produced by conventional pretraining.

Validated at 270M, 600M, and 3B dense scales, and at 10B-A1B MoE.

The work on TST was led by @bloc97_, @gigant_theo, and @theemozilla.

## Siehe auch
- [[40_Areas/ai-news-index|Ai News Index]]
- [[_meta/index/MOC|Master of Ceremonies]]
