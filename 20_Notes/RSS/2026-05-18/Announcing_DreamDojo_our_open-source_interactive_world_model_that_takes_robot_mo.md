---
title: "Announcing DreamDojo: our open-source, interactive world model that takes robot motor controls and generates the future in pixels. No engine, no meshes, no hand-authored dynamics. It's Simulation 2.0. Time for robotics to take the bitter lesson pill.

Real-world robot learning is bottlenecked by time, wear, safety, and resets. If we want Physical AI to move at pretraining speed, we need a simulator that adapts to pretraining scale with as little human engineering as possible.

Our key insights: (1) human egocentric videos are a scalable source of first-person physics; (2) latent actions make them "robot-readable" across different hardware; (3) real-time inference unlocks live teleop, policy eval, and test-time planning *inside* a dream.

We pre-train on 44K hours of human videos: cheap, abundant, and collected with zero robot-in-the-loop. Humans have already explored the combinatorics: we grasp, pour, fold, assemble, fail, retry—across cluttered scenes, shifting viewpoints, changing light, and hour-long task chains—at a scale no robot fleet could match. The missing piece: these videos have no action labels. So we introduce latent actions: a unified representation inferred directly from videos that captures "what changed between world states" without knowing the underlying hardware. This lets us train on any first-person video as if it came with motor commands attached.

As a result, DreamDojo generalizes zero-shot to objects and environments never seen in any robot training set, because humans saw them first.

Next, we post-train onto each robot to fit its specific hardware. Think of it as separating "how the world looks and behaves" from "how this particular robot actuates." The base model follows the general physical rules, then "snaps onto" the robot's unique mechanics. It's kind of like loading a new character and scene assets into Unreal Engine, but done through gradient descent and generalizes far beyond the post-training dataset.

A world simulator is only useful if it runs fast enough to close the loop. We train a real-time version of DreamDojo that runs at 10 FPS, stable for over a minute of continuous rollout. This unlocks exciting possibilities:

- Live teleoperation *inside* a dream. Connect a VR controller, stream actions into DreamDojo, and teleop a virtual robot in real time. We demo this on Unitree G1 with a PICO headset and one RTX 5090.
- Policy evaluation. You can benchmark a policy checkpoint in DreamDojo instead of the real world. The simulated success rates strongly correlate with real-world results - accurate enough to rank checkpoints without burning a single motor.
- Model-based planning. Sample multiple action proposals → simulate them all in parallel → pick the best future. Gains +17% real-world success out of the box on a fruit packing task. 

We open-source everything!! Weights, code, post-training dataset, eval set, and whitepaper with tons of details to reproduce. DreamDojo is based on NVIDIA Cosmos, which is open-weight too. 

2026 is the year of World Models for physical AI. We want you to build with us. Happy scaling! 

Links in thread:"
source: "X - Jim Fan"
author: "Jim Fan"
url: "http://nitter.perennialte.ch/DrJimFan/status/2024895359236051274#m"
published: "Fri, 20 Feb 2026 17:14:09 GMT"
scanned: "2026-05-18"
tags: [rss, x_-_jim_fan, twitter, x, social, ai, ai, dev]
type: social
---

# Announcing DreamDojo: our open-source, interactive world model that takes robot motor controls and generates the future in pixels. No engine, no meshes, no hand-authored dynamics. It's Simulation 2.0. Time for robotics to take the bitter lesson pill.

Real-world robot learning is bottlenecked by time, wear, safety, and resets. If we want Physical AI to move at pretraining speed, we need a simulator that adapts to pretraining scale with as little human engineering as possible.

Our key insights: (1) human egocentric videos are a scalable source of first-person physics; (2) latent actions make them "robot-readable" across different hardware; (3) real-time inference unlocks live teleop, policy eval, and test-time planning *inside* a dream.

We pre-train on 44K hours of human videos: cheap, abundant, and collected with zero robot-in-the-loop. Humans have already explored the combinatorics: we grasp, pour, fold, assemble, fail, retry—across cluttered scenes, shifting viewpoints, changing light, and hour-long task chains—at a scale no robot fleet could match. The missing piece: these videos have no action labels. So we introduce latent actions: a unified representation inferred directly from videos that captures "what changed between world states" without knowing the underlying hardware. This lets us train on any first-person video as if it came with motor commands attached.

As a result, DreamDojo generalizes zero-shot to objects and environments never seen in any robot training set, because humans saw them first.

