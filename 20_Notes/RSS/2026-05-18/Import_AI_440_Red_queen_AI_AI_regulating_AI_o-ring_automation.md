---
title: "Import AI 440: Red queen AI; AI regulating AI; o-ring automation"
source: "Import AI"
url: "https://importai.substack.com/p/import-ai-440-red-queen-ai-ai-regulating"
published: "2026-01-12"
scanned: "2026-05-18"
tags: [rss, import_ai, capture, ai, productivity]
type: capture
---

# Import AI 440: Red queen AI; AI regulating AI; o-ring automation

**Quelle:** [Import AI](https://importai.substack.com/p/import-ai-440-red-queen-ai-ai-regulating)
**Veröffentlicht:** 2026-01-12
**Gescannt:** 2026-05-18

---

## Zusammenfassung

Import AI 440: Red queen AI; AI regulating AI; o-ring automation 

How many of your are LLMs?

 (https://substack.com/@importai) 

 (https://substack.com/@importai) Jack Clark

Jan 12, 2026

52

11

5

Share

Welcome to Import AI, a newsletter about AI research. Import AI runs on arXiv and feedback from readers. If you’d like to support this, please subscribe.

Subscribe

To understand the future of the world, stick AI systems in a petri dish:

…Evolving LLMs to attack other LLMs…

Researchers with Japanese AI startup Sakana have looked at what happens when they evolve LLM-based agents to fight against one another in a competitive programming game from the 1980s called Core War. The results show that “large language models (LLMs) drive an adversarial evolutionary arms race in this domain, where programs continuously adapt to defeat a growing history of opponents rather than a static benchmark”. This research approach gestures both at ways researchers might better study how LLM-dominated niches in the economy or national security world might unfold, and also hints at the strange AI world we’re heading into.

What is Core War? “Core War is a competitive programming game played out in a shared block of computer memory, called the “Core,” where two or more assembly programs fight for survival”, Sakana writes. “Each program, known as a “warrior”, is written in an assembly language called Redcode. These programs are tasked with crashing their competitors while keeping their own processes alive. The simulation runs by alternating between the programs, executing one instruction at a time. A warrior “attacks” by writing invalid instructions (DAT commands) into the memory slots occupied by opponents, causing them to crash upon execution.”

DRQ: To evolve their programs, the authors use a technique they call Digital Red Queen. “DRQ uses MAP-Elites, a quality-diversity algorithm, to optimize warriors within each round, preventing diversity collapse during search. By playing against all previous round champions, DRQ avoids cyclic adaptations across rounds, consistent with techniques in prior work”, they write. “We find that as DRQ is run for many rounds, warriors gradually become more generally robust, as measured by their performance against unseen human-designed warriors.”

    Each warrior calls out to GPT-4 mini (”preliminary experiments did not show significant performance increase with larger models), and is given a prompt which describes the Core War environment as well as a manual for the Redcode assembly language. “To generate a new warrior, the LLM is given a user prompt instructing it to produce a novel Redcode program. To mutate an existing warrior, the LLM is provided with the original program and instructed to modify it in ways that could improve performance.”

Evolution works: Unsurprisingly, evolving agents is very effective:

A one-shot warrior defeats 1.7% of human warriors.

Best-of-N sampling produces a set of warriors that can defeat …

## Notizen

-

## Siehe auch
- [[40_Areas/ai-news-index|Ai News Index]]
- [[40_Areas/productivity-index|Productivity News Index]]
- [[_meta/index/MOC|Master of Ceremonies]]
