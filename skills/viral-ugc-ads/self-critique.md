# AI Self-Critique & Constraint Validator

You must execute a ruthless review before outputting the final script. This is not a soft creative review; this is a compliance check.

## Phase 1: Hard Constraint Validator (Must Pass)

You must explicitly list the requested constraints vs. the actual output.

```markdown
### Constraint Validator
- **Duration:** Expected [X]s | Actual [Y]s -> [PASS/FAIL]
- **Scene Count:** Expected [X] | Actual [Y] -> [PASS/FAIL]
- **Language:** Expected [Language] | Actual [Language] -> [PASS/FAIL]
- **Platform:** Expected [Platform] | Actual [Platform] -> [PASS/FAIL]
```

**Rule:** If ANY of these result in `FAIL`, you MUST output `FAIL - Rewrite Required` and completely rewrite the script to meet the constraints. You cannot proceed to Phase 2.

## Phase 2: Creative Director Review

Score the following elements out of 10. Be harsh. 

### 1. The Demo & Proof Check (Score: X/10)
- Is the Demo an actual transformation? (e.g., "Blank page -> Copy -> Paste -> Video ready")
- Is the Proof concrete? (e.g., "Analytics jump from 210 to 12K", not just "Imagine getting views").
- *Rewrite needed? (Yes/No)*

### 2. Google Flow Physicality (Score: X/10)
- Are the visuals physical actions? (e.g., "Actor taps analytics. Graph instantly collapses. Phone vibrates.")
- Did you avoid boring, static metadata lists (Lens, Lighting) in Production Mode?
- *Rewrite needed? (Yes/No)*

### 3. Pacing & Hooks (Score: X/10)
- Is the 2.5-second cinematic rule enforced?
- Is the hook generic?
- *Rewrite needed? (Yes/No)*

### 4. CTA (Score: X/10)
- Is it a hard, logical prerequisite to the value?
- *Rewrite needed? (Yes/No)*

If any score is < 8/10, state the reason and rewrite that specific section.
