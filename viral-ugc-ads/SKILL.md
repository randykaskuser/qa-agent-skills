---
name: viral-ugc-ads
description: Use when generating short-form video ad scripts (TikTok, Reels, Shorts) optimized for Google Flow/Veo 3. Triggers on requests for UGC scripts, high-retention video ads, or direct response video copy.
---

# Viral UGC Ads Script Generator v2 (Creative Director Edition)

## Overview
This skill operates as a production-grade Creative Director. It does not just fill templates. It uses a decision engine to generate candidate hooks, scores them, selects the best, writes the script using strict cinematic rules, and performs a rigorous self-critique before finalizing the output.

## Core Directives
1. **Never use the first hook generated.** Always generate at least 3, score them, and pick the winner.
2. **Never keep a shot static.** Enforce the 2.5-second cinematic rule.
3. **Never output the first draft.** Always run Self-Critique and rewrite weak sections.
4. **Always use granular Google Flow visual tags.** (Shot, Lens, Lighting, Motion, DOF, Overlay, Subtitle, Sound Cue).

## The Decision Engine Workflow

When generating a script, you MUST execute these steps in order, *and show your work*:

### Step 1: Story Engine Selection
Consult `workflow.md`. Choose the most appropriate Story Framework (Pain/Enemy, Prediction/Reveal, Challenge/Proof, or Story/Conflict) based on the product and audience. State your choice.

### Step 2: Hook Generation & Scoring
Consult `hook-library.md`. 
- Generate AT LEAST 3 candidate hooks. 
- Reject generic hooks, greetings, product intros, and explanations.
- Score each candidate (1-10) on: Curiosity, Shock, Novelty, Relatability, and Swipe Risk (lower is better).
- Sum the scores. Choose the highest-scoring hook.

### Step 3: Script Drafting
Draft the script using:
- `scene-system.md` for the exact metadata and Google Flow visual structure.
- `cinematic-rules.md` to ensure aggressive pacing and motion.
- `voiceover-library.md` for emotional tone tagging.

### Step 4: AI Self-Critique
Run the draft through the strict review engine defined in `self-critique.md`.
Score Hook, Retention, Visual, Voice, and CTA out of 10.
Provide reasons. If any score is < 8/10, REWRITE that section immediately.

### Step 5: Final Output
Output the finalized, polished script ready for production.
