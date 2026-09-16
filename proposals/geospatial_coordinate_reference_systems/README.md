# Geospatial Coordinate Reference Systems for OpenUSD

## Contributors

- **Esri** (Tamrat Belayneh, Simon Haegler)
- **Nvidia** (Aaron Luk)
- The case study, the WKT encoding section and the runtime coordinate
  transformation section are Sébastien Vielliard's work.
- Also draws on work by David de Koning, Sébastien Vielliard, Simon Haegler
  and Tamrat Belayneh in the AOUSD AECO Interest Group.

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
   Geographic coordinates (e.g., UTM easting of 481,948 m)
   exceed the useful range of `float32`.
   Without guidance, implementations store these values
   in `point3f` arrays, causing visible jitter and drift.

4. **Multi-CRS composition is undefined.**
   Real-world projects routinely combine data from different CRS zones
   (e.g., a cross-state pipeline project spanning UTM zones 11 and 12).
   There is no mechanism to compose these into a single USD stage
   with correct spatial alignment.

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
| 3D Engineering / Local | `DERIVEDPROJCRS` | Local X, Y, Z | Site calibration grid |

3D means a complete vertical reference, not an assumed one. A definition that
names only a horizontal coordinate system does not become 3D by being authored
on a prim whose translate has three components: the third number would carry no
datum and no unit, and two readers would be free to take it as ellipsoidal or
orthometric height. A runtime handed a 2D definition reports failure rather than
supplying the missing half.

For dynamic datums (time-dependent reference frames),
WKT 2 supports the `COORDINATEMETADATA` wrapper
with `FRAMEEPOCH` and `EPOCH` clauses
for high-precision applications.

## Case study for the WGS 84 approach

WGS 84 (EPSG:4326) became dominant mainly because GPS uses it natively — every GPS receiver outputs coordinates in this datum. It is a global geodetic reference, so unlike national datums it works anywhere on Earth with one definition. The web mapping ecosystem reinforced this: GeoJSON mandates it, and most APIs and OGC standards default to it. Being a simple longitude/latitude geographic CRS makes it human-readable and easy to re-project from.

### Eiffel Tower example

Currently, OpenUSD georeferencing relies on stage-level metadata to define the relationship between virtual and physical space. Consider a high-fidelity model of the Eiffel Tower:

- Metrics: Authored at a scale of `metersPerUnit = 1.0`.
- Orientation: Configured as Y-Up, a common legacy default in many DCC tools.
- Coordinates: Vertex positions use 32-bit single-precision floats (`float3`).
- Local Origin: To avoid "floating-point jitter" caused by large coordinate values, the center of the square base is placed at `(0,0,0)`.

![Eiffel Tower](./eiffel_tower.png)

### WGS 84 georeferencing approach

