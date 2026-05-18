---
title: "For the past few years, humans have been doing “prompt engineering” to coax the best performance out of different LLMs. In this work, we explored what happens if we train an AI to do that job instead.

By training a Conductor model with RL, we found that it naturally learns to write highly effective, custom instructions for a whole pool of other models. It essentially learns to ‘manage’ them in natural language.

What surprised me most was how it dynamically adapts. For simple factual questions, it just queries one model. But for hard coding problems, it autonomously spins up a whole pipeline of planners, coders, and verifiers.

Really excited to see where this paradigm of “AI managing AI” goes next, especially as we start moving from single-agent chain-of-thought to multi-agent “chain-of-command”.

Link to our #ICLR2026 paper: https://arxiv.org/abs/2512.04388

Along with our TRINITY paper which we announced earlier, this work also powers our new multi-agent system: Sakana Fugu (https://sakana.ai/fugu-beta) 🐡"
source: "X - David Ha"
author: "David Ha"
url: "http://nitter.perennialte.ch/hardmaru/status/2048778095935795338#m"
published: "Mon, 27 Apr 2026 14:55:37 GMT"
scanned: "2026-05-18"
tags: [rss, x_-_david_ha, twitter, x, social, ai, ai, dev]
type: social
---

# For the past few years, humans have been doing “prompt engineering” to coax the best performance out of different LLMs. In this work, we explored what happens if we train an AI to do that job instead.

By training a Conductor model with RL, we found that it naturally learns to write highly effective, custom instructions for a whole pool of other models. It essentially learns to ‘manage’ them in natural language.

What surprised me most was how it dynamically adapts. For simple factual questions, it just queries one model. But for hard coding problems, it autonomously spins up a whole pipeline of planners, coders, and verifiers.

Really excited to see where this paradigm of “AI managing AI” goes next, especially as we start moving from single-agent chain-of-thought to multi-agent “chain-of-command”.

Link to our #ICLR2026 paper: https://arxiv.org/abs/2512.04388

Along with our TRINITY paper which we announced earlier, this work also powers our new multi-agent system: Sakana Fugu (https://sakana.ai/fugu-beta) 🐡

**Quelle:** [X - David Ha](http://nitter.perennialte.ch/hardmaru/status/2048778095935795338#m)  
**Autor:** David Ha  
**Veröffentlicht:** Mon, 27 Apr 2026 14:55:37 GMT  
**Gescannt:** 2026-05-18

---

## Inhalt

For the past few years, humans have been doing “prompt engineering” to coax the best performance out of different LLMs. In this work, we explored what happens if we train an AI to do that job instead. By training a Conductor model with RL, we found that it naturally learns to write highly effective, custom instructions for a whole pool of other models. It essentially learns to ‘manage’ them in natural language. What surprised me most was how it dynamically adapts. For simple factual questions, it just queries one model. But for hard coding problems, it autonomously spins up a whole pipeline of planners, coders, and verifiers. Really excited to see where this paradigm of “AI managing AI” goes next, especially as we start moving from single-agent chain-of-thought to multi-agent “chain-of-command”. Link to our #ICLR2026 paper: arxiv.org/abs/2512.04388 Along with our TRINITY paper which we announced earlier, this work also powers our new multi-agent system: Sakana Fugu ( sakana.ai/fugu-beta ) 🐡 Sakana AI (@SakanaAILabs) Introducing our new work: “Learning to Orchestrate Agents in Natural Language with the Conductor” accepted at #ICLR2026 arxiv.org/abs/2512.04388 What if we trained an AI not to solve problems directly, but to act as a manager that delegates tasks to a diverse team of other AIs? To solve complex tasks, humans rarely work alone; we form teams, delegate, and communicate. Yet, multi-agent AI systems currently rely heavily on rigid, human-designed workflows or simple routers that just pick a single model. We wanted an AI that could dynamically build its own team. We trained a 7B Conductor model using Reinforcement Learning to orchestrate a pool of frontier models (including GPT-5, Gemini, Claude, and open-source models available during the period leading up to ICLR 2026). Instead of executing code, the Conductor outputs a collaborative workflow in natural language. For any given question, the Conductor specifies: 1/ Which agent to call 2/ What specific subtask to give them (acting as an expert prompt engineer) 3/ What previous messages they can see in their context window Through pure end-to-end reward maximization, amazing behaviors emerged. The Conductor learned to adapt to task difficulty: it 1-shots simple factual questions, but autonomously spins up complex planner-executor-verifier pipelines for hard coding problems. The results are very promising: The 7B Conductor surpasses the performance of every individual worker model in its pool, setting new records on LiveCodeBench (83.9%) and GPQA-Diamond (87.5%) at the time of publication. It also significantly outperforms expensive multi-agent baselines like Mixture-of-Agents at a fraction of the cost. One of our favorite features: Recursive Test-Time Scaling! By allowing the Conductor to select itself as a worker, it reads its own team's prior output, realizes if it failed, and spins up a corrective workflow on the fly. This opens a new axis for scaling compute during inference. This research proves that language models can become elite meta-prompt engineers, dynamically harnessing collective intelligence. Alongside our TRINITY research which we announced a few days earlier, this foundational research powers our new multi-agent system: Sakana Fugu! ( sakana.ai/fugu-beta ) 🐡 OpenReview: openreview.net/forum?id=U23A… (ICLR 2026) — http://nitter.perennialte.ch/SakanaAILabs/status/2048777689763639741#m

## Siehe auch
- [[40_Areas/ai-news-index|Ai News Index]]
- [[40_Areas/dev-news-index|Dev News Index]]
- [[_meta/index/MOC|Master of Ceremonies]]
