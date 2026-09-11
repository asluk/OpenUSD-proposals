# Proposal clarifications — Brep↔Mesh correlation framing

**Status:** Held — not currently pursued. The [posted PR comment](https://github.com/PixarAnimationStudios/OpenUSD-proposals/pull/109#issuecomment-4559346157) on PR #109 carries the framing on the thread; these proposal-text edits remain available if a follow-up pass is wanted.

**Target branch (if revived):** `aousd/OpenUSD-proposals:p2-usdsolid-schema` (and optionally `p1-exact-geometry-problem-statement`)

The edits below would tighten the framing without changing substance — making explicit on the page what the PR comment argues on the thread: correlation is a *separate-but-related* concern that belongs in its own proposal, not a TBD inside UsdSolid.

---

## Edit 1 (primary) — `proposals/UsdSolid/README.md`, Open Questions, Brep↔Mesh correlation bullet

### Current text

> **Brep↔Mesh correlation.** Relating a Brep to its tessellated derivatives is deferred (see the companion [problem statement](../cad_geometry/README.md)). One candidate approach raised by Steve Ghee: because gprims are generally derived from Breps in an N:1 relationship, a gprim could back-reference its source Brep(s) by identifier or path via an applied API schema. At runtime, these cross-references would let a Brep discover which gprims represent it (avoiding redundant tessellation) and let a picked gprim trace back to its source. Supporting an array of references would handle the case where a single gprim is derived from multiple Breps. This mechanism is best designed as a follow-up once the core schema is deployed and real-world datasets are available.

### Proposed text

> **Brep↔Mesh correlation.** The relationship between a Brep and its tessellated derivatives is a separate-but-related concern from the Brep schema itself, not a deferred component of it. The source/derived pair pattern is broader than CAD — it recurs across subdivision cages and limit surfaces, simulation results and visualization meshes, LoD chains, and other contexts — and a correlation mechanism designed in concert with these other pairs is more likely to land in a generally useful shape. By design, a correlation can be authored as an applied schema on the *derived* gprim that references the source Brep, entirely outside _UsdSolid_'s domain; the core Brep schema stays self-contained, and the correlation mechanism can evolve on its own timeline. The WG intends to pursue this in a dedicated follow-on proposal, seeded by prior discussions on the topic.
>
> A candidate approach raised by Steve Ghee is sketched here to signal direction: because gprims are generally derived from Breps in an N:1 relationship, a gprim could back-reference its source Brep(s) by identifier or path via an applied schema. At runtime, these cross-references would let a Brep discover which gprims represent it (avoiding redundant tessellation) and let a picked gprim trace back to its source. Supporting an array of references would handle the case where a single gprim is derived from multiple Breps. Variations on this mechanism — including vendor-prefixed proposals — are welcome inputs to the follow-on proposal.

### Rationale

- Leads with "separate-but-related concern… not a deferred component" so the *deferral* reading is closed off in the proposal text itself.
- Adds the generality argument (source/derived pattern beyond CAD) so readers see why the mechanism doesn't belong inside UsdSolid.
- Adds the architectural argument (applied schema on the derived gprim, outside UsdSolid's domain) so readers see USD's composition model is the enabler, not a workaround.
- Replaces vague "follow-up once the core schema is deployed" with explicit "dedicated follow-on proposal, seeded by prior discussions" — gives a concrete next step.
- Keeps Ghee's candidate sketch verbatim; adds an explicit invitation for vendor-prefixed variations.

---

## Edit 2 (optional reinforcement) — `proposals/cad_geometry/README.md`, Design considerations → Principles → Coexistence with meshes

### Current text

> 2. **Coexistence with meshes.** Brep and Mesh representations of the
>    same object should be relatable-so applications can choose which to
>    operate on-but neither should require the other. How they relate
>    (USD relationships, naming conventions, a companion API schema) is
>    important but separable from the core Brep schema.

### Proposed text

> 2. **Coexistence with meshes.** Brep and Mesh representations of the
>    same object should be relatable-so applications can choose which to
>    operate on-but neither should require the other. The natural home
>    for the relationship is an applied schema on the *derived* gprim that
>    references the source Brep — entirely outside the Brep schema's
>    domain. The correlation mechanism is important, but it generalizes
>    beyond Brep↔Mesh (subdivision cages and limit surfaces, simulation
>    results and visualization meshes, LoD chains share the same source/
>    derived pattern), and the WG intends to develop it in a dedicated
>    follow-on proposal rather than inside UsdSolid.

### Rationale

- Promotes the architectural point (applied schema on the derived gprim) from "one of several options" to the natural fit, anchored in USD's composition model.
- Foregrounds the generality so the problem-statement reader doesn't have to reach the schema's Open Questions to understand the scoping decision.
- Mild change in tone; substance unchanged.

### Tradeoff

- If the problem statement has already been read by many reviewers in its current form, changing a Principle introduces re-reading cost. Edit 1 alone may be sufficient if minimizing churn matters. Apply Edit 1 first; Edit 2 only if a broader problem-statement update is happening anyway.

---

## Edit 3 (optional reinforcement) — `proposals/cad_geometry/README.md`, Open questions for discussion → Brep-to-Mesh relationship

### Current text

> - **Brep-to-Mesh relationship.** How should a Brep prim relate to its
>   derived mesh(es)? Options include USD relationships, naming
>   conventions, or a companion API schema.

### Proposed text

> - **Brep-to-Mesh relationship.** How should a Brep prim relate to its
>   derived mesh(es)? Options include USD relationships, naming
>   conventions, or a companion API schema. Because the source/derived
>   pattern is broader than CAD, the WG's intent is to develop the
>   correlation mechanism in a dedicated follow-on proposal rather than
>   inside UsdSolid.

### Rationale

- Same generality + separate-proposal framing as Edits 1 and 2, in three lines.
- Lowest-touch reinforcement; safe to apply on its own if the broader edits are held.
