---
name: readme-drafter
description: Draft an initial project README from a user's project description. Use this skill whenever the user asks you to write, draft, or create a README, project description, or top-level docs for a new or early-stage project — even when they only give a paragraph or two of context. Also use when the user says things like "help me document this project," "I need a README for X," or hands you a repo and asks what should go in the top-level docs. Includes elicitation prompts to gather missing context before drafting, a default section structure, and an anti-pattern checklist to review the draft against before sending.
---

# README Drafter

Draft an initial project README from a user's project description. The
output is a developer-facing README for an early-stage project — the
first thing a new contributor or evaluator reads when they encounter
the repo.

## The job

A developer reading this README is deciding, within about 30 seconds,
whether to keep reading. The README must answer three questions fast:

1. **What is this?** — one sentence, no jargon
2. **Why would I use it instead of the alternatives?** — the
   distinctive bet the project is making
3. **How do I try it right now?** — concrete, runnable

Lead with these three. Everything else (architecture, roadmap,
contribution conventions) is secondary.

## Workflow

Follow these steps in order. Don't skip the elicitation step — it's
the single most important predictor of whether the draft will be
useful.

1. Read what the user provided. Identify which items from the
   **always-ask** list below are missing.
2. If there's a repo available, inspect it before drafting. The actual
   file structure trumps any description the user gives. If a function
   or module is referenced in your draft, verify it exists.
3. Ask for the missing pieces in a single batched message — not one
   question at a time. Frame each question so the user can answer
   briefly.
4. Draft the README following the structure in **Default structure**.
   Skip sections that don't apply rather than padding them.
5. Review the draft against the **Anti-patterns** checklist. Fix what
   you find.
6. Send the draft with an explicit list of:
   - Anything you marked aspirational or TBD
   - Claims you couldn't verify against the repo
   - Sections you skipped and why
   - Concrete follow-up offers ("want me to draft the LICENSE next?")

## Elicitation: what to ask

### Always ask (if not already provided)

Batch all of these into one message. Don't draft until you have answers.

- **Elevator pitch.** "If a developer at a conference asked what this
  is in one sentence, what would you say?" This becomes the README's
  first line.
- **Distinctive bet.** "What does this project do that competitors
  don't, or what does it bet on that they don't?" If the user can't
  answer, flag it — the README will be generic, and you should offer
  to draft a positioning section the user can fill in later.
- **Current status.** "What's actually built and working today vs.
  planned vs. aspirational?" Get specific. A feature that exists but
  hasn't been tested is different from one that exists and works.
- **Primary audience.** "Who is this for — end users, application
  developers, library consumers, contributors, AI agents, or some
  mix?" This shapes the quickstart.
- **Application, library, or both.** "Is this a thing people run, a
  thing people import, or both?" Affects quickstart structure.

### Ask if relevant

- **License intent.** Translate to a specific license rather than
  asking the user to know names. Example: "Open source friendly?
  Commercial use OK? Attribution required? Copyleft?" → MIT, Apache
  2.0, GPL, etc.
- **Comparable projects.** "What other projects occupy a similar space
  that you'd want to acknowledge or differentiate from?" Don't invent
  comparisons — only include projects the user names.
- **Roadmap.** "What are the next 2-3 things planned, in rough order?"
- **Name origin.** If the project name is unusual or evocative, ask
  what it means. A one-line gloss often earns its place.
- **Repo layout.** Either inspect it yourself or ask. Don't invent.

### Skip asking about

- Code of conduct, security policy, badges — add later if the user
  asks; don't bloat the initial README.
- Installation prerequisites you can read from the repo
  (`requirements.txt`, `pyproject.toml`, `package.json`, etc.).

## Drafting principles

**Lead with what works.** If the user has built one piece of a larger
vision, the quickstart uses that piece. Aspirational examples
("imagine you could...") destroy credibility. Real working examples
build it.

**Be precise about status.** Use a status column in the roadmap, or
inline markers (✓ shipped, planned, aspirational). Vague verbs like
"supports" and "provides" become lies the moment they're not strictly
true.

**Show, don't claim.** Every behavioral claim should be backed by
either a code snippet or a pointer to the file that implements it.

- Weak: "Tartarus deduplicates URLs intelligently"
- Strong: a code block showing input and output

**Adopt the user's framing.** If they call it a "knowledge base," don't
rewrite it as a "memory layer." If they invoke specific inspirations,
keep them. Your job is to make their vision legible, not substitute
your own.

**Honest comparisons.** When listing related work, characterize each
project accurately and call out the genuine distinction rather than
claiming superiority.

- Weak: "but ours is better"
- Strong: "more opinionated about X; less focused on Y"

## Default structure

Use this order. Sections are optional unless marked required. Omit
sections that don't apply rather than padding them.

1. **Title and tagline** (required) — Project name, then a
   one-sentence description. No marketing copy.
2. **Name-origin blockquote** (optional) — One or two lines if the
   name has meaning worth knowing.
