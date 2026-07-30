# Creative Director Cinematic Rules (Google Flow Optimized)

Google Flow and Veo 3 require granular, physical, cinematic language. A script that says "show the user looking sad" will fail. A script that specifies camera lenses, lighting, and motion will succeed.

## The 2.5-Second Rule
**NEVER keep the same shot for more than 2.5 seconds.**
If a scene duration is 5 seconds, it MUST contain at least two shots, or a dynamic camera movement combined with an overlay pop.

Every single scene MUST include AT LEAST THREE of the following elements:
- Motion (Actor physical movement)
- Overlay (UI pop, text, tweet bubble)
- Camera Movement (Zoom, push, pan)
- Object Interaction (Holding, dropping, pointing)
- Transition (Match cut, smash zoom, whip pan)
- Sound Cue (Implied sound design for Google Flow)

## Granular Google Flow Tagging
Every scene's `Visual` block must be structured using these exact cinematic parameters:

- **Shot:** Extreme Close Up (ECU), Close Up (CU), Medium Shot (MS), Over The Shoulder (OTS), POV, Macro.
- **Lens:** 24mm (Wide, slightly distorted/raw UGC), 35mm (Standard eye-level), 50mm (Cinematic portrait, flattering), 85mm (Extreme close up portrait).
- **Lighting:** Ring Light (Classic UGC), Natural Window Light (Soft, lifestyle), Dark Bedroom/Screen Glow (Late night worker), Studio Neon (Tech/modern), Harsh Sunlight (Outdoor/active).
- **Environment:** Specific location details (Messy desk with empty coffee cups, minimalist white office, cafe table, gym floor).
- **Camera Motion:** Static Tripod, Handheld Slight Shake (Raw UGC feel), Snap Zoom In, Whip Pan Left/Right, Slow Cinematic Push, Tracking Shot.
- **Depth of Field (DOF):** Shallow (Blurry background, focuses on face/prop), Deep (Everything in focus, good for environments/rooms).
- **Facial Expression:** Explicit physical cues (Furrowed brow, wide eyes, deadpan stare, smirking, sighing, rapid blinking).
- **Overlay:** Exact text, UI elements, charts, notification popups, progress bars.
- **Subtitle:** Typography style (e.g., "Large yellow Hormozi-style text", "Minimalist white text", "Bold red typewriter").
- **Sound Cue:** Audio to accompany the visual (e.g., "SFX: Heavy thump as book drops", "SFX: iPhone notification ping", "SFX: Camera shutter").

## Example of a Fully Compliant Visual Block:
```markdown
**Visual:**
- Shot: Close Up (CU)
- Lens: 35mm
- Lighting: Screen Glow in a dark bedroom
- Environment: Home office desk, messy background
- Camera Motion: Handheld slight shake -> Snap Zoom at 00:02
- Depth of Field (DOF): Shallow
- Facial Expression: Exhausted, rubbing temples, squinting at screen
- Overlay: Red declining analytics chart pops up at top right
- Subtitle: Bold Yellow, high contrast
- Sound Cue: SFX: Glitch sound when chart pops up
- Transition: Whip pan right on "But it's not..."
```
