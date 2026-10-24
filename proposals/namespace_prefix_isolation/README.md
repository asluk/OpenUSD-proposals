# Namespace and Prefix Isolation for USD Extensions

> **Discussion draft - revised October 24, 2026.** Prepared by Aaron Luk (NVIDIA), with AI assistance. This draft develops the functional requirements for a necessary foundation of the USD extension model. It is not approved AOUSD policy. Specific naming syntax, reservation procedures, and governance responsibilities remain open for review.

## Read first: the proposed commitment

- **Reliability:** USD content works predictably across tools and over time.
- **Leadership:** USD turns growing domain demand into deployed capabilities,
  with a clear path from experimentation to shared standards.

Stakeholders are already developing and deploying schemas. Common ownership,
naming isolation, and compatibility guidance are necessary foundations for that
work, alongside a dependable account of the USD behavior extensions build on. Namespace isolation identifies who governs a definition, avoids collisions,
and makes support and compatibility expectations explicit. It does
not by itself make two implementations behave the same way.

The proposed initial work is to:

1. **Define ownership and isolation for schemas and properties.** Cover typed
   schema names, applied API identifiers, and property names; establish how an
   owner reserves an extension name and how conflicts are reported. Mandatory
   naming conventions derive the schema, property, and other covered identifiers
   from that reservation; individual identifiers need no separate reservation.
   Owners may be vendors, community projects, or standards bodies. Map these
   names to capability declarations without requiring a full extension catalog
   or distribution service first.
2. **Make the boundary for independent deployment explicit.** An additive
   extension builds domain behavior on existing composition and value resolution.
   It declares its dependencies and behavior when unsupported. Changes to shared
   behavioral contracts require the relevant agreement; owning a prefix does
   not grant permission to change those contracts.
3. **Work one case through the whole contract.** Identify the owner, authored and
   registered identifiers, required capabilities, unsupported-consumer behavior,
   and policy for incompatible revisions and ownership transitions. Validate the
   naming rules independently of OpenUSD. Use that evidence to compare naming
   mechanisms and expose gaps before broadening the scope.

Governance effort should grow with the shared commitments being requested.
An independently governed extension need not seek standardization. A shared
extension can start under a community or multi-organization owner, and wider
adoption alone does not transfer ownership. Ownership transfers require an
explicit identifier-transition policy, grace periods, and migration paths. Owner,
maturity, version, and implementation support are separate facts.

The vendor extension paradigm and its validation contract must be independent of
OpenUSD's plugin system. OpenUSD can implement the contract through its existing
facilities; other implementations must be able to provide equivalent behavior.
Independent deployment implies no claim that arbitrary extensions work together.
Vendors can declare supported combinations through their own profiles.

### Baseline USD: a working boundary

Here, **baseline USD** means the shared capabilities and behavioral commitments
extensions can rely on. This is a proposed working definition, not an agreed
inventory or a synonym for everything shipped in OpenUSD. Start with references
to the existing specifications and identify which additional shared contracts
need clarification, rather than write a second Core Specification.

