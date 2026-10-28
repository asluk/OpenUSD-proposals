# Namespace and Prefix Isolation for USD Extensions

**Author:** Aaron Luk (NVIDIA)

**Status:** Draft

## Summary

This proposal establishes requirements for naming independently governed USD
extensions. An owner reserves an extension's naming scope and uses prescribed
conventions for the schema identifiers, property names, and other covered names
it introduces. One reservation must suffice for those conforming names without
separate allocation or approval of each identifier.

The naming contract must establish ownership, distinguish independent definitions,
detect naming conflicts, and support identifier transitions. Its rules and
validation must be usable independently of OpenUSD's plugin system. Reservation
must be lightweight enough to support internal prototyping without a complete
feature specification or a commitment to publish.

This proposal develops the Namespace and Prefix Isolation requirement in the
[Steering Committee's USD Extension Ecosystem Governance working proposal](https://docs.google.com/document/d/1zL7Igy5QN6bTHZavczkjaW2U5TBk95hP_Ooa_zL-tJc/edit),
led by Sean Snyders. Naming isolation is one foundation of that broader work.
It establishes how definitions are named and distinguished; it does not approve
their semantics, establish implementation support, or define consumer behavior.
Concrete syntax, reservation procedures, and maintenance responsibilities remain
open for review.

## Motivation

Stakeholders are already developing and deploying USD schemas. Independent
definitions can acquire the same schema identifiers or property names, producing
registration errors, ambiguous interpretation, or silent use of the wrong
definition. The problem affects both the names registered by implementations
and those exchanged in authored content.

A library prefix does not necessarily qualify a scene-facing schema name. A
typed schema name does not automatically qualify its associated applied APIs
or properties. Property opinions may be authored in separate layers without a
local type declaration. A naming convention must address these surfaces together
so independently authored content can be combined without confusing unrelated
definitions.

Common naming rules contribute to reliable content across tools and over time.
Lightweight reservation also supports faster development in parallel across
domains. Those are contributions to the broader reliability and leadership
goals, not claims that naming alone provides behavioral interoperability or a
complete pathway for extension deployment.

Naming isolation must be usable before a complete discovery or distribution
service exists. Discovery can help people find existing work, but listing an
extension neither establishes ownership by itself nor prevents its identifiers
from colliding.

## Scope

The initial contract covers typed schema identifiers, applied API schema
identifiers, and property names. It must explain how their ownership scopes
relate to metadata keys and capability/profile identifiers so these surfaces do
not develop contradictory naming conventions. File format and asset resolver
identifiers remain in the inventory for subsequent work.

The proposal addresses allocation of naming scope, naming conventions, delegation,
collision handling, naming validation, and identifier transitions. Identifier
migration includes changes caused by ownership transfer or incompatible revisions;
this proposal does not define a general semantic versioning system.

The broader extension model must address dependencies, unsupported capabilities,
behavioral compatibility, support claims, deployment policies, and standardization.
This proposal identifies where those concerns use naming information. It does
not set their policies. Binary loading, distribution, sandboxing, certification,
and a complete extension catalog are also outside its scope.

## Terminology

- **Owner:** The vendor, community project, collaboration, or standards body
  authorized to govern a naming scope. Naming authority is distinct from
  intellectual-property ownership of an asset or implementation.
- **Extension:** A related set of definitions governed by an owner. This term
  identifies the unit whose naming scope is reserved; it does not prescribe how
  the definitions are packaged, loaded, or standardized.
- **Reservation:** An allocation associating an extension name, its owner, and
  the naming scope the owner may use under the applicable conventions.
- **Prefix:** The leading token or sequence of tokens denoting ownership or
  scope in an identifier.
- **Namespace:** The space of names scoped by a prefix or equivalent qualification.
- **Naming surface:** A class of identifiers with its own syntax and lookup
  context, such as typed schema identifiers or property names.

Ownership, maturity, version, and implementation support are separate facts.
A marker such as `Prelim` describes maturity, not ownership. A project name does
not establish engine exclusivity. Implementing an existing definition does not
create a new naming authority for it.

## Functional Requirements

### R1. Ownership Legibility

The naming convention must make an identifier's governing ownership scope
apparent without relying on a pipeline-specific convention. The relationship
between that scope and its owner must be verifiable against the reservation
information. A product name or trademark alone does not establish an allocation.

### R2. Hierarchical Scoping

The convention must support owner hierarchies and domain or feature hierarchies.
It must distinguish independent extensions under the same owner as well as
extensions governed by different owners. Delimiter, casing, and token order
remain choices for the concrete convention.

### R3. Owner Sub-Hierarchies and Delegation

An owner must be able to define and delegate sub-scopes independently of the
domain hierarchy. Both a flat owner scope and nested scopes must be expressible.
The convention must not assign fixed meanings to an owner's intermediate levels.
Delegation must identify the authority responsible for the delegated scope.

### R4. Naming Across Surfaces

Every covered surface must have specific rules connecting an extension's
reservation to the identifiers it introduces. Syntax may differ by surface,
but the rules must preserve ownership legibility and isolate independent
definitions, including opinions authored in separate layers.

One extension reservation must suffice for all names it introduces in conformance
with those rules. Individual identifiers need no further reservation. Reuse of
an existing definition retains its existing identity and ownership scope.

### R5. Allocation and Collision Handling

The naming contract must establish how ownership and delegation are recorded,
what constitutes a conflicting allocation or definition, and how conflicts are
reported and resolved. It must distinguish intended reuse of a definition from
independent definitions claiming the same name. A consumer must not silently
substitute a conflicting definition.

A reservation allocates naming scope. It does not approve extension semantics
or make an endorsement, compatibility, or implementation-support claim.

### R6. Identifier Evolution and Ownership Transfer

The contract must provide policies for changes to reserved scope and derived
identifiers. Identifiers do not inherently survive an ownership transfer.
Transfers must identify predecessor and successor scopes, grace periods, and
migration paths for affected names.

Policies must account for typed names, applied API identifiers, property names,
and mixed composed content. They must also state how identifiers distinguish
incompatible revisions where needed. Wider adoption or a change in maturity
alone does not necessarily change ownership. Naming policies must not impose a
universal promotion or renaming sequence.

### R7. Lightweight Reservation

Beginning an internal prototype must be as lightweight as reserving an extension's
naming scope. Reservation must not require a complete specification,
implementation, commitment to publish, or review of feature semantics. An owner
can define conforming names within the allocated scope without individual
approvals. The reservation procedure and upkeep must remain proportionate to
the naming authority being allocated.

### R8. Implementation Independence

The naming contract and its validation must be definable and usable without
OpenUSD's plugin system, schema registry, code generator, or dynamic loading.
Specify naming rules, required inputs, and diagnostic meaning independently of
those facilities. OpenUSD may use them to implement the contract; other
implementations must be able to provide equivalent naming validation without
adopting them.

### R9. Naming Validation and Cost

Validation must distinguish checks on reservations and extension definitions
from checks on authored layers or composed content. Its results must state
their scope and identify missing inputs that prevent a conformance determination.
The absence of a detected collision must not imply that definitions outside the
checked inputs were examined.

Naming checks must support appropriate workflow boundaries and reuse of valid
results. Full validation must not be required on every composition operation or
value query. These requirements neither prescribe a caching strategy nor assume
that validation has no cost.

## Naming Contract

### Allocation and Authority

A concrete convention must explain the relationship between owner scope,
extension name, and the names introduced by that extension. An owner may govern
several extensions, and a collaboration may be the owner from the outset. The
allocation must distinguish their scopes without requiring that every extension
begin as a single-vendor effort.

The reservation information must be sufficient to identify the owner, the
allocated scope, and any relevant delegation or transition. The exact record
format, allocation procedure, and means of obtaining that information remain
design choices. The allocation must be unambiguous without requiring a complete
catalog of every extension, definition, or implementation.

Reserving an extension name is sufficient only in conjunction with naming rules
that isolate its derived identifiers. Administrative review concerns the naming
allocation. Whether the extension's feature semantics require any other review
belongs to the broader extension-governance process.

### Names Across Surfaces

The convention must specify how the same reservation governs typed schema names,
applied API names, and property names. It must also explain how the allocated
scope is recognizable when a property opinion appears without a local type or
API declaration. Association with a typed schema is not a substitute for a rule
on a separately addressable identifier.

Names on different surfaces need not share a literal spelling. They must have
an unambiguous relationship to the reservation under the rules for their lookup
contexts. Internal implementation names and names authored into content must be
identified separately. API instance names likewise must not be confused with
ownership qualification of the API definition.

Owner and domain hierarchy are independent axes. The following examples
illustrate that distinction, not an allocated scope or prescribed syntax:

| Owner hierarchy | Domain hierarchy | Illustrative combined scope |
|---|---|---|
| `AOUSD.GeomWG` | `brep` | `AOUSD.GeomWG.brep` |
| `yoyodyne.tierA` | `dimensional.contabulator` | `yoyodyne.tierA.dimensional.contabulator` |
| `yoyodyne` | `dimensional.contabulator` | `yoyodyne.dimensional.contabulator` |

An owner's levels might represent working groups, divisions, or another internal
structure. `yoyodyne` is the placeholder used in the Profiles proposal. Owner-first
naming is a candidate, but the requirements do not select token order or casing.

Existing shared definitions may be reused under their own identities. The naming
rules apply to definitions an extension introduces; they do not require an
implementer to rename another owner's definition. Adoption of the convention
also needs a transition policy for existing names, rather than assuming that
all deployed content can be renamed immediately.

### Validation

Naming validation falls within the broader validation paradigm represented by
OpenUSD's
[`usdValidation` framework](https://openusd.org/dev/api/md_pxr_2usd_validation_2usd_validation_2_r_e_a_d_m_e.html).
The framework provides an implementation reference, not the definition of naming
conformance. Its APIs, plugins, and registry must not become normative inputs
to an otherwise implementation-independent contract.

Validation rules must identify which inputs support each check. Reservation
checks examine allocation and delegation. Definition checks examine whether
introduced names conform to the allocated scope and whether supplied definitions
conflict. Content checks examine names in the relevant authored or composed
context using the applicable definitions and reservation information.

A scene alone may not contain all those inputs. A validator must distinguish
nonconformance from an inability to determine conformance. Definitions can be
checked when published or installed; content checks can run at suitable asset
or workflow boundaries. Results may be reused while their stated validity
conditions hold. No scheduler, transport protocol, or cache design is selected.

Naming validation establishes only the naming conditions it checked. It does not
verify extension semantics, approve a support claim, or prove that a combination
of extensions behaves correctly.

### Identifier Evolution

An ownership change can affect the reserved extension name, schema identifiers,
and property prefixes. Its transition policy must identify which names change,
the relationship between old and new names, the grace period, and the migration
path. It must state what happens when content uses both naming generations.
Automatic aliasing or conversion is not assumed.

Schema versioning provides relevant precedent. OpenUSD's
[versioning design](https://openusd.org/dev/wp_schema_versioning.html)
distinguishes schema identifiers, families, and major versions. `Cylinder` and
[`Cylinder_1`](https://openusd.org/dev/api/class_usd_geom_cylinder__1.html)
have separate definitions, with the latter exposing top and bottom radii.
Different prims can use different versions; opinions on one prim resolve to one
typed-schema identifier without automatic translation of the old properties.

Ownership migration extends that problem because prefixes, families, and property
names can change together. Existing schema-family machinery does not by itself
express the full relationship. This proposal requires explicit identifier relationships and
migration policies around those changes; the semantic conversion of data and
general schema-versioning policy remain separate work.

## Relationship to Extension Governance

The Steering Committee's broader extension work addresses discovery,
dependencies, compatibility, trust, lifecycle, and standardization. Names are
inputs to that work. The distinction is consequential in several places:

| Broader concern | Contribution of the naming contract |
|---|---|
| Discovery and distribution | Identifiable owners and definitions that a catalog can reference. Reservation does not require a complete catalog or package system. |
| Dependencies and profiles | Unambiguous identifiers for declarations to reference. Naming does not define dependency satisfaction or profile compatibility. |
| Unsupported capabilities | Distinguishable names even when a consumer lacks an implementation. Consumer fallback, warnings, refusal, or preservation obligations are defined elsewhere. |
| Independent deployment and shared behavior | Naming authority for an extension's own definitions. A prefix grants no authority to redefine another owner's names or shared behavioral contracts. |
| Standardization and maturity | Explicit ownership and identifier transitions. Adoption, review status, ownership transfer, and standardization are distinct events. |

The broader vendor extension model also needs implementation-independent
contracts. This proposal establishes that requirement for its naming and
naming-validation portion. It does not settle the wider model by selecting an
OpenUSD plugin mechanism, a shared baseline, an additive-behavior boundary, or a
support-claim policy. Vendors' profiles can describe supported combinations;
naming conformance itself carries no such claim.

## Precedents and Alternatives

The [glTF extension process](https://github.com/KhronosGroup/glTF/blob/main/extensions/README.md)
separates lightweight prefix allocation from publication of feature
specifications. A prefix request supplies a vendor name, requested prefix, and
URL or contact through a GitHub issue; membership and a completed feature
specification are not prerequisites. Its
[prefix table](https://github.com/KhronosGroup/glTF/blob/main/extensions/Prefixes.md)
records companies and projects. This illustrates how an allocation procedure
can remain small while naming rules govern identifiers introduced under it.

The current
[OpenGL registry instructions](https://github.com/KhronosGroup/OpenGL-Registry#defining-new-extensions)
similarly separate reservation of shared enumerant resources from completion and
registration of an extension specification. USD need not adopt numeric allocation
or reproduce every Khronos process. The relevant precedent is separating naming
administration from feature approval.

[USD Profiles and Capabilities](https://github.com/PixarAnimationStudios/OpenUSD-proposals/tree/main/proposals/profiles)
provides a USD naming precedent and demonstrates why capability identifiers also
need ownership conventions. Its illustrative vendor-to-working-group-to-core
progression does not establish a mandatory renaming sequence. The glTF registry
likewise distinguishes prefix categories from maturity and includes ratified
extensions retaining `EXT` names.

[IETF RFC 6838](https://www.rfc-editor.org/rfc/rfc6838) provides an allocation
precedent through media-type registration trees. In contrast,
[custom-element naming rules](https://html.spec.whatwg.org/multipage/custom-elements.html#valid-custom-element-name)
separate custom names from built-in names without isolating independently chosen
custom names from one another. A maturity marker such as `Prelim` has a similar
limitation for unrelated preliminary USD extensions.

Package qualification is another possible scoping mechanism. It must still
satisfy ownership legibility and preserve identity when names move between
dependency sets or appear in separately authored layers. Neither short names
within a package nor an index of implementations alone establishes those rules.

## Case Studies

### B-Rep

The [B-Rep prefix change](https://github.com/aousd/OpenUSD-proposals/pull/2)
exposes several naming surfaces. In the
[reviewed revision](https://github.com/umhoefer/OpenUSD-proposals/commit/3f3350ae7bf45cc9c06c2d566223d3579c0aacc1),
the typed name is `PrelimBrepArray`, the library prefix is `PrelimUsdSolid`, and
applied APIs include `BrepPointAPI` and `BrepCurve3dNurbAPI`. Properties use `brep:`.
The work involves multiple organizations through the Geometry Working Group;
single-vendor ownership would not describe that stewardship accurately.
`Prelim` identifies maturity but does not reserve ownership.

An illustrative excerpt shows the distinct identifiers:

```usda
def PrelimBrepArray "Cube" (
    prepend apiSchemas = ["BrepPointAPI:vertexPoint", "BrepCurve3dNurbAPI:edge3dNurb"]
)
{
    uniform double[] brep:intersectTol3d = [0.00002]
    uniform uint[] brep:regionCount = [2]
}
```

This is not a complete asset or a proposed final spelling. The naming convention
must relate the typed name, each API definition, and the property prefix to the
reserved scope. API instances such as `vertexPoint` and `edge3dNurb` do not
reserve the API definition's name. Property opinions in separate layers must
remain distinguishable without assuming a local type declaration.

Applicability also does not reserve a name. `apiSchemaCanOnlyApplyTo` guides
[`CanApplyAPI`](https://github.com/PixarAnimationStudios/OpenUSD/blob/v26.08/pxr/usd/usd/prim.cpp#L645),
while [`ApplyAPI`](https://github.com/PixarAnimationStudios/OpenUSD/blob/v26.08/pxr/usd/usd/prim.cpp#L825)
does not itself enforce the target list. Another independent definition of
`BrepPointAPI` can still collide regardless of intended target types.

The distinction between internal and scene-facing names matters here. Four
applicability entries previously used `PrelimUsdSolidPrelimBrepArray`; those
entries require the schema identifier `PrelimBrepArray`. The repeated `Prelim`
was not itself the error. The
[October 5 correction](https://github.com/aousd/OpenUSD-proposals/pull/2#issuecomment-5998372106)
is present in the reviewed revision. This is a source-level naming observation,
not generated-plugin end-to-end verification.

The naming test is whether one reservation and its rules cover all these
surfaces, reject an independently conflicting definition, and support a managed
transition if ownership changes. A typed-name migration alone does not migrate
API or property opinions. Domain interpretation of B-Rep data is outside that
test.

### ROS and Newton

[REP 158](https://reps.openrobotics.org/rep-0158-2006/) and the
[ROS schema definitions](https://github.com/ros-simulation/openusd-schemas/blob/main/core/ros/schema.usda)
provide another cross-surface example: `RosContextAPI`, `ros:` properties, and
the internal library prefix `UsdRos`. A runtime ROS namespace such as
`/robot_1/camera` has a separate purpose from extension ownership or a USD prim
path. The convention must establish which names qualify the definitions
exchanged in USD content.

The engine-prefixed layering discussed in
[REP pull request #30](https://github.com/openrobotics/reps/pull/30)
illustrates independently named definitions. Their naming scopes must remain
distinct when their layers contribute to the same scene. This does not test
simulation equivalence, mappings between engine behaviors, or consumer fallback.

A project such as [Newton](https://github.com/newton-physics) may govern an
extension implemented by multiple engines. Its reservation identifies the
project's naming authority, not the set of engines that support it. Additional
adopters need not acquire ownership, and adoption alone need not rename its
identifiers. A transfer of naming authority requires the transition policy in
R6.

## Open Questions

1. What minimum reservation information establishes ownership and delegation,
   and who maintains the records and resolves competing allocations?
2. Which concrete conventions map one extension reservation to typed schema,
   applied API, and property names, including independent extensions under one
   owner? How do metadata and capability/profile names refer to those scopes?
3. What information is needed to validate each surface, and how are conflicting
   definitions distinguished from intended reuse or insufficient inputs?
4. Which existing names need transition arrangements, and how should grace
   periods and mixed old/new content be handled across ownership changes or
   incompatible identifier revisions?

## Implementation Plan

The work has three deliverables:

- A reservation procedure and naming convention covering the initial surfaces,
  delegation, and relationships to adjacent identifier systems. Completion
  requires demonstrating that one allocation suffices for conforming names and
  that independent scopes remain distinct across the covered lookup contexts.
- An implementation-independent naming-validation contract with conforming,
  conflicting, nonconforming, and insufficient-input examples. Completion
  requires equivalent naming determinations without reliance on OpenUSD's
  plugin system, with validation scope and performance expectations stated.
- Identifier-transition guidance covering existing names, ownership transfers,
  grace periods, and mixed composed content. Completion requires a documented
  transition across typed names, applied APIs, and properties without assuming
  automatic semantic conversion.

The B-Rep and ROS/Newton cases will exercise the deliverables from reservation
through authored and registered names, naming validation, and an ownership
transition. Each deliverable needs an authoring and maintenance owner, review
and approval route, and delivery date agreed by the responsible groups. The
worked cases do not require this proposal to settle domain behavior, extension
dependency resolution, support claims, or deployment governance.
