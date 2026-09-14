---
name: viral-ugc-ads
description: Use when generating short-form video ad scripts (TikTok, Reels, Shorts) optimized for Google Flow/Veo 3. Triggers on requests for UGC scripts, high-retention video ads, or direct response video copy.
---

# Viral UGC Ads Script Generator v3 (The Blueprint Edition)

## Overview
This skill operates as a production-grade Creative Director. It relies on a strict **Planning Layer** and **Constraint Enforcement**. It does not jump straight to writing. It calculates, plans, drafts, and ruthlessly critiques.

## Core Directives
1. **Never start writing immediately.** You MUST build a Scene Blueprint first.
2. **Obey Hard Constraints.** If the user asks for 90 seconds and 9 scenes, you output EXACTLY 90 seconds and 9 scenes.
3. **Physical Visuals.** Google Flow wants physical action (e.g., "Actor taps screen, graph collapses"), not just camera lenses.
4. **Ruthless Self-Critique.** If the draft fails the constraint check, you MUST rewrite it. No excuses.

## The Generation Pipeline

When generating a script, you MUST execute these steps in order and explicitly show your work in the response:

### Step 1: Constraint Extraction & Validation
Read the user's brief. Extract: `Duration`, `Scene Count`, `Platform`, `Audience`, `Language`, `Product`. 
If `Duration` or `Scene Count` are not provided, define them explicitly (Default: 60s, 6 scenes) before proceeding.

### Step 2: Scene Planner (The Blueprint)
Consult `planning-engine.md`. Do the math. Divide the duration by the scene count. Allocate specific time blocks to each scene.
Map the emotional arc across the requested number of scenes.

### Step 3: Story Engine & Hook Selection
Consult `workflow.md` to select the philosophical framework.
Consult `hook-library.md` to generate 3 candidate hooks, score them, and pick the winner.

### Step 4: Script Drafting
Draft the script using:
- `cinematic-rules.md` for physical, Google Flow-optimized visual direction.
- `scene-system.md` to format the output. **Always use Production Mode unless Developer Mode is explicitly requested.**

### Step 5: Creative Director & Constraint Review
Consult `self-critique.md`.
Run the Hard Constraint Check (Expected vs Actual). If it fails, state `FAIL - Rewrite Required` and generate again.
Score the creative elements. If any score < 8/10, rewrite.

### Step 6: Final Output
Output the finalized, constraint-validated script.
