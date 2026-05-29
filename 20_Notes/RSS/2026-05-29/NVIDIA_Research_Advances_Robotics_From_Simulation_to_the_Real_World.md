---
title: "NVIDIA Research Advances Robotics From Simulation to the Real World"
source: "NVIDIA Blog"
url: "https://blogs.nvidia.com/blog/icra-research-robotics-simulation-to-real-world/"
published: "2026-05-28"
scanned: "2026-05-29"
tags: [rss, nvidia_blog, capture, learning]
type: capture
---

# NVIDIA Research Advances Robotics From Simulation to the Real World

**Quelle:** [NVIDIA Blog](https://blogs.nvidia.com/blog/icra-research-robotics-simulation-to-real-world/)
**Veröffentlicht:** 2026-05-28
**Gescannt:** 2026-05-29

---

## Zusammenfassung

(https://blogs.nvidia.com/blog/author/kburke/) 

 (https://blogs.nvidia.com/blog/icra-research-robotics-simulation-to-real-world/#disqus_thread) 

 (https://twitter.com/intent/tweet?text=NVIDIA Research Advances Robotics From Simulation to the Real World https%3A%2F%2Fblogs.nvidia.com%2Fblog%2Ficra-research-robotics-simulation-to-real-world%2F) 

 (https://www.facebook.com/sharer/sharer.php?u=https%3A%2F%2Fblogs.nvidia.com%2Fblog%2Ficra-research-robotics-simulation-to-real-world%2F) 

 (https://www.linkedin.com/shareArticle?mini=true&url=https%3A%2F%2Fblogs.nvidia.com%2Fblog%2Ficra-research-robotics-simulation-to-real-world%2F&title=NVIDIA+Research+Advances+Robotics+From+Simulation+to+the+Real+World+%7C+NVIDIA+Blog) 

 (#) 

 (https://blogs.nvidia.com/wp-content/uploads/2026/05/icra-26-corp-blog-option2.mp4) 

	

		

			

Robotics is entering a new phase: moving from controlled demos and scripted automation toward generalizable, reliable embodied autonomy in the real world. 

At the  (https://www.nvidia.com/en-us/events/icra/) International Conference on Robotics and Automation (ICRA), eight of NVIDIA Research’s 28 accepted papers show how simulation-to-real transfer is becoming a foundation for that shift, helping robots perceive, reason, plan and act across dynamic, unpredictable environments.

Together, the papers span the full stack of challenges robot developers face: coordinating multiple arms in parallel, building policies that generalize across robot bodies, grasping novel objects in clutter, performing precise assembly and developing vision-language-action models that reason before they move. 

The throughline is clear: sim-to-real is becoming a foundation for robots that can adapt, generalize, and operate with greater reliability outside the lab.

Coordinating Arms, Navigating Bodies, Grasping Objects

Picture a pharmaceutical lab run by robotic arms: picking up tubes, transferring liquids, mixing reagents — each step taking different amounts of time, all requiring careful coordination. 

Traditional robot scheduling software handles those steps sequentially, one arm at a time. 

ScheduleStream changes that by running computations on GPUs, letting multiple arms plan movements and operate in parallel. The result — a 3x speedup across multi-arm planning scenarios, on hardware like the  (https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/) NVIDIA Jetson edge AI platform. Code for the framework is available on  (https://github.com/NVlabs/ScheduleStream) GitHub. 

 (https://blogs.nvidia.com/wp-content/uploads/2026/05/supplementary.mp4) https://blogs.nvidia.com/wp-content/uploads/2026/05/supplementary.mp4

 

A robot that learns to navigate through a space — avoiding obstacles and finding its destination — usually learns to do it in one body. Put the same navigation software into a differently shaped robot and it often falls apart, because its parts all move differently. 

The COMPASS policy framework solves this by first …

## Notizen

-

## Siehe auch
- [[40_Areas/learning-index|Learning News Index]]
- [[_meta/index/MOC|Master of Ceremonies]]
