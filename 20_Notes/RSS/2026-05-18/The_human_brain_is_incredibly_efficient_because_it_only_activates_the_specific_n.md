---
title: "The human brain🧠 is incredibly efficient because it only activates the specific neurons needed for a thought. Modern LLMs naturally try to do this too (> 95% of neurons in feedforward layers stay silent for any given word), but our hardware punishes them for it.

One of the most frustrating paradoxes in deep learning: making a model do less math often makes it run slower. Why? Because unstructured sparsity introduces irregular memory access, and GPUs are built for predictable, dense blocks of math.

We teamed up with @NVIDIA to try to fix this hardware mismatch. Instead of forcing the GPU to adapt to the sparsity, we built a "Hybrid" format that reshapes the sparsity to fit the GPU. Our sparsity format (TwELL) dynamically routes the 99% of highly sparse tokens through a fast path, and uses a dense backup matrix as a safety valve for the rare, heavy tokens.

Through TwELL and a new set of custom CUDA kernels for both LLM inference and training, we translated theoretical sparsity into actual wall-clock speedups: >20% faster training and inference on H100 GPUs, while also cutting energy consumption and memory requirements.

Paper: https://arxiv.org/abs/2603.23198
Blog: https://pub.sakana.ai/sparser-faster-llms/
Code: https://github.com/SakanaAI/sparser-faster-llms
⚡️"
source: "X - David Ha"
author: "David Ha"
url: "http://nitter.perennialte.ch/hardmaru/status/2052787980344099293#m"
published: "Fri, 08 May 2026 16:29:28 GMT"
scanned: "2026-05-18"
tags: [rss, x_-_david_ha, twitter, x, social, ai, ai, dev]
type: social
---

# The human brain🧠 is incredibly efficient because it only activates the specific neurons needed for a thought. Modern LLMs naturally try to do this too (> 95% of neurons in feedforward layers stay silent for any given word), but our hardware punishes them for it.

One of the most frustrating paradoxes in deep learning: making a model do less math often makes it run slower. Why? Because unstructured sparsity introduces irregular memory access, and GPUs are built for predictable, dense blocks of math.

We teamed up with @NVIDIA to try to fix this hardware mismatch. Instead of forcing the GPU to adapt to the sparsity, we built a "Hybrid" format that reshapes the sparsity to fit the GPU. Our sparsity format (TwELL) dynamically routes the 99% of highly sparse tokens through a fast path, and uses a dense backup matrix as a safety valve for the rare, heavy tokens.

Through TwELL and a new set of custom CUDA kernels for both LLM inference and training, we translated theoretical sparsity into actual wall-clock speedups: >20% faster training and inference on H100 GPUs, while also cutting energy consumption and memory requirements.

Paper: https://arxiv.org/abs/2603.23198
Blog: https://pub.sakana.ai/sparser-faster-llms/
Code: https://github.com/SakanaAI/sparser-faster-llms
⚡️

**Quelle:** [X - David Ha](http://nitter.perennialte.ch/hardmaru/status/2052787980344099293#m)  
**Autor:** David Ha  
**Veröffentlicht:** Fri, 08 May 2026 16:29:28 GMT  
**Gescannt:** 2026-05-18

---

## Inhalt

The human brain🧠 is incredibly efficient because it only activates the specific neurons needed for a thought. Modern LLMs naturally try to do this too (> 95% of neurons in feedforward layers stay silent for any given word), but our hardware punishes them for it. One of the most frustrating paradoxes in deep learning: making a model do less math often makes it run slower. Why? Because unstructured sparsity introduces irregular memory access, and GPUs are built for predictable, dense blocks of math. We teamed up with @NVIDIA to try to fix this hardware mismatch. Instead of forcing the GPU to adapt to the sparsity, we built a "Hybrid" format that reshapes the sparsity to fit the GPU. Our sparsity format (TwELL) dynamically routes the 99% of highly sparse tokens through a fast path, and uses a dense backup matrix as a safety valve for the rare, heavy tokens. Through TwELL and a new set of custom CUDA kernels for both LLM inference and training, we translated theoretical sparsity into actual wall-clock speedups: >20% faster training and inference on H100 GPUs, while also cutting energy consumption and memory requirements. Paper: arxiv.org/abs/2603.23198 Blog: pub.sakana.ai/sparser-faster… Code: github.com/SakanaAI/sparser-… ⚡️ Sakana AI (@SakanaAILabs) How do we make LLMs faster and lighter? Don’t force the GPU to adapt to sparsity. Reshape the sparsity to fit the GPU! ⚡️ Excited to share our new #ICML2026 paper in collaboration with @NVIDIA : "Sparser, Faster, Lighter Transformer Language Models". This work introduces new open-source GPU kernels and data formats for faster inference and training of sparse transformer language models: Paper: arxiv.org/abs/2603.23198 Blog: pub.sakana.ai/sparser-faster… Code: github.com/SakanaAI/sparser-… While LLMs are undoubtedly powerful, they are increasingly expensive to train and deploy, with a large part of this cost coming from their feedforward layers. Yet, an interesting phenomenon occurs inside these layers: For any given token, only a small fraction of the hidden activations actually matter. The rest approximate zero, wasting computation. With ReLU and very mild L1 regularization, this sparsity can exceed 95% with little to no impact on downstream performance. So, can we leverage this sparsity to make LLMs faster? The challenge is hardware. Modern GPUs are optimized for dense matrix multiplications. Traditional sparse formats introduce irregular memory access and overheads that cancel out their theoretical savings for GEMM operations. Our contribution is twofold: 1/ We introduce TwELL (Tile-wise ELLPACK), a new sparse packing format designed to integrate directly in the same optimized tiled matmul kernels without disrupting execution. 2/ We develop custom CUDA kernels that fuse multiple sparse matmuls to maximize throughput and compress TwELL to a hybrid representation that minimizes activation sizes. We used our kernels to train and benchmark sparse LLMs at billion-parameter scales, demonstrating >20% speedups and even higher savings in peak memory and energy. This work will be presented at #ICML2026 . Please check out our blog and technical paper for a deep dive! — http://nitter.perennialte.ch/SakanaAILabs/status/2052787226136990029#m

## Siehe auch
- [[40_Areas/ai-news-index|Ai News Index]]
- [[40_Areas/dev-news-index|Dev News Index]]
- [[_meta/index/MOC|Master of Ceremonies]]
