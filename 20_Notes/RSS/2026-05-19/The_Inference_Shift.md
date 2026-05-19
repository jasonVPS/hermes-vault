---
title: "The Inference Shift"
source: "Stratechery"
url: "https://stratechery.com/2026/the-inference-shift/"
published: "2026-05-11"
scanned: "2026-05-19"
tags: [rss, stratechery, capture, tech]
type: capture
---

# The Inference Shift

**Quelle:** [Stratechery](https://stratechery.com/2026/the-inference-shift/)
**Veröffentlicht:** 2026-05-11
**Gescannt:** 2026-05-19

---

## Zusammenfassung

(https://stratechery.com/2026/the-inference-shift/) The Inference Shift

Monday, May 11, 2026

 (https://stratechery.com/2026/the-inference-shift/) Listen to Podcast

Listen to this post:

 (https://stratechery.com/wp-json/passport/v1/oauth/authlogin?signup_redirect_uri=https%3A%2F%2Fstratechery.com%2Fverify-your-email%2F) Log in to listen

If you were looking for the ideal time to IPO, being a chip company in May 2026 is hard to beat.  (https://www.reuters.com/legal/transactional/cerebras-raise-ipo-price-range-150-160-demand-surges-sources-say-2026-05-10/) Reuters reported over the weekend:

Cerebras Systems is set to raise the size and price of its initial public offering as soon as Monday, as demand for the artificial intelligence chipmaker’s shares continues to climb, two people familiar with the matter told Reuters on Sunday. The company is considering a new IPO price range of $150-$160 a share, up from $115-$125 a share, and raising the number of shares marketed to 30 million from 28 million, said the sources, who asked not to be identified because the information isn’t public yet.

The fundamental driver of the ongoing surge in semiconductor stocks is, of course, AI, particularly the realization that  (https://stratechery.com/2026/agents-over-bubbles/) agents are going to need a lot of compute. What Cerebras represents, however, is something broader: while the compute story for AI has been largely about GPUs, particularly from Nvidia, the future is going to look increasingly heterogeneous.

The GPU Era

The story of how Graphics Processing Units became the center of AI is a well-trodden one, but in brief:

Just as drawing pixels on a computer screen was a parallel process, which meant there was a direct connection between the number of processing units and graphics speed, making AI-related calculations was a parallel process, which meant there was a direct connection between the number of processing units and calculation speed.

Nvidia enabled this dual-usage by making its graphics processors programmable, and created an entire software ecosystem called CUDA to make this programming accessible.

The big difference between graphics and AI has been the size of the problem being solved — models are a lot bigger than video game textures — which has led to a dramatic expansion in high-bandwidth memory (HBM) per GPU, and dramatic innovations in terms of chip-to-chip networking to allow multiple chips to work together as one addressable system. Nvidia has been the leader in both.

The number one use case for GPUs has been training, which stresses the third point in particular. While the calculations within each training step are massively parallel, the steps themselves are serial: every GPU has to share its results with every other GPU before the next step can begin. This is why a trillion-parameter model needs to fit in the aggregate memory of tens of thousands of GPUs that can communicate as one system. Nvidia dominates both problem spaces, …

## Notizen

-

## Siehe auch
- [[40_Areas/tech-index|Tech News Index]]
- [[_meta/index/MOC|Master of Ceremonies]]
