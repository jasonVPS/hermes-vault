---
title: "We trained a humanoid with 22-DoF dexterous hands to assemble model cars, operate syringes, sort poker cards, fold/roll shirts, all learned primarily from 20,000+ hours of egocentric human video with no robot in the loop.

Humans are the most scalable embodiment on the planet. We discovered a near-perfect log-linear scaling law (R² = 0.998) between human video volume and action prediction loss, and this loss directly predicts real-robot success rate.

Humanoid robots will be the end game, because they are the practical form factor with minimal embodiment gap from humans. Call it the Bitter Lesson of robot hardware: the kinematic similarity lets us simply retarget human finger motion onto dexterous robot hand joints. No learned embeddings, no fancy transfer algorithms needed. Relative wrist motion + retargeted 22-DoF finger actions serve as a unified action space that carries through from pre-training to robot execution.

Our recipe is called "EgoScale":

- Pre-train GR00T N1.5 on 20K hours of human video, mid-train with only 4 hours (!) of robot play data with Sharpa hands. 54% gains over training from scratch across 5 highly dexterous tasks.
- Most surprising result: a *single* teleop demo is sufficient to learn a never-before-seen task. Our recipe enables extreme data efficiency.
- Although we pre-train in 22-DoF hand joint space, the policy transfers to a Unitree G1 with 7-DoF tri-finger hands. 30%+ gains over training on G1 data alone.

The scalable path to robot dexterity was never more robots. It was always us.

Deep dives in thread:"
source: "X - Jim Fan"
author: "Jim Fan"
url: "http://nitter.perennialte.ch/DrJimFan/status/2026709304984875202#m"
published: "Wed, 25 Feb 2026 17:22:07 GMT"
scanned: "2026-05-18"
tags: [rss, x_-_jim_fan, twitter, x, social, ai, ai]
type: social
---

# We trained a humanoid with 22-DoF dexterous hands to assemble model cars, operate syringes, sort poker cards, fold/roll shirts, all learned primarily from 20,000+ hours of egocentric human video with no robot in the loop.

Humans are the most scalable embodiment on the planet. We discovered a near-perfect log-linear scaling law (R² = 0.998) between human video volume and action prediction loss, and this loss directly predicts real-robot success rate.

Humanoid robots will be the end game, because they are the practical form factor with minimal embodiment gap from humans. Call it the Bitter Lesson of robot hardware: the kinematic similarity lets us simply retarget human finger motion onto dexterous robot hand joints. No learned embeddings, no fancy transfer algorithms needed. Relative wrist motion + retargeted 22-DoF finger actions serve as a unified action space that carries through from pre-training to robot execution.

Our recipe is called "EgoScale":

- Pre-train GR00T N1.5 on 20K hours of human video, mid-train with only 4 hours (!) of robot play data with Sharpa hands. 54% gains over training from scratch across 5 highly dexterous tasks.
- Most surprising result: a *single* teleop demo is sufficient to learn a never-before-seen task. Our recipe enables extreme data efficiency.
- Although we pre-train in 22-DoF hand joint space, the policy transfers to a Unitree G1 with 7-DoF tri-finger hands. 30%+ gains over training on G1 data alone.

The scalable path to robot dexterity was never more robots. It was always us.

Deep dives in thread:

**Quelle:** [X - Jim Fan](http://nitter.perennialte.ch/DrJimFan/status/2026709304984875202#m)  
**Autor:** Jim Fan  
**Veröffentlicht:** Wed, 25 Feb 2026 17:22:07 GMT  
**Gescannt:** 2026-05-18

---

## Inhalt

We trained a humanoid with 22-DoF dexterous hands to assemble model cars, operate syringes, sort poker cards, fold/roll shirts, all learned primarily from 20,000+ hours of egocentric human video with no robot in the loop.

Humans are the most scalable embodiment on the planet. We discovered a near-perfect log-linear scaling law (R² = 0.998) between human video volume and action prediction loss, and this loss directly predicts real-robot success rate.

Humanoid robots will be the end game, because they are the practical form factor with minimal embodiment gap from humans. Call it the Bitter Lesson of robot hardware: the kinematic similarity lets us simply retarget human finger motion onto dexterous robot hand joints. No learned embeddings, no fancy transfer algorithms needed. Relative wrist motion + retargeted 22-DoF finger actions serve as a unified action space that carries through from pre-training to robot execution.

Our recipe is called "EgoScale":

- Pre-train GR00T N1.5 on 20K hours of human video, mid-train with only 4 hours (!) of robot play data with Sharpa hands. 54% gains over training from scratch across 5 highly dexterous tasks.
- Most surprising result: a *single* teleop demo is sufficient to learn a never-before-seen task. Our recipe enables extreme data efficiency.
- Although we pre-train in 22-DoF hand joint space, the policy transfers to a Unitree G1 with 7-DoF tri-finger hands. 30%+ gains over training on G1 data alone.

The scalable path to robot dexterity was never more robots. It was always us.

Deep dives in thread:

## Siehe auch
- [[40_Areas/ai-news-index|Ai News Index]]
- [[_meta/index/MOC|Master of Ceremonies]]
