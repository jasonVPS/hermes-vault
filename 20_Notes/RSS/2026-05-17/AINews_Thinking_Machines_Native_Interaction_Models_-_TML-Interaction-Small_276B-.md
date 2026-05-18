---
title: "[AINews] Thinking Machines' Native Interaction Models - TML-Interaction-Small 276B-A12B - advances SOTA Realtime Voice and kills standard VAD"
source: "Latent Space"
url: "https://www.latent.space/p/ainews-thinking-machines-native-interaction"
published: "2026-05-12"
scanned: "2026-05-17"
tags: [rss, latent_space, ai, productivity, security]
---

# [AINews] Thinking Machines' Native Interaction Models - TML-Interaction-Small 276B-A12B - advances SOTA Realtime Voice and kills standard VAD

**Quelle:** [Latent Space](https://www.latent.space/p/ainews-thinking-machines-native-interaction)
**Veröffentlicht:** 2026-05-12
**Gescannt:** 2026-05-17

---

## Zusammenfassung

AINews: Weekday Roundups

[AINews] Thinking Machines' Native Interaction Models - TML-Interaction-Small 276B-A12B - advances SOTA Realtime Voice and kills standard VAD

well done, Team Thinky.

May 12, 2026

∙ Paid

59

4

Share

By complete coincidence, the day we released Neil Zeghidour (CEO of Gradium, the for profit spinoff of the vaunted Kyutai Moshi)’s talk on what remains to be built for realtime voice, Thinking Machines emerged for only the third time in a ~year (despite much drama) to drop Interaction Models: A Scalable Approach to Human-AI Collaboration, TML-Interaction-Small is a 276B parameter MoE with 12B active., which immediately advances the state of the art of realtime voice models as Neil had laid out, updating the famously dead GPT 4o “her” demo with far more detailed demos that are presumably far closer to real use:

The full blogpost has lots of demos of the level of continuous interactivity, focusing on streams of “time-aligned microturns” of 200ms each:

Using encoder-free early fusion, with images and audio all processed <200ms, similar to Meta’s Chameleon:

There are a number of official benchmarks that the team shows beating both GPT-Realtime-2 and Gemini 3.1-Flash on basic things like BigBench Audio and IFEval and FD-bench, but the level of interactivity aimed for required making 2 new internal benchmarks for time awareness, simultaneous translation, and visual proactivity:

TimeSpeak: Can the model initiate speech at user-specified times? 

Example: “I want to practice my breathing, remind me to breathe in and out every 4 seconds until I ask you to stop.”

CueSpeak: Can the model speak at the appropriate moment? 

Example: “Everytime I codeswitch and use another language, give me the correct word in the original language.”

RepCount-A contains videos of repeated actions and is adapted into an online counting task - measures continuous visual tracking and timely counting.

ProactiveVideoQA consists of videos with questions, whose answers become available at specific moments. Higher scores require correct answers at the correct times, silence gets partial credit, and incorrect answers are penalized.

Charades is a standard temporal action-localization benchmark. 

Stream a user audio instruction: “Say ‘start’ when the person starts doing {action} then say ‘Stop’ when they stop.”

But look past the numbers: the single most visceral demo is this one buried at the bottom. Play the samples and feel the AGI:

The closing notes leave tantalizing hints to Thinky’s roadmap, including an intriguing pairing of background agents with interactive models, which we like a whole lot.

AI News for 5/9/2026-5/11/2026. We checked 12 subreddits, 544 Twitters and no further Discords. AINews’ website lets you search all past issues. As a reminder, AINews is now a section of Latent Space. You can opt in/out of email frequencies!

AI Twitter Recap

Thinking Machines’ Native Interaction Models and the Shift Beyond Turn-Based AI

Full-duplex …

## Notizen

-
## Siehe auch
- [[40_Areas/ai-news-index|Ai News Index]]
- [[40_Areas/productivity-index|Productivity News Index]]
- [[40_Areas/security-news-index|Security News Index]]
- [[_meta/index/MOC|Master of Ceremonies]]
