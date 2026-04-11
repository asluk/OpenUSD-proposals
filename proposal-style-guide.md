# Proposal Style Guide

## Using PR #105 as a Structural Template

This guide captures lessons learned from drafting the Exact Geometry
Problem Statement proposal using PR #105 (Source Identifiers) as a
structural model. It is intended for anyone — human or AI — drafting
future OpenUSD proposals who wants the organizational clarity of
PR #105 without producing prose that reads like a copy.

### Audience Constraints

Several TAC reviewers are AI-cautious. They will scrutinize documents
that feel templated, repetitive across proposals, or that pattern-match
to LLM output. The goal is a document that feels *familiar* in
organization but *fresh* in voice. As Aaron put it: "the reading
experience should feel familiar but not repetitive."

---

## 1. What to Borrow: Structural Template

PR #105 established a section progression that works well for problem
statement proposals. Reuse the *skeleton*, not the *sentences*.

### Section Order (proven effective)

1. **Introduction** — Frame the gap. 3–5 paragraphs max.
2. **Motivation / Problem Statement** — Why now, what's broken.
3. **Industry Use Cases** — Domain-grouped evidence. Anchor with
   1–2 cross-cutting "hero" use cases before domain-specific material.
4. **Existing Mechanisms in USD** — What USD already offers, where
   it falls short. Be precise about schema types, precision, and
   actual API surface.
5. **Design Considerations** — Numbered principles, open questions,
   risks. This is where reviewers spend the most time.
6. **Relationship to Other Proposals** — How this fits the broader
   landscape.
7. **Next Steps** — Concrete, sequenced.
8. **Appendices** — Glossaries, AI disclosure, supplementary data.

### Folder Naming

PR #105 used `identifier_separation_of_concerns`. Do *not* mirror
the naming pattern directly — e.g., `exact_geometry_separation_of_concerns`
is too symmetric. Choose a name that reflects your proposal's specific
framing: `exact_geometry_problem_statement` is better.

### Target Length

~400–600 lines for a problem statement. PR #105 landed at ~1209 lines
but that includes a full comparison analysis. A pure problem statement
should be leaner.

### Table of Contents

Include one. PR #105's TOC style (linked markdown headers) is
effective and worth reusing directly — no one will notice a TOC
format echo.

---

## 2. Prose Differentiation: Varying the Voice

This is the most important section. Structural similarity is
acceptable; prose similarity is not. The following patterns were
identified as echoes between PR #105 and the first draft of the
exact geometry proposal, and should be avoided in future proposals.

### Opener Patterns to Avoid

PR #105 opens with a construction like:

> "As OpenUSD adoption [verb]... a [noun] has emerged"

Do not replicate this. Lead with the *gap* or the *consequence*, not
the growth narrative. Example alternative: start with what users
cannot do today and why it matters.

### The Pivot Sentence

PR #105 uses:

> "[X] serves [domain] well. They are insufficient for [Y]."

This "works for A, breaks for B" pivot is effective but becomes a
fingerprint when repeated across proposals. Alternatives:

- Lead with the insufficiency: "USD's mesh primitives assume the
  geometry is already tessellated..."
- Use a concrete scenario: "When an engineer imports a turbine blade
  into a USD pipeline, the first step is..."
- Merge the pivot into a single sentence: "While subdivision surfaces
  handle organic forms, they discard the parametric definitions that
  CAD workflows depend on."

### Bold-Opener Numbered Lists

PR #105 uses many numbered lists where each item starts with a bold
term followed by a description. This rhythm is fine occasionally, but
if every list in your proposal follows the same pattern, vary it:

- Use a mix of bold-lead and plain-sentence items
- Occasionally use paragraphs instead of lists for 3-item sets
- Turn some lists into short tables when the data is genuinely tabular

### Sentence Cadence

PR #105 tends toward short declarative pairs:

> "X is Y. Z is W. This means Q."

Break this up with:

