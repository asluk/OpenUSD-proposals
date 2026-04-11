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
