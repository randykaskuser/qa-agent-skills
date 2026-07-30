# Visual Language & Google Flow Constraints

## Google Flow Prompting Principles

Google Flow and Veo 3 require specific, descriptive, physical language. They do not understand marketing concepts. You must describe the *scene*, not the *message*.

**Bad**: "Show the user feeling frustrated with their low engagement."
**Good**: "Close up of a tired man in his 20s, holding a glowing smartphone in a dark room. He sighs and rubs his eyes. The screen reflects on his face."

## Camera Direction Glossary

Always use precise camera terminology in the `Visual:` block:

### Angles
- **Extreme Close Up (ECU)**: Eyes only, or just a mouth. High intensity.
- **Close Up (CU)**: Face and shoulders. Good for direct address.
- **Medium Shot (MS)**: Waist up. Good for demonstrating objects with hands.
- **Over the Shoulder (OTS)**: Looking at a screen or object from the actor's perspective.
- **POV (Point of View)**: Camera is the actor's eyes.
- **High Angle**: Looking down. Makes subject look small/struggling.
- **Low Angle**: Looking up. Makes subject look powerful/confident.

### Movements
- **Snap Zoom**: Very fast zoom in to emphasize a point.
- **Slow Push**: Gradual creep inward to build tension.
- **Whip Pan**: Fast blur transition to a new subject.
- **Handheld**: Slight shake, feels authentic/raw UGC.
- **Static/Locked off**: Tripod shot, feels stable/professional.

## Lighting & Environment

Always specify the environment to maintain consistency.
- **Ring Light / Creator Setup**: Bright, even lighting, LED strips in background. (Standard UGC look).
- **Cinematic Dark**: Moody, single light source, dark background. (For serious or high-value topics).
- **Natural Light / Window**: Soft, authentic, daytime. (For relatable, casual lifestyle hooks).

## On-Screen Text (Overlays)

Text on screen is as important as the voiceover.

### Rules for Overlays:
1. **Never transcribe the VO exactly**. If the VO says "This is why your videos are failing," the text should say "Reason 1:" or "Failing videos?".
2. **Keep it short**. Max 4-5 words per text pop.
3. **Use UI elements**. Instead of plain text, use:
   - Fake tweet bubbles
   - iOS notification popups
   - Progress bars
   - Analytics charts (green arrows going up, red going down)
   - Comment bubbles

## Props and Actions

Props add realism and give actors something to do with their hands.
- **The Phone Hold**: Actor holds phone in one hand, pointing at it with the other.
- **The Drink Sip**: Starting a video by taking a sip of coffee/matcha (creates a natural pause).
- **The Walk and Talk**: Actor walking down a street holding the camera (adds kinetic energy).
- **The Desktop Point**: Pointing at a laptop screen with a pen.

## Google Flow Specific Prompt Construction

When generating the final visual directions, format them so they can be easily adapted into Google Flow prompts:

`[Shot Size] + [Subject Description] + [Action] + [Environment] + [Lighting] + [Camera Movement]`

*Example for Script output:*
**Camera**: Close up, young woman in hoodie, holding a coffee cup, sitting in a messy bedroom, natural morning light, handheld slight shake.