The first useful baseline note would name those references and versions, explain
what an extension may build on without changing them, and distinguish preserving
data from interpreting it correctly. Support for unfamiliar schemas, metadata,
or domain behavior must be checked for the particular surface and operation;
there is no blanket claim here that every consumer preserves every extension.
The [boundary discussion](#independent-adoption-and-baseline-boundaries) develops
this distinction, including integration with UsdGeom transforms.

**Review sought:** Identify concrete gaps, counterexamples, and missing functional
requirements. Test lightweight reservation, mandatory naming conventions,
ownership transitions, profile-based support claims, and validation independent
of OpenUSD against a worked case. The objective is alignment on requirements,
usable guidance, and accountable follow-through. Specific mechanisms remain
reviewable; implementation choices follow the functional contract.

## Contents

1. [Introduction](#introduction)
2. [Problem Statement](#problem-statement)
3. [Functional Requirements](#functional-requirements)
4. [Survey of Approaches](#survey-of-approaches)
5. [Case Study: `Prelim` in the UsdSolid B-Rep Proposal](#case-study-prelim-in-the-usdsolid-b-rep-proposal)
6. [Case Study: ROS and Newton](#case-study-ros-and-newton)
7. [Design Considerations](#design-considerations)
8. [Open Questions for Discussion](#open-questions-for-discussion)
9. [Relationship to Other Proposals](#relationship-to-other-proposals)
10. [Next Steps](#next-steps)

## Introduction

This proposal develops requirements for identifying the owners of USD extensions
and isolating their identifiers across tools and authored content. The aim is to
support reliable interoperability while letting independently governed capabilities
ship, gain production experience, and evolve toward broader agreement where useful.

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

- **Reliability:** USD content works predictably across tools and over time.
  Explicit ownership, dependencies, and compatibility expectations let adopters
  understand what a tool's support claim means and how unsupported capabilities
  affect a workflow. Supporting USD does not require every application to
  implement every extension.
- **Leadership:** USD turns growing domain demand into deployed capabilities,
  with a clear path from experimentation to shared standards.
  Independently governed extensions let domains prototype, ship, learn
  from production use, and correct designs without waiting for full AOUSD
  approval of each new feature. Proven capabilities can then seek broader
  adoption and standardization with evidence from that experience.

Baseline USD, vendor and domain extensions, profiles, and a multi-part specification
are mechanisms for achieving these outcomes. Namespace isolation supplies the
ownership and naming foundation for independently governed extensions. This
proposal develops that mechanism; it does not settle baseline scope, conformance
infrastructure, or the organization of specification Parts.

The proposed first deliverable covers typed schema identifiers, applied API schema
identifiers, and property names. It must identify how those names relate to
capability/profile identifiers and metadata dictionary keys, so these surfaces do
not acquire incompatible ownership conventions. File format and asset resolver
identifiers remain in the inventory for subsequent work; binary plugin loading,
distribution, and sandboxing are separate concerns. Concrete cases can identify
missing surfaces without delaying agreement on the common requirements.

## Functional Requirements

These requirements describe the functional contract. Concrete syntax and mechanisms
will be evaluated against them. The initial deliverable must include specific
naming conventions for every covered surface; an extension name alone does not
isolate schema or property identifiers unless those identifiers follow the rules.

### Terminology

This document uses **prefix** and **namespace** as related but distinct terms:

- A **prefix** is the leading token, or sequence of tokens, in an identifier that denotes ownership or scope (e.g. `nvidia`, `KHR_`, `AOUSD.GeomWG`).
- A **namespace** is the space of identifiers scoped by a given prefix -- a prefix establishes a namespace, within which further hierarchy (domain, feature, version) is composed.
- An **extension reservation** records an extension name and its governing owner. Together with mandatory surface-specific naming rules, it establishes the scope for identifiers introduced by the extension. Reservation does not approve feature semantics or imply implementation support.
- **Ownership**, **maturity**, **version**, and **implementation support** answer different questions: who
  controls a definition, how much agreement or validation it has received,
  which semantic contract applies, and which consumers implement that contract.
  An owner can be a vendor, an externally governed community project, a
  multi-organization collaboration, or a standards body. An owner's name does
  not imply that an extension is exclusive to one engine, or that another engine
  implements it. A marker such as `Prelim` expresses maturity;
  it does not by itself identify an owner or reserve names against other
  preliminary extensions.

Where the distinction doesn't matter, this document refers to them together as "namespace/prefix."

### Hierarchy composition

An identifier composed under this convention carries at least two independent axes:

- **Owner hierarchy**: who governs the extension. May be a single flat token, or a multi-level hierarchy the owner defines for its own purposes. That sub-hierarchy is the owner's own to define -- this convention doesn't prescribe what the intermediate levels mean. A standards body's sub-levels might be working groups; a single vendor's sub-levels might be internal tiers, divisions, product lines, or something else entirely. Either kind of owner needs the *option* of a sub-hierarchy, not just consortium-style owners.
- **Domain hierarchy**: what functional area the extension addresses, and how specific a feature within that area it names.

Illustrative combinations (delimiter, casing, and token order are not prescribed):

| Owner hierarchy | Domain hierarchy | Illustrative combined scope |
|---|---|---|
| `AOUSD.GeomWG` | `brep` | `AOUSD.GeomWG.brep` |
| `yoyodyne.tierA` | `dimensional.contabulator` | `yoyodyne.tierA.dimensional.contabulator` |
| `yoyodyne` | `dimensional.contabulator` | `yoyodyne.dimensional.contabulator` |

The AOUSD example is illustrative, not a namespace allocation. A vendor's internal
levels need not correspond to working groups. `yoyodyne` is the Profiles proposal's
placeholder vendor. The B-Rep family includes `BrepArray` and its associated API
schemas; a shared domain token does not itself establish ownership.

### A. Namespace and prefix isolation requirements

- **R1 -- Ownership legibility.** The convention must make ownership of an extension identifier immediately visible, without prior knowledge of a pipeline-specific convention.
- **R2 -- Hierarchical scoping.** The convention must support nested/hierarchical scoping on both axes above, without prescribing a specific delimiter, casing rule, or token ordering.
- **R3 -- Owner sub-hierarchy independence.** The owner portion of an identifier must support its own internal sub-hierarchy, independent of and orthogonal to the extension's domain/feature hierarchy. This applies to standards bodies, community projects, multi-organization collaborations, and vendors structuring their namespaces (e.g. into internal tiers, divisions, or product lines). The convention should not assume what an owner's sub-hierarchy levels mean, only that they can exist. A single flat owner token and a multi-level owner hierarchy must both be expressible under the same convention.
- **R4 -- Mandatory conventions for each naming surface.** Schemas, properties,
  and other covered identifiers introduced by an extension must follow specific
  naming conventions derived from its reserved extension name and ownership
  scope. Concrete syntax may differ by surface, but each must satisfy R1-R3 and
  preserve isolation in authored content, including separately authored layers.
  Reserving the extension name must be sufficient to allocate conforming names
  within that scope; individual schema and property names require no further
  reservation. Reusing an existing definition retains its governing identity;
  implementing it does not create a separately owned definition.
- **R5 -- Ownership assurance and collision handling.** Specify how an extension
  name and its owner are recorded, how sub-scopes are delegated, and how naming
  violations and conflicting definitions are detected and reported. Reservation
  and mandatory naming conventions work together: a bare naming suggestion is
  insufficient. No mechanism may silently substitute a conflicting definition.
  The procedure must be proportionate to establishing identity, rather than a
  review of feature semantics. Its exact administrative mechanism remains open.
- **R6 -- Independent entry, evolution, and ownership transitions.** Independently
  governed extensions can prototype and ship within the naming and baseline
  contract without seeking standardization. Community and multi-organization
  work may enter directly under shared governance. Wider adoption or a change
  in maturity does not itself transfer ownership. Identifiers do not inherently
  survive an ownership transfer: define predecessor/successor relationships,
  grace periods, migration paths, and expectations for mixed composed content.
  Incompatible revisions likewise require explicit version and compatibility
  policies. Broader agreement is optional and does not automatically imply
  inclusion in the baseline or AOUSD ratification.
- **R7 -- Lightweight entry and proportionate commitments.** Beginning an internal
  prototype should be as lightweight as reserving an extension name. Reservation
  must not require a complete specification, implementation, commitment to
  publish, or AOUSD approval of feature semantics. Conforming identifiers are
  allocated under the reservation without further individual approvals.
  Documentation and evidence grow with publication, compatibility, support,
  and standardization commitments. Changes to existing shared contracts or use
  of another owner's namespace require the relevant agreement. New domain
  behavior or integration requirements alone do not require central governance.
- **R8 -- Implementation-independent extension and validation contracts.** The
  vendor extension paradigm, naming rules, and validation contract must be
  definable and usable without OpenUSD's plugin system. Specify the inputs,
  conformance conditions, and expected diagnostic meaning so independent
  implementations can provide equivalent validation. OpenUSD's facilities may
  implement the contract without becoming prerequisites for it.
- **R9 -- Validation with proportionate cost.** Naming conformance and collision
  detection belong within the broader validation paradigm represented by
  `usdValidation`. Define validation scope and required inputs, including which
  checks concern extension definitions and which concern authored or composed
  content. Permit checks at appropriate workflow boundaries and reuse of valid
  results; do not require full validation on every composition or value query.
  Performance matters, but the requirements do not prescribe a caching strategy
  or claim validation is free. Validation of declarations does not prove semantic
  compatibility or support for combinations of extensions.

These requirements establish entry and validation obligations. They imply no
claim that independently valid extensions can be combined arbitrarily. Vendors
can declare supported combinations through their own profiles, with evidence
appropriate to the claim.

### B. Relationship to discoverability

Adapted from Gordon Bradley's comment on the governance doc:

- Define the set of extension points that meaningfully extend USD (property, schema type, file format, asset resolver, metadata, and others not yet named).
- Provide a unified extension model letting companies, individuals, and working groups (e.g. AECO) define a related set of those extension points as a shareable, optional extension to USD.
- Define a discovery/registration mechanism to reduce duplicated effort. Collision-surfacing is a secondary benefit of this mechanism, not its primary purpose -- that is covered by R5 above.

## Survey of Approaches

Existing USD-native precedent and external standards bodies offer mechanisms to
compare. The case studies below examine how those requirements apply to concrete
extensions; neither their adoption nor their naming establishes an AOUSD policy.

| Source | Syntax | Collision prevention | Reservation or allocation | Promotion path |
|---|---|---|---|---|
| **USD Profiles** (proposal PR #75, Dhruv Govil, merged 2025-01; updated by PR #110, Nick Porcino, merged 2026-06; now shipped in OpenUSD as `usdProfiles`) | Reverse-domain (e.g. `usd.geom.skel`, `yoyodyne.dimensional.contabulator`) | Unique-prefix convention + mandatory ancestral derivation from the `usd` root capability | None | Yes -- worked example in Appendix B: vendor (`epic.nanite`) &rarr; AOUSD WG standardization (`aousd.meshlet`) &rarr; USD core (`usd.meshlet`) |
| **Khronos glTF extension registry** | `PREFIX_scope_feature`, prefix uppercase + underscore, remainder lowercase snake_case | Reserved owner prefix plus mandatory naming rules | Yes -- GitHub issue with prefix, owner, and contact (`Prefixes.md`); not a feature review | Specification maturity stages: Proposal &rarr; Initial Draft &rarr; Review Draft &rarr; Release Candidate &rarr; Ratified. Prefix category and maturity are distinct; ratified extensions can retain `EXT_`. |
| **OpenGL extension registry** | Vendor/category naming conventions for extensions and API identifiers | Naming rules plus allocation of shared enumerant resources | Small reservation PR for enumerant blocks; completion and registration of a specification are separate steps | Vendor, multi-vendor, and approved extensions are distinct commitments |
| **IETF RFC 6838** (media type registration trees) | `facet.subtype`, e.g. `vnd.bigcompany.funnypictures` | Tree-based: `vnd.` (vendor), `prs.` (personal), `x.` (private/experimental, explicitly not for interop) | Yes -- IANA, centralized and heavyweight | None -- no formal vendor-to-standards graduation |
| **W3C Custom Elements (Web Components)** | Mandatory hyphen in the local name | Structural guarantee only: spec commits that no future built-in HTML/SVG/MathML element name will contain a hyphen | None | N/A |

These precedents do not require every extension to pass through a vendor prefix,
then a multi-vendor prefix, then a ratified prefix. The
[glTF registry](https://github.com/KhronosGroup/glTF/blob/main/extensions/README.md)
allows `KHR` for work intended for ratification, and lists ratified extensions that
retain `EXT` to preserve their established names. Its specification maturity stages
are distinct from prefix categories. Likewise, the Profiles proposal's worked
example illustrates a possible vendor-to-WG-to-core path; it does not establish a
mandatory renaming sequence for this proposal. Direct multi-vendor or WG entry is allowed under R6. A maturity change alone does
not require a new owner; an ownership transfer needs an explicit identifier
transition, grace periods, and migration paths.

### Lightweight allocation: the applicable Khronos precedent

The [glTF reservation instructions](https://github.com/KhronosGroup/glTF/blob/main/extensions/README.md)
ask for a prefix, vendor name, and URL/contact through a GitHub issue; membership
is not required. A completed feature specification is not an input to that
reservation. The [prefix table](https://github.com/KhronosGroup/glTF/blob/main/extensions/Prefixes.md)
records companies and projects. For example, the
[Bevy request](https://github.com/KhronosGroup/glTF/issues/2497) is a short request
with a contact URL. glTF separately specifies extension naming rules and a
template and pull-request route for publishing extension specifications.

The current [OpenGL registry instructions](https://github.com/KhronosGroup/OpenGL-Registry#defining-new-extensions)
separate reserving enumerant blocks through a small XML-file PR from completing
and registering an extension specification. Allocation becomes official when the
reservation PR is merged. The repository cautions that older process documents
are largely outdated; use the current instructions rather than treating legacy
allocation policies as the present procedure.

The applicable requirement is a lightweight naming allocation, followed by
independent development under mandatory naming conventions. This proposal does
not equate a glTF owner-prefix reservation with a USD extension-name reservation,
or require USD to allocate OpenGL-style numeric resources. It carries over the
separation between administrative allocation and technical approval. A small
reservation record must suffice to start; conforming schema and property names
then follow without separate reservations. No turnaround guarantee is inferred
from the Khronos procedures.

USD must specify the naming relationship across each covered surface, including
opinions authored in separate layers. That is work for the convention, not
additional approval work for every identifier.

## Case Study: `Prelim` in the UsdSolid B-Rep Proposal

The B-Rep proposal provides a concrete example of a question the requirements
above state abstractly: **which extension surfaces does a marker attach to?**

Its governance journey is the one R6 describes. The schema was worked in the AOUSD
Geometry Working Group, socialized with other interest groups, and put up as
OpenUSD-proposals PRs -- more than one organization behind it, and past the point
where a single-vendor prefix would describe it accurately. `Prelim` is being
considered as a marker for preliminary status. The marker does not specify which
owner governs the extension or reserves its naming scope.

### What the marker landed on

[aousd/OpenUSD-proposals PR #2](https://github.com/aousd/OpenUSD-proposals/pull/2)
adds the prefix to the typed prim, `BrepArray` becoming `PrelimBrepArray`. The
library already carried it as `PrelimUsdSolid`. Left unprefixed: the applied API
schemas (`BrepPointAPI`, `BrepCurve3dNurbAPI`, `BrepCurveUvNurbAPI`,
`BrepSurfaceNurbAPI`), the property namespace prefix `brep`, and the authored
examples in the proposal's own README, which still read `def BrepArray`.

The four applied API definitions use `apiSchemaCanOnlyApplyTo` to express intended
applicability to the prefixed type. When encoded correctly, this associates the
API with the target type's maturity marker without changing the API identifier.

An earlier revision used `PrelimUsdSolidPrelimBrepArray` in those entries. That
internal type name follows from combining the library prefix and class name;
the repeated `Prelim` alone is not an error. OpenUSD 26.08's
[`CanApplyAPI` check](https://github.com/PixarAnimationStudios/OpenUSD/blob/v26.08/pxr/usd/usd/prim.cpp#L645)
looks up these entries by schema identifier, however, so the intended target entry
is `PrelimBrepArray`. [The author corrected the four entries on October 5](https://github.com/aousd/OpenUSD-proposals/pull/2#issuecomment-5998372106);
the [reviewed revision](https://github.com/umhoefer/OpenUSD-proposals/commit/3f3350ae7bf45cc9c06c2d566223d3579c0aacc1)
contains that correction. This addresses the lookup issue; an end-to-end check
with the generated B-Rep plugin remains separate from this source review.

Keeping the API identifiers stable reduces the number of identifiers that would
change if graduation removed the marker. A prim authored with `PrelimBrepArray` also exposes preliminary
status through its type name. It does not establish ownership or isolate every
identifier the extension introduces.

### Where it does not hold

**Schema identifiers are globally registered; applicability checks do not reserve names.**
With correct target identifiers, `apiSchemaCanOnlyApplyTo` guides `CanApplyAPI`;
[`ApplyAPI` itself](https://github.com/PixarAnimationStudios/OpenUSD/blob/v26.08/pxr/usd/usd/prim.cpp#L825)
does not enforce that target list. Another party defining a differently-shaped `BrepPointAPI`
collides in the schema registry regardless of either API's intended target types.
That is R5, and structural association does not address it.

**Library naming does not qualify every scene identifier.** `libraryPrefix`
qualifies the internal type name. It does not automatically provide ownership
scope for scene-facing schema identifiers or property names. Each surface needs
an explicit naming rule.

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

This is R4 and R6 in practice: one extension reservation must cover all conforming
identifiers through explicit surface-specific rules. A maturity change alone need
not change ownership; an ownership transfer requires a managed identifier transition
with grace periods and migration paths.

## Case Study: ROS and Newton

[REP 158](https://reps.openrobotics.org/rep-0158-2006/) develops OpenUSD asset
conventions for robotics, including ROS integration and physics-engine-specific
features. It provides a second case for separating ownership from applicability
and from a path to standardization.

The [ROS schema definitions](https://github.com/ros-simulation/openusd-schemas/blob/main/core/ros/schema.usda)
use scene-facing names such as `RosContextAPI` and `ros:` properties, alongside
the separate internal library prefix `UsdRos`. The ownership convention must
describe each surface explicitly; one spelling does not automatically qualify
the others. A runtime ROS namespace, such as `/robot_1/camera`, has a different
purpose from either a USD prim path or an ownership prefix.

During review, [PR #30](https://github.com/openrobotics/reps/pull/30) removed a
proposed intermediate `ExtendedPhysics` stage in favor of separately layered,
prefixed engine extensions, with mappings where semantics align and reporting
when features are ignored or approximated. This is a domain-specific deployment
policy to learn from, rather than a universal requirement that every extension
pass through the same tiers or rename itself on promotion.

For a project such as [Newton](https://github.com/newton-physics), the governing
project and the engines that implement particular behaviors are separate facts.
A project-owned extension could be adopted by multiple implementations while
remaining governed outside AOUSD. A project prefix alone establishes neither
engine exclusivity nor portability. Those are support and compatibility claims
that need definitions and evidence. Vendors can declare supported extension
combinations through their own profiles. Naming isolation and independent
deployment imply no combination claim.

The resulting checks for this proposal are:

- **Who governs the identifiers?** Include community and project stewardship;
  naming examples are not proof of a reservation or conflict-handling mechanism.
- **What survives composition, and what is implemented?** Layers let users
  compose or select opinions. Prefixes isolate identifiers. Neither proves
  that two engines implement equivalent behavior or that fallback preserves
  the intended simulation.
- **What happens when support is missing?** State which features are required,
  which may be ignored or approximated, and how the consumer makes any loss
  visible. A common report format is a further design question.

ROS integration can interpret the USD values obtained through ordinary
composition and value resolution, then apply domain behavior. That illustrates
the proposed additive boundary. Any proposal to change those underlying USD
rules would be a different commitment requiring the relevant broader review.

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

### Independence from OpenUSD's plugin system

The vendor extension paradigm and its validation contract must be independent of
OpenUSD's plugin system, including `plugInfo.json`, C++ namespace macros (`PXR_NS`),
and dynamic loading. R8 applies to the contract for naming, declarations, and
validation, not just to the ability to avoid loading a binary plugin. OpenUSD may
use its existing infrastructure to implement these requirements. Other
implementations must be able to satisfy them without adopting that infrastructure.

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

### Validation and performance

Naming conformance and collision detection fall under the validation concerns
represented by OpenUSD's
[`usdValidation` framework](https://openusd.org/dev/api/md_pxr_2usd_validation_2usd_validation_2_r_e_a_d_m_e.html).
That framework supports core, schema, and client-provided rules, with validators
registered through plugins or directly through registry APIs. Its
[`UsdValidationContext`](https://openusd.org/dev/api/class_usd_validation_context.html)
can run selected validators over layers, stages, or prims. These are useful
implementation facilities; they are not an implementation-independent contract.

The extension model expands the need to express validation rules and diagnostic
meaning independently of OpenUSD. Specify the reservation record and extension
definitions required for a check, what authored/composed content is in scope,
and how a violation is located and reported. A scene alone need not contain all
ownership or definition information. An incomplete set of validation inputs must
not be mistaken for a successful check of all relevant definitions.

Enforcement need not mean preventing every nonconforming authoring operation.
Validation can occur when definitions are published or installed, or at asset
and workflow boundaries as appropriate to the check. The contract must allow
efficient validation and reuse of results under stated validity conditions;
it must not impose full naming validation on every composition or value query.
Checking definition names and checking a composed asset have different scopes
and costs. No particular caching scheme, validation scheduler, or OpenUSD runtime
hook is selected here.

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

Vendors can define their own profiles to state which extension combinations they
support. Two extensions may be individually conforming and additive while
prescribing incompatible domain behavior, such as different controls for the same
robot link. Independent deployment and naming isolation make no inherent claim
that their combination is supported. Such a claim must be explicit; declaring it
is distinct from demonstrating it.

### Independent adoption and baseline boundaries

For this proposal, **baseline USD** refers to the shared capabilities and behavioral
commitments on which extensions can rely. The
[AOUSD Core Specification](https://aousd.org/usd-core-specification/) provides
normative definitions of data representation, scene construction, and interchange
formats. A lightweight baseline description could reference those definitions and
make extension boundaries and compatibility expectations explicit. The precise
baseline inventory remains a separate question; neither inclusion in an OpenUSD
distribution nor adoption of an extension alone establishes that inventory.

The distinction matters for unsupported data. The published
[Core Specification 1.0.1, Extension Metadata Fields](https://github.com/aousd/specifications-public/blob/main/core/1.0.1/core_spec.md#extension-metadata-fields)
leaves reading and authoring unknown extension metadata fields to the
implementation, and does not allow extension fields to be required to consume
a layer. Its [schema scope](https://github.com/aousd/specifications-public/blob/main/core/1.0.1/core_spec.md#scope-5)
also leaves the mechanism for defining and ingesting schema extensions to the
implementation. These provisions must not be expanded into a general guarantee
that arbitrary extension data survives every operation. A baseline or extension
contract should specify the surface, operation, dependency, and tested expectation.

The proposed behavioral boundary is that an **additive extension builds on USD's
existing composition and value-resolution semantics**. Its USD-authored inputs
continue to use those semantics; it adds domain interpretation or computation on
top of the resolved values. Authored extension opinions can change resolved values through
ordinary USD mechanisms without changing the rules by which values are resolved.

Geospatial and B-Rep capabilities illustrate a boundary worth examining: their
domain behavior can build on core value resolution while requiring an explicit
relationship with shared behavior such as
[UsdGeom transforms](https://openusd.org/release/api/class_usd_geom_xformable.html).
Using an existing behavioral contract, adding domain behavior or an integration
requirement for supporting consumers, and changing an existing shared contract
are different commitments. Vendors can develop and deploy new domain behavior
and integration requirements among supporting consumers without central feature
approval. A new integration requirement alone does not transfer governance to
AOUSD. Changing the meaning of an existing shared identifier or contract requires
the relevant broader agreement. Architectural collaboration can help resolve
integration questions without becoming a prerequisite for all independent deployment. Namespace isolation identifies ownership; it does not
establish behavioral compatibility by itself.

The proposed entry rule is that an owner may publish and ship an additive,
owner-prefixed schema without full AOUSD approval of its feature semantics. Lightweight extension
reservation and mandatory naming conventions establish its naming scope without
turning individual schema or property definitions into a feature-review queue. For publication and support claims, the extension must
state its semantics, baseline/version dependencies, and expected behavior when a
consumer lacks support. A consumer may decline an extension; preserving its data
does not imply correctly interpreting it.

For example, independently developed text and line-style schemas could use
their governing owner's identifiers and build adoption among willing applications.
This illustrative pathway should not require waiting for inclusion in OpenUSD's
core distribution or AOUSD's highest governance tier.

An extension that changes shared composition or value-resolution rules, redefines
an existing baseline identifier's semantics, or uses another owner's namespace
crosses a different boundary. Those changes need the relevant broader agreement
even during initial rollout.

Governance should be proportionate to the commitments being sought:

| Commitment | Proposed review and evidence |
|---|---|
| **Internal prototype** | Lightweight extension-name reservation and conforming identifier naming; no complete specification or central feature approval required to begin. |
| **Published independently governed extension** | Document semantics, dependencies, compatibility policy, and unsupported-consumer behavior; validate naming conformance. Vendors may declare supported combinations in their profiles. Additive work can ship without full AOUSD feature approval. |
| **Shared, multi-vendor extension** | Agree stewardship and compatibility policy; demonstrate that participating implementations interpret the extension consistently. |
| **AOUSD standard extension or domain specification** | Formal technical review, explicit support and conformance expectations, and maintenance commitments, informed by production experience. |
| **Change to the shared baseline** | Broader review of cross-domain applicability, effects on existing content and implementations, ongoing test and maintenance responsibilities, and compatibility or migration costs. |

These commitments do not prescribe a mandatory sequence or require promotion.
Some extensions may remain independently governed. A change in maturity alone need not rename identifiers. A transfer of ownership
requires an explicit identifier-transition policy, grace periods, and migration
paths; existing content does not become the successor definition merely because
governance has changed. Production experience may also reveal a
mistaken design; revisions need an explicit compatibility policy regardless of
whether the extension seeks promotion. Broader technical agreement, resource
prioritization, and escalation authority are distinct decisions and should have
named owners rather than being collapsed into one approval step.

### Evolution and ownership migration: schema-versioning precedent

Ownership migration extends an existing schema-evolution problem. OpenUSD's
[schema-versioning design](https://openusd.org/dev/wp_schema_versioning.html)
distinguishes an identifier from its family and major version. For example,
`Cylinder` and
[`Cylinder_1`](https://openusd.org/dev/api/class_usd_geom_cylinder__1.html)
provide separate schema definitions; the latter exposes top and bottom radii.
Different prims in a composed scene can use different versions. Opinions on the
same prim resolve to a single typed-schema identifier; composition does not
automatically translate an old property representation into a new one.

Ownership transfer can change the prefix, the schema family, and property names.
OpenUSD's current family/version mechanism does not by itself express that whole
relationship. The requirement is broader: identify predecessor and successor
contracts, specify grace periods and migration paths, and define expectations for
mixed authored and composed content. Applicable versioning paradigms provide
precedent; this proposal does not select automatic aliasing, conversion, or a
new schema-family mechanism. Transitions must account for typed names, applied
API identifiers, and properties rather than assuming one rename covers them all.

## Open Questions for Discussion

These questions seek gaps in the functional requirements and workable guidance
for foundations needed by extensions already being developed and deployed.
The priority is aligning on the functional contract and turning it into usable guidance.

1. **Lightweight reservation and naming.** What minimum reservation record and
   surface-specific naming rules make one extension reservation sufficient for
   all identifiers it introduces? Show a concrete collision or ambiguous case
   that the proposed requirements fail to handle, including separately authored
   property opinions. Identify any missing initial surface.
2. **Implementation-independent validation.** What inputs, conformance rules,
   and diagnostic meaning must be shared so OpenUSD and independent
   implementations can provide equivalent checks? Distinguish checks on
   definitions from checks on layers or composed content, and specify appropriate
   validation boundaries without requiring repeated checks on every value query.
3. **Independent behavior and explicit support claims.** Show a case in which
   adding domain behavior requires changing an existing shared contract. Identify
   that contract and the agreement needed. Use vendor-defined profiles to make
   combination support explicit; do not infer it from naming conformance.
4. **Evolution and ownership transfer.** Work through grace periods, predecessor
   and successor identifiers, migration paths, and mixed composed content for
   incompatible versions or ownership changes. Which requirements extend beyond
   existing schema-family/version paradigms?
5. **Worked case and accountable delivery.** Apply R1-R9 to B-Rep or ROS/Newton.
   Record the authoring and maintenance owners, a concrete deliverable, its
   completion test, target date, and the appropriate approving forum. A TAC
   sponsor and small authoring group are candidates, subject to confirmed mandate
   and capacity; do not assume an unassigned body will perform the work.

Specific naming syntax and administrative mechanisms remain open for review.
The immediate priority is agreement on functional requirements, followed by a
reviewable convention and demonstrated case.

## Relationship to Other Proposals

- **USD Profiles** (proposal PR #75, Dhruv Govil; updated by PR #110, Nick Porcino; shipped in OpenUSD as `usdProfiles`, with its own [overview](https://github.com/PixarAnimationStudios/OpenUSD/blob/dev/docs/user_guides/schemas/UsdProfiles/overview.md) and [ClaimsAPI](https://github.com/PixarAnimationStudios/OpenUSD/blob/dev/docs/user_guides/schemas/UsdProfiles/ClaimsAPI.md) documentation, which supersedes the proposals): this document builds on and extends its naming and graduation-pathway model rather than proposing a competing scheme.
- **Separation of Concerns for Identifiers in USD** (in progress, this repo): adjacent but distinct -- that proposal addresses identifying instances against external systems; this document addresses ownership/naming of the extension surface itself.
- **Authorship** (PR #106) and **IP Protection** (PR #107): not namespace-related in substance, but used here as structural precedent for how recent AOUSD cross-cutting proposals are organized.

## Next Steps

- Align on R1-R9 using concrete gaps and counterexamples. Preserve implementation
  independence and lightweight entry as requirements when evaluating mechanisms.
- Assign an authoring owner and maintenance owner. For each agreed work item,
  record its deliverable, completion test, target date, dependencies, and approving
  forum; confirm mandate and capacity rather than implying an appointment.
- Specify the minimal extension reservation record and mandatory naming rules for
  typed schemas, applied API schemas, and properties, with mappings to metadata
  and capability/profile identifiers. One extension reservation must suffice for conforming
  identifiers without individual approvals or a complete discovery system.
- Specify an implementation-independent validation contract, using usdValidation
  as an implementation reference. Demonstrate equivalent outcomes for a shared
  set of conforming and nonconforming examples without requiring OpenUSD's plugin
  system. Record validation scope and performance expectations.
- Work the B-Rep and ROS/Newton cases through naming, domain integration,
  vendor-profile support claims, unsupported-consumer behavior, incompatible
  revisions, and ownership transitions with grace periods and migration paths.
- Compare concrete syntax and administrative procedures against the requirements.
  Produce usable guidance and record unresolved choices with accountable owners.
