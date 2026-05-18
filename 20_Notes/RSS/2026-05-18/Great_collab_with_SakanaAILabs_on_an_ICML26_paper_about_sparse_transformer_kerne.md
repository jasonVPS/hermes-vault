---
title: "Great collab with @SakanaAILabs on an #ICML26 paper about sparse transformer kernels + formats optimized for modern NVIDIA GPU execution.

• TwELL sparse packing
• Fused CUDA kernels
• 20%+ inference/training speedups at scale

Paper + code below 👇"
source: "X - NVIDIA AI"
author: "NVIDIA"
url: "http://nitter.perennialte.ch/NVIDIAAI/status/2052801759777874207#m"
published: "Fri, 08 May 2026 17:24:13 GMT"
scanned: "2026-05-18"
tags: [rss, x_-_nvidia_ai, twitter, x, social, ai, ai, dev]
type: social
---

# Great collab with @SakanaAILabs on an #ICML26 paper about sparse transformer kernels + formats optimized for modern NVIDIA GPU execution.

• TwELL sparse packing
• Fused CUDA kernels
• 20%+ inference/training speedups at scale

Paper + code below 👇

**Quelle:** [X - NVIDIA AI](http://nitter.perennialte.ch/NVIDIAAI/status/2052801759777874207#m)  
**Autor:** NVIDIA  
**Veröffentlicht:** Fri, 08 May 2026 17:24:13 GMT  
**Gescannt:** 2026-05-18

---

## Inhalt

Great collab with @SakanaAILabs on an #ICML26 paper about sparse transformer kernels + formats optimized for modern NVIDIA GPU execution. • TwELL sparse packing • Fused CUDA kernels • 20%+ inference/training speedups at scale Paper + code below 👇 hardmaru (@hardmaru) The human brain🧠 is incredibly efficient because it only activates the specific neurons needed for a thought. Modern LLMs naturally try to do this too (> 95% of neurons in feedforward layers stay silent for any given word), but our hardware punishes them for it. One of the most frustrating paradoxes in deep learning: making a model do less math often makes it run slower. Why? Because unstructured sparsity introduces irregular memory access, and GPUs are built for predictable, dense blocks of math. We teamed up with @NVIDIA to try to fix this hardware mismatch. Instead of forcing the GPU to adapt to the sparsity, we built a "Hybrid" format that reshapes the sparsity to fit the GPU. Our sparsity format (TwELL) dynamically routes the 99% of highly sparse tokens through a fast path, and uses a dense backup matrix as a safety valve for the rare, heavy tokens. Through TwELL and a new set of custom CUDA kernels for both LLM inference and training, we translated theoretical sparsity into actual wall-clock speedups: >20% faster training and inference on H100 GPUs, while also cutting energy consumption and memory requirements. Paper: arxiv.org/abs/2603.23198 Blog: pub.sakana.ai/sparser-faster… Code: github.com/SakanaAI/sparser-… ⚡️ — http://nitter.perennialte.ch/hardmaru/status/2052787980344099293#m

## Siehe auch
- [[40_Areas/ai-news-index|Ai News Index]]
- [[40_Areas/dev-news-index|Dev News Index]]
- [[_meta/index/MOC|Master of Ceremonies]]
