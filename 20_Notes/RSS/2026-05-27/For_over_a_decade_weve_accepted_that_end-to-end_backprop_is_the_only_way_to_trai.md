---
title: "For over a decade, we’ve accepted that end-to-end backprop is the only way to train deep networks. But holding the entire network in memory all at once is why AI training is hitting a resource wall.

We found a new way to break the network into blocks and train them independently. The trick? Treating the network’s forward pass like a diffusion model denoising a signal.

This reinterpretation slashes the memory needed to train deep models. In our #ICLR2026 paper (https://arxiv.org/abs/2506.14202), we matched end-to-end performance across ViTs, DiTs, and LLMs. We did this while training just one isolated block at a time."
source: "X - David Ha"
author: "David Ha"
url: "http://nitter.perennialte.ch/hardmaru/status/2059648995132367277#m"
published: "Wed, 27 May 2026 14:52:41 GMT"
scanned: "2026-05-27"
tags: [rss, x_-_david_ha, twitter, x, social, ai, ai, dev]
type: social
---

# For over a decade, we’ve accepted that end-to-end backprop is the only way to train deep networks. But holding the entire network in memory all at once is why AI training is hitting a resource wall.

We found a new way to break the network into blocks and train them independently. The trick? Treating the network’s forward pass like a diffusion model denoising a signal.

This reinterpretation slashes the memory needed to train deep models. In our #ICLR2026 paper (https://arxiv.org/abs/2506.14202), we matched end-to-end performance across ViTs, DiTs, and LLMs. We did this while training just one isolated block at a time.

**Quelle:** [X - David Ha](http://nitter.perennialte.ch/hardmaru/status/2059648995132367277#m)  
**Autor:** David Ha  
**Veröffentlicht:** Wed, 27 May 2026 14:52:41 GMT  
**Gescannt:** 2026-05-27

---

## Inhalt

For over a decade, we’ve accepted that end-to-end backprop is the only way to train deep networks. But holding the entire network in memory all at once is why AI training is hitting a resource wall. We found a new way to break the network into blocks and train them independently. The trick? Treating the network’s forward pass like a diffusion model denoising a signal. This reinterpretation slashes the memory needed to train deep models. In our #ICLR2026 paper ( arxiv.org/abs/2506.14202 ), we matched end-to-end performance across ViTs, DiTs, and LLMs. We did this while training just one isolated block at a time. Sakana AI (@SakanaAILabs) Introducing DiffusionBlocks: Block-wise Neural Network Training via Diffusion Interpretation pub.sakana.ai/diffusionblock… What if we didn’t have to hold an entire neural network in memory to train it? Standard neural net training optimizes all parameters jointly. As a result, the memory required during training grows linearly with the depth of the network. In our #ICLR2026 paper, we propose DiffusionBlocks, a principled framework to train networks one block at a time, drastically reducing memory requirements while matching end-to-end performance. With DiffusionBlocks, we split the network into blocks and train them one at a time, so you only need memory for a single block. How? We explicitly assign each block a role: to move the representation a little closer to the target than the block before it did. That role turns out to be precisely what a diffusion model does, step by step. Each block only needs to optimize its own objective and can be trained independently. We validated this across five different architectures: • ViT • DiT • Masked diffusion • Autoregressive transformers • Recurrent-depth transformers In each case, performance is competitive with end-to-end training while using a fraction of the memory. This perspective also extends naturally to recurrent-depth (Looped) transformers, which apply the same network iteratively and normally require expensive backpropagation through time (BPTT). Viewed through DiffusionBlocks, we can replace those multiple iterations with a single forward pass during training. Read our paper and code, to learn more. Paper: arxiv.org/abs/2506.14202 GitHub: github.com/SakanaAI/Diffusio… 🐟 — http://nitter.perennialte.ch/SakanaAILabs/status/2059648778051924281#m

## Siehe auch
- [[40_Areas/ai-news-index|Ai News Index]]
- [[40_Areas/dev-news-index|Dev News Index]]
- [[_meta/index/MOC|Master of Ceremonies]]
