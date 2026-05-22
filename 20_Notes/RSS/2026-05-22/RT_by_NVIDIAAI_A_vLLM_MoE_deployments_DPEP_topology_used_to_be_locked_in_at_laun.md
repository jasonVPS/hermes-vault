---
title: "RT by @NVIDIAAI: A vLLM MoE deployment's DP/EP topology used to be locked in at launch — scaling or swapping config meant a full restart, in-flight traffic dropped. Elastic Expert Parallelism changes that. One API call resizes a live deployment:

curl -X POST localhost:8000/scale_elastic_ep \
  -d '{"new_data_parallel_size": 16}'

Under the hood: standby comm groups span the target topology, EPLB redistributes experts across the new EP group, and weights are transferred directly between GPUs over NVIDIA NVLink/RDMA. The same runtime reconfiguration path is what fault-tolerant serving needs: evict failed ranks, redistribute their experts, bring replacements back, no restart.

Thanks to @NVIDIAAI, Sky Computing, @anyscalecompute, @RedHat_AI, and the community. 

📖 http://vllm.ai/blog/2026-05-14-elastic-expert-parallelism"
source: "X - NVIDIA AI"
author: "NVIDIA"
url: "http://nitter.perennialte.ch/vllm_project/status/2057602243860574463#m"
published: "Thu, 21 May 2026 23:19:37 GMT"
scanned: "2026-05-22"
tags: [rss, x_-_nvidia_ai, twitter, x, social, ai, ai, dev]
type: social
---

# RT by @NVIDIAAI: A vLLM MoE deployment's DP/EP topology used to be locked in at launch — scaling or swapping config meant a full restart, in-flight traffic dropped. Elastic Expert Parallelism changes that. One API call resizes a live deployment:

curl -X POST localhost:8000/scale_elastic_ep \
  -d '{"new_data_parallel_size": 16}'

Under the hood: standby comm groups span the target topology, EPLB redistributes experts across the new EP group, and weights are transferred directly between GPUs over NVIDIA NVLink/RDMA. The same runtime reconfiguration path is what fault-tolerant serving needs: evict failed ranks, redistribute their experts, bring replacements back, no restart.

Thanks to @NVIDIAAI, Sky Computing, @anyscalecompute, @RedHat_AI, and the community. 

📖 http://vllm.ai/blog/2026-05-14-elastic-expert-parallelism

**Quelle:** [X - NVIDIA AI](http://nitter.perennialte.ch/vllm_project/status/2057602243860574463#m)  
**Autor:** NVIDIA  
**Veröffentlicht:** Thu, 21 May 2026 23:19:37 GMT  
**Gescannt:** 2026-05-22

---

## Inhalt

RT by @NVIDIAAI: A vLLM MoE deployment's DP/EP topology used to be locked in at launch — scaling or swapping config meant a full restart, in-flight traffic dropped. Elastic Expert Parallelism changes that. One API call resizes a live deployment:

curl -X POST localhost:8000/scale_elastic_ep \
  -d '{"new_data_parallel_size": 16}'

Under the hood: standby comm groups span the target topology, EPLB redistributes experts across the new EP group, and weights are transferred directly between GPUs over NVIDIA NVLink/RDMA. The same runtime reconfiguration path is what fault-tolerant serving needs: evict failed ranks, redistribute their experts, bring replacements back, no restart.

Thanks to @NVIDIAAI, Sky Computing, @anyscalecompute, @RedHat_AI, and the community. 

📖 http://vllm.ai/blog/2026-05-14-elastic-expert-parallelism

## Siehe auch
- [[40_Areas/ai-news-index|Ai News Index]]
- [[40_Areas/dev-news-index|Dev News Index]]
- [[_meta/index/MOC|Master of Ceremonies]]
