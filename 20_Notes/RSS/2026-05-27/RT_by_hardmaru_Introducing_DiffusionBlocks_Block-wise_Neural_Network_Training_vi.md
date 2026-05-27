---
title: "RT by @hardmaru: Introducing DiffusionBlocks: Block-wise Neural Network Training via Diffusion Interpretation

http://pub.sakana.ai/diffusionblocks

What if we didn’t have to hold an entire neural network in memory to train it?

Standard neural net training optimizes all parameters jointly. As a result, the memory required during training grows linearly with the depth of the network.

In our #ICLR2026 paper, we propose DiffusionBlocks, a principled framework to train networks one block at a time, drastically reducing memory requirements while matching end-to-end performance.

With DiffusionBlocks, we split the network into blocks and train them one at a time, so you only need memory for a single block.

How? We explicitly assign each block a role: to move the representation a little closer to the target than the block before it did. That role turns out to be precisely what a diffusion model does, step by step. Each block only needs to optimize its own objective and can be trained independently.

We validated this across five different architectures:

• ViT
• DiT
• Masked diffusion
• Autoregressive transformers
• Recurrent-depth transformers

In each case, performance is competitive with end-to-end training while using a fraction of the memory.

This perspective also extends naturally to recurrent-depth (Looped) transformers, which apply the same network iteratively and normally require expensive backpropagation through time (BPTT). Viewed through DiffusionBlocks, we can replace those multiple iterations with a single forward pass during training.

Read our paper and code, to learn more.

Paper: https://arxiv.org/abs/2506.14202
GitHub: https://github.com/SakanaAI/DiffusionBlocks
🐟"
source: "X - David Ha"
author: "David Ha"
url: "http://nitter.perennialte.ch/SakanaAILabs/status/2059648778051924281#m"
published: "Wed, 27 May 2026 14:51:49 GMT"
scanned: "2026-05-27"
tags: [rss, x_-_david_ha, twitter, x, social, ai, ai, dev]
type: social
---

# RT by @hardmaru: Introducing DiffusionBlocks: Block-wise Neural Network Training via Diffusion Interpretation

http://pub.sakana.ai/diffusionblocks

What if we didn’t have to hold an entire neural network in memory to train it?

Standard neural net training optimizes all parameters jointly. As a result, the memory required during training grows linearly with the depth of the network.

In our #ICLR2026 paper, we propose DiffusionBlocks, a principled framework to train networks one block at a time, drastically reducing memory requirements while matching end-to-end performance.

With DiffusionBlocks, we split the network into blocks and train them one at a time, so you only need memory for a single block.

How? We explicitly assign each block a role: to move the representation a little closer to the target than the block before it did. That role turns out to be precisely what a diffusion model does, step by step. Each block only needs to optimize its own objective and can be trained independently.

We validated this across five different architectures:

• ViT
• DiT
• Masked diffusion
• Autoregressive transformers
• Recurrent-depth transformers

In each case, performance is competitive with end-to-end training while using a fraction of the memory.

This perspective also extends naturally to recurrent-depth (Looped) transformers, which apply the same network iteratively and normally require expensive backpropagation through time (BPTT). Viewed through DiffusionBlocks, we can replace those multiple iterations with a single forward pass during training.

Read our paper and code, to learn more.

Paper: https://arxiv.org/abs/2506.14202
GitHub: https://github.com/SakanaAI/DiffusionBlocks
🐟

**Quelle:** [X - David Ha](http://nitter.perennialte.ch/SakanaAILabs/status/2059648778051924281#m)  
**Autor:** David Ha  
**Veröffentlicht:** Wed, 27 May 2026 14:51:49 GMT  
**Gescannt:** 2026-05-27

---

## Inhalt

RT by @hardmaru: Introducing DiffusionBlocks: Block-wise Neural Network Training via Diffusion Interpretation

http://pub.sakana.ai/diffusionblocks

What if we didn’t have to hold an entire neural network in memory to train it?

Standard neural net training optimizes all parameters jointly. As a result, the memory required during training grows linearly with the depth of the network.

In our #ICLR2026 paper, we propose DiffusionBlocks, a principled framework to train networks one block at a time, drastically reducing memory requirements while matching end-to-end performance.

With DiffusionBlocks, we split the network into blocks and train them one at a time, so you only need memory for a single block.

How? We explicitly assign each block a role: to move the representation a little closer to the target than the block before it did. That role turns out to be precisely what a diffusion model does, step by step. Each block only needs to optimize its own objective and can be trained independently.

We validated this across five different architectures:

• ViT
• DiT
• Masked diffusion
• Autoregressive transformers
• Recurrent-depth transformers

In each case, performance is competitive with end-to-end training while using a fraction of the memory.

This perspective also extends naturally to recurrent-depth (Looped) transformers, which apply the same network iteratively and normally require expensive backpropagation through time (BPTT). Viewed through DiffusionBlocks, we can replace those multiple iterations with a single forward pass during training.

Read our paper and code, to learn more.

Paper: https://arxiv.org/abs/2506.14202
GitHub: https://github.com/SakanaAI/DiffusionBlocks
🐟

## Siehe auch
- [[40_Areas/ai-news-index|Ai News Index]]
- [[40_Areas/dev-news-index|Dev News Index]]
- [[_meta/index/MOC|Master of Ceremonies]]