The [omniGeospatial](https://docs.omniverse.nvidia.com/kit/docs/omni.usd.schema.geospatial/0.0.1/USD_SCHEMAS.html) schema (and [Hydra plugin](https://github.com/NVIDIA-Omniverse/OpenUSD-plugin-samples/tree/main/src/hydra-plugins#creating-a-custom-hydra-20-scene-index-for-geospatially-aware-transforms) as introduced by Nvidia Omniverse) georeferences such a model by applying a `WGS84ReferencePositionAPI` to a parent `Xform` prim.

This establishes a global anchor using:

- Latitude: 48.8584 N
- Longitude: 2.2945 E
- Altitude: 33.0 m (Height above the WGS84 ellipsoid).

The runtime engine then performs an Earth-Centered, Earth-Fixed (ECEF) conversion and a rotation into a Local Tangent Plane, such as East-North-Up (ENU).

### Limitations of only using a WGS 84 anchor point

While likely sufficient for visual effects work, the above method is inadequate for high-precision Survey and Construction for two primary reasons:

1. Datum Ambiguity: The term "WGS84" technically denotes a Datum Ensemble with an inherent low accuracy of approximately 2 meters. WGS84 coordinates are dynamic, changing over time due to tectonic plate motions, and up to 10 cm per year. For WGS84 coordinates to be accurate, they must be provided with the corresponding realization and measurement epoch (e.g., "WGS 84 (G2296) at epoch 2026.25"). This necessary detail is currently unsupported in standard USD schemas.

2. Axis Orientation: The current definition of "USD North" lacks the precision needed to align with the "True North" of a national geodetic Coordinate Reference System (CRS). Furthermore, AECO projects often require heights to be referenced to the geoid (orthometric height) for gravity-dependent systems, such as drainage. Current USD methods cannot precisely align with local vertical systems (like IGN 69) or map projections (like Lambert 93), which for example are the official systems used for AECO projects in France.

## Encoding the CRS: OGC WKT 2.1.11

We propose updating the OpenUSD schema to support describing the Coordinate Reference System (CRS) as a self-contained [WKT v2.1.11](https://docs.ogc.org/is/18-010r11/18-010r11.pdf) string ("Well-known text representation of coordinate reference systems"). This is equivalent to [ISO 19162:2019](https://www.iso.org/standard/76496.html).

This section covers the encoding only. The schema that carries it, and how a
CRS binds to the scene graph, are in [Design overview](#design-overview) and
[Detailed design](#detailed-design) below.

Key benefits:

- Standardization: Uses a mature, ISO-compliant format widely adopted in GIS and engineering.
- Self-Contained: Encodes all necessary parameters (ellipsoid, datum, projection, and units) in a single string, eliminating runtime database dependencies.
- Precision: Supports accurate definition of any Coordinate Reference Systems.

### WKT examples

The two examples here are worked against the case study. Reference encodings
of common CRS types are in [Appendix A](#appendix-a-wkt-examples).

#### WGS 84 ENU (east-north-up) local tangent plane

The following WKT string could be used to replace the approach using `WGS84ReferencePositionAPI` (see [case study](#case-study-for-the-wgs-84-approach) above). It defines a 3D local coordinate system centered at the Eiffel Tower with a Y-Up orientation. Note that this example encodes the up axis in the CRS itself, while [Stage metadata: metersPerUnit and upAxis](#stage-metadata-metersperunit-and-upaxis) below recommends `upAxis = "Z"` for geospatial scenes, and the worked examples in this document set it. Which of the two carries the up axis is [open question 1](#open-questions).

```lisp
GEODCRS["Y-Up Local Tangent Plane at Eiffel Tower",
    BASEGEOGCRS["WGS 84",
        DATUM["World Geodetic System 1984",
            ELLIPSOID["WGS 84", 6378137, 298.257223563, LENGTHUNIT["metre", 1]],
            ID["EPSG", 6326]],
        ID["EPSG", 4979]],
    DERIVINGCONVERSION["Topocentric at Eiffel Tower",
        METHOD["Geographic/topocentric conversions", ID["EPSG", 9837]],
        PARAMETER["Latitude of topocentric origin", 48.8584,
            ANGLEUNIT["degree", 0.0174532925199433], ID["EPSG", 8834]],
        PARAMETER["Longitude of topocentric origin", 2.2945,
            ANGLEUNIT["degree", 0.0174532925199433], ID["EPSG", 8835]],
        PARAMETER["Ellipsoidal height of topocentric origin", 33.0,
            LENGTHUNIT["metre", 1.0], ID["EPSG", 8836]]],
    CS[Cartesian, 3],
    AXIS["X", east], AXIS["Y", up], AXIS["Z", south],
    LENGTHUNIT["metre", 1]]
```

#### Derived CRS with affine site calibration

For projects requiring high accuracy, we can compute the transformation between the National CRS (e.g., Lambert-93 + IGN69) and the USD local CRS using least squares. This transformation—which can include affine transformations (EPSG 9624) and vertical adjustment planes to account for localized vertical deviations—can be encoded directly into the WKT string.

```lisp
COMPOUNDCRS["Site Local Coordinate System (X East, Y Up, Z South)",
    DERIVEDPROJCRS["Site Local Horizontal (Derived from ETRS89-FRA/Lambert-93)",
        BASEPROJCRS["ETRS89-FRA [RGF93 v2b] / Lambert-93",
            BASEGEOGCRS["ETRS89-FRA [RGF93 v2b]",
                DATUM["ETRS89-FRA [RGF93 v2b]",
                    ELLIPSOID["GRS 1980", 6378137, 298.257222101,
                        LENGTHUNIT["metre", 1]]],
                ID["EPSG", 9782]],
            CONVERSION["Lambert-93",
                METHOD["Lambert Conic Conformal (2SP)", ID["EPSG", 9802]],
                PARAMETER["Latitude of false origin", 46.5,
                    ANGLEUNIT["degree", 0.0174532925199433], ID["EPSG", 8821]],
                PARAMETER["Longitude of false origin", 3,
                    ANGLEUNIT["degree", 0.0174532925199433], ID["EPSG", 8822]],
                PARAMETER["Latitude of 1st standard parallel", 44,
                    ANGLEUNIT["degree", 0.0174532925199433], ID["EPSG", 8823]],
                PARAMETER["Latitude of 2nd standard parallel", 49,
                    ANGLEUNIT["degree", 0.0174532925199433], ID["EPSG", 8824]],
                PARAMETER["Easting at false origin", 700000,
                    LENGTHUNIT["metre", 1.0], ID["EPSG", 8826]],
                PARAMETER["Northing at false origin", 6600000,
                    LENGTHUNIT["metre", 1.0], ID["EPSG", 8827]]],
            ID["EPSG", 9794]],
        DERIVINGCONVERSION["Site Calibration Horizontal Affine",
            METHOD["Affine parametric transformation", ID["EPSG", 9624]],
            PARAMETER["A0", 10.0, LENGTHUNIT["metre", 1.0], ID["EPSG", 8623]],
            PARAMETER["A1", 1.00005, SCALEUNIT["unity", 1.0], ID["EPSG", 8624]],
            PARAMETER["A2", 0.00001, SCALEUNIT["unity", 1.0], ID["EPSG", 8625]],
            PARAMETER["B0", 5.0, LENGTHUNIT["metre", 1.0], ID["EPSG", 8639]],
            PARAMETER["B1", -0.00001, SCALEUNIT["unity", 1.0], ID["EPSG", 8640]],
            PARAMETER["B2", 1.00005, SCALEUNIT["unity", 1.0], ID["EPSG", 8641]]],
        CS[Cartesian, 2],
        AXIS["X", east, ORDER[1]],
        AXIS["Z", south, ORDER[3]],
        LENGTHUNIT["metre", 1.0]],
    VERTCRS["Site Local Vertical (Inclined Plane)",
        BASEVERTCRS["NGF-IGN69 height",
            VDATUM["Nivellement General de la France - IGN69",
                ID["EPSG", 5119]],
            ID["EPSG", 5720]],
        DERIVINGCONVERSION["Inclined Plane Vertical Adjustment",
            METHOD["Vertical Offset and Slope", ID["EPSG", 1046]],
            PARAMETER["Vertical Offset", 1.5,
                LENGTHUNIT["metre", 1.0], ID["EPSG", 8603]],
            PARAMETER["Inclination in latitude", 0.00001,
                ANGLEUNIT["radian", 1.0], ID["EPSG", 8730]],
            PARAMETER["Inclination in longitude", 0.00001,
                ANGLEUNIT["radian", 1.0], ID["EPSG", 8731]]],
        CS[vertical, 1],
        AXIS["Y", up, ORDER[2]],
        LENGTHUNIT["metre", 1.0]]
]
```

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
   Child prims should inherit their parent's CRS,
   just as they inherit material bindings.
   Overrides at any level in the hierarchy are supported.

5. **Precision-aware.**
   The design must address the float32 limitation
   of `point3f` geometry by separating large geospatial offsets
   (double-precision transforms) from local vertex positions (single-precision).

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

### Schema design

Two new schemas are introduced:

| Schema | Type | Purpose |
|--------|------|---------|
| `CoordinateReferenceSystem` | Typed (IsA) | Defines a CRS as a first-class USD prim |
| `CRSBindingAPI` | Applied (HasA) | Binds a CRS prim to a `UsdGeomXformable` |

This two-schema approach separates the CRS *definition*
from the CRS *usage*,
so that a single CRS definition is named by many prims
rather than copied onto each of them.
A CRS library layer is brought into a scene the usual way, by reference or
sublayer; the binding itself is a relationship and composes as one.

### CRS library pattern

CRS definitions are intended to live in shared **library layers**
(e.g., `crs_library.usda`) that can be referenced by any scene:

```
crs_library.usda
├── /CRS/WGS84_UTM11N        (CoordinateReferenceSystem)
├── /CRS/NAD83_UTM11N        (CoordinateReferenceSystem)
├── /CRS/NAD83_CA_Zone5      (CoordinateReferenceSystem)
└── /CRS/WGS84_Geographic3D  (CoordinateReferenceSystem)
```

This pattern is analogous to shared material libraries in M&E workflows.
Authoring tools can ship standard CRS libraries,
and users can create custom ones for local/site-specific CRS definitions.

### CRS binding and inheritance

The `CRSBindingAPI` is applied to a `UsdGeomXformable` prim.
It declares one relationship, `crs:binding`, targeting a
`CoordinateReferenceSystem` prim on the same stage or in a layer the stage
composes.

CRS bindings inherit down the prim hierarchy.
A prim without its own binding resolves its CRS by walking up to the nearest
ancestor that has one, and that nearest binding wins outright.
`UsdShadeMaterialBindingAPI` works the same way, and the resemblance stops
there: there are no purpose-restricted bindings, no collection-based bindings
and no binding-strength metadata. What those add is a way for several bindings
to compete for one prim, which for an appearance is ordinary authoring and for a
coordinate reference system means somebody is wrong about what the coordinates
mean. That is for a checker to catch, not for a precedence order to resolve.

A child prim may override its parent's CRS
by applying its own `CRSBindingAPI` targeting a different CRS.
This is how multi-CRS scenes are composed
(e.g., one subtree in UTM zone 11N, another in UTM zone 18N).

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

## Detailed design

### CoordinateReferenceSystem typed schema

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
    doc = "WGS 84 / UTM zone 11N (EPSG:32611) + EGM2008 height (EPSG:3855)"
)
{
    uniform token crs:wkt = """COMPOUNDCRS["WGS 84 / UTM zone 11N + EGM2008 height",
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
            ID["EPSG",32611]],
        VERTCRS["EGM2008 height",
            VDATUM["EGM2008 geoid"],
            CS[vertical,1],
                AXIS["gravity-related height (H)",up,
                    LENGTHUNIT["metre",1.0]],
            ID["EPSG",3855]]]"""
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

    /// Return the WKT token of the CRS in effect on `prim`: walk the composed
    /// prim and its ancestors to the nearest authored crs:binding
    /// relationship, validate its composed target list, and read crs:wkt from
    /// the single CoordinateReferenceSystem prim it targets. Geometry
    /// ancestors are not searched for crs:wkt, and an invalid nearest binding
    /// is an error rather than a reason to continue to a farther one. Binding
    /// is read from composed prims, including opinions introduced by
    /// references and inherits.
    static TfToken ComputeCoordinateReferenceSystem(UsdPrim const &prim);
};
```

### CRSBindingAPI applied schema

A single-apply API schema that binds a CRS to a `UsdGeomXformable` prim.

**Schema type name:** `CRSBindingAPI`
**Can only apply to:** `Xformable`

**Relationships:**

| Relationship | API Name | Targets | Description |
|--------------|----------|---------|-------------|
| `crs:binding` | `crsBinding` | one `CoordinateReferenceSystem` prim | The CRS the bound prim's coordinates are expressed in |

A relationship rather than a reference. A reference would compose the CRS prim's
contents into the bound prim, putting `crs:wkt` on geometry and copying the
definition to every site that uses it; a relationship names the definition and
leaves it in one place.

Relationship targets compose as a list, not as a scalar. `Bind()` authors an
explicit one-target list, and an explicit list in a stronger layer does replace
what weaker layers contributed. An ordinary target addition does not: it
composes with them, so a prim can end up carrying two targets without any single
layer having authored two. Exactly one composed target is expected. An empty
target list and multiple targets are both authoring errors rather than an
unbinding mechanism, which is what keeps a choice between two CRS definitions
from being settled by the order they happen to compose in.

**Binding does not modify the prim's transform stack.** `Bind()` authors the
relationship and nothing else. That a bound prim's `xformOp:translate` reads as
an absolute position in the bound CRS is a rule the runtime applies when it
resolves; it is not recorded in the layer. See
[Transform stack and resetXformStack](#transform-stack-and-resetxformstack).

**C++ API:**

```cpp
class UsdGeospatialCRSBindingAPI : public UsdAPISchemaBase {
public:
    static UsdGeospatialCRSBindingAPI Apply(const UsdPrim &prim);
    static bool CanApply(const UsdPrim &prim,
                         std::string *whyNot = nullptr);

    UsdRelationship CreateCRSBindingRel() const;
    UsdRelationship GetCRSBindingRel() const;

    /// Author crs:binding as an explicit one-target relationship list
    /// naming a CRS prim in the composed stage.
    bool Bind(UsdGeospatialCoordinateReferenceSystem const &crs) const;
};
```

### Complete scene example

The following example places a simplified building
at the Esri headquarters in Redlands, California (34.0561°N, 117.1956°W),
using WGS 84 / UTM zone 11N (EPSG:32611) compounded with EGM2008 height
(EPSG:3855), so the translate's third component carries a datum and a unit.

```usda
#usda 1.0
(
    defaultPrim = "World"
    metersPerUnit = 1
    upAxis = "Z"
)

# ── Stage root: CRS-bound to UTM 11N ────────────────────────────────
def Xform "World" (
    apiSchemas = ["CRSBindingAPI"]
)
{
    rel crs:binding = </CRS/WGS84_UTM11N>
    uniform token[] xformOpOrder = ["xformOp:translate"]

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
        apiSchemas = ["CRSBindingAPI"]
    )
    {
        rel crs:binding = </CRS/WGS84_UTM18N>
        uniform token[] xformOpOrder = ["xformOp:translate"]
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
        uniform token crs:wkt = """COMPOUNDCRS["WGS 84 / UTM zone 11N + EGM2008 height",
            PROJCRS["WGS 84 / UTM zone 11N", ..., ID["EPSG",32611]],
            VERTCRS["EGM2008 height", ..., ID["EPSG",3855]]]"""
    }

    def CoordinateReferenceSystem "WGS84_UTM18N"
    {
        uniform token crs:wkt = """COMPOUNDCRS["WGS 84 / UTM zone 18N + EGM2008 height",
            PROJCRS["WGS 84 / UTM zone 18N", ..., ID["EPSG",32618]],
            VERTCRS["EGM2008 height", ..., ID["EPSG",3855]]]"""
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
#include "pxr/usd/usdGeospatial/crsBindingAPI.h"
#include "pxr/usd/usdGeom/xform.h"

// Define a CRS prim
auto crs = UsdGeospatialCoordinateReferenceSystem::Define(
    stage, SdfPath("/CRS/WGS84_UTM11N"));
crs.CreateWellKnownTextAttr().Set(VtValue(TfToken(wktString)));

// Create a geolocated Xform
auto xform = UsdGeomXform::Define(stage, SdfPath("/World"));
auto api = UsdGeospatialCRSBindingAPI::Apply(xform.GetPrim());
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
api = UsdGeospatial.CRSBindingAPI.Apply(world.GetPrim())
api.Bind(crs)

# Set geospatial position
world.AddTranslateOp(UsdGeomXformOp.PrecisionDouble).Set(
    Gf.Vec3d(481948.63, 3768393.52, 400.0))
```

## Runtime coordinate transformation

### When coordinates must be harmonized

There are several runtime situations where coordinates defined in different CRS need to be harmonized:

- rendering
- stage queries (e.g. bounding boxes)
- indirect transformation requests (e.g. upon stage flattening)
- explicit transformation requests using the new API calls

### The transformation abstraction

We propose to introduce an internal abstraction to compute coordinate transformations from one CRS to another:

```text
transform(inout ArrayVector3d coordinates, in WKT crsIn, in WKT crsOut)
```

The OpenUSD plugin system is employed to register implementations.

### Target CRS and runtime reprojection

The **Target CRS** for a resolve pass is the one supplied by the host
application or API caller, or where the caller supplies none, the CRS bound to
the composed `defaultPrim` of the root layer stack. All prims whose bound CRS
differs from it are **reprojected** — their transforms are mathematically
converted from the source CRS to the Target CRS.

A Hydra 2.0 Scene Index Filter for rendering and API methods for computation are
both ways to implement this, over an abstracted interface to third-party CRS
libraries (PROJ, GDAL, Esri projection engine, and others). [Runtime
behavior](#runtime-behavior) below describes what any implementation has to
produce, without assuming either.

### Runtime behavior

The rules here are stated on their own terms. Where a choice could plausibly
have been made another way, what the other way costs has been measured on a real
scene rather than estimated; those figures, and the implementations they come
from, are in
[Appendix C](#appendix-c-reference-implementations-and-measurements), which is
not part of this description.

#### Which CRS applies to a prim

The binding is the `crs:binding` relationship declared by `CRSBindingAPI`.
Composition and binding stay orthogonal and both use mechanisms USD already has:
the relationship is the binding edge, and the CRS prim it points at may itself
have arrived by a `references` or `payload` arc from a shared library layer.
Nothing bespoke, and no asset-path attribute in the binding path.

A prim's CRS is found by walking from the prim toward the root of the composed
stage and taking the nearest authored binding. A georeferenced scene binds at its
root, so every prim in it inherits one — a prim with nothing bound at or above it
is a scene with content outside its own frame, which is an authoring defect rather
than a mode this description supports.

Where several ancestors carry bindings, the nearest one wins. There is no
further ladder: no purpose-restricted bindings, no collection-based bindings, no
binding strength by which an ancestor overrides its descendants, and no analogue
of `GeomSubsets`.

Those mechanisms exist so that several bindings can compete for one prim, and
that is the wrong shape here. A material binding assigns an appearance, which is
arbitrary and legitimately multi-valued — the same mesh can have a preview look
and a final look, which is what purposes are for. A CRS binding records what a
prim's coordinates already mean, and there is one answer. A preview CRS is not a
thing; the variability that would reach for one is a choice of **target**, which
is a caller's parameter and is described below. Collection bindings would also
cost the property that makes resolution cheap to reason about: the answer for a
prim is found by walking its ancestors and stopping, where a collection anywhere
on the stage could otherwise claim it. And two different bindings competing for
one prim does not mean a precedence question, it means somebody is wrong about
what the coordinates mean — which a checker should catch rather than a ladder
silently settle.

What is reused is the part worth reusing: someone who understands material
binding already understands this one. Nearest authored binding wins.

It also means inheriting the cost shape. Resolving a prim's CRS is an ancestor
walk, a relationship hop to a prim that may be anywhere in the composed stage, and
then turning a WKT string into something that can transform coordinates — the last
dominating, and none of it worth repeating per prim. `UsdShadeMaterialBindingAPI`
has the same shape and answers it with caches passed through resolution.

#### Which CRS the scene resolves into

Everything in a single resolve pass lands in one target CRS: the one supplied by
the host application or API caller, or where the caller supplies none, the CRS
bound to the composed `defaultPrim` of the root layer stack. A caller-supplied
target is what lets two georeferenced stages with different `defaultPrim`
bindings be brought into one scene, and it is the case the PROJ example above
already demonstrates by transforming into EPSG:10499.

Where neither is available — a stage carrying CRS bindings with nothing bound to
its `defaultPrim`, opened without a target — there is no default to fall back
on. Picking one silently would place the whole scene somewhere nobody asked for,
so this is handled the same way as any other transform that cannot be computed,
and it is an authoring-time error a checker catches.

A prim whose CRS already *is* the target is left alone rather than sent on an
identity round trip through the transformation engine, which would only
introduce noise into content that needed no work.

#### What an anchor establishes

The nearest prim at or above a given prim that carries **its own** binding and an
authored transform is that prim's **anchor**. What the anchor contributes to the
prim's world transform is a *frame* — orientation and translation — not just a
position.

A binding therefore does two things, and they are worth separating because the
material-binding parallel suggests the wrong answer on the second. An **inherited**
binding says which coordinate reference system this part of the scene is expressed
in. A binding **authored on the prim itself** additionally says that this prim's
transform is a position in that system rather than an offset within its parent's
frame — and that holds even when the system is the one it would have inherited
anyway. Re-binding the same material is a no-op; re-binding the same CRS is what
makes a prim an anchor.

This is the most consequential thing in the section, and the naive
implementation gets it wrong in a way that looks right at first. That
implementation reprojects the anchor position and writes it into the translation
of an otherwise identity matrix, which is correct exactly where the source and
target axes happen to align. Everywhere else the subtree keeps world `+Z` when
its local `+Z` should point along the ellipsoidal normal at the anchor — at
mid-latitudes, tens of degrees away from geocentric `+Z`. The result is not
subtle: assets lie on their side, and a building offset from its anchor lands
well away from where closed-form geodesy puts it.

Which frame the anchor establishes follows from the kind of CRS it is bound to —
the *source* CRS, which the runtime already has in hand:

| Anchor's CRS | Frame it establishes | What descendant offsets mean |
|---|---|---|
| Geographic or geocentric | The topocentric (east-north-up) basis at the anchor position, originating at that position expressed in the target CRS | Local metric offsets in that topocentric frame |
| Projected (UTM, State Plane, site-calibrated, …) | The anchor's grid plane | Offsets in the anchor's grid coordinates and units |

For a projected anchor, a descendant's origin is computed by adding its offset
to the anchor's position *in grid coordinates* and transforming that grid point
into the target CRS — not by lifting the offset through the anchor's topocentric
basis. Grid axes are not topocentric axes; they differ by grid convergence and
point scale. Lifting grid-authored offsets through a true east-north-up basis
produces a systematic error that grows with the lever from the anchor to the
geometry. Selecting the frame from the source CRS instead puts both paths on the
same point.

This is also the specific answer to the objection that composing a local
transform onto an anchor position "is not correct in the general case for a
spherical target CRS." It is not correct in general — choosing the composition
frame from the source CRS is what makes it correct.

One qualification worth stating plainly: an orientation basis is only meaningful
when the target CRS is geocentric. For a planar target the orientation is
implicit in the target's own grid, and the anchor contributes position only.

Below the anchor, everything is plain USD. For a prim `D` under an anchor `A`:

```text
world(D) = localToAnchor(D) ∘ anchorFrame(A)
```

where `localToAnchor(D)` is `D`'s ordinary authored transform expressed relative
to `A`, computed from the standard `UsdGeomXformable` stack with no geospatial
interpretation applied to it at all. In the projected case the translation is
computed in-plane as described above, while rotation and scale come from
`localToAnchor(D)` unchanged.

A prim carrying its *own* position and binding is an anchor in its own right,
and its ancestors' georeferencing does not additionally accumulate onto it: two
georeferenced positions in one chain are two absolute statements, not a base and
an offset. That makes anchor-versus-child a real authoring distinction, and
getting it wrong is the most common way to misplace a georeferenced scene.
Authoring a building corner as an independent georeferenced leaf, where relative
placement was intended, misplaces it by the whole distance between the two
georeferenced positions; re-authoring it as an ordinary Cartesian child places
it exactly.

#### Everything that is not an anchor

A georeferenced scene is a place, and most of what is in it does not carry a
coordinate reference system of its own. A bollard, a light, a piece of survey
equipment sits where it sits, relative to something that does. That does not make
it any less placed on the Earth — it is placed the way things in a place are
placed, relative to their surroundings. Only anchors carry a CRS; everything
beneath one is plain USD, and authoring a scene requires no per-prim geodesy.

Four things follow, and together they are what makes such a scene editable by
someone who does not know what an ellipsoid is.

**A prim without its own binding is placed by its ordinary authored transform,
relative to the nearest anchor above it.** Being in a georeferenced scene changes
nothing about how it is authored, parented, or moved.

**Editing that transform changes where that prim is, and nothing else.** Because
resolution is a computed view and nothing resolved was written into the scene, no
stored placement goes stale and no other prim needs revisiting.

**Moving an anchor moves everything beneath it; moving a child does not move its
anchor.** Those are different edits with different reach, and which one is being
made is determined by whether the prim carries its own binding.

**A prim's frame is determinable from the composed stage without resolving it.** A
tool that needs to know what one metre east means at a particular prim can ask
locally, without a resolve pass over the whole scene.

That last one is what lets a hand edit respect the planet. A Cartesian offset
sits in a frame this description defines precisely, so a tool can work out what a
geodetic intent — stay on the surface, hold this altitude — amounts to as an offset,
and write that. A widget that does the geodesy produces plain numbers; the runtime
that later resolves them knows nothing about the intent and does not need to.

The limit worth stating is that the scene does not record the intent either. Opened
in a tool without that widget, the object still moves — it moves in the frame rather
than along the surface, and nothing marks the difference. That is the same division
this description keeps everywhere: the scene carries state, not behavior.

#### Precision, axis order, units, and epoch

**Precision.** CRS coordinates, anchor positions, anchor frames and resolved
world transforms are carried in double precision, and resolved absolute
coordinates are not written into single-precision geometry attributes such as
`point3f[] points`. Frame-based composition is what makes this affordable rather
than merely desirable: the large magnitudes — about 6.4 × 10⁶ m for an
Earth-surface geocentric position — stay inside the double-precision anchor
frame, and vertices below the anchor stay small local offsets. Absolute float32
geocentric positions lose accuracy at that magnitude by a margin that matters for
survey work; the same geometry carried as localized float32 offsets under a
double-precision anchor holds it, by orders of magnitude. This is the two-tier
scheme from
[Precision handling](#precision-handling), stated as the runtime's side of the
bargain.

**Axis order.** The anchor position is ordered `(x = longitude or easting,
y = latitude or northing, z = height)` regardless of the axis order the CRS
authority declares in the WKT, and the runtime hands the components to the
transformation engine in that order — the `always_xy` convention — rather than
re-ordering them from the WKT `AXIS` clauses. USD is not the right venue to
relitigate authority axis order. Fixing it at the boundary means a scene reads
the same no matter which authority defined its CRS, and it removes a class of
bug that inspection cannot catch: a transposed easting and northing is usually
still a perfectly valid coordinate.

**Units.** The anchor position is in the units the bound CRS declares, not in
`metersPerUnit`. Where the two differ, the runtime converts when producing world
transforms rather than assuming metres.

**Epoch.** Where a CRS carries a coordinate epoch — dynamic datums — the runtime
passes it to the transformation engine as the time coordinate of a 4D transform.
Where none is authored, it does not invent one.

#### When the transform cannot be computed

A runtime that implements this description will still meet transforms it cannot
produce: no registered transformation engine, WKT that cannot be parsed or is
unsupported, a missing transformation grid, a point outside the transformation's
domain of validity.

In none of those cases does it fall back to placing the prim at its unresolved
authored transform, or substitute an identity transform. It reports the failure,
and either omits the affected prims or declines the stage.

The reason is that a substituted transform is indistinguishable from a computed
one. A caller that receives a matrix has no way to tell that the geodesy behind it
did not happen, so a quiet fallback converts a missing grid file into content that
is confidently in the wrong place. Reporting keeps the failure where it can be
acted on, and the cost of being wrong here is measured in hundreds of metres
rather than in precision.

What degrades gracefully is the metadata. Where reprojection is unavailable, CRS
definitions and bindings survive read and write round trips even though placement
cannot be computed, so the failure stays recoverable in a tool that does have an
engine.

#### When a consumer cannot resolve at all

A consumer with no CRS support is a different situation, and not one this
description can impose anything on.

What such a consumer sees is worth stating, because it is the reason any of this
matters. A coordinate-neutral scene draws at bare local offsets — near the centre
of the planet rather than on its surface, with nothing raised — and to that
consumer it is indistinguishable from a correct scene. Nothing is malformed;
ordinary transform composition simply answers a question that was never asked of
it.

**So the requirement falls on the stage, not on the consumer: a stage whose
correct placement depends on CRS resolution must be able to declare that
dependency, and a consumer must be able to read the declaration without traversing
the stage.** What a consumer does with it — refuse, defer to a resolver, warn, or
proceed — is its own call. An extension is in no position to oblige runtimes to
behave differently for it, and one that tried would be asking every runtime to
know about every extension in order to know when to object.

Two things follow. The declaration is a contract rather than an enforcement: a
consumer that ignores it still gets it wrong, and nothing here changes that. And
because the dependency is a property of the data rather than an assertion by an
author, it should be derivable rather than remembered — an author who omits it has
a defect a tool can find. The mechanism belongs to the host format, and for
OpenUSD it is described in [Declaring the dependency](#declaring-the-dependency)
below.

#### Where the behavior can run

Nothing above depends on Hydra, on rendering, or on any particular evaluation
architecture. A runtime implements this description by producing these world
transforms, by whatever mechanism. Query paths — bounding boxes, point
instancing, physics, world-transform queries — are the same behavior as
rendering, not a reduced version of it. "Does this work without a renderer" is
the first question a GIS or AECO pipeline asks, and the answer here is
structural rather than a promise: the description is stated over the composed
stage, and nothing in it refers to a render path.

What the transformation engine is asked to do is narrow, and deliberately so.
The abstraction above it moves coordinates from one CRS to another. Deriving the
anchor's orientation basis, selecting the frame from the kind of source CRS,
localizing offsets, and deciding what happens when a transform cannot be
computed all sit on the runtime's side of that line. An engine that only moves
points is enough to implement everything described here, which is what leaves
PROJ, GDAL and a vendor projection engine interchangeable behind it. The
coordinate epoch needs no separate channel either, since a dynamic CRS carries
it in its own WKT.

Resolution is a computed view. Resolved transforms, injected anchor frames and
reprojected coordinates are not written back into the authored layers of the
stage being resolved; they live in a scene index, a query result, an execution
output, or a new output layer. The authored scene stays coordinate-neutral,
which is what keeps the CRS intent inspectable — once placement has been baked
into a matrix, the intent has collapsed and there is nothing left to check
against.

That also settles what this costs a runtime that does not want it, which is
nothing. No existing transform evaluation has to change and nothing has to be
intercepted: the behavior is computed over the composed stage by something a
consumer chooses to run, so a pipeline with no interest in georeferencing behaves
exactly as it did before. Requiring a hook in the host's evaluation would be the
same mistake as authoring the reset into a layer — one puts a geospatial decision
into a code path every caller inherits, the other into data every consumer
inherits, and both spend something belonging to people who did not ask for it.

An anchor frame does establish a fresh basis: the anchor's ancestors' transforms
do not compose on top of an already-resolved world transform. Where the computed
representation has a `resetXformStack` concept, as Hydra's xform schema does,
that is where the semantic is recorded. The distinction is worth stating,
because the two can read as contradictory and are not — *not re-composing under
the parents* is required; *recording that in an authored layer* is what the
previous paragraph rules out.

Flattening into a target CRS is this same evaluation with the results written
out, and produces the same world transforms as a resolve pass over the same
stage with the same target. A stage flattened this way records the target CRS it
was flattened into, drops the resolution-required declaration since resolution
is no longer needed, and keeps the CRS definitions and original bindings where
it can — discarding them makes the flattening irreversible and throws away what
a checker or a later re-resolve would need. Resolving an already-resolved stage
changes nothing: the transformation is not applied a second time.

#### How closely independent runtimes agree

Exact agreement between independent implementations is not achievable, and not
worth asking for: transformation engines differ in grid handling and in
floating-point operation order. What is worth asking for is that an
implementation state how closely it agrees, as a distance in target-CRS units at
a stated coordinate magnitude. A count of matching digits is not comparable
across CRS families.

No threshold is set here. The AOUSD core specification declines to prescribe a
numerical tolerance for value resolution, on the grounds that acceptable
deviation depends on hardware, floating-point behaviour, compiler behaviour and
implementation choices. The same reasoning holds here, and one further source
applies that does not arise in value resolution: two engines can differ by
metres because they have different datum operations or different grids
available, and neither is in error.

Implementations are encouraged to measure their deviation and to state it — the
agreement achieved, in target-CRS units at a stated magnitude, and against what
it was compared. An adopter deciding whether an implementation suits their work
needs that number; they do not need it to be the same number as everyone else's,
and nothing here makes a particular number the difference between an
implementation of this schema and something else.

For orientation, and not as a requirement: the survey control this data derives
from is generally good to centimetres, so agreement at the millimetre scale sits
comfortably below the accuracy of the source.

#### What a checker can catch at authoring time

Several of the ways to get this wrong are mechanically detectable in the
authored scene, which matters because a runtime description that nothing
validates against will be violated at render time. `usdchecker` is the natural
home.

| Invariant | Cost of violating it |
|---|---|
| Anchor-versus-child is unambiguous: a prim carrying a position beneath another such prim is flagged unless it declares an overriding binding | Misplacement by the whole anchor-to-leaf distance |
| Descendant offsets are authored in the frame the anchor's CRS implies | Systematic misplacement, growing with the lever |
| A stage carrying CRS bindings declares that resolution is required | Silent placement near the planet's centre |
| A binding resolves to a prim that actually carries a valid CRS definition | Resolver failure at load |
| A stage carrying CRS bindings binds one at its `defaultPrim`, so no prim is outside the scene's frame | Content placed outside any frame |
| A stage that expects to resolve without a caller-supplied target binds a geocentric or projected CRS at its `defaultPrim` | No usable target: geographic is not a resolve target |
| A georeferenced prim does not also carry a conflicting authored transform | Ambiguous placement |

A coordinate-neutral authored scene is what makes these checkable at all: the
CRS intent is still present as data.

#### What this description does not settle

Three things are deliberately not settled here.

**The local origin.** The anchor position is authored on `xformOp:translate`.
Where a CRS is itself constructed for a site, its natural origin and the anchor
are the same point, and the position could be taken from the CRS's `CONVERSION`
parameters instead of authored. That is additive later: a CRS that supplies its
own origin lets the authored translate be omitted, and nothing written against
this description stops working.

**A geographic Target CRS.** Resolving into latitude and longitude would mean
defining what a world transform is in an angular space, since a metric offset
composed onto a position in degrees is not a linear operation and changes
meaning with latitude. This description does not cover it, and a runtime asked
for one reports that rather than producing a plausible-looking result.
Geographic CRSs remain fully supported as sources, and as an output encoding for
a point query. The Target CRS is a caller or runtime choice and is never
authored into a scene, so covering this later breaks no content.

**External grid files.** WKT2 names transformation grids — geoid grids for
vertical datums, NADCON, proprietary grids — without embedding them, so a
transform that needs one needs the file. Resolving those is not covered here. An
asset-path property on the `CoordinateReferenceSystem` prim is the natural way to carry them
and is additive: a CRS without one behaves exactly as described above.

**Units and axes that vary within a stage.** `metersPerUnit` and `upAxis` are
stage-wide in OpenUSD today, and this description reads them as authored. A CRS
that does not declare an up axis leaves it ambiguous, and composing CRSs is
where geospatial will eventually need both to vary. That is an OpenUSD question
rather than one this schema settles, and it is not a small one: every asset
written so far assumes those values are uniform across a stage, so whatever
makes them vary has to say what happens to that content.

### Default Implementation using the "PROJ" library

The OpenSource [PROJ](https://proj.org/) library can be used to create a bidirectional "transformer" object by parsing the USD WKT2 string and defining the target Coordinate Reference System (CRS) by its EPSG code.

The following sample code, using the `pyproj` library (a common Python binding for PROJ), demonstrates how to create a transformer between the Derived CRS with Affine Site Calibration WKT string provided in the document and the target EPSG:10499.

```python
import pyproj

# 1. Define the Coordinate Reference Systems (CRS)

# 1a. Create a CRS object from the USD WKT string.
crs_from = pyproj.CRS.from_wkt(USD_WKT_STRING)

# 1b. Create a CRS object from the target EPSG code.
crs_to = pyproj.CRS.from_string("EPSG:10499")

# 2. Create the Transformer
transformer = pyproj.Transformer.from_crs(crs_from, crs_to)

# Example usage
target_x, target_y, target_z = transformer.transform(usd_x, usd_z, usd_y)
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

A CRS-bound prim's `xformOp:translate` has to be read as an **absolute position**
in the bound CRS, not as a relative offset from its parent. Without that, USD's
standard transform concatenation adds the geospatial coordinates of parent and
child together and the world-space position is nonsense.

**The runtime applies that semantic when it resolves the binding, and the
authored scene carries no opinion about it.** `Runtime behavior` above states it
as a requirement on any implementation.

The alternative reaches the same placement and costs more than it looks.
`Bind()` calling `SetResetXformStack()` **writes `!resetXformStack!` into the
prim's `xformOpOrder` in the layer**, which puts a runtime decision into the
scene description: every consumer of that layer inherits it, changing it later
means rewriting content, and the authoring-time checks lose the data they check
against, because a scene that has already had placement folded into it no longer
carries the CRS intent to check.

### Declaring the dependency

`Runtime behavior` above requires that a stage be able to declare that its correct
placement depends on CRS resolution, without saying how. In OpenUSD that mechanism
already exists: **USD Profiles**, as shipped —
[overview](https://github.com/PixarAnimationStudios/OpenUSD/blob/dev/docs/user_guides/schemas/UsdProfiles/overview.md)
and [ClaimsAPI](https://github.com/PixarAnimationStudios/OpenUSD/blob/dev/docs/user_guides/schemas/UsdProfiles/ClaimsAPI.md).

What is needed is a **capability**, not a profile. Profiles are tagged nodes
representing a pipeline's target; capabilities are the named features a prim relies
on, arranged in a DAG. This schema introduces one capability — resolving a CRS
binding into a placement — and nothing else.

Three properties of the mechanism make it a good fit:

- **The schema declares the implication itself.** An applied API schema names its
  implied capabilities in `customData.extraPlugInfo.impliesCapabilities` in its
  `schema.usda`; `usdGenSchema` propagates that into the library's `plugInfo.json`
  with no separate registration. So applying the binding API is what implies the
  capability, and the declaration follows from the data rather than from an author
  remembering.
- **The degradation vocabulary already says the right thing.** `UsdProfilesClaimsAPI`
  classifies each capability usage as `hard`, `soft` or `enhancement`, where `hard`
  means a consumer lacking the capability will produce incorrect results. That is
  precisely this case, and it is already generic — a consumer can act on `hard`
  without knowing what a coordinate reference system is.
- **It is derivable.** `PopulateCapabilityUsages()` walks a prim's descendants,
  queries the implied capabilities of every applied API schema, and writes the
  merged result. A pipeline step or save hook can produce the declaration; nobody
  hand-authors it.

The declaration lands in `customData` on a prim under the key `profilesInfo`, so a
consumer reads it from the stage root without traversing.

#### The capability identifier

The identifier is not settled here, because it depends on a question larger than
this proposal: what an extension is called before it is ratified. This schema has
been worked in an interest group and is authored by more than one organization, so
neither a core `usd.*` token nor a single-vendor token describes it accurately. The
shipped Profiles documentation shows non-core capabilities using their own
reverse-domain prefixes and participating in the same DAG, which is the pattern to
follow.

Candidates, on the assumption that a preliminary multi-organization tier gets a
marker of its own:

| Candidate | Reading |
|---|---|
| `aousd.prelim.geospatial.crs` | Owner and tier, then a domain node and the feature beneath it |
| `aousd.prelim.crs` | Owner and tier, then a single flat domain token |

The first reserves a `geospatial` node this proposal does not fill — tiles, imagery,
point clouds and level of detail would sit beside CRS — which is either useful
groundwork or an overclaim depending on whether those are expected to follow. The
second claims only what is introduced here.

Whichever is chosen, the capability's predecessor is `usd.core`, and the move to a
ratified identifier later is a deprecation edge in the DAG rather than a break:
Profiles reports `ValidPath`, `Deprecated` and `DeprecationConflict` for exactly
this, so content authored against the preliminary name keeps resolving with a clear
status.

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

The `CRSBindingAPI` is restricted to `UsdGeomXformable` prims.
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
map directly to this proposal's `CoordinateReferenceSystem` and `CRSBindingAPI`.
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
| **D: Typed prim + applied API (this proposal)** | `CoordinateReferenceSystem` prim + `CRSBindingAPI` | Clean separation of definition and usage; one relationship naming a shared definition; inheritance by ancestor walk | Requires new schema registration |

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
   The same question applies to the up axis, and this document
   currently answers it both ways: the WGS 84 ENU example encodes
   Y-up in the CRS, while the stage metadata section recommends
   `upAxis = "Z"` and the scene examples use it.
   A path forward is to decide whether the CRS may declare an up axis
   at all, or whether the stage metadata is always authoritative
   and the CRS is read in its own declared axes.

2. **Axis mapping.**
   Geospatial CRS axis orders vary
   (some are Easting/Northing, others Northing/Easting).
   How does this interact with USD's coordinate conventions?

3. **Third-party library abstraction.**
   [Runtime coordinate transformation](#runtime-coordinate-transformation)
   now gives the signature and says implementations register through
   the OpenUSD plugin system, so the shape is settled.
   A dynamic CRS carries its coordinate epoch in its own WKT
   (see [Appendix A](#appendix-a-wkt-examples)), so that needs no
   parameter of its own.
   What is still open is how failure is reported: the signature returns
   nothing, and a transform that cannot be computed should be surfaced
   rather than quietly skipped.

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

3. **Settle what the transformation abstraction must carry**
   beyond coordinates — epoch, orientation, and failure reporting.

4. **Collaborate with the Geometry Working Group**
   on double-precision geometry support.

5. **Implement the Hydra 2.0 Scene Index Filter**
   for runtime CRS reprojection.

6. **Produce interoperability guidelines**
   for glTF, IFC, CityGML, and 3D Tiles exchange.

7. **Ship standard CRS library files**
   with common EPSG definitions.

8. **Make the sample WKT strings consistent**
   in their use of WKT v2 elements,
   so the same CRS is described the same way throughout.

9. **Demonstrate the accuracy claim**
   by extending the PROJ sample above
   into a worked conversion from USD coordinates
   to a national CRS, with the expected accuracy stated
   and checked.

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

These are reference encodings of common CRS types. The two examples worked
against the case study are in [WKT examples](#wkt-examples) above.

### WGS 84 / UTM zone 11N (EPSG:32611) + EGM2008 height (EPSG:3855)

A projected CRS is two-dimensional on its own. The 3D requirement is met by
compounding it with a vertical CRS, which is what gives the third coordinate a
datum and a unit.

```lisp
COMPOUNDCRS["WGS 84 / UTM zone 11N + EGM2008 height",
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
        ID["EPSG",32611]],
    VERTCRS["EGM2008 height",
        VDATUM["EGM2008 geoid"],
        CS[vertical,1],
            AXIS["gravity-related height (H)",up,
                LENGTHUNIT["metre",1.0]],
        ID["EPSG",3855]]]
```

### Compound CRS: NAD83 / California zone 5 (ftUS) + NAVD88 height

```lisp
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

```lisp
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

```lisp
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

## Appendix C: Reference implementations and measurements

Not part of the proposal. [Runtime behavior](#runtime-behavior) is stated on its
own terms; this appendix records the implementations it was written alongside
and what they measure, so a reader who wants the evidence behind a choice can
find it, and so an independent implementation has something to check itself
against.

The implementations themselves are listed in
[Prototype implementations](#prototype-implementations); the figures here come
from the Hydra 2.0 scene index filter and the stage-level resolver in that
table.

Every figure below comes from a runnable test rather than an estimate. The scene
behind most of them is a building in NAD83 / UTM 17N under a WGS 84 / UTM 30N
anchor, with roughly a 420 m lever from anchor to corner.

| What was measured | Result | Source |
|---|---|---|
| Resolving an anchor as a position only, with no frame | 410 m misplacement | `test_anchor_injection.py` |
| Projected offsets lifted through a topocentric basis instead of the anchor's grid | 4.86 m misplacement | `test_coexist_vs_baked.py` |
| Selecting the composition frame from the source CRS instead | 0.0 mm | `test_coexist_vs_baked.py` |
| A georeferenced leaf authored where a Cartesian child was intended | 418.9 m misplacement | `test_illformed_assets.py` (G1) |
| Absolute float32 geocentric positions at Earth-surface magnitude | 162 mm lost | `test_float32_localization.py` |
| The same geometry as localized float32 offsets under a double-precision anchor | 0.0003 mm | `test_float32_localization.py` |
| A stage with no resolution-required declaration, opened without a resolver | 6,369 km silent misplacement | `test_illformed_assets.py` (G3) |
| The two binding and position carriers, on the same scene | agree to 0.0 mm | `testenv_equivalence.py` |

On agreement between independent runtimes: the C++ Hydra 2.0 scene index and the
Python stage-level resolver share no runtime code, and resolve a 3,526-vertex
railway asset into the same target CRS at median 0.40 mm, worst 0.68 mm, well
inside the accuracy of the survey control behind it. Across five CRS
families and both hemispheres — UTM 18N, UTM 56S, NZTM2000, UTM 17S at the
equator, UTM 33N at 78°N — the same single code path reproduces closed-form
geodesy at 0.0 mm, with the authored EPSG code the only difference between
cases. Both run as continuous tests, on Linux and Windows.
