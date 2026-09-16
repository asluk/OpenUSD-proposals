# Geospatial Coordinate Reference Systems for OpenUSD
## Contributors
- **Esri** (Tamrat Belayneh, Simon Haegler)
- **Nvidia** (Aaron Luk)
- Also based on work by David de Koning, Sebastien Vielliard, Simon Haegler, Tamrat Belayneh in the AOUSD AECO Interest Group.

## Contents

- [Introduction](#introduction)
- [Motivation](#motivation)
  - [The geospatial gap in OpenUSD](#the-geospatial-gap-in-openusd)
  - [The expanding scope of USD](#the-expanding-scope-of-usd)
- [Problem statement](#problem-statement)
  - [Placing 3D content on the Earth](#placing-3d-content-on-the-earth)
  - [Why this matters now](#why-this-matters-now)
- [Background: Coordinate Reference Systems](#background-coordinate-reference-systems)
  - [Geographic vs. Projected CRS](#geographic-vs-projected-crs)
  - [CRS encodings: OGC WKT, EPSG, and WKID](#crs-encodings-ogc-wkt-epsg-and-wkid)
  - [3D CRS types](#3d-crs-types)
- [Terms](#terms)
- [Design overview](#design-overview)
  - [Principles](#principles)
  - [Functional requirements](#functional-requirements)
  - [Schema design](#schema-design)
  - [CRS library pattern](#crs-library-pattern)
  - [CRS binding and inheritance](#crs-binding-and-inheritance)
  - [Precision handling](#precision-handling)
  - [Target CRS and runtime reprojection](#target-crs-and-runtime-reprojection)
- [Detailed design](#detailed-design)
  - [GeospatialCRS typed schema](#geospatialcrs-typed-schema)
  - [GeospatialCRSBindingAPI applied schema](#geospatialcrsbindingapi-applied-schema)
  - [Complete scene example](#complete-scene-example)
  - [CRS library example](#crs-library-example)
  - [Programmatic authoring (C++)](#programmatic-authoring-c)
  - [Programmatic authoring (Python)](#programmatic-authoring-python)
- [Interaction with existing USD features](#interaction-with-existing-usd-features)
  - [Stage metadata: metersPerUnit and upAxis](#stage-metadata-metersperunit-and-upaxis)
  - [Transform stack and resetXformStack](#transform-stack-and-resetxformstack)
  - [Composition arcs](#composition-arcs)
  - [Relationship to UsdGeom](#relationship-to-usdgeom)
- [Industry use cases](#industry-use-cases)
  - [Architecture, Engineering, Construction, and Operations (AECO)](#aeco)
  - [GIS and digital twins](#gis-and-digital-twins)
  - [Infrastructure and utilities](#infrastructure-and-utilities)
  - [Defense and simulation](#defense-and-simulation)
- [Interoperability](#interoperability)
  - [glTF geospatial extension](#gltf-geospatial-extension)
  - [IFC and BIM workflows](#ifc-and-bim-workflows)
  - [CityGML and OGC 3D Tiles](#citygml-and-ogc-3d-tiles)
- [Design considerations](#design-considerations)
  - [Why WKT and not bare EPSG codes](#why-wkt-and-not-bare-epsg-codes)
  - [Why a typed prim and not stage metadata](#why-a-typed-prim-and-not-stage-metadata)
  - [Alternate approaches considered](#alternate-approaches-considered)
  - [Open questions](#open-questions)
  - [Risks](#risks)
- [Relationship to other proposals](#relationship-to-other-proposals)
- [Prototype implementations](#prototype-implementations)
- [Next steps](#next-steps)
- [References](#references)
- [Appendix A: WKT examples](#appendix-a-wkt-examples)
- [Appendix B: AI-assisted drafting](#appendix-b-ai-assisted-drafting)

## Introduction

This proposal introduces first-class support for
**Geospatial Coordinate Reference Systems (CRS)** in OpenUSD.
It defines two new schemas that allow USD scenes to declare
*where on a celestial body* their 3D content is located,
enabling interoperability with GIS, AECO, digital twin,
and simulation workflows that require real-world positioning.

The core idea is simple:
a CRS definition is stored as an OGC WKT string on a typed prim,
and an applied API schema binds that CRS to any `UsdGeomXformable` prim
in the scene hierarchy.
Child prims inherit their parent's CRS binding,
and a runtime reprojection pipeline transforms geometry
between different CRS zones within a single composed stage.

This proposal is the result of collaborative work
within the AOUSD AECO Interest Group,
with contributions from Esri, Pixar, NVIDIA, Bentley, and Trimble.

## Motivation

### The geospatial gap in OpenUSD

OpenUSD provides a powerful scene description framework
with rich support for geometry, materials, lighting, and physics.
However, it currently has no mechanism to express
*where a scene is located in or on a celestial body*.

A building model authored in USD can describe its shape,
appearance, and internal structure in exquisite detail —
but there is no standard way to say
"this building sits at 34.0561°N, 117.1956°W"
or "these coordinates are in UTM zone 11N."

This is not a niche requirement.
Every AECO project, every digital twin,
every GIS visualization, and every urban simulation
needs to place 3D content at real-world coordinates.
Without a standard mechanism, each tool and pipeline
invents its own custom metadata,
leading to data loss at interchange boundaries
and preventing true interoperability.

### The expanding scope of USD

USD was originally designed for film production workflows,
where scenes exist in an abstract coordinate space
and absolute position on the Earth is irrelevant.

As USD adoption expands into AECO, GIS, defense, simulation,
and digital twin applications through the AOUSD alliance,
the need for geospatial positioning has become critical.
These industries routinely work with coordinate reference systems,
and their tools (ArcGIS, QGIS, FME, Bentley, Trimble, etc.)
all expect CRS metadata on imported geometry.

The glTF format has already recognized this need
with its own geospatial extension proposal.
IFC 5 is evaluating USD as a potential foundation.
OpenUSD must provide a standard answer
to the question "where is this scene?"

## Problem statement

### Placing 3D content on a celestial body

To place a 3D model at a real-world location, three things are needed:

1. **A Coordinate Reference System (CRS)** that defines
   the mathematical relationship between coordinates and positions
   on the Earth's surface (e.g., "UTM zone 11N" or "WGS 84 geographic").

2. **Coordinates** in that CRS
   (e.g., Easting = 481,948.63 m, Northing = 3,768,393.52 m).

3. **A binding mechanism** that associates the CRS
   with the geometry in the scene graph.

USD currently provides none of these as first-class features.
Users must fall back to custom metadata, primvars,
or out-of-band sidecar files to convey this information —
all of which are opaque to USD's composition engine,
rendering pipeline, and standard tooling.

### Why this matters now

1. **Data loss at interchange boundaries.**
   CRS metadata stored in `customData` or proprietary attributes
   is routinely stripped during USD export/import cycles
   across different tools.

2. **No standard for CRS inheritance.**
   Without a defined inheritance model,
   every prim in a large scene must redundantly carry CRS metadata,
   or tools must implement ad-hoc resolution logic.

3. **Precision hazards.**
   A UTM easting of 481,948 m exceeds the useful range of `float32`,
   and implementations store it in a `point3f` array anyway,
   because nothing tells them not to.
   The result is visible jitter and drift
   in scenes that look correct on paper.

4. **Multi-CRS composition is undefined.**
   A cross-state pipeline spans UTM zones 11 and 12,
   and a regional twin draws on imagery, terrain and vectors
   that each arrive in their own CRS.
   Today the only way to put them on one stage
   is to convert them all first,
   which is a cost the largest projects cannot pay.

5. **Industry adoption is blocked.**
   GIS vendors, AECO tool makers, and digital twin platforms
   cannot fully adopt USD without a standard way to express CRS,
   because it is a foundational requirement for their workflows.

## Background: Coordinate Reference Systems

This section provides context for readers unfamiliar with geospatial concepts.

### Geographic vs. Projected CRS

A **Geographic CRS** uses angular coordinates
(latitude and longitude in degrees)
on a mathematical model of the Earth's shape (an ellipsoid).
Example: WGS 84 (EPSG:4326) — the CRS used by GPS.

A **Projected CRS** mathematically projects
the curved Earth surface onto a flat 2D plane.
Coordinates are linear (metres or feet).
Example: UTM zone 11N (EPSG:32611) — used for Southern California.

Every projected CRS contains a base geographic CRS,
a projection method (e.g., Transverse Mercator, Lambert Conformal Conic),
and projection parameters (central meridian, scale factor, false easting, etc.).

### CRS encodings: OGC WKT, EPSG, and WKID

There are several ways to identify a CRS:

| Encoding | Description | Example |
|----------|-------------|---------|
| **EPSG code** | Integer ID from the IOGP geodesy registry | `32611` |
| **WKID** | Well-Known ID — same concept, used by Esri (includes Esri-specific codes beyond EPSG) | `32611` |
| **OGC WKT** | Self-contained text string defining the full CRS (ISO 19162:2019) | `PROJCRS["WGS 84 / UTM zone 11N", ...]` |
| **PROJ string** | Compact string for the PROJ library | `+proj=utm +zone=11 +datum=WGS84` |

This proposal uses **OGC WKT 2** (ISO 19162:2019)
as the canonical CRS encoding,
with EPSG authority identifiers embedded within the WKT via `ID["EPSG", code]`.

### 3D CRS types

All CRS definitions in this proposal must be 3D.
The supported types are:

| Type | WKT Keyword | Axes | Example |
|------|-------------|------|---------|
| 3D Projected | `COMPOUNDCRS` (PROJCRS + VERTCRS) | Easting, Northing, Up | NAD83 / UTM 11N + NAVD88 height |
| 3D Geographic | `GEOGCRS` with 3 axes | Lat, Lon, Height | WGS 84 (EPSG:4979) |
| 3D Geocentric (ECEF) | `GEODCRS` | X, Y, Z | ITRF2020 |
| 3D Engineering | `DERIVEDPROJCRS` | Site X, Y, Z | Construction project grid |

For dynamic datums (time-dependent reference frames),
WKT 2 supports the `COORDINATEMETADATA` wrapper
with `FRAMEEPOCH` and `EPOCH` clauses
for high-precision applications.

## Terms

The background above covers the geodesy.
This section fixes the words this proposal uses for its own constructs,
and separates several that mean different things
to the industries this proposal serves.
Everything after this point uses these terms as defined here.

### Terms this proposal defines

**CRS binding.**
A statement that the coordinates of a prim,
and of its subtree down to the next binding,
are expressed in a named CRS.
It says nothing about where the prim sits in any other CRS,
and nothing about where the coordinates came from.

**Target CRS.**
The CRS a stage resolves into,
taken from the CRS bound to the composed `defaultPrim`.
A consumer asks for world transforms in this CRS,
and prims bound to a different one are converted into it on read.
It is a property of the stage, not of any asset in it.

**Anchor.**
A prim whose transform states a position in its bound CRS
rather than an offset from its parent.
An anchor is where geodetic coordinates enter a scene;
everything beneath it is ordinary USD placement in metres.

**Placement.**
Where an instance sits and how it is oriented within a CRS,
authored as transform operations on or below an anchor.
Placement is survey data: it differs for every instance,
and it is the record of a real-world decision about a real-world object.

**Conformance.**
A correction for the authoring conventions of a source asset —
its up axis, its units, the orientation it was modelled in.
Conformance is not survey data.
It is identical for every instance of that asset,
and separating it from placement is what keeps the asset reusable.

### Terms that collide

**Base.**
Three different things are called *base* by the industries this proposal serves,
and this proposal uses none of them unqualified.

- A **project's base CRS**, in GIS practice,
  is the CRS a project works in and brings its data into.
  This proposal calls that the **Target CRS**.
- **`BASEGEOGCRS`**, in WKT 2,
  is the geographic CRS a projected or derived CRS is built *from*.
  It sits underneath a CRS definition, not above a project.
- A **project base point**, in surveying practice,
  is a point on the ground, not a CRS.

**Local.**
Two established and incompatible uses.

- In AECO, a **local CRS** is a project or construction grid:
  a flat Cartesian grid agreed for a site,
  with its own origin and its axes along the construction drawings.
  It does not degrade with distance because it does not model curvature;
  it is simply the CRS of that site.
  This proposal says **engineering CRS** or **project grid**.
- In GIS, **local** usually means a local tangent plane —
  a topocentric CRS such as ENU, exact at its origin
  and degrading as you move away from it.
  This proposal says **topocentric CRS**.

A statement that local works well and a statement that local does not scale
are both true, about different things.

**Localization.**
In ISO/TS 15143-4 and in construction machine control,
the operation of relating a site's working coordinates to a geodetic CRS.
It is expressed in WKT 2 as a derived CRS,
so this proposal introduces no construct for it.

### Terms this proposal avoids

**Frame** is reserved.
In OpenUSD it reads as a time sample.
Where a reference system is meant, this proposal says **CRS**;
where the geodetic sense is meant, it says **reference frame** in full,
as in *International Terrestrial Reference Frame*.

**Extent** is reserved.
It is the `UsdGeomBoundable` attribute holding a prim's local bounding box.
Where geographic size is meant, this proposal says so directly.

## Design overview

### Principles

1. **Industry agnosticism.**
   The CRS mechanism must serve GIS, AECO, M&E, simulation,
   and defense equally — no single industry's conventions are privileged.

2. **Self-contained CRS definitions.**
   A USD file must carry all information needed to interpret its coordinates
   without relying on external registry lookups at runtime.

3. **Composition-friendly.**
   CRS definitions and bindings must compose correctly
   through all USD composition arcs (references, sublayers, inherits, etc.).

4. **Inheritance.**
   A CRS applies to a subtree.
   Any prim that needs a different one says so
   and its own subtree follows it.

5. **Precision-aware.**
   Geospatial magnitude is never carried
   in storage that cannot hold it.
   Where a format constrains precision,
   the design keeps the large values out of it
   rather than asking authors to accept the loss.

6. **Minimal disruption.**
   No changes to existing USD schemas or core APIs.
   The geospatial schemas are additive and optional.

7. **Extensible.**
   Third-party CRS libraries (PROJ, GDAL, Esri, Trimble)
   are abstracted behind an internal API.
   OpenUSD itself does not validate or interpret WKT strings.

8. **Interoperable.**
   The design should facilitate round-trip exchange
   with glTF (geospatial extension), IFC, CityGML, and OGC 3D Tiles.

### Functional requirements

What a solution has to do, stated without reference to any mechanism.
These are what an implementation is checked against,
and the terms on which a design change is argued:
it either serves one of these or it does not.

Each requirement is one sentence.
The italic text that follows it is rationale or a case from practice,
and carries no requirement of its own.

1. **Coordinate interpretation.**
   Every coordinate in a scene can be traced
   to a declaration of the CRS it is expressed in.

   *An easting of 481,948 and a northing of 3,767,521
   are a valid pair in every one of the sixty UTM zones,
   and name a different place on the Earth in each.
   Coordinates without a CRS are not approximately located.
   They are not located at all.*

2. **Recorded locations.**
   A location can be recorded in a named CRS,
   and other content positioned relative to it.

   *Content in a scene is modelled in local distances —
   a door three metres from a building's origin,
   a camera turning about the point it stands on.
   A recorded location is where those distances meet the Earth:
   one position, stated in a CRS,
   that the rest of the assembly is measured from.
   Because distances are added to it,
   it has to be stated in a system whose units are distances.*

3. **Source coordinates left as authored.**
   Data authored in one CRS can be used by a project working in another
   without its stored coordinates being rewritten.

   *The conversion still happens, as something a runtime does
   when it resolves a scene into the project's CRS.
   What this rules out is the other approach:
   reprojecting every dataset into the project's CRS on the way in
   and storing the result.
   A regional project draws on imagery, terrain and vector data
   published in WGS 84, and at that size
   the reprojected copies cost more to hold than the originals
   and no longer interoperate with the tools that produced them.*

4. **Several CRSs in one scene.**
   Data expressed in different CRSs can occupy one scene
   and still align correctly.

   *A pipeline crosses UTM zones 11 and 12.
   Neither zone is wrong for the half of the route it covers,
   so neither half should have to move into the other's zone
   to be seen alongside it.*

5. **A CRS suited to the project's size.**
   A project can be expressed in a CRS appropriate to its size,
   and the scheme never obliges it to use one
   whose error grows with distance from a chosen origin.

   *A topocentric CRS is a plane laid against a curved Earth.
   Its departure from the surface grows with the square of distance —
   about 8 cm at 1 km from the origin, about 785 m at 100 km.
   That is a geometric property of the projection, not a rounding error,
   and no amount of precision reduces it.
   On a building site it is invisible; across a country it is disqualifying.
   A construction project grid has no such term at all:
   it reads (1000, 1000) at its origin,
   runs its axes along the construction drawings,
   and is exact across the whole site because it models no curvature.
   Both have to be expressible, and neither is the general case.*

6. **Magnitude and detail together.**
   A scene carries coordinates of geospatial magnitude
   and detail at millimetre scale at the same time,
   with neither degrading the other.

   *A UTM easting needs about seven significant digits before the decimal point.
   Single-precision floating point has roughly seven digits in total,
   so storing that easting directly leaves nothing for the millimetres,
   and the geometry visibly jitters.
   The two cannot share one storage format,
   and the scheme has to say how they are kept apart.*

7. **Unambiguous coordinates.**
   A recorded coordinate is unambiguous
   in its units and in its axis order.

   *Both failures are silent.
   A latitude of 48.8584 read as 48 metres is a plausible number,
   and so is an easting and northing read in the wrong order —
   EPSG:3006 declares northing first, as do several other national grids.
   Nothing about the resulting scene looks wrong enough to investigate.*

8. **Placement separate from conformance.**
   Where an instance sits is recorded separately
   from the corrections its source asset needs
   to be usable at all.

   *Place the same tower fifty times across a site
   and there are fifty survey records, all different,
   and one rotation correcting the asset's up axis, the same every time.
   Recording them together means the up-axis correction
   is copied into fifty survey records,
   where it looks like something a surveyor measured.*

9. **One definition per CRS.**
   A CRS used in many places is defined once and referred to,
   not restated at each use.

   *A project has one CRS and thousands of prims in it.
   Repeating the definition makes the ones that drift
   indistinguishable from the ones that were meant to differ.*

10. **Positions that move.**
    A position that changes over time is correct
    at any moment it is asked for,
    not only at the moments it was recorded.

    *A satellite reports latitude, longitude and altitude at intervals.
    Converting each report into a Cartesian CRS first
    and interpolating between the results
    draws a straight line through the planet rather than a path over it.
    One degree of arc either side of the equator
    puts the midpoint 971 m below the surface.
    The order of the two operations is the whole difference.*

### Schema design

Two new schemas are introduced:

| Schema | Type | Purpose |
|--------|------|---------|
| `GeospatialCRS` | Typed (IsA) | Defines a CRS as a first-class USD prim |
| `GeospatialCRSBindingAPI` | Applied (HasA) | Binds a CRS prim to a `UsdGeomXformable` |

This two-schema approach separates the CRS *definition*
from the CRS *usage*,
allowing a single CRS definition to be shared
across many prims and scenes via USD references.

### CRS library pattern

CRS definitions are intended to live in shared **library layers**
(e.g., `crs_library.usda`) that can be referenced by any scene:

```
crs_library.usda
├── /CRS/WGS84_UTM11N       (GeospatialCRS)
├── /CRS/NAD83_UTM11N        (GeospatialCRS)
├── /CRS/NAD83_CA_Zone5      (GeospatialCRS)
└── /CRS/WGS84_Geographic3D  (GeospatialCRS)
```

This pattern is analogous to shared material libraries in M&E workflows.
Authoring tools can ship standard CRS libraries,
and users can create custom ones for local/site-specific CRS definitions.

### CRS binding and inheritance

The `GeospatialCRSBindingAPI` is applied to a `UsdGeomXformable` prim
and references a `GeospatialCRS` prim (from the same stage or an external layer).

CRS bindings inherit down the prim hierarchy.
A prim without a direct CRS binding
resolves its CRS by walking up to the nearest ancestor
that has one — analogous to `UsdShadeMaterialBindingAPI` resolution.

A child prim may override its parent's CRS
by applying its own `GeospatialCRSBindingAPI` with a different CRS reference.
This is how multi-CRS scenes are composed
(e.g., one subtree in UTM zone 11N, another in UTM zone 18N).

This is also how a project holds data it has not converted.
An asset referenced into a scene keeps its own coordinates
and binds the CRS it was authored in;
the CRS the project works in is the stage's Target CRS;
where the asset sits within that project is its transform stack.
Those are three separate statements
and the schema keeps them separate:
a CRS binding is always about the coordinates of the prim it is on,
never about a CRS the prim is being brought into.
Nothing is reprojected on ingest,
and no dataset has to be converted
to sit alongside one that arrived in a different CRS.

**A CRS binding may name any CRS.**
What is constrained is anchoring, not binding.
An anchor's `xformOp:translate` is a length in the bound CRS's axes,
so a prim can only be anchored in a CRS
whose coordinate system is `CS[Cartesian, 3]` with length axes —
a projected, geocentric or engineering CRS.
A geographic CRS describes the coordinates of the data bound to it
and is reprojected into the Target CRS on read;
it is not a CRS a position is authored into,
because a translate holding 48.8584 would be read as 48 metres.
Deriving a topocentric CRS from a geographic one
is the way to anchor near a geographic location,
and is routine in any GIS package.

### Precision handling

USD mesh geometry uses `point3f[]` (float32),
which provides ~7 decimal digits of precision.
A UTM easting of 481,948.63 requires 8+ significant digits,
so storing geospatial coordinates directly in `point3f` causes visible artifacts.

The solution is a two-tier approach:

| Tier | Data | Type | Precision |
|------|------|------|-----------|
| **Anchor** | Geospatial position | `double3 xformOp:translate` | float64 (~15 digits) |
| **Detail** | Mesh vertices | `point3f[] points` | float32 (~7 digits) |

The large CRS coordinates are carried in the double-precision
`xformOp:translate` on the CRS-bound `Xform` prim.
Mesh vertex positions are small offsets (typically < 1 km)
relative to that anchor, staying well within float32 range.

### Target CRS and runtime reprojection

The **Target CRS** for a stage is defined by the CRS
bound to the composed `defaultPrim` of the root layer stack.

At render/query time, all prims whose bound CRS
differs from the Target CRS are **reprojected** —
their transforms are mathematically converted
from the source CRS to the Target CRS.

This reprojection is implemented as a
**Hydra 2.0 Scene Index Filter** (for rendering)
and as API methods (for computation),
using an abstracted interface to third-party CRS libraries
(PROJ, GDAL, Esri projection engine, etc.).

## Detailed design

### GeospatialCRS typed schema

A concrete typed schema that defines a CRS as a first-class USD prim.

**Prim type name:** `CoordinateReferenceSystem`

**Attributes:**

| Attribute | API Name | Type | Variability | Description |
|-----------|----------|------|-------------|-------------|
| `crs:wkt` | `wellKnownText` | `uniform token` | Uniform | OGC WKT 2 string (ISO 19162:2019) defining the CRS |

The `crs:wkt` attribute is `uniform` because a CRS definition
does not vary over time or across a mesh.
It is a `token` (not `string`) to enable efficient caching and comparison.

**USDA syntax:**

```usda
def CoordinateReferenceSystem "WGS84_UTM11N" (
    doc = "WGS 84 / UTM zone 11N (EPSG:32611)"
)
{
    uniform token crs:wkt = """PROJCRS["WGS 84 / UTM zone 11N",
        BASEGEOGCRS["WGS 84",
            DATUM["World Geodetic System 1984",
                ELLIPSOID["WGS 84",6378137,298.257223563,
                    LENGTHUNIT["metre",1.0]]],
            PRIMEMERIDIAN["Greenwich",0,
                ANGLEUNIT["degree",0.0174532925199433]],
            ID["EPSG",4326]],
        CONVERSION["UTM zone 11N",
            METHOD["Transverse Mercator",
                ID["EPSG",9807]],
            PARAMETER["Latitude of natural origin",0,
                ANGLEUNIT["degree",0.0174532925199433],
                ID["EPSG",8801]],
            PARAMETER["Longitude of natural origin",-117,
                ANGLEUNIT["degree",0.0174532925199433],
                ID["EPSG",8802]],
            PARAMETER["Scale factor at natural origin",0.9996,
                SCALEUNIT["unity",1.0],
                ID["EPSG",8805]],
            PARAMETER["False easting",500000,
                LENGTHUNIT["metre",1.0],
                ID["EPSG",8806]],
            PARAMETER["False northing",0,
                LENGTHUNIT["metre",1.0],
                ID["EPSG",8807]]],
        CS[Cartesian,2],
            AXIS["(E)",east,ORDER[1],
                LENGTHUNIT["metre",1.0]],
            AXIS["(N)",north,ORDER[2],
                LENGTHUNIT["metre",1.0]],
        ID["EPSG",32611]]"""
}
```

**C++ API:**

```cpp
class UsdGeospatialCoordinateReferenceSystem : public UsdTyped {
public:
    static UsdGeospatialCoordinateReferenceSystem
    Define(const UsdStagePtr &stage, const SdfPath &path);

    static UsdGeospatialCoordinateReferenceSystem
    Get(const UsdStagePtr &stage, const SdfPath &path);

    UsdAttribute GetWellKnownTextAttr() const;
    UsdAttribute CreateWellKnownTextAttr(
        VtValue const &defaultValue = VtValue(),
        bool writeSparsely = false) const;

    /// Walk up the prim hierarchy from `prim` and return the WKT token
    /// of the first ancestor (or self) with a valid crs:wkt attribute.
    static TfToken ComputeCoordinateReferenceSystem(UsdPrim const &prim);
};
```

### GeospatialCRSBindingAPI applied schema

A single-apply API schema that binds a CRS to a `UsdGeomXformable` prim.

**Schema type name:** `BindingAPI`
**Can only apply to:** `Xformable`

**Behavior:**

When `Bind()` is called, the schema:
1. Adds a USD **reference** to the specified `GeospatialCRS` prim
   (internal or external).
2. Calls `SetResetXformStack()` on the prim,
   ensuring `!resetXformStack!` appears in the `xformOpOrder`,
   so the prim's `xformOp:translate` is interpreted
   as an absolute position in the bound CRS.

**C++ API:**

```cpp
class UsdGeospatialBindingAPI : public UsdAPISchemaBase {
public:
    static UsdGeospatialBindingAPI Apply(const UsdPrim &prim);
    static bool CanApply(const UsdPrim &prim,
                         std::string *whyNot = nullptr);

    /// Bind via internal reference to a CRS prim on the same stage.
    bool Bind(UsdGeospatialCoordinateReferenceSystem const &crs) const;

    /// Bind via external reference to a CRS prim in another layer.
    bool Bind(std::string const &layerPath,
              SdfPath const &crsPrimPath) const;
};
```

### Complete scene example

The following example places a simplified building
at the Esri headquarters in Redlands, California (34.0561°N, 117.1956°W),
using WGS 84 / UTM zone 11N (EPSG:32611).

```usda
#usda 1.0
(
    defaultPrim = "World"
    metersPerUnit = 1
    upAxis = "Z"
)

# ── Stage root: CRS-bound to UTM 11N ────────────────────────────────
def Xform "World" (
    apiSchemas = ["GeospatialCRSBindingAPI"]
    references = [@./crs_library.usda@</CRS/WGS84_UTM11N>]
)
{
    uniform token[] xformOpOrder = ["!resetXformStack!", "xformOp:translate"]

    # Esri HQ — UTM 11N coordinates (metres)
    double3 xformOp:translate = (481948.63, 3768393.52, 400)

    # ── Building inherits CRS from /World ────────────────────────────
    def Xform "EsriCampus" (
        references = [@./esri_hq_building.usda@</EsriHQ>]
    )
    {
        # Local offset (metres) — stays within float32 range
        double3 xformOp:translate = (0, 0, 0)
        uniform token[] xformOpOrder = ["xformOp:translate"]
    }

    # ── Different CRS zone in the same scene ─────────────────────────
    def Xform "NewYorkCity" (
        apiSchemas = ["GeospatialCRSBindingAPI"]
        references = [@./crs_library.usda@</CRS/WGS84_UTM18N>]
    )
    {
        uniform token[] xformOpOrder = ["!resetXformStack!", "xformOp:translate"]
        # Times Square — UTM 18N coordinates (metres)
        double3 xformOp:translate = (583960, 4507523, 10)

        def Xform "TimesSquareBuilding"
        {
            double3 xformOp:translate = (0, 0, 0)
            uniform token[] xformOpOrder = ["xformOp:translate"]

            def Mesh "Walls"
            {
                int[] faceVertexCounts = [4, 4, 4, 4, 4, 4]
                int[] faceVertexIndices = [
                    0,1,2,3, 4,7,6,5, 0,4,5,1,
                    1,5,6,2, 2,6,7,3, 4,0,3,7
                ]
                point3f[] points = [
                    (-25,-15,0),(25,-15,0),(25,15,0),(-25,15,0),
                    (-25,-15,60),(25,-15,60),(25,15,60),(-25,15,60)
                ]
            }
        }
    }
}
```

Key observations:
- `/World` is bound to UTM 11N (EPSG:32611) — this is the **Target CRS**.
- `/World/EsriCampus` has no CRS binding — it **inherits** UTM 11N from `/World`.
- `/World/NewYorkCity` overrides with UTM 18N (EPSG:32618).
  At runtime, its geometry would be **reprojected** to UTM 11N.
- Mesh vertices (`point3f[]`) are small local offsets.
  Large geospatial positions are in `double3 xformOp:translate`.

### CRS library example

```usda
#usda 1.0

def "CRS" {
    def CoordinateReferenceSystem "WGS84_UTM11N"
    {
        uniform token crs:wkt = """PROJCRS["WGS 84 / UTM zone 11N",
            BASEGEOGCRS["WGS 84", ...],
            CONVERSION["UTM zone 11N", ...],
            ID["EPSG",32611]]"""
    }

    def CoordinateReferenceSystem "WGS84_UTM18N"
    {
        uniform token crs:wkt = """PROJCRS["WGS 84 / UTM zone 18N",
            BASEGEOGCRS["WGS 84", ...],
            CONVERSION["UTM zone 18N", ...],
            ID["EPSG",32618]]"""
    }

    def CoordinateReferenceSystem "NAD83_CA_Zone5_ftUS"
    {
        uniform token crs:wkt = """PROJCRS["NAD83 / California zone 5 (ftUS)",
            BASEGEOGCRS["NAD83", ...],
            CONVERSION["SPCS83 California zone 5", ...],
            ID["EPSG",2229]]"""
    }
}
```

### Programmatic authoring (C++)

```cpp
#include "pxr/usd/usdGeospatial/coordinateReferenceSystem.h"
#include "pxr/usd/usdGeospatial/bindingAPI.h"
#include "pxr/usd/usdGeom/xform.h"

// Define a CRS prim
auto crs = UsdGeospatialCoordinateReferenceSystem::Define(
    stage, SdfPath("/CRS/WGS84_UTM11N"));
crs.CreateWellKnownTextAttr().Set(VtValue(TfToken(wktString)));

// Create a geolocated Xform
auto xform = UsdGeomXform::Define(stage, SdfPath("/World"));
auto api = UsdGeospatialBindingAPI::Apply(xform.GetPrim());
api.Bind(crs);

// Set geospatial coordinates (UTM 11N, metres)
UsdGeomXformOp translateOp = xform.AddTranslateOp(
    UsdGeomXformOp::PrecisionDouble);
translateOp.Set(GfVec3d(481948.63, 3768393.52, 400.0));

// Resolve CRS for any prim (walks up hierarchy)
TfToken wkt = UsdGeospatialCoordinateReferenceSystem
    ::ComputeCoordinateReferenceSystem(somePrim);
```

### Programmatic authoring (Python)

```python
from pxr import Usd, UsdGeom, UsdGeospatial, Gf

stage = Usd.Stage.CreateNew("scene.usda")
stage.SetMetadata("metersPerUnit", 1.0)
UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)

# Define CRS
crs = UsdGeospatial.CoordinateReferenceSystem.Define(
    stage, "/CRS/WGS84_UTM11N")
crs.CreateWellKnownTextAttr().Set(wkt_string)

# Bind to Xform
world = UsdGeom.Xform.Define(stage, "/World")
stage.SetDefaultPrim(world.GetPrim())
api = UsdGeospatial.BindingAPI.Apply(world.GetPrim())
api.Bind(crs)

# Set geospatial position
world.AddTranslateOp(UsdGeomXformOp.PrecisionDouble).Set(
    Gf.Vec3d(481948.63, 3768393.52, 400.0))
```

## Interaction with existing USD features

### Stage metadata: metersPerUnit and upAxis

The `metersPerUnit` stage metadata defines the unit scale
for the entire stage.
When a CRS uses units other than metres
(e.g., US survey feet for State Plane CRS),
the CRS's unit definition in the WKT string
should be consistent with `metersPerUnit`,
or the runtime must apply a unit conversion.

The `upAxis` metadata ("Y" or "Z") defines the stage's up direction.
Most geospatial CRS conventions use Z-up,
so scenes authored with geospatial CRS
should typically set `upAxis = "Z"`.

The precise interaction between stage units/axes
and CRS-defined units/axes requires further specification
and is flagged as an [open question](#open-questions).

### Transform stack and resetXformStack

The `GeospatialCRSBindingAPI` emits `!resetXformStack!`
at the beginning of the `xformOpOrder` for CRS-bound prims.
This ensures that the `xformOp:translate` value
is interpreted as an **absolute position** in the bound CRS,
not as a relative offset from a parent transform.

Without this reset, USD's standard transform concatenation
would add the geospatial coordinates of parent and child,
producing nonsensical world-space positions.

### Composition arcs

CRS bindings compose through standard USD composition arcs:

- **References:** CRS library prims are imported via `references`.
- **Sublayers:** CRS libraries can be included as sublayers.
- **Inherits:** CRS class prims can be inherited
  (as demonstrated in the POC implementations).
- **Payloads:** CRS bindings survive payload loading/unloading.

The standard USD composition order (LIVRPS) applies;
a stronger arc can override a weaker arc's CRS binding.

### Relationship to UsdGeom

The `GeospatialCRSBindingAPI` is restricted to `UsdGeomXformable` prims.
It does not modify `UsdGeomMesh`, `UsdGeomPoints`, or other geometry schemas.
Geometry prims remain unchanged —
their vertex positions are always local offsets
relative to the nearest ancestor `Xform`.

## Industry use cases

### AECO

Building Information Modeling (BIM) workflows require
placing architectural models at surveyed site coordinates.
A hospital designed in Revit or ArchiCAD
must be positioned at its planned construction site
for clash detection, permitting, and construction coordination.

With this proposal, a BIM model exported to USD
retains its real-world position via CRS metadata,
enabling seamless integration with GIS site maps
and other geolocated assets.

### GIS and digital twins

Digital twin platforms aggregate data from dozens of sources
(LiDAR, photogrammetry, BIM, IoT sensors)
into a unified 3D view of a city, campus, or infrastructure network.
All this data arrives in various CRS —
the platform must reproject everything into a common frame.

This proposal provides the standard mechanism
for each USD layer to declare its CRS,
enabling the digital twin platform to compose and reproject
automatically rather than relying on manual coordinate transformations.

### Infrastructure and utilities

Pipeline, rail, and utility networks span hundreds of kilometres,
often crossing multiple UTM zones or State Plane regions.
A single USD stage must compose assets from different CRS zones
and display them correctly in a unified view.

The multi-CRS composition and runtime reprojection
described in this proposal directly address this use case.

### Defense and simulation

Military simulation and training environments
require precise geolocation of terrain, buildings, and vehicles
in CRS tied to national geodetic reference frames.
Dynamic datums and coordinate epochs
(supported via WKT 2's `COORDINATEMETADATA`)
are essential for high-precision positioning.

## Interoperability

### glTF geospatial extension

The Khronos Group is developing a geospatial extension for glTF
that encodes CRS metadata on nodes.
The approach is conceptually similar to this proposal
(CRS definition + binding to scene graph nodes).
Alignment between the USD and glTF approaches
would facilitate round-trip exchange between the two formats.

### IFC and BIM workflows

IFC (Industry Foundation Classes) is the open standard for BIM data.
IFC 5 is evaluating USD as a potential geometry backbone.
IFC's `IfcMapConversion` and `IfcProjectedCRS` entities
map directly to this proposal's `GeospatialCRS` and `GeospatialCRSBindingAPI`.
A standard USD CRS mechanism would simplify IFC-to-USD conversion.

### CityGML and OGC 3D Tiles

CityGML and OGC 3D Tiles both carry CRS metadata.
Converting these formats to USD currently requires
discarding or side-channeling CRS information.
This proposal preserves it as first-class scene data.

## Design considerations

### Why WKT and not bare EPSG codes

The proposal uses full OGC WKT 2 strings
rather than simple EPSG integer codes for several reasons:

1. **Self-contained.**
   A WKT string carries the complete CRS definition.
   No external registry lookup is needed at runtime.

2. **Supports custom CRS.**
   Site calibration grids, local engineering CRS,
   and derived projected CRS have no EPSG code.
   WKT can represent any CRS.

3. **Authority IDs are embedded.**
   The WKT `ID["EPSG", 32611]` clause provides
   the familiar integer code for tools that prefer it,
   so nothing is lost.

4. **Dynamic datums.**
   WKT 2 supports `DYNAMIC[FRAMEEPOCH[...]]` and `EPOCH[...]`
   for time-dependent reference frames — critical for
   high-precision surveying and tectonic-plate-aware applications.

5. **ISO standard.**
   OGC WKT 2 is formally standardized as ISO 19162:2019,
   ensuring long-term stability and broad industry support.

### Why a typed prim and not stage metadata

CRS could theoretically be stored as stage-level metadata
(like `metersPerUnit`).
This was rejected because:

1. **A stage often contains multiple CRS zones.**
   Stage metadata is a single value;
   a prim-based approach supports different CRS
   at different points in the hierarchy.

2. **Composition.**
   Prim-level CRS composes through references and sublayers.
   Stage metadata has limited composition semantics.

3. **Reuse.**
   A CRS prim can be referenced by many scenes.
   Stage metadata must be duplicated.

### Alternate approaches considered

| Approach | Mechanism | Pros | Cons |
|----------|-----------|------|------|
| **A: Primvar** | `asset primvars:geolocation:crs` | Auto-inheritance via primvar system | Requires custom asset-path resolution; non-standard prim types |
| **B: String primvar + inherits** | `string primvars:geolocation:crs:wkt` + `inherits` | Simplest implementation; leverages both inherits and primvar inheritance | WKT duplicated on every inheriting prim in flattened stage |
| **C: Abstract class + plain attribute** | `class` prims with `crs:wkt` attribute | Idiomatic USD class usage | No automatic inheritance for plain attributes; requires manual parent-walking |
| **D: Typed prim + applied API (this proposal)** | `GeospatialCRS` prim + `GeospatialCRSBindingAPI` | Clean separation of definition and usage; reference-based binding; API-driven inheritance | Requires new schema registration |

Approach D was selected because it provides the cleanest separation
of concerns, composes naturally through USD references,
and follows established patterns
(cf. `UsdShadeMaterialBindingAPI`).

The other approaches (A, B, C) were explored in
[proof-of-concept implementations](https://github.com/mistafunk/aousd-geospatial-pocs)
and informed the final design.

### Open questions

1. **Interaction with `metersPerUnit` and `upAxis`.**
   How should the CRS's unit definition interact with `metersPerUnit`?
   Should the runtime enforce consistency, convert automatically,
   or leave it to the authoring tool?

2. **Axis mapping.**
   Geospatial CRS axis orders vary
   (some are Easting/Northing, others Northing/Easting).
   How does this interact with USD's coordinate conventions?

3. **Third-party library abstraction.**
   What is the concrete API for plugging in PROJ, GDAL,
   or other CRS transformation libraries?
   Is this a USD plugin interface or a build-time dependency?

4. **WKT validation.**
   Should OpenUSD validate WKT strings at authoring time?
   The current position is that validation is the responsibility
   of authoring tools, not the USD runtime.

5. **Single-precision geometry.**
   The float32 limitation of `point3f` is a fundamental constraint.
   Collaboration with the Geometry Working Group is needed
   to evaluate double-precision geometry support
   for geospatial-scale scenes.

6. **Reprojection performance.**
   CRS reprojection is computationally expensive.
   What caching, LOD, and batching strategies
   should the Hydra Scene Index Filter employ?

7. **glTF interop.**
   How precisely should the USD and glTF geospatial extensions align?
   Should there be a formal mapping specification?

8. **IFC 5 requirements.**
   What additional CRS features (if any)
   does IFC 5 require that are not yet covered?

### Risks

1. **WKT complexity.**
   WKT strings are verbose and easy to author incorrectly.
   Mitigation: provide standard CRS library files
   and authoring-tool validation.

2. **Third-party dependency.**
   Correct reprojection requires PROJ or an equivalent library.
   If no CRS library is available, the runtime cannot reproject.
   Mitigation: graceful degradation — CRS metadata is preserved
   even without a reprojection engine.

3. **Performance.**
   Per-prim reprojection at render time
   could be expensive for large scenes.
   Mitigation: implement caching, pre-transform at export,
   and batch reprojection in the Scene Index Filter.

4. **Adoption resistance.**
   M&E users who do not need geospatial features
   may perceive this as unnecessary complexity.
   Mitigation: the schemas are optional and additive —
   they do not affect scenes that do not use them.

## Relationship to other proposals

- **[OpenExec](../openexec/README.md):**
  Geospatial reprojection could leverage the OpenExec framework
  for deferred evaluation of CRS transformations.

- **[Semantic Schema](../semantic_schema/README.md):**
  Geospatial prims could carry semantic labels
  (e.g., "building", "road", "terrain") for GIS classification.

- **[Identifier Separation of Concerns](../identifier_separation_of_concerns/README.md):**
  BIM/GIS assets often carry source identifiers
  (IFC GlobalId, GIS feature ID) that should survive
  round-trip through USD.

- **[Revise Use of Layer Metadata](../revise_use_of_layer_metadata/README.md):**
  Relevant to the discussion of whether CRS belongs at
  the stage level vs. prim level.

## Prototype implementations

Working prototype implementations exist:

| Implementation | Approach | Repository |
|----------------|----------|------------|
| **usdGeospatial schema** | C++ typed schema + applied API, PROJ integration | [mistafunk/USD (geospatial-prototype branch)](https://github.com/mistafunk/USD/tree/geospatial-prototype/pxr/usd/usdGeospatial) |
| **POC: Asset primvar** | Python + primvar with asset path | [mistafunk/aousd-geospatial-pocs (David de Koning)](https://github.com/mistafunk/aousd-geospatial-pocs) |
| **POC: String primvar + inherits** | Python + WKT in primvar + class inherits | [mistafunk/aousd-geospatial-pocs (David de Koning)](https://github.com/mistafunk/aousd-geospatial-pocs) |
| **POC: Class inheritance** | Python + abstract class with manual parent-walk | [mistafunk/aousd-geospatial-pocs (Simon Haegler)](https://github.com/mistafunk/aousd-geospatial-pocs) |
| **Esri HQ placement demo** | Python + usd-core + pyproj, USDA scene files | This proposal's accompanying files |

## Next steps

1. **Gather community feedback** on this proposal
   through the OpenUSD-proposals review process.

2. **Formalize the schema definition** (`schema.usda`)
   and register the `usdGeospatial` library
   in the OpenUSD build system.

3. **Define the third-party library abstraction API**
   for CRS parsing and reprojection.

4. **Collaborate with the Geometry Working Group**
   on double-precision geometry support.

5. **Implement the Hydra 2.0 Scene Index Filter**
   for runtime CRS reprojection.

6. **Produce interoperability guidelines**
   for glTF, IFC, CityGML, and 3D Tiles exchange.

7. **Ship standard CRS library files**
   with common EPSG definitions.

## References

| Resource | Link |
|----------|------|
| AOUSD Geospatial CRS Working Document | [Google Doc](https://docs.google.com/document/d/1v9A5SCSz_yvoExFgb9kJ5qPo4CAAGZtXnvS2ZptfvXc) |
| OGC WKT-CRS Standard (ISO 19162:2019) | [OGC 18-010r7](https://docs.ogc.org/is/18-010r7/18-010r7.html) |
| OGC Abstract Spec: CRS (ISO 19111) | [OGC 18-058](https://docs.ogc.org/is/18-058/18-058.html) |
| EPSG Geodetic Parameter Registry | [epsg.org](https://epsg.org/) |
| Esri: Coordinate Systems — What's the Difference? | [ArcGIS Blog](https://www.esri.com/arcgis-blog/products/arcgis-pro/mapping/coordinate-systems-difference) |
| PROJ Library | [proj.org](https://proj.org/) |
| usdGeospatial Prototype (C++) | [GitHub](https://github.com/mistafunk/USD/tree/geospatial-prototype/pxr/usd/usdGeospatial) |
| Geospatial POC Implementations | [GitHub](https://github.com/mistafunk/aousd-geospatial-pocs) |
| OpenUSD | [GitHub](https://github.com/PixarAnimationStudios/OpenUSD) |
| AOUSD Geospatial Presentation | [Google Slides](https://docs.google.com/presentation/d/13hVKSXQjJ1IAAj2ZLQL8klVAHC22GBcqNvV2WYqRWRY) |

## Appendix A: WKT examples

### WGS 84 / UTM zone 11N (EPSG:32611)

```
PROJCRS["WGS 84 / UTM zone 11N",
    BASEGEOGCRS["WGS 84",
        DATUM["World Geodetic System 1984",
            ELLIPSOID["WGS 84",6378137,298.257223563,
                LENGTHUNIT["metre",1.0]]],
        PRIMEMERIDIAN["Greenwich",0,
            ANGLEUNIT["degree",0.0174532925199433]],
        ID["EPSG",4326]],
    CONVERSION["UTM zone 11N",
        METHOD["Transverse Mercator",
            ID["EPSG",9807]],
        PARAMETER["Latitude of natural origin",0,
            ANGLEUNIT["degree",0.0174532925199433],
            ID["EPSG",8801]],
        PARAMETER["Longitude of natural origin",-117,
            ANGLEUNIT["degree",0.0174532925199433],
            ID["EPSG",8802]],
        PARAMETER["Scale factor at natural origin",0.9996,
            SCALEUNIT["unity",1.0],
            ID["EPSG",8805]],
        PARAMETER["False easting",500000,
            LENGTHUNIT["metre",1.0],
            ID["EPSG",8806]],
        PARAMETER["False northing",0,
            LENGTHUNIT["metre",1.0],
            ID["EPSG",8807]]],
    CS[Cartesian,2],
        AXIS["(E)",east,ORDER[1],
            LENGTHUNIT["metre",1.0]],
        AXIS["(N)",north,ORDER[2],
            LENGTHUNIT["metre",1.0]],
    ID["EPSG",32611]]
```

### Compound CRS: NAD83 / California zone 5 (ftUS) + NAVD88 height

```
COMPOUNDCRS["NAD83 / California zone 5 (ftUS) + NAVD88 height (ftUS)",
    PROJCRS["NAD83 / California zone 5 (ftUS)",
        BASEGEOGCRS["NAD83",
            DATUM["North American Datum 1983",
                ELLIPSOID["GRS 1980",6378137,298.257222101,
                    LENGTHUNIT["metre",1.0]]],
            ID["EPSG",4269]],
        CONVERSION["SPCS83 California zone 5 (US Survey feet)",
            METHOD["Lambert Conic Conformal (2SP)",
                ID["EPSG",9802]],
            PARAMETER["Latitude of false origin",33.5,
                ANGLEUNIT["degree",0.0174532925199433]],
            PARAMETER["Longitude of false origin",-118,
                ANGLEUNIT["degree",0.0174532925199433]],
            PARAMETER["Latitude of 1st standard parallel",35.4666666666667,
                ANGLEUNIT["degree",0.0174532925199433]],
            PARAMETER["Latitude of 2nd standard parallel",34.0333333333333,
                ANGLEUNIT["degree",0.0174532925199433]],
            PARAMETER["Easting at false origin",6561666.667,
                LENGTHUNIT["US survey foot",0.304800609601219]],
            PARAMETER["Northing at false origin",1640416.667,
                LENGTHUNIT["US survey foot",0.304800609601219]]],
        CS[Cartesian,2],
            AXIS["(E)",east,LENGTHUNIT["US survey foot",0.304800609601219]],
            AXIS["(N)",north,LENGTHUNIT["US survey foot",0.304800609601219]],
        ID["EPSG",2229]],
    VERTCRS["NAVD88 height (ftUS)",
        VDATUM["North American Vertical Datum 1988"],
        CS[vertical,1],
            AXIS["gravity-related height (H)",up,
                LENGTHUNIT["US survey foot",0.304800609601219]],
        ID["EPSG",6360]]]
```

### 3D Geographic with dynamic datum and epoch

```
COORDINATEMETADATA[
    GEOGCRS["WGS 84 (G2296)",
        DYNAMIC[FRAMEEPOCH[2024]],
        DATUM["World Geodetic System 1984 (G2296)",
            ELLIPSOID["WGS 84",6378137,298.257223563,
                LENGTHUNIT["metre",1.0]]],
        PRIMEMERIDIAN["Greenwich",0,
            ANGLEUNIT["degree",0.0174532925199433]],
        CS[ellipsoidal,3],
            AXIS["geodetic latitude (Lat)",north,ORDER[1],
                ANGLEUNIT["degree",0.0174532925199433]],
            AXIS["geodetic longitude (Lon)",east,ORDER[2],
                ANGLEUNIT["degree",0.0174532925199433]],
            AXIS["ellipsoidal height (h)",up,ORDER[3],
                LENGTHUNIT["metre",1.0]],
        ID["EPSG",10605]],
    EPOCH[2026.0]]
```

### 3D Geocentric (ECEF) with dynamic datum

```
GEODCRS["ITRF2020",
    DYNAMIC[FRAMEEPOCH[2015]],
    DATUM["International Terrestrial Reference Frame 2020",
        ELLIPSOID["GRS 1980",6378137,298.257222101,
            LENGTHUNIT["metre",1.0]]],
    PRIMEMERIDIAN["Greenwich",0,
        ANGLEUNIT["degree",0.0174532925199433]],
    CS[Cartesian,3],
        AXIS["(X)",geocentricX,ORDER[1],
            LENGTHUNIT["metre",1.0]],
        AXIS["(Y)",geocentricY,ORDER[2],
            LENGTHUNIT["metre",1.0]],
        AXIS["(Z)",geocentricZ,ORDER[3],
            LENGTHUNIT["metre",1.0]],
    ID["EPSG",9990]]
```

## Appendix B: AI-assisted drafting

This proposal was drafted with the assistance of Claude (Anthropic).
The AI was provided with the AOUSD Geospatial CRS working document,
the existing POC implementations, the usdGeospatial prototype README,
OGC standards documentation, and the OpenUSD proposals format guidelines.
All technical content was reviewed, verified,
and refined by the human authors.
