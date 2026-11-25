---
name: technical-blogger
description: Write, edit or translate a technical article — engineering post, tutorial, investigation, case study, benchmark or SOP — built around one main claim, with facts, observations, measurements and hypotheses kept apart. Use when the user wants to draft, rewrite or translate (EN/ID) a technical blog post or procedure. Not for checking a finished draft before publish (use technical-blogger-reviewer).
---

# Technical Blogger

Write and refine technical articles, investigations and Standard Operating Procedures (SOPs).

Settle the article type, main claim and evidence (Phases 0–2) before drafting, because they decide the structure. Pick the structure that fits the type rather than defaulting to "Problem → Solution".

## Phase 0 — Determine Article Type
Choose ONE article type that defines the structure and intent:
- **SOP / Procedural:** Goal is to *Teach an exact execution protocol* (e.g., Emergency cloudy eye treatment).
- **Investigation / Field Notes:** Goal is to *Convince the reader of a hypothesis or observation* (e.g., DJI O4 Pro low-frequency vibration sensitivity).
- **Tutorial / How-To:** Goal is to *Teach a reproducible implementation* (e.g., Setting up Playwright MCP).
- **Case Study / Incident Report:** Goal is to *Analyze what happened, why it broke, and lessons learned*.
- **Review / Benchmark:** Goal is to *Evaluate expectations vs. measured reality*.

## Phase 1 — Determine the Single Main Claim
You must complete and explicitly state this sentence before outlining:
> **"This article exists to convince the reader that __________________."**
*(Example: "This article exists to convince the reader that cloudy eye in predator fish is caused by ammonia burn, not bacteria, and requires daily full-tank dosing." OR "This article exists to convince the reader that O4 Pro jitter is a hardware sensitivity issue, so don't blame your tuning.")*
**Every single paragraph in the article must support this main claim.**

## Phase 2 — Determine Evidence Level (Epistemological Rigor)
You must strictly separate facts from assumptions. In technical writing (especially like Cloudflare or OpenAI Research), you must categorize information into:
1. **Known:** Proven vendor specs or established science.
2. **Observed:** What was visually or operationally witnessed.
3. **Measured:** Hard data (e.g., Blackbox logs, pH/Ammonia ppm, runtime ms).
4. **Suspected / Hypothesis:** Educated engineering theory based on evidence.
5. **Speculation / Unknown:** Explicitly declared limitations and unanswered questions.
*Never state a hypothesis as a proven fact.*

## Phase 3 — Build Argument Hierarchy (Type-Specific Outlines)
DO NOT use a generic "Problem → Solution" outline. Use the hierarchy matching the Article Type from Phase 0:

### For Investigation / Field Notes:
1. What We Know (Baseline context)
2. What We Observed (The anomaly)
3. What is Consistent across occurrences
4. What is Inconsistent / Counter-evidence
5. The Hypothesis (Why we suspect X)
6. What Remains Unconfirmed (Explicit boundaries of claims)
7. Practical Takeaways / Risk Mitigation

### For SOP / Procedural:
1. Core Understanding (Why common folk remedies fail)
2. Pre-treatment Preparation & Assumption Declarations (e.g., "All doses based on 100L")
3. Tools & Chemical Mechanics (Why each chemical is used)
4. Operational Dosage Table (with explicit reference volumes)
5. Daily Execution Protocol (Day-by-day actions)
6. What to Avoid (and WHY)
7. Recovery Phase

### For Tutorial / Case Study:
1. Context & Objective
2. Constraints & Trade-offs
3. Architecture / System Design
4. Implementation Step-by-Step
5. Verification & Testing
6. Limitations & Future Scope

## Phase 4 — Technical Drafting Rules (Anti-AI Tone)
When drafting, you must follow these strict style rules:
- **Be spartan and informative.** Use short, impactful sentences.
- **Use active voice.** Avoid passive voice.
- **Punctuation strictness:** AVOID em dashes (—). Use commas, periods, or semicolons. Use headings, tables and lists where the content needs them (a dosage table, numbered steps), and plain prose elsewhere; keep emphasis asterisks out of body prose.
- **NO DRAMA OR FLUFF:** Do not write dramatic conclusions (e.g., "This tests your discipline"). Conclusions must reinforce the **Single Main Claim** from Phase 1.
- **Plain words.** Write the way one engineer explains something to another: concrete nouns and verbs, no hype, no stock openers or closers. Cut an intensifier or hedge that adds nothing. Keep a hedge that marks real uncertainty, because Phase 2 depends on it.

## Phase 5 — Reader Simulation & Actionability Test
Before returning the draft, simulate being the reader:
- *If this is an SOP:* "I have an arbitrary tank/system size. Can I execute this without asking a single clarifying question? Are all units and reference volumes explicit?"
- *If this is an Investigation:* "Did this article convince me of the Main Claim? Did it clearly separate measured facts from speculation?"
If "No", rewrite immediately.

---

## IF EDITING AN EXISTING ARTICLE
1. Identify the Article Type (Phase 0) and Single Main Claim (Phase 1).
2. Jump directly to Phase 5 (Reader Simulation) to audit the draft against its specific Argument Hierarchy (Phase 3) and Evidence Level (Phase 2).
3. Present your audit, identifying where the article loses its Main Claim or blurs speculation with fact.
4. Rewrite the failing sections according to Phase 4 (Technical Drafting Rules).

## MDX Frontmatter & Multilingual Rules
- Ensure exact MDX frontmatter: `title`, `description`, `locale`, `domain`, `slug`, `canonicalGroup`, `publishedAt`, `updatedAt`, `tags`, `featured`, `draft`, `coverImage`.
- **Translations:** DO NOT summarize. Preserve hierarchy and evidence levels.
- **Indonesian:** Keep standard technical terms in English, because Indonesian practitioners code-switch (e.g., "water changes", "siphon", "biological filter", "ammonia", "crash", "micro-jitter", "blackbox", "throttle punch", "low-pass").

---
**Execution Instructions:** 
Start by outputting Phase 0 (Article Type), Phase 1 (Single Main Claim), and Phase 2 (Evidence Level). Ask for user confirmation before building the Outline (Phase 3).