# Namespace and Prefix Isolation for USD Extensions

**Author:** Aaron Luk (NVIDIA)

**Status:** Draft

## Summary

This proposal defines requirements for ownership and naming isolation across USD
extensions. An owner reserves an extension name and uses prescribed naming
conventions for the schemas, properties, and other identifiers it introduces.
One reservation establishes the extension's naming scope. Individual identifiers
within that scope require no separate reservation or feature approval.

The goal is to let independently governed capabilities develop and deploy in
parallel while maintaining predictable USD behavior across tools and over time.
The extension model, including its validation requirements, must be independent
of OpenUSD's plugin system. Vendors can declare supported combinations through
their own profiles; independent deployment implies no compatibility claim for
arbitrary combinations.

This is a requirements proposal. Concrete naming syntax, reservation procedures,
and governance responsibilities remain to be selected. It develops the Namespace
and Prefix Isolation requirement in
[Sean Snyders' USD Extension Ecosystem Governance proposal](https://docs.google.com/document/d/1zL7Igy5QN6bTHZavczkjaW2U5TBk95hP_Ooa_zL-tJc/edit).

## Motivation

Stakeholders are already developing and deploying USD schemas. Without common
ownership and naming rules, independent definitions can acquire the same
identifiers. Depending on the surface and consumer, the result can be a
registration error, ambiguous interpretation, or silent use of the wrong
definition. Divergent conventions also increase the cost of moving content
between tools and reconciling independently developed capabilities.

USD exposes several naming surfaces: typed schema identifiers, applied API schema
identifiers, property names, metadata keys, capability and profile identifiers,
file format identifiers, and asset resolver identifiers. A library name or runtime
registration convention does not necessarily qualify the identifiers authored
into a scene. Isolation must cover the names exchanged in content as well as
those registered by an implementation.

Common rules support two related goals. Reliability requires predictable content
across tools and over time. Leadership requires faster deployment in parallel
across domains, with a path to shared standards where useful. Establishing
ownership and naming scope should enable that work without requiring central
approval of every feature.

Naming isolation is distinct from discovery. A catalog can help people find
existing work, but the naming contract must be usable before a complete
discovery or distribution service exists. Conversely, a unique prefix does not
establish that a consumer implements the extension or that its behavior is
compatible with another extension.

## Goals and Scope

The initial naming conventions cover typed schemas, applied API schemas, and
properties. They must also define how these names relate to metadata keys and
capability/profile identifiers so those surfaces do not develop incompatible
ownership conventions.

The proposal requires:

- Legible ownership and isolation of independent definitions, including opinions
  authored in separate layers.
- Lightweight entry for internal prototypes and independently deployed extensions.
- Explicit policies for incompatible revisions and ownership transfers.
- Validation rules that any implementation can use, with proportionate cost.
- A boundary between independently governed domain behavior and changes to shared
  USD contracts.

File format and asset resolver identifiers remain in the extension inventory for
subsequent work. Binary loading, distribution, sandboxing, certification, and a
complete extension catalog are outside this proposal. It also does not define
the full shared baseline, select a naming syntax, or prescribe the organization
of a multi-part specification.

## Terminology

- **Owner:** The vendor, community project, multi-organization collaboration, or
  standards body governing an extension's definitions.
- **Extension reservation:** A record of an extension name and its owner. Together
  with mandatory naming conventions, it establishes the scope for identifiers
  introduced by that extension.
- **Prefix:** The leading token or sequence of tokens identifying ownership or
  scope in a name.
- **Namespace:** The space of identifiers scoped by a prefix.
- **Baseline USD:** The shared capabilities and behavioral commitments on which
  extensions rely. This is a working term for this proposal, not an agreed
  inventory or a synonym for everything shipped in OpenUSD.
- **Additive extension:** Domain interpretation or computation built on existing
  USD composition and value resolution. Its authored opinions can change resolved
  values through ordinary USD mechanisms without changing those mechanisms.

Ownership, maturity, version, and implementation support are separate facts.
Ownership identifies who controls a definition. Maturity describes its review or
production status. Version identifies a semantic contract. Implementation support
is a claim requiring evidence. A maturity marker such as `Prelim` does not
reserve ownership, and an owner's name does not imply engine exclusivity.

## Functional Requirements

### R1. Ownership Legibility

The naming convention must make the governing ownership scope apparent from an
extension identifier without relying on a pipeline-specific convention.

### R2. Hierarchical Scoping

The convention must support both an owner hierarchy and a domain or feature
hierarchy. Delimiter, casing, and token order may vary by naming surface.

### R3. Owner Sub-Hierarchies

An owner must be able to define its own sub-hierarchy independently of the
extension's domain hierarchy. The rules must support both a flat owner name and
nested ownership scopes without assigning fixed meanings to the intermediate
levels. This applies equally to vendors, projects, collaborations, and standards
bodies.

### R4. Naming Conventions Across Surfaces

Each covered surface must have specific naming rules derived from the extension
reservation and its ownership scope. Typed schema names, applied API identifiers,
and property names must all follow their applicable rules. Syntax may differ by
surface, but each convention must satisfy R1-R3 and preserve isolation when
content is composed from independently authored layers.

One extension reservation must suffice for all conforming identifiers it
introduces. Individual identifiers require no additional reservation. Reusing an
existing definition retains that definition's governing identity; implementing it
does not create a separately owned definition.

### R5. Reservation and Collision Handling

The reservation procedure must establish the extension name, its owner, and any
delegated sub-scopes. The naming and validation rules must identify violations
and conflicting definitions and specify how they are reported and resolved.
A consumer must not silently substitute a conflicting definition.

Reservation establishes naming scope. It does not approve feature semantics or
make a support or endorsement claim.

### R6. Evolution and Ownership Transfer

Independently governed extensions may remain independent or seek broader
agreement. Work may enter directly under community or multi-organization
governance. Adoption or a change of maturity alone does not transfer ownership
or imply AOUSD ratification or baseline inclusion.

Identifiers do not inherently survive a transfer of ownership. A transfer must
define the relationship between predecessor and successor definitions, grace
periods, and migration paths. Incompatible revisions likewise require explicit
version and compatibility policies. Both kinds of transition must account for
typed names, applied API identifiers, properties, and mixed composed content.

### R7. Lightweight Entry

Beginning an internal prototype must be as lightweight as reserving an extension
name. Reservation must not require a complete specification, implementation,
commitment to publish, or AOUSD approval of feature semantics. Conforming
identifiers can then be defined without individual approvals.

Documentation and evidence increase with the publication, compatibility, support,
or standardization commitments being made. Additive domain behavior can develop
and deploy among supporting consumers without central feature approval. Changes
to existing shared contracts, or use of another owner's namespace, require the
relevant agreement.

### R8. Implementation Independence

The vendor extension paradigm, naming conventions, and validation contract must
be definable and usable independently of OpenUSD's plugin system. Specify the
required inputs, conformance conditions, and diagnostic meaning so other
implementations can provide equivalent validation. OpenUSD may implement the
contract through its existing facilities without making them prerequisites for
other implementations.

### R9. Validation and Performance

Naming conformance and collision detection are validation concerns. The contract
must distinguish checks on extension definitions from checks on authored layers
or composed content and identify the inputs needed for each.

Validation must support appropriate workflow boundaries and reuse of results
under stated validity conditions. Full naming validation must not be required on
every composition operation or value query. The requirements do not prescribe
a caching strategy or assume that validation has no cost.

Validation of naming or declarations does not prove semantic compatibility,
implementation support, or support for a combination of extensions.

## Design Considerations

### Naming Scope and Hierarchy

The extension reservation and naming conventions work together. Reserving only
the extension name is insufficient if the schema and property names it
introduces remain unconstrained. Once those rules are defined, reserving each
individual identifier would add unnecessary administration.

The following scopes illustrate the two hierarchy axes. They do not prescribe
syntax or allocate names:

| Owner hierarchy | Domain hierarchy | Illustrative combined scope |
|---|---|---|
| `AOUSD.GeomWG` | `brep` | `AOUSD.GeomWG.brep` |
| `yoyodyne.tierA` | `dimensional.contabulator` | `yoyodyne.tierA.dimensional.contabulator` |
| `yoyodyne` | `dimensional.contabulator` | `yoyodyne.dimensional.contabulator` |

An owner's intermediate levels may represent working groups, divisions, tiers,
or another structure of its choosing. `yoyodyne` is the placeholder vendor used
in the Profiles proposal. A shared domain token such as `brep` does not itself
establish ownership.

Owner-first naming is one candidate. Other token orders must still make
ownership clear and isolate independently governed definitions. A product name,
trademark, internal library prefix, or runtime registration mechanism does not
automatically reserve every scene-facing identifier.

### Shared Behavior and Independent Extensions

Baseline commitments should reference existing specifications and versions,
including the [AOUSD Core Specification](https://aousd.org/usd-core-specification/),
and identify additional shared contracts where needed. They should not form a
second Core Specification or depend on inclusion in an OpenUSD distribution.

An additive extension interprets or computes from normally resolved USD values.
Geospatial positioning and B-Rep illustrate how new domain behavior can require
integration with shared facilities such as
[UsdGeom transforms](https://openusd.org/release/api/class_usd_geom_xformable.html).
Using an existing contract, adding an integration requirement for supporting
consumers, and changing that contract are different commitments. A new
integration requirement alone does not require central governance. Redefining an
existing shared identifier or changing shared composition, value-resolution, or
behavioral rules requires the relevant broader agreement.

Published extensions must state their semantics, baseline/version dependencies,
and behavior when a consumer lacks support. Preserving data is distinct from
interpreting it. Published
[Core Specification 1.0.1](https://github.com/aousd/specifications-public/blob/main/core/1.0.1/core_spec.md#extension-metadata-fields)
leaves reading and authoring unknown extension metadata fields to implementations
and does not permit those fields to be required to consume a layer. Its
[schema scope](https://github.com/aousd/specifications-public/blob/main/core/1.0.1/core_spec.md#scope-5)
also leaves schema definition and ingestion mechanisms implementation-defined.
These provisions do not establish blanket preservation of arbitrary extension
data through every operation. Expectations must identify the surface, operation,
dependency, and relevant version.

### Profiles and Support Claims

Independent extensions can prescribe incompatible domain behavior even when
their names are isolated and each is additive. Two extensions might, for
example, direct the pose of the same robot link. Neither independent deployment
nor naming conformance claims that the combination is supported.

Vendors can define their own profiles declaring supported combinations. The
mapping from extension identifiers to capability and profile identifiers must
be explicit, as must the evidence behind a support claim.

The current
[UsdProfiles overview](https://github.com/PixarAnimationStudios/OpenUSD/blob/dev/docs/user_guides/schemas/UsdProfiles/overview.md)
distinguishes capability usage and compatibility claims from the registry that
loads capability definitions. [ClaimsAPI](https://github.com/PixarAnimationStudios/OpenUSD/blob/dev/docs/user_guides/schemas/UsdProfiles/ClaimsAPI.md)
supports degradation classes (`hard`, `soft`, and `enhancement`) and profile
compatibility claims with exceptions. It provides a candidate declaration
mechanism, not proof of conformance or a namespace reservation system.

The semantics of these declarations and queries must remain distinct from how
an implementation discovers definitions. Another implementation could obtain
equivalent definitions from a manifest, database, or service without adopting
OpenUSD's `plugInfo.json` registry mechanism.

### Validation

Naming checks belong within the broader validation paradigm represented by
OpenUSD's
[`usdValidation` framework](https://openusd.org/dev/api/md_pxr_2usd_validation_2usd_validation_2_r_e_a_d_m_e.html).
The framework supports core, schema, and client rules, with validators registered
through plugins or directly through registry APIs.
[`UsdValidationContext`](https://openusd.org/dev/api/class_usd_validation_context.html)
can run selected validators over layers, stages, or prims.

These facilities provide an implementation reference. The extension contract
must specify validation inputs, conformance conditions, and diagnostics
independently of those APIs. A scene alone may not contain enough information
to establish ownership or identify the applicable definition; a validator may
also need reservation records and extension definitions. Missing inputs must
not be mistaken for successful validation of the corresponding requirements.

Checks can run when definitions are published or installed, and at asset or
workflow boundaries appropriate to the check. Definition checks and composed
content checks have different scopes and costs. The contract should permit
reuse of valid results without imposing a particular scheduler or runtime hook.

### Versioning and Migration

Ownership migration extends the existing schema-evolution problem. OpenUSD's
[schema-versioning design](https://openusd.org/dev/wp_schema_versioning.html)
distinguishes identifiers, families, and major versions. `Cylinder` and
[`Cylinder_1`](https://openusd.org/dev/api/class_usd_geom_cylinder__1.html)
provide separate definitions; the latter exposes top and bottom radii. Different
prims in a composed scene can use different versions. Opinions on the same prim
resolve to a single typed-schema identifier without automatically translating
an old property representation into a new one.

An ownership transfer can change the prefix, schema family, and property names.
Current schema-family/version machinery does not by itself express that entire
relationship. The transition policy must identify predecessor and successor
contracts, grace periods, migration paths, and expectations for mixed content.
Automatic aliasing or conversion is not assumed.

## Precedents and Alternatives

### glTF and OpenGL Extensions

The [glTF extension process](https://github.com/KhronosGroup/glTF/blob/main/extensions/README.md)
provides a useful precedent for lightweight allocation. A vendor requests a
prefix through a GitHub issue containing the prefix, vendor name, and URL or
contact. Membership is not required, and a completed extension specification is
not an input to prefix reservation. The
[prefix table](https://github.com/KhronosGroup/glTF/blob/main/extensions/Prefixes.md)
records companies and projects. The
[Bevy request](https://github.com/KhronosGroup/glTF/issues/2497), for example,
is a short request with a contact URL. Naming rules and the process for publishing
an extension specification are specified separately.

The current
[OpenGL registry instructions](https://github.com/KhronosGroup/OpenGL-Registry#defining-new-extensions)
separate reserving enumerant blocks through a small XML-file pull request from
completing and registering an extension specification. Allocation becomes
official when the reservation is merged. The repository cautions that its older
process documents are largely outdated.

The applicable principle is separating administrative allocation from approval
of feature semantics. USD need not adopt OpenGL's numeric allocation scheme,
and a glTF owner-prefix reservation is not identical to a USD extension-name
reservation. USD also needs explicit conventions covering each schema and
property naming surface, including separately authored layers.

Neither precedent requires a universal vendor-to-multi-vendor-to-standard
sequence. The glTF registry distinguishes prefix categories from specification
maturity and includes ratified extensions retaining `EXT` names. Wider adoption,
ownership transfer, and standardization must be treated as distinct events.

### USD Profiles

[USD Profiles and Capabilities](https://github.com/PixarAnimationStudios/OpenUSD-proposals/tree/main/proposals/profiles)
provides an existing naming and declaration precedent. Its proposal history
includes an illustrative vendor-to-working-group-to-core progression; that
example does not establish a mandatory promotion or renaming sequence here.
Current implementation documentation is the reference for the shipped APIs.

### Other Naming Approaches

[IETF RFC 6838](https://www.rfc-editor.org/rfc/rfc6838) uses registration trees for
media types, including vendor and personal trees. It offers a precedent for
explicit allocation and ownership records, but USD need not reproduce that
registration process.

[W3C custom elements](https://html.spec.whatwg.org/multipage/custom-elements.html#valid-custom-element-name)
use a naming rule that separates custom names from built-in element names. That
structural separation alone does not isolate independently chosen custom names.
Similarly, a maturity prefix such as `Prelim` cannot distinguish two unrelated
preliminary USD extensions.

Package qualification is another way to scope identifiers. To meet this
proposal's requirements, it would need to preserve legible ownership and naming
isolation in exchanged content and separately authored layers. Neither a
package-local short name nor a discovery catalog alone provides that contract.

## Case Studies

### B-Rep Preliminary Schemas

The [B-Rep prefix change](https://github.com/aousd/OpenUSD-proposals/pull/2)
illustrates why each naming surface needs a rule. In the
[reviewed revision](https://github.com/umhoefer/OpenUSD-proposals/commit/3f3350ae7bf45cc9c06c2d566223d3579c0aacc1),
the typed schema is `PrelimBrepArray` and the library prefix is `PrelimUsdSolid`.
Applied API names such as `BrepPointAPI` and `BrepCurve3dNurbAPI` and the `brep:`
property prefix do not carry the same marker. The work was developed through
the Geometry Working Group and involved multiple organizations; a single-vendor
owner would not describe its stewardship accurately. `Prelim` identifies
maturity, not ownership.

The following illustrative excerpt is not a complete B-Rep asset:

```usda
def PrelimBrepArray "Cube" (
    prepend apiSchemas = ["BrepPointAPI:vertexPoint", "BrepCurve3dNurbAPI:edge3dNurb"]
)
{
    uniform double[] brep:intersectTol3d = [0.00002]
    uniform uint[] brep:regionCount = [2]
}
```

The type name, API identifiers, property names, and API instance names are
different surfaces. `libraryPrefix` qualifies an internal type name but does
not automatically qualify every scene-facing identifier. A property opinion can
also be authored in an override layer without a local type declaration or
`apiSchemas` opinion. Its interpretation then depends on the composed prim and
applicable schema definition.

Applicability does not reserve a name. `apiSchemaCanOnlyApplyTo` guides
[`CanApplyAPI`](https://github.com/PixarAnimationStudios/OpenUSD/blob/v26.08/pxr/usd/usd/prim.cpp#L645);
[`ApplyAPI`](https://github.com/PixarAnimationStudios/OpenUSD/blob/v26.08/pxr/usd/usd/prim.cpp#L825)
does not itself enforce that target list. Another definition of `BrepPointAPI`
can still collide regardless of intended target types.

An earlier revision used the internal type name
`PrelimUsdSolidPrelimBrepArray` in four applicability entries. The repeated
`Prelim` follows from combining the library prefix and class name; it was not
itself the error. Those entries require the schema identifier `PrelimBrepArray`.
[The October 5 correction](https://github.com/aousd/OpenUSD-proposals/pull/2#issuecomment-5998372106)
is present in the reviewed revision. This resolves the source lookup issue;
generated-plugin end-to-end validation is a separate task.

One extension reservation must cover the typed name, applied API names, and
properties through their respective naming rules. Changing maturity alone need
not transfer ownership. If ownership changes, migration must account for
`typeName`, `apiSchemas`, and property opinions; renaming only the typed schema
does not migrate the other surfaces. The
[schema-generation guide](https://openusd.org/release/api/_usd__page__generating_schemas.html)
describes the distinction between authored opinions and built-in schema
properties, which can exist without individual authored specs.

### ROS and Newton

[REP 158](https://reps.openrobotics.org/rep-0158-2006/) develops USD conventions
for robotics. The [ROS schemas](https://github.com/ros-simulation/openusd-schemas/blob/main/core/ros/schema.usda)
use names such as `RosContextAPI`, `ros:` properties, and the separate internal
library prefix `UsdRos`. Each surface needs an explicit ownership convention.
A runtime ROS namespace such as `/robot_1/camera` serves a different purpose
from a USD prim path or extension-ownership prefix.

During review, [REP pull request #30](https://github.com/openrobotics/reps/pull/30)
removed an intermediate `ExtendedPhysics` stage in favor of separately layered,
prefixed engine extensions, mappings where semantics align, and reporting when
features are ignored or approximated. This is a deployment precedent, not a
mandatory promotion ladder.

A project such as [Newton](https://github.com/newton-physics) may govern an
extension implemented by several engines without transferring it to AOUSD.
A project prefix establishes neither engine exclusivity nor equivalent behavior.
Ordinary composition, naming isolation, and simulation portability are separate
guarantees. Supported combinations belong in explicit vendor-profile claims.

ROS integration can interpret normally resolved USD values and add domain
behavior without changing composition or value resolution. The extension must
still distinguish required capabilities from features that may be ignored or
approximated and state how consumers expose missing support.

## Open Questions

1. What is the minimum reservation record, and which concrete naming conventions
   satisfy the requirements across schemas, properties, metadata, and capability
   identifiers? Which existing identifiers require a transition policy?
2. Which inputs and diagnostic definitions are needed for equivalent validation
   across implementations? How should validation scope and the validity of reused
   results be specified?
3. Which existing shared contracts must extensions declare as dependencies, and
   which domain-integration cases require a change to those contracts?
4. How should predecessor and successor definitions be related across ownership
   transfers, including grace periods and mixed composed content? Which parts
   extend beyond existing schema-family/version mechanisms?
5. Who maintains the reservation records and naming conventions, resolves
   ownership disputes, and approves changes to the shared rules?

## Implementation Plan

The first deliverable is a naming convention for typed schemas, applied API
schemas, and properties, with a minimal reservation procedure and explicit
relationships to metadata and capability/profile identifiers. It must support
lightweight prototyping without depending on a complete catalog or distribution
service.

A second deliverable is an implementation-independent validation contract with
conforming and nonconforming examples. OpenUSD's validation framework can provide
one implementation. Equivalent outcomes must be demonstrable without requiring
its plugin system or registration APIs.

A worked case will exercise reservation, authored and registered names,
dependencies, unsupported-consumer behavior, vendor-profile claims, incompatible
revisions, and an ownership transition. The B-Rep and ROS/Newton cases provide
starting points. The convention, validation contract, and worked case each need
a maintenance owner and a completion test. Delivery dates and approving forums
must be agreed by the responsible groups.
