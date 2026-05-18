---
title: "Scaling massive monolithic LLMs continues to yield incredible results. But to truly unlock their ceiling, the next frontier is test-time compute and dynamic orchestration.

Nature solves complex problems through collaborative ecosystems. In our new #ICLR2026 paper, we evolved a small coordinator. Instead of competing with the monoliths, it orchestrates them. It learns to dynamically assign Thinker, Worker, and Verifier roles to a pool of frontier models—combining their strengths to hit SOTA on LiveCodeBench.

This research is part of the engine powering our new product: Sakana Fugu https://sakana.ai/fugu-beta/ 🐡"
source: "X - David Ha"
author: "David Ha"
url: "http://nitter.perennialte.ch/hardmaru/status/2048192503552335923#m"
published: "Sun, 26 Apr 2026 00:08:41 GMT"
scanned: "2026-05-18"
tags: [rss, x_-_david_ha, twitter, x, social, ai, ai, dev]
type: social
---

# Scaling massive monolithic LLMs continues to yield incredible results. But to truly unlock their ceiling, the next frontier is test-time compute and dynamic orchestration.

Nature solves complex problems through collaborative ecosystems. In our new #ICLR2026 paper, we evolved a small coordinator. Instead of competing with the monoliths, it orchestrates them. It learns to dynamically assign Thinker, Worker, and Verifier roles to a pool of frontier models—combining their strengths to hit SOTA on LiveCodeBench.

This research is part of the engine powering our new product: Sakana Fugu https://sakana.ai/fugu-beta/ 🐡

**Quelle:** [X - David Ha](http://nitter.perennialte.ch/hardmaru/status/2048192503552335923#m)  
**Autor:** David Ha  
**Veröffentlicht:** Sun, 26 Apr 2026 00:08:41 GMT  
**Gescannt:** 2026-05-18

---

## Inhalt

Scaling massive monolithic LLMs continues to yield incredible results. But to truly unlock their ceiling, the next frontier is test-time compute and dynamic orchestration. Nature solves complex problems through collaborative ecosystems. In our new #ICLR2026 paper, we evolved a small coordinator. Instead of competing with the monoliths, it orchestrates them. It learns to dynamically assign Thinker, Worker, and Verifier roles to a pool of frontier models—combining their strengths to hit SOTA on LiveCodeBench. This research is part of the engine powering our new product: Sakana Fugu sakana.ai/fugu-beta/ 🐡 Sakana AI (@SakanaAILabs) What if instead of building one giant AI, we evolved a coordinator to orchestrate a diverse team of specialized AIs? 🐟 Excited to share our new paper: “TRINITY: An Evolved LLM Coordinator”, published as a conference paper at #ICLR2026 ! Paper: arxiv.org/abs/2512.04695 In nature, complex problems are rarely solved by a single monolithic entity, but rather by the coordinated efforts of specialized individuals working together. Yet, modern AI development is heavily focused on endlessly scaling up single, massive monolithic models, yielding diminishing returns. While model merging offers a way to combine different skills, it is often impractical due to mismatched neural architectures and the closed-source nature of top-performing models. To address this, we took a macro-level approach: test-time model composition. We introduce TRINITY, a system that fuses the complementary strengths of diverse, state-of-the-art models without needing to modify their underlying weights. TRINITY processes queries over multiple turns. At each step, a lightweight coordinator assigns one of three distinct roles to an LLM from its available pool: 1/ Thinker: Devises high-level strategies and analyzes the current state. 2/ Worker: Executes concrete problem-solving steps. 3/ Verifier: Evaluates if the current solution is complete and correct. By dynamically assigning these roles, the coordinator effectively offloads complex reasoning and skill execution onto the external models. What makes TRINITY unique is its extreme efficiency. The coordinator relies on the hidden states of a compact language model and a small routing head. In total, it has fewer than 20K learnable parameters. Training this system presented a massive challenge. Traditional Reinforcement Learning (REINFORCE) failed because the gradients had a low signal-to-noise ratio due to binary rewards and weak parameter coupling. Imitation learning (Supervised Fine-Tuning) was ruled out because generating multi-turn labels is prohibitively expensive. Our solution? We turned to nature-inspired algorithms. We optimized the coordinator using a derivative-free evolutionary algorithm. We found that evolution is uniquely suited to optimize this tight, high-dimensional coordination problem where traditional gradient-based methods fail. The results are very promising. In our experiments, TRINITY consistently outperforms existing multi-agent methods and individual models across various benchmarks. At the time of publication, it set a new state-of-the-art record on LiveCodeBench, achieving an 86.2% pass@1 score. More importantly, it demonstrated incredible generalization. Without any retraining, TRINITY transferred zero-shot to four unseen tasks (AIME, BigCodeBench, MT-Bench, and GPQA). On average, the evolved coordinator surpassed every individual constituent model in its pool, including GPT-5, Gemini 2.5-Pro, and Claude-4-Sonnet (the top frontier models available at the time of our #ICLR2026 submission last year). This work is central to Sakana AI's vision. We believe the future of AI isn't just about scaling monolithic models, but engineering collaborative, diverse AI ecosystems that can adapt and combine their strengths. We invite the community to read the paper and explore these ideas! Paper: arxiv.org/abs/2512.04695 OpenReview: openreview.net/forum?id=5HaR… This foundational research is part of the core engine powering our multi-agent product: Sakana Fugu 🐡👇 — http://nitter.perennialte.ch/SakanaAILabs/status/2048181386868293639#m

## Siehe auch
- [[40_Areas/ai-news-index|Ai News Index]]
- [[40_Areas/dev-news-index|Dev News Index]]
- [[_meta/index/MOC|Master of Ceremonies]]