Next, we post-train onto each robot to fit its specific hardware. Think of it as separating "how the world looks and behaves" from "how this particular robot actuates." The base model follows the general physical rules, then "snaps onto" the robot's unique mechanics. It's kind of like loading a new character and scene assets into Unreal Engine, but done through gradient descent and generalizes far beyond the post-training dataset.

A world simulator is only useful if it runs fast enough to close the loop. We train a real-time version of DreamDojo that runs at 10 FPS, stable for over a minute of continuous rollout. This unlocks exciting possibilities:

- Live teleoperation *inside* a dream. Connect a VR controller, stream actions into DreamDojo, and teleop a virtual robot in real time. We demo this on Unitree G1 with a PICO headset and one RTX 5090.
- Policy evaluation. You can benchmark a policy checkpoint in DreamDojo instead of the real world. The simulated success rates strongly correlate with real-world results - accurate enough to rank checkpoints without burning a single motor.
- Model-based planning. Sample multiple action proposals → simulate them all in parallel → pick the best future. Gains +17% real-world success out of the box on a fruit packing task. 

We open-source everything!! Weights, code, post-training dataset, eval set, and whitepaper with tons of details to reproduce. DreamDojo is based on NVIDIA Cosmos, which is open-weight too. 

2026 is the year of World Models for physical AI. We want you to build with us. Happy scaling! 

Links in thread:

**Quelle:** [X - Jim Fan](http://nitter.perennialte.ch/DrJimFan/status/2024895359236051274#m)  
**Autor:** Jim Fan  
**Veröffentlicht:** Fri, 20 Feb 2026 17:14:09 GMT  
**Gescannt:** 2026-05-18

---

## Inhalt

Announcing DreamDojo: our open-source, interactive world model that takes robot motor controls and generates the future in pixels. No engine, no meshes, no hand-authored dynamics. It's Simulation 2.0. Time for robotics to take the bitter lesson pill.

Real-world robot learning is bottlenecked by time, wear, safety, and resets. If we want Physical AI to move at pretraining speed, we need a simulator that adapts to pretraining scale with as little human engineering as possible.

Our key insights: (1) human egocentric videos are a scalable source of first-person physics; (2) latent actions make them "robot-readable" across different hardware; (3) real-time inference unlocks live teleop, policy eval, and test-time planning *inside* a dream.

We pre-train on 44K hours of human videos: cheap, abundant, and collected with zero robot-in-the-loop. Humans have already explored the combinatorics: we grasp, pour, fold, assemble, fail, retry—across cluttered scenes, shifting viewpoints, changing light, and hour-long task chains—at a scale no robot fleet could match. The missing piece: these videos have no action labels. So we introduce latent actions: a unified representation inferred directly from videos that captures "what changed between world states" without knowing the underlying hardware. This lets us train on any first-person video as if it came with motor commands attached.

As a result, DreamDojo generalizes zero-shot to objects and environments never seen in any robot training set, because humans saw them first.

Next, we post-train onto each robot to fit its specific hardware. Think of it as separating "how the world looks and behaves" from "how this particular robot actuates." The base model follows the general physical rules, then "snaps onto" the robot's unique mechanics. It's kind of like loading a new character and scene assets into Unreal Engine, but done through gradient descent and generalizes far beyond the post-training dataset.

A world simulator is only useful if it runs fast enough to close the loop. We train a real-time version of DreamDojo that runs at 10 FPS, stable for over a minute of continuous rollout. This unlocks exciting possibilities:

- Live teleoperation *inside* a dream. Connect a VR controller, stream actions into DreamDojo, and teleop a virtual robot in real time. We demo this on Unitree G1 with a PICO headset and one RTX 5090.
- Policy evaluation. You can benchmark a policy checkpoint in DreamDojo instead of the real world. The simulated success rates strongly correlate with real-world results - accurate enough to rank checkpoints without burning a single motor.
- Model-based planning. Sample multiple action proposals → simulate them all in parallel → pick the best future. Gains +17% real-world success out of the box on a fruit packing task. 

We open-source everything!! Weights, code, post-training dataset, eval set, and whitepaper with tons of details to reproduce. DreamDojo is based on NVIDIA Cosmos, which is open-weight too. 

2026 is the year of World Models for physical AI. We want you to build with us. Happy scaling! 

Links in thread:

## Siehe auch
- [[40_Areas/ai-news-index|Ai News Index]]
- [[40_Areas/dev-news-index|Dev News Index]]
- [[_meta/index/MOC|Master of Ceremonies]]
