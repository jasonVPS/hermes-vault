---
title: "[AINews] not much happened today"
source: "Latent Space"
url: "https://www.latent.space/p/ainews-not-much-happened-today"
published: "2026-04-29"
scanned: "2026-05-17"
tags: [rss, latent_space, ai, security]
---

# [AINews] not much happened today

**Quelle:** [Latent Space](https://www.latent.space/p/ainews-not-much-happened-today)
**Veröffentlicht:** 2026-04-29
**Gescannt:** 2026-05-17

---

## Zusammenfassung

AINews: Weekday Roundups

[AINews] not much happened today

a quiet day.

Apr 29, 2026

∙ Paid

42

Share

When we made the AINews → Substack move, we committed to having Matt Levine style op-eds every day, but some days there just isn’t much going on and we will just say so - we are working on small essays around inference demand and multiagents, but today is not that day.

Interesting model releases from Nvidia Nemotron, Poolside, and Alec Radford, but it’s unclear any of them will stand the test of time. GPT-6 hype is beginning.

AI News for 4/27/2026-4/28/2026. We checked 12 subreddits, 544 Twitters and no further Discords. AINews’ website lets you search all past issues. As a reminder, AINews is now a section of Latent Space. You can opt in/out of email frequencies!

AI Twitter Recap

Inference Systems, vLLM 0.20, and the Hardware/Kernel Race Around DeepSeek V4

vLLM’s latest release is heavily about memory and MoE serving efficiency: vLLM v0.20.0 shipped with TurboQuant 2-bit KV cache for 4× KV capacity, FA4 re-enabled for MLA prefill on SM90+, a new vLLM IR foundation, fused RMSNorm for a reported 2.1% end-to-end latency improvement, plus support updates spanning DeepSeek V4 MegaMoE on Blackwell, Jetson Thor, ROCm, Intel XPU, and easier GB200/Grace-Blackwell setup. In parallel, SemiAnalysis highlighted early DeepSeek V4 Pro serving results on B200/B300/H200/GB200 disaggregated setups, claiming B300 can be up to 8× faster than H200 for this workload and pointing to upcoming vLLM 0.20 benchmarking with DeepGEMM MegaMoE, which fuses EP dispatch + EP combine + GEMMs + SwiGLU into a single mega-kernel.

DeepSeek support: several posts focused on serving tradeoffs: Jeremy Howard noted DeepSeek V4’s support for prefill as a capability many providers have dropped, while Maharshi pointed out the overheads of dynamic activation quantization, arguing that static quantization often wins on inference speed despite calibration cost. There was also growing interest in alternate stack portability: teortaxesTex argued DeepSeek is structurally moving away from CUDA lock-in via TileKernels, suggesting model vendors may increasingly optimize for heterogeneous or domestic accelerator fleets rather than NVIDIA-only deployment.

Open Model Releases: Poolside Laguna XS.2, NVIDIA Nemotron 3 Nano Omni, and TRELLIS.2

Poolside made its first public model release with an unusually deployment-friendly open-weight coder: @poolsideai announced Laguna XS.2, a 33B total / 3B active MoE coding model trained fully in-house, released under Apache 2.0, and advertised as able to run on a single GPU. Poolside’s broader release also included Laguna M.1 and an agent harness, emphasizing that the company trained from scratch on its own data, training infra, RL, and inference stack. Community summaries added more color: Aymeric Roucher described two coder models—225B/23B active and 33B/3B active—with hybrid attention, FP8 KV cache, and claimed performance near Qwen-3.5; Ollama …

## Notizen

-
## Siehe auch
- [[40_Areas/ai-news-index|Ai News Index]]
- [[40_Areas/security-news-index|Security News Index]]
- [[_meta/index/MOC|Master of Ceremonies]]
