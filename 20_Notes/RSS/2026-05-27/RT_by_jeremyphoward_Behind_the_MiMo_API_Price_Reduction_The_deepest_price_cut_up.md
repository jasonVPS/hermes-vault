---
title: "RT by @jeremyphoward: Behind the MiMo API Price Reduction:
The deepest price cut, up to 99%, is for Input (Cache Hit). The core reason is our inference framework now supports hierarchical KV cache optimization for SWA. Production inference engine tests show this optimization increases cached token capacity by 5x, equivalent to an 80% reduction in caching costs. Combined with Cache Read Overlap among multiple Full Attention modules in the Hybrid model, actual costs are further reduced.

Prices for Input (Cache Miss) and Output are also reduced by 60%-80%. This mainly benefits from the extreme 1:7 Full:SWA sparsity ratio brought by the model architecture (the prefill compute of the 70-layer MiMo-V2.5-Pro roughly equals a 10-layer GQA model). This kept our original inference costs well below the industry average, naturally leaving a 2x-3x profit margin in pricing. This price adjustment simply reflects our decision to pass these structural cost efficiencies directly to developers.

Operating at these newly reduced API prices, our production inference engine is running at near full capacity, and we can still essentially break even. We previously advised LLM companies not to "blindly cut prices" precisely because very few model architectures and inference optimizations can keep API costs from running at a loss. If more architectures that save compute and KV cache emerge, along with better inference Infra to drive down API costs, this will form an excellent virtuous cycle in the industry.

More crucially, affordable, high-performance model APIs will drive real, sustained, and at-scale inference demand. This upstream demand pulls forward the development of the entire AI infrastructure chain—including chips, servers, optical transceivers, PCBs, liquid cooling, power, energy storage, and data centers—serving as a strategic fulcrum for a systemic revaluation of AI hardware. In the long run, this injects more affordable and accessible compute into both training and inference pipelines, accelerating the parallel evolution of global AGI across multiple regions and technical routes.

For more technical details, we will release a detailed Blog post later."
source: "X - Jeremy Howard"
author: "Jeremy Howard"
url: "http://nitter.perennialte.ch/_LuoFuli/status/2059618247553745204#m"
published: "Wed, 27 May 2026 12:50:30 GMT"
scanned: "2026-05-27"
tags: [rss, x_-_jeremy_howard, twitter, x, social, ai, ai, dev]
type: social
---

# RT by @jeremyphoward: Behind the MiMo API Price Reduction:
The deepest price cut, up to 99%, is for Input (Cache Hit). The core reason is our inference framework now supports hierarchical KV cache optimization for SWA. Production inference engine tests show this optimization increases cached token capacity by 5x, equivalent to an 80% reduction in caching costs. Combined with Cache Read Overlap among multiple Full Attention modules in the Hybrid model, actual costs are further reduced.

Prices for Input (Cache Miss) and Output are also reduced by 60%-80%. This mainly benefits from the extreme 1:7 Full:SWA sparsity ratio brought by the model architecture (the prefill compute of the 70-layer MiMo-V2.5-Pro roughly equals a 10-layer GQA model). This kept our original inference costs well below the industry average, naturally leaving a 2x-3x profit margin in pricing. This price adjustment simply reflects our decision to pass these structural cost efficiencies directly to developers.

Operating at these newly reduced API prices, our production inference engine is running at near full capacity, and we can still essentially break even. We previously advised LLM companies not to "blindly cut prices" precisely because very few model architectures and inference optimizations can keep API costs from running at a loss. If more architectures that save compute and KV cache emerge, along with better inference Infra to drive down API costs, this will form an excellent virtuous cycle in the industry.

More crucially, affordable, high-performance model APIs will drive real, sustained, and at-scale inference demand. This upstream demand pulls forward the development of the entire AI infrastructure chain—including chips, servers, optical transceivers, PCBs, liquid cooling, power, energy storage, and data centers—serving as a strategic fulcrum for a systemic revaluation of AI hardware. In the long run, this injects more affordable and accessible compute into both training and inference pipelines, accelerating the parallel evolution of global AGI across multiple regions and technical routes.

For more technical details, we will release a detailed Blog post later.

**Quelle:** [X - Jeremy Howard](http://nitter.perennialte.ch/_LuoFuli/status/2059618247553745204#m)  
**Autor:** Jeremy Howard  
**Veröffentlicht:** Wed, 27 May 2026 12:50:30 GMT  
**Gescannt:** 2026-05-27

---

## Inhalt

RT by @jeremyphoward: Behind the MiMo API Price Reduction:
The deepest price cut, up to 99%, is for Input (Cache Hit). The core reason is our inference framework now supports hierarchical KV cache optimization for SWA. Production inference engine tests show this optimization increases cached token capacity by 5x, equivalent to an 80% reduction in caching costs. Combined with Cache Read Overlap among multiple Full Attention modules in the Hybrid model, actual costs are further reduced.

Prices for Input (Cache Miss) and Output are also reduced by 60%-80%. This mainly benefits from the extreme 1:7 Full:SWA sparsity ratio brought by the model architecture (the prefill compute of the 70-layer MiMo-V2.5-Pro roughly equals a 10-layer GQA model). This kept our original inference costs well below the industry average, naturally leaving a 2x-3x profit margin in pricing. This price adjustment simply reflects our decision to pass these structural cost efficiencies directly to developers.

Operating at these newly reduced API prices, our production inference engine is running at near full capacity, and we can still essentially break even. We previously advised LLM companies not to "blindly cut prices" precisely because very few model architectures and inference optimizations can keep API costs from running at a loss. If more architectures that save compute and KV cache emerge, along with better inference Infra to drive down API costs, this will form an excellent virtuous cycle in the industry.

More crucially, affordable, high-performance model APIs will drive real, sustained, and at-scale inference demand. This upstream demand pulls forward the development of the entire AI infrastructure chain—including chips, servers, optical transceivers, PCBs, liquid cooling, power, energy storage, and data centers—serving as a strategic fulcrum for a systemic revaluation of AI hardware. In the long run, this injects more affordable and accessible compute into both training and inference pipelines, accelerating the parallel evolution of global AGI across multiple regions and technical routes.

For more technical details, we will release a detailed Blog post later.

## Siehe auch
- [[40_Areas/ai-news-index|Ai News Index]]
- [[40_Areas/dev-news-index|Dev News Index]]
- [[_meta/index/MOC|Master of Ceremonies]]