3. **Status line** (required if not 1.0) — One line. "Status: early,"
   "Status: beta," "Status: production." Include what specifically
   works today.
4. **Why** — Problem the project solves and the bet it makes. 2-4
   short paragraphs. Skip if the project is purely utilitarian (small
   CLI tool, small library).
5. **Design principles or philosophy** — Only if the project has them
   and they constrain how it gets built. 3-6 commitments. Skip for
   small projects.
6. **Architecture** — ASCII diagram showing main components and data
   flow. Skip if there's only one component. ASCII is preferred over
   image assets for portability.
7. **Quickstart** (required) — Concrete, runnable. If the project is
   both an application and a library, show both modes on the same
   example. Use real input and real output.
8. **Repository layout** — Tree showing where things live. Mark
   aspirational paths if any. Skip for single-file projects.
9. **Extending / using the primitives** — How others build on this.
   For library-style projects, show how to use individual functions in
   isolation. Skip for application-only projects.
10. **Roadmap** — Table with stage / status / notes columns. Honest
    about shipped vs. planned. Skip for stable projects.
11. **Contributing** — One paragraph plus a pointer to a full guide if
    one exists. Skip if not open to contributions.
12. **Related work** — Honest characterization of similar projects.
    Skip if the user can't name any.
13. **License** (required if it exists) — One line plus a link to the
    file.

## Tone

- Confident but honest. The project should sound worth using without
  pretending it's more done than it is.
- Concrete nouns and verbs. Avoid "powerful," "robust," "seamless,"
  "intuitive," "cutting-edge."
- Active voice. "Tartarus stores X," not "X is stored by Tartarus."
- No emoji in section headers unless the user uses them. Sparingly
  elsewhere if at all.
- No AI-generated-README tells: marketing-flavored bullet lists,
  feature-grids of vague capabilities, "elevate your workflow" copy.

## Anti-patterns

Review every draft against this checklist before sending. These are
the most common AI-README failure modes.

- **Fake examples.** Code blocks showing imports and function calls
  that don't actually exist. Verify before including; if you can't
  verify, mark the example as aspirational or omit it.
- **Vague claims.** "Fast," "scalable," "easy to use" with no
  evidence. Replace with specifics or remove.
- **Premature scaffolding.** Sections for code of conduct, security
  policy, FAQ, contributors list when the project has none of those
  things yet.
- **Roadmap as wishlist.** A roadmap with 30 items in no clear order
  is noise. 5-10 items with clear status and rough order is signal.
- **Over-claiming uniqueness.** Almost no project is genuinely the
  first or only thing in its space. Acknowledge prior art.
- **Hidden status.** Mixing "shipped" and "planned" features in the
  same paragraph without distinguishing them. A reader should never
  have to guess what they can run today.
- **Invented relationships.** Don't claim a project is "inspired by"
  or "similar to" anything the user didn't mention.
- **Bloat.** A README over ~400 lines is almost always padded. Split
  into a short README plus a longer design doc.

## Length

A first README for an early project should be roughly 150-400 lines.
Longer is fine if the project is mature and the content earns it;
shorter is fine for genuinely small projects. If you're approaching
500 lines on an early project, cut.

## When sending the draft

Include a short post-draft note that covers:

- **What you skipped and why.** Don't make the user wonder whether you
  forgot a section or deliberately omitted it.
- **What you couldn't verify.** Any claim about behavior, file
  structure, or function signatures that you couldn't check against
  the repo.
- **What you'd offer next.** Concrete follow-ups: drafting a
  CONTRIBUTING.md, writing a design doc for a specific module, helping
  decide a TBD (license, name, etc.).

This makes the draft a starting point for collaboration rather than a
take-it-or-leave-it artifact.

## Examples

### Example 1: minimal description, single-file project

**Input from user:** "I made a small Python utility that converts CSV
files to nicely formatted markdown tables. Can you write a README?"

**Approach:** Ask the always-ask items in a batched message, then
inspect the file. Likely a short README — maybe 80 lines — with
title, status, quickstart (both CLI and library usage), and
optionally a tiny design-decisions paragraph. Skip architecture,
roadmap, related work unless the user asks for them.

### Example 2: vision-stage project with one working piece

**Input from user:** "I'm building a personal knowledge base called X.
Right now I have a script that does Y. Eventually it'll do Z and W."

**Approach:** Status line is essential here — make sure the reader
knows Y works and Z/W don't. Quickstart uses Y. Roadmap lists Y as
shipped, Z and W as planned with rough order. Related work section
worth asking about since this kind of project has obvious neighbors.

### Example 3: mature library

**Input from user:** "I have an established Python library for X. It
needs a README refresh — the current one is outdated."

**Approach:** Read the current README and the repo first. Ask what
specifically is outdated. Status line probably not needed (it's a
mature library). Focus on quickstart and a clean API overview. Roadmap
optional. Related work probably worth including for positioning.