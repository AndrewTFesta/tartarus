# Trigger Tests — `readme-drafter`

15 test cases for evaluating whether the `readme-drafter` skill
triggers when it should and stays quiet when it shouldn't. JSON form
at `evals/trigger_tests.json` for machine runs.

## Summary

| Category | Should fire | Count |
|----------|-------------|-------|
| Clear positives | ✓ | 5 |
| Implicit positives | ✓ | 3 |
| Adversarial negatives | ✗ | 5 |
| Edge cases | varies | 2 |
| **Total** | | **15** |

Target rates:
- Clear positives: ~100% trigger rate (anything less is a serious gap)
- Implicit positives: ~80%+ (some miss is acceptable; users can rephrase)
- Adversarial negatives: <20% trigger rate (over-triggering is more annoying than under-triggering)
- Edge cases: whichever way matches your design intent

## Clear positives — should fire

These should reliably trigger the skill. If any of them fail, the
description is too narrow.

| # | Query | Notes |
|---|-------|-------|
| 1 | "Can you write me a README for my project? It's a small Python CLI that converts CSVs into markdown tables." | Canonical trigger: explicit ask + project context. |
| 2 | "I need to draft a README.md for the repo I just made. Here's the project description: [paragraph about a knowledge graph tool]" | Same intent, different phrasing. |
| 3 | "Help me write up what this project does. It's an early-stage tool for syncing notes between Obsidian and an SQLite store." | README-language without the word "README." |
| 4 | "I just pushed my code to GitHub and the repo looks naked. What should I put in the top-level docs?" | "Top-level docs" + "naked repo" = first-README signals. |
| 5 | "Create a README for this codebase." | Minimal phrasing. No project info — skill should fire and elicit. |

## Implicit positives — should fire

The user wants a README but doesn't use the word. These test whether
the skill catches the intent.

| # | Query | Notes |
|---|-------|-------|
| 6 | "I built a tool and I want to share it. How should I document it for other developers?" | Documenting a tool for developers = README. |
| 7 | "I'm open-sourcing my side project this week. Can you help me get the docs ready for the launch?" | Open-sourcing context strongly implies README. |
| 8 | "What's a good first thing to write when starting a new repo, before adding any code?" | The "good first thing" for a new repo is the README. Subtler than 6/7. |

## Adversarial negatives — should NOT fire

These are the false-positive traps. Each one is plausibly README-adjacent
but isn't a drafting request.

| # | Query | Why it shouldn't fire |
|---|-------|----------------------|
| 9 | "Can you explain what a README typically contains? I want to understand the conventions before I write my own." | Informational, not a draft request. |
| 10 | "There's a typo in my README on line 14. Can you fix it?" | Edit, not draft. One-line fix. |
| 11 | "Write me a short description of what Python is good for." | About a language, not a project. |
| 12 | "Can you draft a README for the conference room booking process at my office?" | Uses the word "README" but not for software. Tests over-reliance on the literal word. |
| 13 | "My README is too long and reads like a sales pitch. Can you tighten it up and make it more honest?" | Editing existing, not drafting. Skill is scoped to initial drafts. |

## Edge cases — design decision

Both could legitimately go either way. The "should it fire" call
depends on how broadly you want this skill scoped.

| # | Query | Tension |
|---|-------|---------|
| 14 | "I have a Python library and a CLI tool that both wrap the same core logic. I want to publish them as one package. How should I structure the top-level documentation so both audiences are served?" | Asking an architectural question about docs that strongly implies README work. Skill could fire and offer to draft, or could just answer architecturally. |
| 15 | "Here's the current README for my project. Can you make it better?" | Existing README + improvement request. Scoping the skill to initial drafts says no fire; broadening to all README work says yes. |

Both edge cases double as scope-setting prompts: if your gut says the
skill should fire on #14 or #15, the description needs to be widened.
If your gut says it shouldn't, the current scope is right.

## How to run

If using the skill-creator tooling:

```bash
python -m scripts.run_loop \
  --eval-set evals/trigger_tests.json \
  --skill-path . \
  --model <model-id> \
  --max-iterations 5 \
  --verbose
```

This runs each query 3 times against the skill's description and
reports trigger rates per category, then proposes description
improvements based on what failed. Splits 60/40 train/test internally
to avoid overfitting.

If running manually (light-tier eval), just present each query to a
Claude instance with the skill installed and note whether it activates.
3 runs per query is enough to spot consistent vs. flaky behavior.

## What to look for in the results

- **Pattern of failures across categories.** Consistent miss on
  implicit positives = description too literal (anchors only on "README"
  rather than intent). Consistent false-fire on adversarial negatives =
  description too broad (matches anything documentation-adjacent).
- **Variance within a category.** If 4 of 5 clear positives fire
  reliably and one is flaky, the flaky one is telling you something
  specific — probably a phrasing the description doesn't anticipate.
- **Edge case outcomes.** These are the scope decisions you've now
  made through testing rather than through guessing. Update the skill
  description to match what you decided.
