# Scene System & Output Formats

Every scene in the final output must adhere to the selected Output Mode. 

## Default: Production Mode
Unless the user explicitly asks for "Developer Mode", always output the script using **Production Mode**. This keeps the focus on creative direction, physical action, and copy, rather than burying the user in technical metadata.

```markdown
---
## Scene [Number] — [Scene Type/Role] ([Duration]s)

**Goal:** [Psychological Objective]
**Emotion:** [Target Viewer Emotion]

**Visual:** 
[Rich, physical Google Flow description. e.g., Actor taps analytics. Graph instantly collapses. Phone vibrates. Camera slowly pushes into an exhausted exhale.]

**Voiceover:**
**Tone:** [Emotional Delivery Style]
[Line 1 - Max 10 words]
[Line 2 - Max 10 words]
```

## Optional: Developer Mode
Only use this if explicitly requested. It includes full Google Flow parameters.

```markdown
---
## Scene [Number] — [Scene Type/Role] ([Duration]s)

### Psychological Strategy
- **Goal:** [Why this scene exists]
- **Target Emotion:** [e.g., Frustration]
- **Viewer Inner Thought:** ["What the viewer should be thinking"]

### Visual Direction (Google Flow Metadata)
- **Shot:** [e.g., Close Up (CU)]
- **Lens:** [e.g., 35mm]
- **Lighting:** [e.g., Dark room, screen glow]
- **Environment:** [e.g., Messy home office desk]
- **Camera Motion:** [e.g., Handheld slight shake -> Snap Zoom at 0:02]
- **Depth of Field:** [e.g., Shallow]
- **Physical Action:** [e.g., Actor taps screen, graph collapses]
- **Overlay:** [e.g., Red declining graph graphic]
- **Subtitle:** [e.g., Bold yellow text]
- **Sound Cue:** [e.g., SFX: Glitch sound]

### Voiceover
**Tone:** [Emotional Delivery Style]
[Line 1 - Max 10 words]
[Line 2 - Max 10 words]
```
