---
title: "RT by @jeremyphoward: Excited to share our new paper: RoPE Distinguishes Neither Positions Nor Tokens in Long Contexts, Provably

LLMs often fail on inputs well within their advertised context lengths. We show that these failures are not merely engineering issues, but from intrinsic limitations of RoPE in long contexts.

Main finding: In long contexts, RoPE-based attention frequently assigns the same attention weight to a token even when it is moved to different positions. Similarly, it can assign the same attention weight to different tokens at the same position.

In this sense, RoPE attention fails to distinguish both where a token appears and what token appears there — hence the title.

We prove these results theoretically and verify them empirically. While the theoretical analysis focuses on a single attention head, we complement it with experiments on real multi-layer, multi-head LLMs.
The experiments confirm failures predicted by our theory: LLMs optimized for needle-in-a-haystack-style retrieval will inevitably struggle on a very simple task that asks for the k-th item in a list.

My personal takeaway: advertised context lengths should be interpreted with care. Future long-context LMs may require rethinking how position and token order are represented. With current architectures, agentic frameworks that break long contexts into shorter ones may be a more effective way to work around the intrinsic limitations of RoPE.

Paper: https://arxiv.org/abs/2605.15514

Huge congrats to my student Yufeng Du and others!"
source: "X - Jeremy Howard"
author: "Jeremy Howard"
url: "http://nitter.perennialte.ch/haopeng_uiuc/status/2056780781930860699#m"
published: "Tue, 19 May 2026 16:55:26 GMT"
scanned: "2026-05-19"
tags: [rss, x_-_jeremy_howard, twitter, x, social, ai, ai]
type: social
---

# RT by @jeremyphoward: Excited to share our new paper: RoPE Distinguishes Neither Positions Nor Tokens in Long Contexts, Provably

LLMs often fail on inputs well within their advertised context lengths. We show that these failures are not merely engineering issues, but from intrinsic limitations of RoPE in long contexts.

Main finding: In long contexts, RoPE-based attention frequently assigns the same attention weight to a token even when it is moved to different positions. Similarly, it can assign the same attention weight to different tokens at the same position.

In this sense, RoPE attention fails to distinguish both where a token appears and what token appears there — hence the title.

We prove these results theoretically and verify them empirically. While the theoretical analysis focuses on a single attention head, we complement it with experiments on real multi-layer, multi-head LLMs.
The experiments confirm failures predicted by our theory: LLMs optimized for needle-in-a-haystack-style retrieval will inevitably struggle on a very simple task that asks for the k-th item in a list.

My personal takeaway: advertised context lengths should be interpreted with care. Future long-context LMs may require rethinking how position and token order are represented. With current architectures, agentic frameworks that break long contexts into shorter ones may be a more effective way to work around the intrinsic limitations of RoPE.

Paper: https://arxiv.org/abs/2605.15514

Huge congrats to my student Yufeng Du and others!

**Quelle:** [X - Jeremy Howard](http://nitter.perennialte.ch/haopeng_uiuc/status/2056780781930860699#m)  
**Autor:** Jeremy Howard  
**Veröffentlicht:** Tue, 19 May 2026 16:55:26 GMT  
**Gescannt:** 2026-05-19

---

## Inhalt

RT by @jeremyphoward: Excited to share our new paper: RoPE Distinguishes Neither Positions Nor Tokens in Long Contexts, Provably

LLMs often fail on inputs well within their advertised context lengths. We show that these failures are not merely engineering issues, but from intrinsic limitations of RoPE in long contexts.

Main finding: In long contexts, RoPE-based attention frequently assigns the same attention weight to a token even when it is moved to different positions. Similarly, it can assign the same attention weight to different tokens at the same position.

In this sense, RoPE attention fails to distinguish both where a token appears and what token appears there — hence the title.

We prove these results theoretically and verify them empirically. While the theoretical analysis focuses on a single attention head, we complement it with experiments on real multi-layer, multi-head LLMs.
The experiments confirm failures predicted by our theory: LLMs optimized for needle-in-a-haystack-style retrieval will inevitably struggle on a very simple task that asks for the k-th item in a list.

My personal takeaway: advertised context lengths should be interpreted with care. Future long-context LMs may require rethinking how position and token order are represented. With current architectures, agentic frameworks that break long contexts into shorter ones may be a more effective way to work around the intrinsic limitations of RoPE.

Paper: https://arxiv.org/abs/2605.15514

Huge congrats to my student Yufeng Du and others!

## Siehe auch
- [[40_Areas/ai-news-index|Ai News Index]]
- [[_meta/index/MOC|Master of Ceremonies]]
