---
title: "[AINews] DeepSeek V4 Pro (1.6T-A49B) and Flash (284B-A13B), Base and Instruct — runnable on Huawei Ascend chips"
source: "Latent Space"
url: "https://www.latent.space/p/ainews-deepseek-v4-pro-16t-a49b-and"
published: "2026-04-25"
scanned: "2026-05-17"
tags: [rss, latent_space, ai, security]
---

# [AINews] DeepSeek V4 Pro (1.6T-A49B) and Flash (284B-A13B), Base and Instruct — runnable on Huawei Ascend chips

**Quelle:** [Latent Space](https://www.latent.space/p/ainews-deepseek-v4-pro-16t-a49b-and)
**Veröffentlicht:** 2026-04-25
**Gescannt:** 2026-05-17

---

## Zusammenfassung

AINews: Weekday Roundups

[AINews] DeepSeek V4 Pro (1.6T-A49B) and Flash (284B-A13B), Base and Instruct — runnable on Huawei Ascend chips

The prodigal Tiger returns... but is no longer the benchmarks leader.

Apr 25, 2026

∙ Paid

52

Share

After a couple months’ delay and lots of speculation, DeepSeek finally released the heavily anticipated DSV4, the first major version model since DSV3 (Dec 2024) and DSR1 (Jan 2025). It brings the DeepSeek family up in line with Kimi K2.6, the current open model leader, and Xiaomi Mimo 2.5, a lesser known family released 2 days ago.

The DSV4 family is roughly a Gemini 3.1, GPT 5.4, Opus 4.6 level model, up to 1.6T MOE withtrained on 32T tokens with FP4, with 1M token context (supported by their new Compressed Sparse Attention (CSA) and Heavily Compressed Attention (HCA) techniques), and incredibly rarely, they released both the Base and Instruct versions - surely setting the stage for a possible “DeepSeek R2” in future, though this one already has reasoning effort.

The technical report is a typically dense 58 pages, demonstrating training and inference insights and improvements from the Manifold Constrained Hyper-Connections (mHC) paper they released in January, continued usage of Moonshot’s Muon, and CSA/HCA’s overall INCREDIBLE efficiency improvements on DeepSeek 3.2-Exp’s already impressive Sparse Attention - at 1M tokens, requiring only 27% of FLOPs and 10% of KV cache memory compared with DeepSeek-V3.2:

The geopolitical backdrop behind the Huawei CANN compatibility is DeepSeek weaning dependence off export-controlled NVIDIA/CUDA chips — Ascends are still a quarter the supply of H100s, but this is an important milestone for Chinese total independence.

AI News for 4/23/2026-4/24/2026. We checked 12 subreddits, 544 Twitters and no further Discords. AINews’ website lets you search all past issues. As a reminder, AINews is now a section of Latent Space. You can opt in/out of email frequencies!

AI Twitter Recap

Top Story: DeepSeek V4

DeepSeek released DeepSeek-V4 Pro and DeepSeek-V4 Flash, its first major architecture refresh since V3 and first clear two-tier lineup, with 1M-token context, hybrid reasoning/non-reasoning modes, an MIT license, and a technical report detailed enough that multiple researchers called it one of the most important or best-written model papers of the year. Across the reactions, the factual consensus is that V4 materially advances open-weight long-context and agentic coding performance while remaining somewhat behind the top closed frontier models overall. Independent benchmarkers place V4 Pro around the #2 open-weights tier, roughly near Kimi K2.6 / GLM-5.1 / strong Claude Sonnet-class to Opus-ish depending on benchmark and mode, with especially strong long-context and agentic performance; opinions diverge on how close it is to GPT-5.x / Opus 4.7 and on whether this is “democratizing” progress or an architecture so complex that few open labs can realistically reproduce it. …

## Notizen

-
## Siehe auch
- [[40_Areas/ai-news-index|Ai News Index]]
- [[40_Areas/security-news-index|Security News Index]]
- [[_meta/index/MOC|Master of Ceremonies]]