- Compound sentences joined by em dashes or semicolons
- Longer sentences that embed the qualifier inline ("...which, unlike
  tessellated meshes, preserves the original parametric definition")
- Questions ("What happens when a pipeline receives a STEP file?")
- Leading with dependent clauses ("Because USD currently lacks...")

### Paragraph Openings

If three consecutive paragraphs start with the subject-verb pattern
("USD provides...", "USD supports...", "USD lacks..."), at least one
should lead differently — with a prepositional phrase, a scenario, or
a dependent clause.

### Transitions Between Sections

PR #105 tends to end sections cleanly and start the next with a
topic sentence. This is fine for some transitions, but add variety:

- Use a bridge sentence at the end of one section that previews the
  next ("With the problem scoped, the question becomes what USD
  already offers.")
- Start a section with a question
- Start with a concrete example that the section will then generalize

### The "Core Observation" Pattern

PR #105 uses "The core observation is that..." or similar framing
devices. These are effective *once*. Do not replicate them. Find
your own framing device, or better, let the evidence lead to the
conclusion without announcing it.

---

## 3. Quality Passes

After the draft is structurally complete, run these passes in order.
Each pass has a distinct focus. Do not combine them — you will miss
things.

### Pass 1: Overconfident Claims

Read every assertion and ask: "Can I verify this?" Flag:

- **Universals** ("all", "every", "always", "never", "universally")
  — downgrade to "nearly all", "most", "typically"
- **Unverifiable numbers** ("millions of users", "billions of
  dollars") — replace with qualitative language ("large user bases",
  "significant market") or cite a source
- **Industry requirements stated as fact** ("This is a hard
  requirement") — hedge to "widely regarded as a prerequisite" or
  "commonly expected"
- **Absolute technical claims** ("X is unreliable", "Y is
  impossible") — soften to "X is challenging", "Y has not been
  demonstrated"

The principle: reviewers who care about rigor will catch overstated
claims and discount the entire section. Hedging costs nothing;
overclaiming costs credibility.

### Pass 2: Fact-Check

Verify every factual claim against primary sources. LLMs hallucinate
technical details with high confidence. In the exact geometry
proposal, 5 factual errors were found across 680 lines. Common
failure modes:

- **Schema precision** — Read `schema.usda` directly; do not trust
  cached knowledge. Example: UsdGeomNurbsPatch *does* have trim
  curves (RiTrimCurve encoding), but the first draft said
  "unsupported."
- **Vendor/product claims** — Verify every product name, company
  attribution, and feature claim. Example: "Autodesk Platform
  Services" was cited as a USD integration but could not be verified.
- **Standards references** — Check ISO numbers, RFC numbers, year
  of publication, and exact titles. Example: the glossary was claimed
  to map to "PRC, STEP, Parasolid, ACIS, and Open Cascade" but
  actually maps to a different set of kernels.
- **Open-source vs commercial** — Verify licensing. Open Cascade
  (LGPL) was grouped with "commercial kernels" in the first draft.
- **Feature absence claims** — "USD does not support X" is dangerous.
  Search the codebase. A missed feature makes the whole argument
  weaker.

Chunk the fact-check into digestible pieces (5 chunks worked well
for a 680-line document): Products & Platforms, USD Technical Claims,
Standards & Theory, External Links, Organizational Claims.

### Pass 3: Hero Use Cases

After writing domain-specific use cases, step back and identify the
1–2 scenarios that cut across multiple domains. Elevate these to
a cross-cutting section *before* the domain-specific material.
Readers who skim will hit the strongest motivation first.

### Pass 4: Self-Contained References

Any link to an external document that might 404 for the reader
(org-restricted repos, working group internal docs) should be
replaced with inline content or an appendix. If the external
document is short enough, fold it in. The proposal should stand
alone.

---

## 4. Operational Lessons (AI-Assisted Drafting)

These are process lessons from drafting the exact geometry proposal
with an AI agent across a multi-hour session.

### Chunk Writes Into Phases

Do not attempt to write a 600-line document in one pass. Break it
into 4–6 phases of ~100–150 lines each. Commit after every phase.
Context windows are finite and unpredictable — a compaction event
mid-write can lose uncommitted work.

Proven phase structure for a problem statement proposal:

1. Introduction + Motivation + Problem Statement (~150 lines)
2. Industry Use Cases (~100 lines)
3. Existing Mechanisms in USD (~100 lines)
4. Design Considerations (~150 lines)
5. Relationships + Next Steps + Appendices (~100 lines)

### Use sed for Large File Edits

Once a document exceeds ~500 lines, the read/write cycle in an AI
agent's context window becomes dangerous: reading the file consumes
enough context that the subsequent write triggers compaction before
it can execute. Use `sed` for targeted in-place edits instead.

Example — inserting content at a specific line:

```bash
sed -i '660r /dev/stdin' README.md << 'EOF'
## Appendix A: New Content

Content goes here.
EOF
```

Example — replacing a specific line:

```bash
sed -i 's/old exact text/new exact text/' README.md
```

### Plan Before Writing (TASK.md)

Before starting a large document, write a TASK.md with:

- Phase breakdown with target line counts
- Ordered checklist (mark items done as you go)
- Key constraints and decisions

This prevents context overrun and gives a recovery point after
compaction.

### Commit Early, Commit Often

Every completed phase gets its own commit. Squash later when the
author is satisfied. Losing work to a context window reset is
avoidable if you commit after each meaningful unit.

### AI Disclosure

Include an appendix (not a footnote) disclosing AI assistance.
Be specific about what the AI did and what the human did. Readers
who are AI-cautious will look for this; transparency builds trust.
If the proposal's structure follows a prior proposal, say so
explicitly: "familiar but not repetitive" is the goal.

### Anonymize Before Pushing

Strip all real names from commits, branch metadata, and document
text before pushing to public branches. Use role-based references
("a TAC reviewer noted...") instead of names.

---

## 5. Checklist

Before opening a PR, verify:

- [ ] Section order follows the proven progression (§1)
- [ ] Folder name does not mirror PR #105's naming pattern
- [ ] No consecutive paragraphs share the same opening structure
- [ ] No "core observation is that..." or similar PR #105 framing
- [ ] Bold-opener lists are not the only list style used
- [ ] All universals hedged ("nearly all", "typically", "most")
- [ ] All factual claims verified against primary sources
- [ ] Hero use cases appear before domain-specific material
- [ ] External links that may 404 are replaced with inline content
- [ ] AI disclosure appendix is present and specific
- [ ] All names anonymized
- [ ] Document is self-contained (no required external documents)
- [ ] Squashed to a single commit on top of the base branch

---

## 6. Lessons from PR #3 (IP Protection Proposal)

The IP Protection proposal (PR #3 on `asluk/OpenUSD-proposals`) went
through its own language refinement, revealing additional patterns
worth generalizing.

### Reduce AI-isms

The second commit explicitly aimed to "reduce AI-isms and diverge from
identifiers proposal voice." Common AI writing patterns to watch for:

- **Walls of text.** Break dense paragraphs into bullets and sub-bullets.
  Reviewers skim; give them structure.
- **Overly smooth transitions.** AI prose tends to connect everything
  too neatly. Real technical writing has rougher edges — direct
  statements, occasional sentence fragments, questions that hang.
- **Hedging pileups.** One hedge per claim is enough. "It is worth
  noting that it may potentially be the case that..." is three hedges
  where one would do.
- **Symmetrical phrasing.** AI tends to produce parallel constructions
  across sections ("In domain X, the challenge is Y. In domain Z, the
  challenge is W."). Vary the structure between parallel sections.

### Avoid Prescriptive Language in Problem Statements

PR #3's third commit softened language "to avoid reading as proposed
USD changes." A problem statement should:

- Frame gaps, not solutions.
- Use the "USD role" column in tables to point to open questions,
  not name specific mechanisms.
- Make any forward-looking suggestions conditional: "If the community
  determines that X is desirable, a follow-up proposal could explore Y."
- Add disclaimers on illustrative code blocks: these are examples of
  the *problem*, not proposed syntax.

### USD Terminology Precision

- **"variant"** has a specific meaning in USD (variant sets/selections).
  Do not use it casually to mean "alternative" or "approach." This was
  caught and fixed in PR #3.
- **"final"** is not a current USD keyword. Fact-check every claim
  about USD language-level features against the actual spec.
- Avoid ambiguity with terms like "flatten," "compose," "override,"
  "opinion" — these all have precise USD semantics.

### Vendor Neutrality

PR #3 dropped specific vendor platform names and product mentions
from the body text. Guidelines:

- Name companies in the contributor list and use cases, not in
  technical analysis.
- Replace "Vendor X's product Y does Z" with "PLM systems typically
  provide Z."
- If a specific product is essential context, use it in a use case
  section with attribution, not in design principles.

### Line Width

Wrap prose at ~75 characters. This is a readability choice — GitHub
diffs, terminal editors, and side-by-side reviews all benefit from
shorter lines. PR #105 did not enforce this; PR #3 did.

### Multi-Author Proposals

PR #3 was co-authored by practitioners from three companies plus an
AI agent. When multiple humans contribute:

- Credit all authors in the header.
- Use `Co-Authored-By` trailers in commits.
- Ensure the voice is consistent — one author (or the AI) should do
  the final language pass.
- Remove internal references (JIRA links, internal doc IDs) before
  pushing.
