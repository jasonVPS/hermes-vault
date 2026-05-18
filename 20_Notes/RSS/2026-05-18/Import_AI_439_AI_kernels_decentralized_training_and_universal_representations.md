---
title: "Import AI 439: AI kernels; decentralized training; and universal representations"
source: "Import AI"
url: "https://importai.substack.com/p/import-ai-439-ai-kernels-decentralized"
published: "2026-01-05"
scanned: "2026-05-18"
tags: [rss, import_ai, capture, ai]
type: capture
---

# Import AI 439: AI kernels; decentralized training; and universal representations

**Quelle:** [Import AI](https://importai.substack.com/p/import-ai-439-ai-kernels-decentralized)
**Veröffentlicht:** 2026-01-05
**Gescannt:** 2026-05-18

---

## Zusammenfassung

Import AI 439: AI kernels; decentralized training; and universal representations 

How might a hypothetical superintelligence represent a soul to itself?

 (https://substack.com/@importai) 

 (https://substack.com/@importai) Jack Clark

Jan 05, 2026

45

6

2

Share

Welcome to Import AI, a newsletter about AI research. Import AI runs on arXiv and feedback from readers. If you’d like to support this, please subscribe.

Subscribe

Facebook uses GPT, Claude, and Llama to write its own kernels:

…LLM-driven infrastructure optimization at the hyperscale…

Facebook researchers have published details on KernelEvolve, a software system which uses AI to automate the design of new kernels to optimize AI models for serving ads on the company’s network of web platforms. KernelEvolve is a neat example of how AI systems have got good enough to automate and speed up parts of AI development - here, the design of kernels to optimize inference of hundreds of different models running on multiple chip architectures.

What KernelEvolve is: The software is “designed to take kernel specifications as input and automate the process of kernel generation and optimization for recommendation model across heterogeneous hardware architectures through multiple programming abstractions, including Triton, CuTe DSL, and low-level hardware diagnostic languages, spanning the full hardware-software optimization stack”.

How it works: The core of the software is a system to take in a user request (e.g, “Generate a Triton kernel for MTIA v3”) which then goes through a mixture of internal (Llama, CWM) and external (GPT, Claude) language models, which then produce candidate kernels that get evaluated through a variety of tools and, if they’re good, are added to an external knowledge database which then gets used to further improve future prompts.

It works well: By using this software, Facebook says it has cut the development time of new kernels “from weeks to hours”, and in production tests has yielded kernels on par with hand-designed ones, and in some cases has delivered performance improves of up to 17 times above existing PyTorch baselines. Kernels built using this software have been deployed across NVIDIA GPUs, AMD GPUs, and Meta’s own custom MTIA chips.

    “KernelEvolve achieves substantial speedups spanning LLM inference workloads (Llama-3.1-8B: Vanilla Attention 4.6×, SDPA-MLP 3.3×), convolutional transformers (conv1d: 6.5×, conv2d: 4.7×), memory-bound data preprocessing operators critical for model enablement (MapId: 4.1×, MBDT: 9.3×, Batch Event Truncate: 9.8×), compute-intensive fusion kernels in ranking models (WuKong Optimized FM: 4.0×, InterFormer PFFN: 2.5×), MTIA-specific optimizations (RMSNorm 2D backward: 17×), and retrieval operations (Sparse Inverted Index: 1.25×)”, Facebook writes.

Saturates KernelBench: “We validate KernelEvolve on the publicly-available KernelBench suite, achieving 100% pass rate on all 250 problems across three difficulty levels, and 160 …

## Notizen

-

## Siehe auch
- [[40_Areas/ai-news-index|Ai News Index]]
- [[_meta/index/MOC|Master of Ceremonies]]
