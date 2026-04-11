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
