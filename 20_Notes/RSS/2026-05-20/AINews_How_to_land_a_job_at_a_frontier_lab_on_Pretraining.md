---
title: "[AINews] How to land a job at a frontier lab (on Pretraining)"
source: "Latent Space"
url: "https://www.latent.space/p/ainews-how-to-land-a-job-at-a-frontier"
published: "2026-05-19"
scanned: "2026-05-20"
tags: [rss, latent_space, capture, ai]
type: capture
---

# [AINews] How to land a job at a frontier lab (on Pretraining)

**Quelle:** [Latent Space](https://www.latent.space/p/ainews-how-to-land-a-job-at-a-frontier)
**Veröffentlicht:** 2026-05-19
**Gescannt:** 2026-05-20

---

## Zusammenfassung

(https://www.latent.space/s/ainews/?utm_source=substack&utm_medium=menu) AINews: Weekday Roundups

[AINews] How to land a job at a frontier lab (on Pretraining)

a quiet day before google i/o lets us amplify a notable blogpost

May 19, 2026

∙ Paid

39

Share

It is the day before Google I/O, when the next major Gemini releases are expected to be previewed, and it will probably be a quiet week from competitors, though  (https://news.ycombinator.com/item?id=48182281) Anthropic and  (https://news.ycombinator.com/item?id=48182754) OpenAI both had minor wins today, and Cursor shipped their  (https://news.ycombinator.com/item?id=48182516) first SpaceXAI model with some nice detail on synthetic data/reward hacking and continued pretraining with  (https://news.smol.ai/issues/25-07-11-kimi-k2) Muon. However the probable lasting title story candidate from today will be Vlad Feinberg’s (understandably Google/TPU centric)  (https://vladfeinberg.com/2026/05/10/how-to-land-a-job-at-a-frontier-lab.html) notes on job preparation, specifically on Pretraining:

 (https://substackcdn.com/image/fetch/$s_!W6LK!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F2e69d902-1d29-4e8c-834c-41e83b07223f_1194x604.png) 

Specifically he references last year’s  (https://jax-ml.github.io/scaling-book/) Scaling handbook from DeepMind, and kernel work is an important part:

The biggest bottleneck and innermost loop of all LLM work is performance work that makes abstract, logical changes to the LLM practical to run. Every project needs people who can tune the LLMs at the kernel level. It is a skill you can pick up and is the most direct path into the labs.

There’s a surprise mention of DSLs for kernel dev, of which there is a  (https://x.com/yaroslavvb/status/2053669022684877076) concise history:
 (https://x.com/yaroslavvb/status/2053669022684877076) 

Yaroslav Bulatov@yaroslavvb

What is the reason for proliferation of DSLs in the last year? 

2:50 AM · May 11, 2026 · 6.93K Views

7 Replies · 72 Likes

For someone at this level of the stack, surprisingly he also calls out Agent Work like  (https://www.latent.space/p/ainews-ai-engineer-worlds-fair-autoresearch) autoresearch and AlphaEvolve. He ends with a surprisingly simple exercise:
 (https://x.com/swyx/status/2056478391008977404) 

swyx🛬 SFO@swyx

this seems quite doable in the space of a single 2-3 hour workshop — any brave soul want to try to livecode this for people as a learning exercise?

Vlad Feinberg @FeinbergVlad

How to land a job at a frontier lab 

https://t.co/oHIqLgBMbC

8:53 PM · May 18, 2026 · 61.6K Views

22 Replies · 11 Reposts · 408 Likes

But the real hiring test is in the bottom paragraphs:

Derive Chinchilla laws for this; see how they differ for dense vs MoE architectures. 

Code your solution from scratch in jax by hand if you actually want the learning experience.

Next, assuming you used jax.lax.ragged_dot for the MoE layer; write a pallas …

## Notizen

-

## Siehe auch
- [[40_Areas/ai-news-index|Ai News Index]]
- [[_meta/index/MOC|Master of Ceremonies]]
