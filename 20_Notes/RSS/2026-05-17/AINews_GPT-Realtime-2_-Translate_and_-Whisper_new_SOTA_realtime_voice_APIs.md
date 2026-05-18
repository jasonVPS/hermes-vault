---
title: "[AINews] GPT-Realtime-2, -Translate, and -Whisper: new SOTA realtime voice APIs"
source: "Latent Space"
url: "https://www.latent.space/p/ainews-gpt-realtime-2-translate-and"
published: "2026-05-08"
scanned: "2026-05-17"
tags: [rss, latent_space, ai, dev, productivity, security]
---

# [AINews] GPT-Realtime-2, -Translate, and -Whisper: new SOTA realtime voice APIs

**Quelle:** [Latent Space](https://www.latent.space/p/ainews-gpt-realtime-2-translate-and)
**Veröffentlicht:** 2026-05-08
**Gescannt:** 2026-05-17

---

## Zusammenfassung

AINews: Weekday Roundups

[AINews] GPT-Realtime-2, -Translate, and -Whisper: new SOTA realtime voice APIs

OpenAI continues deploying GPT-5 everywhere

May 08, 2026

∙ Paid

73

1

Share

OpenAI launched realtime-1.5 3 months ago, but it was a relative drop in the bucket because it was still 4o based intelligence (a +5% bump in Big Bench Audio). You could tell the sheer confidence in today’s realtime-2 release (with a +15.2% bump in BBA), and it was appropriately well received:

As the blogpost explains, 3 models are being released, which one might simplify to “voice-in, voice-out, and voice-to-voice”:

The focus is less about “voice quality”, and more on usability. TLDR:

Preambles: Developers can enable short phrases before a main response, like “let me check that” or “one moment while I look into it”.

Parallel tool calls and tool transparency: The model can call multiple tools at once and make those actions audible with phrases like “checking your calendar” or “looking that up now,” helping agents stay responsive while completing tasks.

Stronger recovery behavior: The model can recover more gracefully by saying things like “I’m having trouble with that right now,” instead of failing or breaking.

Longer context: 32K → 128K

Stronger domain understanding: The model better retains specialized terminology, proper nouns, healthcare terms, and other vocabulary

More controllable tone and delivery: The model can better adjust its tone—speaking calmly, empathetically, or upbeat, based on context

Adjustable reasoning effort: Developers can now select from minimal, low, medium, high, and xhigh reasoning levels, with low as the default.

The Demo video showed off how the audio model is better tuned when the main speaker is speaking to someone else, so it stops interrupting so much:

AI News for 5/6/2026-5/7/2026. We checked 12 subreddits, 544 Twitters and no further Discords. AINews’ website lets you search all past issues. As a reminder, AINews is now a section of Latent Space. You can opt in/out of email frequencies!

AI Twitter Recap

Top Story: GPT-Realtime-2 and OpenAI voice AI commentary

What happened

OpenAI launched three new streaming audio models in the Realtime API: GPT-Realtime-2, GPT-Realtime-Translate, and GPT-Realtime-Whisper. OpenAI positioned GPT-Realtime-2 as its “most intelligent voice model yet,” bringing “GPT-5-class reasoning” to real-time voice agents that can listen, reason, handle interruptions, use tools, and sustain longer conversations as they unfold @OpenAI. The companion models target live speech translation and transcription: GPT-Realtime-Translate supports streaming translation from 70+ input languages into 13 output languages, while GPT-Realtime-Whisper streams transcription/captions as speech is produced @OpenAI, @OpenAIDevs. OpenAI said the models are available in the Realtime API now, while ChatGPT voice upgrades are still pending: “Stay tuned, we’re cooking” @OpenAI. Sam Altman framed the launch around a …

## Notizen

-
## Siehe auch
- [[40_Areas/ai-news-index|Ai News Index]]
- [[40_Areas/dev-news-index|Dev News Index]]
- [[40_Areas/productivity-index|Productivity News Index]]
- [[40_Areas/security-news-index|Security News Index]]
- [[_meta/index/MOC|Master of Ceremonies]]
