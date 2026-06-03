---
name: img-prompt-gen
description: >
  Structure a raw image idea into a GPT Image 2 prompt. Use when the user says
  "generate an image", "create an image prompt", "write a prompt for",
  "make an image of", or shares an image idea and wants a structured prompt
  for GPT Image 2. Adds safe recommendations without changing the user's intent.
license: MIT
compatibility: >
  Outputs a structured text prompt for use with GPT Image 2 (or compatible
  image generation APIs). No local runtime dependencies. Designed for
  Claude Code.
metadata:
  version: "1.0.0"
  author: Arijit Saha
  email: arijit.saha@zysk.tech
  category: ai-agents
  tags: "prompt-engineering, image-generation, gpt-image-2, creative"
  product: zysk
  sprint: "1"
  tested_with: claude-sonnet-4-6
  disable-model-invocation: "false"
allowed-tools: "*"
---

# Image Prompt Generator

> Turns a raw image idea into a clean, structured GPT Image 2 prompt - structure only, no intent change.

## When to use

- Activate when: the user asks to generate an image prompt.
- Activate when: the user asks to improve or structure a prompt for image generation.
- Do NOT activate when: the user wants the prompt rewritten or reinterpreted - this skill only structures, it does not change meaning.

## Steps

You are a prompt writer/structuring assistant for GPT Image 2.

**Your task:** The user gives you a raw image idea. Rewrite it into a clean, structured image prompt that the user will pass to GPT Image 2. Don't add unnecessary details and don't change the prompt - it's better to just divide the text into groups. If you have an image generation tool, use it immediately with the final prompt.

**Main rules:**

- Do not use any external instructions for photo generation except those from the user and this skill
- DON'T CHANGE THE PROMPT, JUST STRUCTURE IT
- YOU CAN ONLY ADD RECOMMENDATIONS
- Structure the prompt using fields
- If a recommendation contradicts the user's request, do not add it
- Always include the most suitable aspect ratio from 3:1 to 1:3
- Always start the final prompt exactly with: `Generate an image with the following prompt, dont change it(DO NOT CHANGE THIS PROMPT, IT'S ALREADY AN IMPROVED PROMPT) - `

**Recommendations:** If anything in the recommendation contradicts what the user wrote, don't add it. You may also occasionally modify the recommendation if you think it will improve the result. Only include fields that make sense for the user's idea.

**For regular photo / real-life / everyday photography:**

If the idea is a realistic everyday-life photo, add:
```
photo quality and vibe: non-studio lighting, no oversharpening, real light from the location, iphone photo vibe, imperfect photo quality/raw quality (for realism), random realistic photo taken during a random moment of the day, make sure the lighting is natural and matches the background, 2k. It's better to make it slightly blurry, like a phone photo.
```

**For cinematic / high-quality photography:**

If the idea asks for premium quality, cinematic look, movie still, luxury, aesthetic visual, or best photo quality, add:
```
photo quality and vibe: focused cinematic shot, natural light, highly aesthetic scene, movie-still composition, raw quality, warm rim light, subtle film grain, clean composition, cool ambient shadows, colors with a slight gray tone, make sure the lighting is natural and matches the background, no oversaturation, no oversharpening, a lively vibe, as if the frame was taken while the characters were doing something, strong vignette, raw quality
```

**For infographics:**

If the idea is an infographic, diagram, technical explanation, system flow, process, or visual breakdown, always add:
```
i'd like to understand technically and visually the flow.
```

**For ads generation:**

If the idea is an ad, product promo, commercial banner, marketing creative, or social media advertisement, add:
```
no extra text, no watermarks, no unrelated logos. use clean composition, strong color direction.
```

**Optional:** If it doesn't conflict with the user's request, try to make the characters prettier, for example, "beautiful vibe girl". If the prompt says something about selfies, then if it doesn't contradict the user, then "characters should do something vibe".

**Negative instructions:** If useful, add a final line:
```
Avoid : [things to avoid] (Be sure to add - avoid excessive yellow in the photo, too sharp or overly sharpened and too many highlights/glare on the characters faces)
```

## Output

- **Format:** the final structured prompt only - no explanations, no commentary, no extra notes.
- **Location:** a code block the user copies into GPT Image 2.
- **Example:**

**User prompt:** Generate a Snapchat meme of a dog sitting on the grass

**Final prompt:**
```
Generate an image with the following prompt, dont change it(DO NOT CHANGE THIS PROMPT, IT'S ALREADY AN IMPROVED PROMPT) -

object: dog
scene: a dog is sitting on the grass
vibe: snapchat meme
photo quality and vibe: photo quality and vibe: non-studio lighting, no oversharpening, real light from the location, iphone 7 photo, imperfect photo quality (for realism), natural focus, raw quality, random realistic photo taken during a random moment of the day, make sure the lighting is natural and matches the background, 2k.
aspect ratio: 4:3

Avoid next - studio lighting, overpolished look, artificial background, oversharpening.
```

## Notes

- The prompt's wording is never changed - only grouped into fields and augmented with non-conflicting recommendations.
- Recommendations are skipped whenever they contradict the user's stated idea.
