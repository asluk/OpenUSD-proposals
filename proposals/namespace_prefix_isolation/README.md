# Namespace and Prefix Isolation for USD Extensions

> **Draft status -- under active review, not yet complete.** This is an AI-assisted working draft by Aaron Luk (NVIDIA), originally prepared as discussion input for the 2026-09-04 AOUSD TAC meeting and now being revised based on that discussion and further review. Content, framing, examples, and citations are subject to change without notice. This is **not** an AOUSD position, **not** a finalized proposal, and **not** citable as a reference. If you've come across this outside of direct collaboration with the author, please treat it as incomplete and reach out before relying on anything in it.

## Contents

1. [Introduction](#introduction)
2. [Problem Statement](#problem-statement)
3. [Functional Requirements](#functional-requirements)
4. [Survey of Approaches](#survey-of-approaches)
5. [Case Study: `Prelim` in the UsdSolid B-Rep Proposal](#case-study-prelim-in-the-usdsolid-b-rep-proposal)
6. [Design Considerations](#design-considerations)
7. [Open Questions for Discussion](#open-questions-for-discussion)
8. [Relationship to Other Proposals](#relationship-to-other-proposals)
9. [Next Steps](#next-steps)

## Introduction

This document responds to the "Namespace and Prefix Isolation" requirement raised in the AOUSD USD Extension Ecosystem Governance Proposal (Sean Snyders, Trimble, 2026-06-22), and to the comment thread on that requirement (Guy Martin, F. Sebastian Grassia, Aaron Luk). It separates namespace/prefix isolation from discoverability, per Grassia's comment, and works it into a standalone requirements framework with a survey of relevant precedent -- both from other standards bodies and from within the OpenUSD/AOUSD ecosystem itself.

## Problem Statement

USD's extension surface is not a closed set, and this document's scope should be read accordingly. What's visible today -- property names, applied/typed schema type names, metadata dictionary keys (e.g. `assetInfo` sub-dictionaries), file format identifiers, and asset resolver identifiers -- is a starting inventory, not a boundary. New extension points may emerge as USD evolves. A namespace/prefix convention should be defined in terms general enough to extend to surfaces it does not yet name, rather than being scoped only to today's known list.

The core failure mode motivating this work is concrete, not hypothetical: two vendors or domains can independently introduce identically-named extensions -- on any of these surfaces -- with different semantics. When assets carrying both move between tools, the result is silent, undetected data corruption rather than a visible error.

## Functional Requirements

These requirements describe properties a solution must satisfy, not a specific syntax or mechanism.

### Terminology

This document uses **prefix** and **namespace** as related but distinct terms:

- A **prefix** is the leading token, or sequence of tokens, in an identifier that denotes ownership or scope (e.g. `nvidia`, `KHR_`, `AOUSD.GeomWG`).
- A **namespace** is the space of identifiers scoped by a given prefix -- a prefix establishes a namespace, within which further hierarchy (domain, feature, version) is composed.

Where the distinction doesn't matter, this document refers to them together as "namespace/prefix."

### Hierarchy composition

An identifier composed under this convention carries at least two independent axes:

- **Owner hierarchy**: who governs the extension. May be a single flat token, or a multi-level hierarchy the owner defines for its own purposes. That sub-hierarchy is the owner's own to define -- this convention doesn't prescribe what the intermediate levels mean. A standards body's sub-levels might be working groups; a single vendor's sub-levels might be internal tiers, divisions, product lines, or something else entirely. Either kind of owner needs the *option* of a sub-hierarchy, not just consortium-style owners.
- **Domain hierarchy**: what functional area the extension addresses, and how specific a feature within that area it names.

Examples composing both axes (delimiter and casing are illustrative only, not prescribed):

```
AOUSD.GeomWG . brep
└─────┬─────┘   └┬─┘
 owner hierarchy domain (schema-level: `BrepArray` and its
                          associated API schemas -- `BrepPointAPI`,
                          `BrepCurve3dNurbAPI`, `BrepCurveUvNurbAPI`,
                          `BrepSurfaceNurbAPI` -- all share the `Brep`
                          domain token. UsdSolid B-rep proposal,
                          PR #109, Aaron Luk & Joe Umhoefer)
(alliance > working group -- AOUSD doesn't
 have sub-WGs today, but R3 requires the
 convention support that deeper nesting if
 AOUSD adds it later)

yoyodyne.tierA . dimensional.contabulator
└───────┬──────┘   └─────────┬──────────┘
   owner hierarchy        domain hierarchy
(a single vendor's own internal sub-hierarchy --
 not necessarily "working groups"; the owner
 defines what its own sub-hierarchy levels mean)

yoyodyne . dimensional.contabulator
└───┬───┘   └─────────┬──────────┘
 owner            domain hierarchy
(flat, no sub-hierarchy)
```

(`yoyodyne` is the Profiles proposal's own placeholder vendor, reused here for consistency -- these examples make no claim about any real organization's structure.)

### A. Namespace & Prefix Isolation (standalone requirement)

- **R1 -- Ownership legibility.** The convention must make ownership of an extension identifier immediately visible, without prior knowledge of a pipeline-specific convention.
- **R2 -- Hierarchical scoping.** The convention must support nested/hierarchical scoping on both axes above, without prescribing a specific delimiter, casing rule, or token ordering.
- **R3 -- Owner sub-hierarchy independence.** The owner/vendor portion of an identifier must support its own internal sub-hierarchy, independent of and orthogonal to the extension's domain/feature hierarchy. This applies whether the owner is a standards body (organized into working groups) or a single vendor structuring its own namespace (e.g. into internal tiers, divisions, or product lines) -- the convention should not assume what an owner's sub-hierarchy levels mean, only that they can exist. A single flat vendor token and a multi-level owner hierarchy must both be expressible under the same convention.
- **R4 -- Syntax may vary by extension surface.** Different extension surfaces (property names, schema/type names, capability or profile identifiers, etc.) may reasonably use different concrete syntaxes, provided each satisfies R1--R3. The requirement is on the properties each syntax must guarantee (legibility, hierarchy, owner-sub-hierarchy support) -- not a single notation mandated uniformly everywhere.
- **R5 -- Collision-prevention guarantee.** Some mechanism -- stronger than convention alone -- should give independent parties confidence that their top-level tokens will not collide. The proportionate strength of this mechanism is an open question (see below).
- **R6 -- Tiered/graduated lifecycle, with a variable starting point.** Vendor-specific conventions should be able to ship immediately; proven conventions should have a path to multi-vendor or core status over time. The lifecycle itself remains sequential (vendor &rarr; multi-vendor &rarr; ratified/core), but the starting point within it need not always be the vendor-specific stage -- a submission can enter directly at the multi-vendor or working-group-authored stage if that's where consensus already exists, the same way Khronos's prefix-request process lets a submission request a multi-vendor `EXT_` prefix directly rather than first shipping a vendor-specific one. From whatever point it enters, the remaining stages still proceed in order.
- **R7 -- Proportionate governance cost.** The common case (one vendor, one schema) should not require the same process as a core-track schema.

### B. Discoverability (separate requirement, not conflated with A)

Adapted from Gordon Bradley's comment on the governance doc:

- Define the set of extension points that meaningfully extend USD (property, schema type, file format, asset resolver, metadata, and others not yet named).
- Provide a unified extension model letting companies, individuals, and working groups (e.g. AECO) define a related set of those extension points as a shareable, optional extension to USD.
- Define a discovery/registration mechanism to reduce duplicated effort. Collision-surfacing is a secondary benefit of this mechanism, not its primary purpose -- that is covered by R5 above.

## Survey of Approaches

Ranked by relevance: existing AOUSD/USD-native precedent first, then external standards bodies, then field evidence from production use.

| Source | Syntax | Collision prevention | Registry | Promotion path |
|---|---|---|---|---|
| **USD Profiles proposal** (merged PR #75, Nick Porcino) | Reverse-domain (e.g. `usd.geom.skel`, `yoyodyne.dimensional.contabulator`) | Unique-prefix convention + mandatory ancestral derivation from the `usd` root capability | None | Yes -- worked example in Appendix B: vendor (`epic.nanite`) &rarr; AOUSD WG standardization (`aousd.meshlet`) &rarr; USD core (`usd.meshlet`) |
| **Khronos glTF extension registry** | `PREFIX_scope_feature`, prefix uppercase + underscore, remainder lowercase snake_case | Reserved prefix per vendor, requested via issue | Yes -- lightweight, file-based (`Prefixes.md`) | Yes -- 5 stages: Proposal &rarr; Initial Draft &rarr; Review Draft &rarr; Release Candidate &rarr; Ratified (vendor &rarr; `EXT_` multi-vendor &rarr; `KHR_` ratified) |
| **IETF RFC 6838** (media type registration trees) | `facet.subtype`, e.g. `vnd.bigcompany.funnypictures` | Tree-based: `vnd.` (vendor), `prs.` (personal), `x.` (private/experimental, explicitly not for interop) | Yes -- IANA, centralized and heavyweight | None -- no formal vendor-to-standards graduation |
| **W3C Custom Elements (Web Components)** | Mandatory hyphen in the local name | Structural guarantee only: spec commits that no future built-in HTML/SVG/MathML element name will contain a hyphen | None | N/A |

These promotion paths remain sequential, but the entry point within them can vary. Khronos's prefix-request process (a GitHub issue) is the same mechanism used to request a multi-vendor `EXT_` prefix directly -- entering the sequence at that stage rather than at single-vendor, with ratification into `KHR_` still to follow. Likewise, the Profiles proposal's worked example doesn't require every extension to start at the vendor stage -- a working-group-authored capability can enter directly at the AOUSD-WG tier and proceed from there toward core integration.

Field evidence from production use (illustrative, not proposed as a template):

- A property-naming convention in production today (NVIDIA's SimReady Foundation) uses colon-delimited, camelCase tokens (matching USD's existing colon-delimited property idiom, e.g. `primvars:`), governed by tier ownership with no central registry and no graduation path today. It is not a static single-organization case, though: SimReady is moving toward its own working-group structure and toward tiers that are not NVIDIA-specific -- for example [Newton](https://github.com/newton-physics), an open physics engine developed jointly across multiple organizations. Read this way, it's a live example of a vendor-originated namespace mid-transition toward the multi-vendor tier this proposal's lifecycle (R6) describes, not just a cautionary single-vendor case -- and it is itself still working through the collisions that arise along that path.
- A separate reverse-domain convention has been adopted for capability/rule/profile identifiers (a different namespace than property names), explicitly built on the Profiles proposal's naming approach. Its versioning syntax diverged from the Profiles proposal's own (dot-integer vs. underscore-integer) -- concrete evidence that a documented convention drifts without an enforcement mechanism.
- A third, distinct collision-prevention mechanism observed in production: package-scoped resolution. Short identifiers are implicitly scoped to their owning package; cross-package references require full qualification; the same short identifier in two different packages causes no conflict unless an unqualified reference becomes ambiguous across packages actually installed together. Collision detection happens at resolve/consumption time rather than at authoring/registration time -- a middle point between a central registry and convention-only, worth naming as a third option distinct from that binary.

## Case Study: `Prelim` in the UsdSolid B-Rep Proposal

The B-Rep proposal is the first live instance of these requirements meeting a real
schema, and it is worth reading closely because it exposes a question the
requirements above state abstractly: **which extension surfaces does a marker attach
to?**

Its governance journey is the one R6 describes. The schema was worked in the AOUSD
Geometry Working Group, socialized with other interest groups, and put up as
OpenUSD-proposals PRs -- more than one organization behind it, and past the point
where a single-vendor prefix would describe it accurately. `Prelim` is being
considered as the marker for exactly that status: not one company's, and not yet
ratified.

### What the marker landed on

[aousd/OpenUSD-proposals PR #2](https://github.com/aousd/OpenUSD-proposals/pull/2)
adds the prefix to the typed prim, `BrepArray` becoming `PrelimBrepArray`. The
library already carried it as `PrelimUsdSolid`. Left unprefixed: the applied API
schemas (`BrepPointAPI`, `BrepCurve3dNurbAPI`, `BrepCurveUvNurbAPI`,
`BrepSurfaceNurbAPI`), the property namespace prefix `brep`, and the authored
examples in the proposal's own README, which still read `def BrepArray`.

Joe Umhoefer's rationale for leaving the applied APIs unprefixed is that they can
only be applied to the prefixed type -- `apiSchemaCanOnlyApplyTo` constrains them to
`PrelimBrepArray`, so the marker is carried structurally rather than in their names.

That rationale has real merit. It minimizes renaming at graduation: one type name
changes rather than six. And from authored data the status is legible, because the
prim type is visible at the point of use.

### Where it does not hold

**Type names are globally registered; the application constraint is local.**
`apiSchemaCanOnlyApplyTo` restricts where an API schema may be applied. It does not
reserve the name. Another party defining a differently-shaped `BrepPointAPI`
collides in the schema registry regardless of what either one can be applied to.
That is R5, and structural association does not address it.

**The argument generalizes further than intended.** If association through
containment is sufficient, the typed prim needed no prefix either -- it already sits
inside `PrelimUsdSolid`. The same reasoning excuses the change the PR makes.

**And the surfaces that persist in content received nothing.** The marker is on the
library and the type name, both of which exist only in the schema registry. Every
surface that ends up in a customer's file is unmarked:

```usda
def BrepArray "Cube" (
    prepend apiSchemas = ["BrepPointAPI:vertexPoint", "BrepCurve3dNurbAPI:edge3dNurb"]
)
{
    uniform double[] brep:intersectTol3d = [0.00002]
    uniform uint[] brep:regionCount = [2]
    uniform point3d[] brep:edge3dNurb:curve3d:nurb:controlVertices = [...]
}
```

Two sources of `brep:` appear here. The typed schema declares its own properties with
the namespace built into their names, so they are authored on every instance. And
the multiple-apply instancing composes API schema instance names into property paths
-- `brep:edge3dNurb:...` -- so the applied schemas do leave a trace in authored data,
through instance names rather than through type names.

If a preliminary design changes at ratification, content authored in the interim
carries `brep:` properties whose semantics differ from ratified `brep:` properties,
with nothing in the file to distinguish them.

### The question this poses

Stating it as a requirement question rather than a naming preference:

**Does a maturity or ownership marker belong on the surfaces that persist in authored
data, or on the surfaces that exist in the schema registry?** The B-Rep PR currently
answers "registry," and the asymmetry appears to be incidental rather than chosen.

The answer has a cost either way, which is why it needs deciding rather than
defaulting. Marking the property namespace -- `prelimBrep:intersectTol3d` -- makes
status legible in the one place that outlives every tool, and makes graduation a
content migration rather than a schema rename. Not marking it keeps graduation cheap
and keeps property names readable, at the price of authored data that cannot be
dated.

This is R4 in practice. R4 permits different surfaces to use different concrete
syntaxes, provided each satisfies R1--R3. It does not say a surface may carry no
marker at all, and the B-Rep case shows that the distinction between "different
syntax" and "absent" has not yet been drawn.

## Design Considerations

### Separability from OpenUSD's plugin system

The namespace/prefix paradigm, and its enforcement, should be separable from OpenUSD's plugin system -- `pluginfo.json`, C++ namespace macros (`PXR_NS`), `dlopen`-based dynamic loading, or any other mechanism a given runtime happens to use to implement extensibility. The convention, and any enforcement mechanism built around it, should be definable and usable without depending on OpenUSD's plugin system to exist.

This separability holds even inside mechanisms that happen to use OpenUSD's plugin system today. The Profiles proposal's `ProfileAPI` has two distinct layers: a **query contract** -- what an explicit query (authored capability metadata on a prim, resolved via standard USD value resolution) or an introspective query (capabilities inferred from schema/scene analysis) is supposed to return, given a prim or scene -- and a **registration mechanism** -- how a runtime populates the capability graph that answers those queries. The Profiles proposal describes the latter via `pluginfo.json` / `schema.usda` and OpenUSD's existing `PlugInfo` machinery, because that fits the reference implementation. But the query contract itself is implementation-agnostic: a different runtime could populate an equivalent capability graph from a database, a sidecar manifest, or a service call, and still correctly answer the same queries. Only the registration mechanism is OpenUSD-plugin-specific; the query contract is not. AOUSD's governance role, following the same separability principle, is to normatively specify the query contract that capabilities and profiles must satisfy -- not to require `pluginfo.json`-based registration as the only conforming implementation. The AOUSD Core Specification 1.0 already draws an analogous distinction for schemas generally: it specifies schema conformance without prescribing a plugin or registry mechanism.

This is worth stating explicitly because a related conflation is already visible in the governance doc's own comment thread (a question about whether "sandboxing" extensions is even possible given OpenUSD's `dlopen`-based plugin loading). That is a legitimate question about a different requirement (trust/sandboxing) than namespace/prefix isolation, and naming the separability principle explicitly should help keep the two separate in discussion.

### Profiles as the cross-cutting declaration mechanism

Namespace and prefix isolation defines the naming layer: how an identifier for a property, schema, capability, or other extension surface is constructed so that ownership is legible and collisions are preventable. It does not by itself address how an asset declares which extensions or capabilities it requires.

The USD Profiles proposal's `ProfileAPI` (PR #75, Nick Porcino) is an existing, already-accepted mechanism for exactly that: assets carry explicit or introspectively-derived declarations of the capabilities/profiles they require, using identifiers this namespace/prefix convention would govern. As discussed under Separability above, it is the query contract of `ProfileAPI` -- not any particular registration mechanism -- that is relevant here. Namespace/prefix isolation (Functional Requirements, section A) and Discoverability (section B) are complementary, not competing, requirements -- Profiles' declaration mechanism is one candidate vehicle for satisfying the Discoverability requirement, not a mandated one. Governance of how vendor extensions get folded into or referenced by profiles is deferred to AOUSD, consistent with how the Profiles proposal itself defers canonical-capability governance to OpenUSD/AOUSD.

## Open Questions for Discussion

1. Which collision-prevention strength does AOUSD actually need: convention-only, a lightweight file-based registry, a centralized registry, or resolve-time ambiguity detection? This is a governance-cost tradeoff (R7), not a right-or-wrong call.
2. Does the convention need to cover schema/type names and asset resolver identifiers, in addition to property names (SimReady, USD's own colon idiom) and capability/profile identifiers (the Profiles proposal and its adopters)? None of the precedent surveyed above directly addresses schema/type-name or asset-resolver naming. IETF's media type registration (RFC 6838) is the closest existing analog for file-format identification, but it is a different namespace than USD's own file-format plugin identifiers, not a direct precedent for them.
3. Can namespace/prefix isolation ship independently of the discoverability/registry track, with discoverability layered on later?
4. Ownership: is this a TAC front-line concern with SC escalation for unresolved priority conflicts, or does it belong with a dedicated working or interest group?

## Relationship to Other Proposals

- **USD Profiles proposal** (merged PR #75, Nick Porcino): this document builds on and extends the Profiles proposal's naming and graduation-pathway model rather than proposing a competing scheme.
- **Separation of Concerns for Identifiers in USD** (in progress, this repo): adjacent but distinct -- that proposal addresses identifying instances against external systems; this document addresses ownership/naming of the extension surface itself.
- **Authorship** (PR #106) and **IP Protection** (PR #107): not namespace-related in substance, but used here as structural precedent for how recent AOUSD cross-cutting proposals are organized.

## Next Steps

- Resolve the open questions above into concrete requirements: the specific collision-prevention mechanism (R5), and the extension-surface coverage boundary.
- Evaluate candidate concrete syntaxes against R1--R7, rather than adopting one by default -- the Profiles proposal's reverse-domain notation is a strong existing candidate, not the only one capable of satisfying the requirements.
- Define how vendor/domain extension identifiers relate to `ProfileAPI`'s query contract, so that namespace/prefix isolation and Discoverability compose rather than requiring two separate declaration mechanisms.
- Establish ongoing ownership of the convention: a dedicated working group, or a TAC-front-line concern with SC escalation for unresolved priority conflicts.
