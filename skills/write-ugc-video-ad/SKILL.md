---
name: write-ugc-video-ad
description: Use when generating short-form video ad scripts (TikTok, Reels, Shorts) optimized for Google Flow/Veo 3. Triggers on requests for UGC scripts, high-retention video ads, or direct response video copy.
---

# Viral UGC Ads Script Generator v3 (The Blueprint Edition)

## Overview
This skill operates as a production-grade Creative Director. It plans the scene timing first, drafts to that plan, then checks the draft against the brief.

## Core Directives
1. **Blueprint first.** Build the Scene Blueprint before the script, because the timing decides what each scene can hold.
2. **Match the brief exactly.** A brief for 90 seconds and 9 scenes gets 90 seconds and 9 scenes.
3. **Physical Visuals.** Google Flow wants physical action (e.g., "Actor taps screen, graph collapses"), not just camera lenses.
4. **Check before delivering.** Fix any draft that misses a constraint, then deliver the corrected version.

## The Generation Pipeline

Work through these steps in order. The response contains the Scene Blueprint, the chosen framework and hook with a one-line reason each, the constraint check, and the script.

### Step 1: Constraint Extraction & Validation
Read the user's brief. Extract: `Duration`, `Scene Count`, `Platform`, `Audience`, `Language`, `Product`. 
If `Duration` or `Scene Count` are not provided, define them explicitly (Default: 60s, 6 scenes) before proceeding.

### Step 2: Scene Planner (The Blueprint)
Consult `planning-engine.md`. Do the math. Divide the duration by the scene count. Allocate specific time blocks to each scene.
Map the emotional arc across the requested number of scenes.

### Step 3: Story Engine & Hook Selection
Consult `workflow.md` to select the philosophical framework.
Consult `hook-library.md` to draft 3 candidate hooks and pick the strongest.

### Step 4: Script Drafting
Draft the script using:
- `cinematic-rules.md` for physical, Google Flow-optimized visual direction.
- `scene-system.md` to format the output. **Always use Production Mode unless Developer Mode is explicitly requested.**

### Step 5: Creative Director & Constraint Review
Consult `self-critique.md`.
Run the Hard Constraint Check (Expected vs Actual) and rewrite whatever misses.
Answer the creative review questions and rewrite the weak sections.

### Step 6: Final Output
Output the finalized, constraint-validated script.
