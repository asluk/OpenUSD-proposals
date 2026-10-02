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

This document responds to the "Namespace and Prefix Isolation" requirement raised in the [AOUSD USD Extension Ecosystem Governance Proposal](https://docs.google.com/document/d/1zL7Igy5QN6bTHZavczkjaW2U5TBk95hP_Ooa_zL-tJc/edit) (Sean Snyders, Trimble, 2026-06-22), and to the comment thread on that requirement (Guy Martin, F. Sebastian Grassia, Aaron Luk). It separates namespace/prefix isolation from discoverability, per Grassia's comment, and works it into a standalone requirements framework with a survey of relevant precedent -- both from other standards bodies and from within the OpenUSD/AOUSD ecosystem itself.

## Problem Statement

USD's extension surface is not a closed set. Property names, applied/typed schema
identifiers, metadata dictionary keys (e.g. `assetInfo` sub-dictionaries), capability
identifiers, file format identifiers, and asset resolver identifiers form a starting
inventory. The requirements should be extensible to new surfaces as USD evolves.

Two vendors or domains can independently introduce identically named extensions
with different semantics. Depending on the surface and runtime, collisions can
produce registration errors, ambiguous interpretation, or silent use of the wrong
semantics when assets move between tools. Naming isolation must address both the
identifiers a runtime registers and those that content authors exchange.

### Outcomes and initial scope

This proposal supports two ecosystem outcomes:

- **Prevent cratering:** preserve a reliable content ecosystem in which adopters
  can reason about compatibility and the meaning of a support claim. Supporting
  USD does not require every application to implement every extension.
- **Prevent stagnation:** let domains prototype, ship, and build adoption within
  safe scopes without waiting for full AOUSD approval of each new feature.

Baseline USD, namespaces, profiles, and specification Parts are mechanisms for
achieving these outcomes. This proposal develops the naming mechanism; it does
not settle baseline scope, conformance infrastructure, or the organization of Parts.

The proposed first deliverable covers typed schema identifiers, applied API schema
identifiers, and property names. It must identify how those names relate to
capability/profile identifiers and metadata dictionary keys, so these surfaces do
not acquire incompatible ownership conventions. File format and asset resolver
identifiers remain in the inventory for subsequent work; binary plugin loading,
distribution, and sandboxing are separate concerns. This phased scope is proposed
for review, rather than a limit on the eventual extension model.

## Functional Requirements

These requirements describe properties a solution must satisfy, not a specific syntax or mechanism.

### Terminology

This document uses **prefix** and **namespace** as related but distinct terms:

- A **prefix** is the leading token, or sequence of tokens, in an identifier that denotes ownership or scope (e.g. `nvidia`, `KHR_`, `AOUSD.GeomWG`).
- A **namespace** is the space of identifiers scoped by a given prefix -- a prefix establishes a namespace, within which further hierarchy (domain, feature, version) is composed.
- **Ownership**, **maturity**, and **version** answer different questions: who
  controls a definition, how much agreement or validation it has received, and
  which semantic contract applies. A marker such as `Prelim` expresses maturity;
  it does not by itself identify an owner or reserve names against other
  preliminary extensions.

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
- **R5 -- Ownership assurance and collision handling.** The solution must specify
  how top-level ownership is established, how an owner delegates sub-namespaces,
  and how conflicting definitions are detected and resolved. A naming convention
  alone, with no ownership or conflict-handling mechanism, does not meet this
  requirement. Candidate mechanisms include lightweight prefix reservation,
  verifiable owner-controlled namespaces with validation, and explicit
  qualification with ambiguity detection. The choice and its guarantees remain
  open; no mechanism should silently select one of two conflicting definitions.
- **R6 -- Independent entry and a path to broader agreement.** Vendor extensions
  should be able to ship immediately within the agreed naming and baseline
  constraints. Proven extensions should have a path to multi-vendor or core
  consideration, and a submission may enter directly at a multi-vendor or
  working-group stage when agreement already exists. Graduation is optional and
  requires evidence and agreement; adoption does not imply AOUSD ratification.
  A change of governance or maturity must not imply an automatic identifier
  rename. Any renaming, aliasing, versioning, or content migration needs an
  explicit compatibility policy.
- **R7 -- Proportionate governance cost.** An additive extension within an owner's
  namespace should be self-enabled without full AOUSD feature approval upfront.
  Establishing namespace ownership must be distinct from approving the extension's
  semantics. Changes to the shared baseline or use of a namespace governed by
  others require the relevant broader agreement.

### B. Discoverability (separate requirement, not conflated with A)

Adapted from Gordon Bradley's comment on the governance doc:

- Define the set of extension points that meaningfully extend USD (property, schema type, file format, asset resolver, metadata, and others not yet named).
- Provide a unified extension model letting companies, individuals, and working groups (e.g. AECO) define a related set of those extension points as a shareable, optional extension to USD.
- Define a discovery/registration mechanism to reduce duplicated effort. Collision-surfacing is a secondary benefit of this mechanism, not its primary purpose -- that is covered by R5 above.

## Survey of Approaches

Ranked by relevance: existing AOUSD/USD-native precedent first, then external standards bodies, then field evidence from production use.

| Source | Syntax | Collision prevention | Prefix reservation registry | Promotion path |
|---|---|---|---|---|
| **USD Profiles** (proposal PR #75, Dhruv Govil, merged 2025-01; updated by PR #110, Nick Porcino, merged 2026-06; now shipped in OpenUSD as `usdProfiles`) | Reverse-domain (e.g. `usd.geom.skel`, `yoyodyne.dimensional.contabulator`) | Unique-prefix convention + mandatory ancestral derivation from the `usd` root capability | None | Yes -- worked example in Appendix B: vendor (`epic.nanite`) &rarr; AOUSD WG standardization (`aousd.meshlet`) &rarr; USD core (`usd.meshlet`) |
| **Khronos glTF extension registry** | `PREFIX_scope_feature`, prefix uppercase + underscore, remainder lowercase snake_case | Reserved prefix per vendor, requested via issue | Yes -- lightweight, file-based (`Prefixes.md`) | Specification maturity stages: Proposal &rarr; Initial Draft &rarr; Review Draft &rarr; Release Candidate &rarr; Ratified. Prefix category and maturity are distinct; ratified extensions can retain `EXT_`. |
| **IETF RFC 6838** (media type registration trees) | `facet.subtype`, e.g. `vnd.bigcompany.funnypictures` | Tree-based: `vnd.` (vendor), `prs.` (personal), `x.` (private/experimental, explicitly not for interop) | Yes -- IANA, centralized and heavyweight | None -- no formal vendor-to-standards graduation |
| **W3C Custom Elements (Web Components)** | Mandatory hyphen in the local name | Structural guarantee only: spec commits that no future built-in HTML/SVG/MathML element name will contain a hyphen | None | N/A |

These precedents do not require every extension to pass through a vendor prefix,
then a multi-vendor prefix, then a ratified prefix. The
[glTF registry](https://github.com/KhronosGroup/glTF/blob/main/extensions/README.md)
allows `KHR` for work intended for ratification, and lists ratified extensions that
retain `EXT` to preserve their established names. Its specification maturity stages
are distinct from prefix categories. Likewise, the Profiles proposal's worked
example illustrates a possible vendor-to-WG-to-core path; it does not establish a
mandatory renaming sequence for this proposal. Direct multi-vendor or WG entry and
stable identifiers across changes in maturity remain options to evaluate under R6.

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
considered as a marker for preliminary status. The marker does not specify which
owner governs the extension or reserves its identifiers.

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

That rationale reduces the number of identifiers that would change if graduation
removed the marker. A prim authored with `PrelimBrepArray` also exposes preliminary
status through its type name. It does not establish ownership or isolate every
identifier the extension introduces.

### Where it does not hold

**Type names are globally registered; the application constraint is local.**
`apiSchemaCanOnlyApplyTo` restricts where an API schema may be applied. It does not
reserve the name. Another party defining a differently-shaped `BrepPointAPI`
collides in the schema registry regardless of what either one can be applied to.
That is R5, and structural association does not address it.

**Library naming does not qualify every scene identifier.** A library name or C++
namespace does not automatically provide ownership scope for its registered schema
identifiers or property names. Each surface needs an explicit naming rule.

**Authored content carries both type and property identifiers.** A concrete prim's
type name persists as `typeName`; explicitly applied API schema identifiers persist
in `apiSchemas`. Built-in schema properties can exist through a prim definition
without being individually authored. These distinctions are documented in
[OpenUSD's schema generation guide](https://openusd.org/release/api/_usd__page__generating_schemas.html).

The following illustrative excerpt uses the proposed typed name; the B-Rep README
examples still use the earlier `BrepArray` spelling. It is not a complete B-Rep asset:

```usda
def PrelimBrepArray "Cube" (
    prepend apiSchemas = ["BrepPointAPI:vertexPoint", "BrepCurve3dNurbAPI:edge3dNurb"]
)
{
    uniform double[] brep:intersectTol3d = [0.00002]
    uniform uint[] brep:regionCount = [2]
}
```

Here, `PrelimBrepArray` carries maturity information, while `BrepPointAPI`,
`BrepCurve3dNurbAPI`, and the authored `brep:` properties do not carry an owner or
maturity marker. Multiple-apply property names also incorporate instance names
such as `edge3dNurb`; that instance name does not reserve the API schema identifier.

The type provides useful context when present. A property opinion may also be
authored in a separate override layer without a local type declaration or
`apiSchemas` opinion. Its interpretation then depends on composition and the
applicable schema definition. A property prefix keeps the governing owner visible
in that setting, but still needs version/dependency information
when semantics change. A missing prefix alone does not prove content is
uninterpretable; the question is whether the complete contract isolates independent
definitions and distinguishes incompatible versions.

### The question this poses

Stating it as a requirement question rather than a naming preference:

**Which identifiers need ownership isolation, and how are maturity and incompatible
versions represented across authored data and runtime registration?**

Answer this for the typed name, every applied API identifier, and property names,
including opinions authored in separate layers. `Prelim` alone cannot isolate two
independent preliminary extensions. An owner-qualified prefix and a separate
maturity/version declaration may be preferable to encoding all three in each name;
the exact syntax remains open.

Renaming a typed schema can already require migration of authored `typeName`
opinions. Renaming an explicitly applied API can require migration of `apiSchemas`;
renaming properties adds another migration surface. Prefixing only the typed schema
therefore does not make graduation a content-free registry change. Conversely,
keeping property names stable can be safe when the owner maintains a compatible
contract and incompatible changes have an explicit version/migration policy.

This is R4 and R6 in practice: assess each surface's ownership rule and compatibility
cost, while allowing governance maturity to change without unnecessary renaming.

## Design Considerations

### Ownership across naming surfaces

An owner-first convention is a candidate to evaluate consistently across property,
schema, and capability identifiers. A feature or product token alone does not
establish namespace ownership; having a trademark does not itself reserve a USD
identifier under an agreed naming mechanism. If a product or domain token is used
as the outermost component, the convention must still establish its governing
owner and satisfy R1 and R5. This applies equally to independently governed and
consortium-governed extensions. Token ordering remains a design choice to compare,
rather than an already selected syntax.

### Separability from OpenUSD's plugin system

The namespace/prefix paradigm, and its enforcement, should be separable from OpenUSD's plugin system -- `plugInfo.json`, C++ namespace macros (`PXR_NS`), `dlopen`-based dynamic loading, or any other mechanism a given runtime happens to use to implement extensibility. The convention, and any enforcement mechanism built around it, should be definable and usable without depending on OpenUSD's plugin system to exist.

The current [UsdProfiles overview](https://github.com/PixarAnimationStudios/OpenUSD/blob/dev/docs/user_guides/schemas/UsdProfiles/overview.md)
distinguishes `UsdProfilesClaimsAPI`, which records capability usages and profile
compatibility claims, from `UsdProfileRegistry`, which loads capability definitions
from `plugInfo.json` and supports graph queries. Schema implications can be declared
in `schema.usda` and propagated into plugin metadata by code generation.

A future AOUSD extension model should distinguish the semantics of declarations
and compatibility queries from how a runtime discovers those definitions. Another
implementation could populate equivalent definitions from a manifest, database, or
service, provided it satisfies the agreed contract. The OpenUSD implementation is
a useful reference; its documentation does not itself establish an AOUSD normative
contract for independent implementations. The namespace convention should work
across those implementations without requiring OpenUSD's plugin machinery.

This is worth stating explicitly because a related conflation is already visible in the governance doc's own comment thread (a question about whether "sandboxing" extensions is even possible given OpenUSD's `dlopen`-based plugin loading). That is a legitimate question about a different requirement (trust/sandboxing) than namespace/prefix isolation, and naming the separability principle explicitly should help keep the two separate in discussion.

### Profiles as the cross-cutting declaration mechanism

Namespace and prefix isolation defines the naming layer: how an identifier for a property, schema, capability, or other extension surface is constructed so that ownership is legible and collisions are preventable. It does not by itself address how an asset declares which extensions or capabilities it requires.

The current [ClaimsAPI documentation](https://github.com/PixarAnimationStudios/OpenUSD/blob/dev/docs/user_guides/schemas/UsdProfiles/ClaimsAPI.md)
describes capability usages with `hard`, `soft`, or `enhancement` degradation classes,
and profile compatibility claims with optional exceptions. Claims are stored in
`customData` under `profilesInfo`; usages can also be populated from declared schema
and file format implications. These are declarations whose evidentiary basis still
needs to be defined for a given support or conformance claim.

This provides a candidate vehicle for declaring extension use and making unsupported
capabilities visible. It does not establish namespace ownership, provide extension
distribution, or prove semantic conformance by itself. Define the mapping from
extension identifiers to capability/profile identifiers and the evidence behind
claims separately. Using this mechanism need not make OpenUSD's registration
implementation mandatory, or make a complete discovery system a prerequisite for
shipping the naming convention.

### Independent adoption and baseline boundaries

The proposed entry rule is that an owner may publish and ship an additive,
owner-prefixed schema without full AOUSD approval of its feature semantics. Prefix
ownership is a naming obligation, not a feature-review queue. The extension must
state its semantics, baseline/version dependencies, and expected behavior when a
consumer lacks support. A consumer may decline an extension; preserving its data
does not imply correctly interpreting it.

For example, independently developed text and line-style schemas could use
Autodesk-owned identifiers and build adoption among willing applications. This is
an illustrative pathway, not a claim that Autodesk has accepted a particular
schema or naming syntax. It should not require waiting for inclusion in OpenUSD's
core distribution or AOUSD's highest governance tier.

An extension that changes shared composition behavior, redefines an existing
baseline identifier, or uses another owner's namespace crosses a different
boundary. Those changes need broader review. Using the current Core Specification
as a starting baseline is a candidate for discussion; namespace isolation does not
decide that boundary on its own.

Graduation should consider documented semantics, independent adoption and
interoperability evidence, conformance expectations, and compatibility/migration
costs. Some extensions may remain independently governed. Broader technical
agreement, resource prioritization, and escalation authority are distinct decisions
and should have named owners rather than being collapsed into one approval step.

## Open Questions for Discussion

1. Which ownership and conflict-handling mechanism satisfies R5 at proportionate
   cost: lightweight prefix reservation, owner-controlled namespaces with validation,
   qualification with ambiguity detection, or a combination? A bare convention is
   insufficient under the proposed requirement. How are conflicts reported without
   silently substituting another owner's semantics?
2. Is the proposed schema-first deliverable the right initial scope? Specify typed
   names, applied API identifiers, and property names, with mappings to metadata and
   capability/profile identifiers. Which additional surfaces are urgent enough to
   include now, and which require a subsequent work item?
3. Can namespace isolation and the minimum ownership mechanism ship before a full
   extension discovery/distribution system? Prefix reservation, if selected, must
   not be conflated with a catalog of all extension implementations.
4. What precisely makes an extension additive within baseline constraints, and what
   triggers broader review? Use concrete schema and composition examples, including
   an application declining an extension, before drafting the boundary rule.
5. For the B-Rep case, which owner governs each identifier, how is preliminary status
   represented, and what compatibility policy applies to incompatible changes or
   later graduation?
6. Who authors and maintains the convention? A candidate arrangement is a TAC
   sponsor with a small authoring group, dedicated maintenance ownership, and SC
   escalation for resource/priority conflicts. Confirm the mandates and capacity
   rather than assuming TAC itself can perform all implementation and upkeep.

## Relationship to Other Proposals

- **USD Profiles** (proposal PR #75, Dhruv Govil; updated by PR #110, Nick Porcino; shipped in OpenUSD as `usdProfiles`, with its own [overview](https://github.com/PixarAnimationStudios/OpenUSD/blob/dev/docs/user_guides/schemas/UsdProfiles/overview.md) and [ClaimsAPI](https://github.com/PixarAnimationStudios/OpenUSD/blob/dev/docs/user_guides/schemas/UsdProfiles/ClaimsAPI.md) documentation, which supersedes the proposals): this document builds on and extends its naming and graduation-pathway model rather than proposing a competing scheme.
- **Separation of Concerns for Identifiers in USD** (in progress, this repo): adjacent but distinct -- that proposal addresses identifying instances against external systems; this document addresses ownership/naming of the extension surface itself.
- **Authorship** (PR #106) and **IP Protection** (PR #107): not namespace-related in substance, but used here as structural precedent for how recent AOUSD cross-cutting proposals are organized.

## Next Steps

- Confirm a TAC sponsor and authoring/maintenance owners; record deliverables,
  capacity, dependencies, and the approving body for decisions beyond their mandate.
- Agree the initial surface inventory and the ownership/conflict-handling mechanism
  (R5), independently of a complete discovery/distribution system.
- Evaluate candidate concrete syntaxes against R1--R7, rather than adopting one by default -- the Profiles proposal's reverse-domain notation is a strong existing candidate, not the only one capable of satisfying the requirements.
- Walk the B-Rep and independently owned schema cases through each naming surface,
  unsupported-consumer behavior, incompatible version, and graduation/migration
  policy. Record unresolved choices with an owner and next action.
- Define how extension identifiers map to ClaimsAPI capability/profile declarations
  and what evidence supports compatibility claims, while keeping the contract
  separable from OpenUSD's plugin implementation.
