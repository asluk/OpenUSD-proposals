---
orphan: true
---
# Conceptual Data Mapping: IDTA 02035-1 Digital Battery Passport (Part 1) ↔ OpenUSD (Bidirectional)

```{important}
**{octicon}`tag;1em` Document Version:** {bdg-secondary}`0.1.0`
<br>**{octicon}`calendar;1em` Last Update:** {bdg-secondary}`2026-04-02`
```

## Introduction

### Overview

This document defines a **bidirectional** mapping between the **IDTA 02035-1 Digital Battery Passport – Part 1: Digital Nameplate** (DBP Nameplate) and OpenUSD. It covers both translation directions:

- **DBP → USD**: How AAS Submodel data is encoded in a USD prim using `DppNameplateAPI` and `BatteryNameplateAPI` applied schemas.
- **USD → DBP**: How USD prim data is read back and reconstructed into a conformant AAS `BatteryNameplate` Submodel instance.

The one-way (DBP → USD) mapping is covered in detail in the companion document [`dpp_to_openusd_mapping.md`](./dpp_to_openusd_mapping.md). This document focuses on the additional concerns introduced by the reverse direction: round-trip fidelity, data that cannot survive the round-trip, and USD-native concepts that have no DBP equivalent.

```{note}
**Dependency on the Source Identifier proposal.** Several mappings in this document — in particular `URIOfTheProduct`, `ManufacturerIdentifier`, `EUDeclarationOfConformity`, and `ResultsOfTestReportsProvingCompliance` — use a `sourceId:dpp:*` source identifier mechanism to store external AAS identifiers verbatim alongside USD attributes. This mechanism is defined in the [Identifier Separation of Concerns proposal](./README.md) and is not yet part of the OpenUSD standard. The mappings in this document are written on the assumption that the proposal will be accepted and standardized. Where `assetInfo` sub-dictionaries or `asset[]` attributes are mentioned as alternatives, these are fallback encodings for toolchains that predate source id support.
```

### References

#### DBP Reference

| Version | Reference Documents |
|---|---|
| 1.0 (February 2026) | IDTA 02035-1: Digital Battery Passport – Part 1: Digital Nameplate |
| — | DIN DKE SPEC 99100: Requirements for data attributes of the battery passport (February 2025) |
| — | EU Battery Regulation (EU) 2023/1542, Article 77 and Annex XIII |
| — | IDTA-02006: Digital Nameplate for Industrial Equipment 3.0 (parent template) |
| — | IDTA-01001-3-1-2: Specification of the Asset Administration Shell Part 1: Metamodel (V3.1.2) |

#### OpenUSD Reference

| Version | Reference Documents |
|---|---|
| 24.08 | [OpenUSD C++ and Schema Documentation](https://openusd.org/release/api/index.html), [OpenUSD Github Repository](https://github.com/PixarAnimationStudios/OpenUSD), [USD Terms and Concepts](https://openusd.org/release/glossary.html) |

### General Assumptions and Constraints

- **Two-way mapping** (DBP ↔ USD). Round-trip fidelity is a goal but is not fully achievable; lossy fields are explicitly documented.
- The DBP Nameplate is encoded in USD using two applied API schemas: `DppNameplateAPI` (generic nameplate fields from IDTA-02006) and `BatteryNameplateAPI` (battery-specific additions from IDTA-02035). See [`dpp_to_openusd_mapping.md`](./dpp_to_openusd_mapping.md) for the full DBP → USD direction.
- **USD → DBP** reconstruction assumes the USD prim has both schemas applied. A prim with only `DppNameplateAPI` cannot produce a complete `BatteryNameplate` submodel instance; it can produce a partial IDTA-02006 nameplate.
- **AAS structural context** (Asset, AssetAdministrationShell, Submodel containment hierarchy) is not represented in USD. The USD → DBP direction produces only a Submodel instance; the surrounding AAS envelope must be provided by the receiving system.
- **MLP (MultiLanguageProperty)** fields suffer a partial round-trip: USD stores only the primary string value. Language variants stored in `customData` survive, but depend on the USD tool respecting that convention.
- **semanticIds** are preserved in `customData` for provenance. They survive round-trip only if USD tooling does not strip `customData`.
- **USD-native concepts** (composition arcs, time-varying attributes, variant sets, relationships) have no DBP equivalent and are silently dropped on USD → DBP export. See [USD-Native Concepts](#usd-native-concepts).
- USD `token` values for `dpp:lifeCycleStage` map to ECLASS IRDIs via the lookup table in [Appendix A](#appendix-a-lifecycle-stage-irdi-token-mapping). This lookup is required for a conformant USD → DBP export.

### Definitions, Acronyms, Abbreviations

| Term or Abbreviation | Description |
|---|---|
| AAS | Asset Administration Shell – the IDTA/Industrie 4.0 digital twin framework |
| DBP | Digital Battery Passport (IDTA 02035-1 series) |
| SMT | Submodel Template – a standardized AAS submodel definition |
| SM | Submodel – top-level container of related data elements in AAS |
| SMC | SubmodelElementCollection – an unordered named group of SubmodelElements |
| SML | SubmodelElementList – an ordered list of SubmodelElements of the same type |
| MLP | MultiLanguageProperty – a Property with per-language-code string values |
| IRDI | International Registration Data Identifier – semantic ID format (IEC CDD/ECLASS) |
| semanticId | AAS mechanism for linking a SubmodelElement to a concept definition |
| `DppNameplateAPI` | Applied USD API schema for generic DPP nameplate fields (IDTA-02006 origin) |
| `BatteryNameplateAPI` | Applied USD API schema for battery-specific nameplate fields (IDTA-02035 additions) |
| `MarkingAPI` | Applied USD API schema for a single marking entry |
| `assetInfo` | USD metadata dictionary for asset-level identification metadata |
| `customData` | USD metadata dictionary for arbitrary user/domain data on a prim |
| Round-trip | A DBP → USD → DBP transformation; data survives if the final DBP instance is equivalent to the original |
| Lossless | A field that survives round-trip without data loss |
| Lossy | A field that loses information during round-trip (e.g., language variants in MLP) |
| Dropped | Data that is discarded and cannot be recovered during round-trip |

---

## Concepts

### High-Level Concept Mapping

| DBP (AAS) | Schema | OpenUSD | Round-trip | Notes |
|---|---|---|---|---|
| [BatteryNameplate (Submodel)](#batterynameplate-submodel) | both | Prim with `DppNameplateAPI` + `BatteryNameplateAPI` | Partial | AAS envelope (Asset, AAS) not round-tripped; Submodel instance only |
| [URIOfTheProduct](#urioftheproduct) | `DppNameplateAPI` | `sourceId:dpp:uriOfTheProduct` (string) + `dpp:uriOfTheProduct` (asset) | Lossless | Source id entry is the primary cross-system identifier; `assetInfo["identifier"]` written as fallback for tools without source id support |
| [ManufacturerName](#manufacturername) | `DppNameplateAPI` | `dpp:manufacturerName` (string) | Lossy | Primary language value only; language tag lost |
| [AddressInformation](#addressinformation) | `DppNameplateAPI` | `dpp:address:*` attributes or child prim | Lossless | All mandatory fields preserved |
| [SerialNumber](#serialnumber) | `DppNameplateAPI` | `dpp:serialNumber` (string) | Lossless | Direct string mapping |
| [DateOfManufacture](#dateofmanufacture) | `DppNameplateAPI` | `dpp:dateOfManufacture` (string) | Lossless | ISO 8601 string preserved |
| [DateOfPuttingIntoService](#dateofputtingintoservice) | `DppNameplateAPI` | `dpp:dateOfPuttingIntoService` (string) | Lossless | ISO 8601 string preserved; absent if not authored |
| [UniqueFacilityIdentifier](#uniquefacilityidentifier) | `DppNameplateAPI` | `dpp:uniqueFacilityIdentifier` (string) | Lossless | Direct string mapping |
| [Markings (SML)](#markings) | `DppNameplateAPI` | Child prims under `Markings/` scope | Lossy | SML ordering not guaranteed from child prim iteration |
| [LifeCycleStage](#lifecyclestage) | `BatteryNameplateAPI` | `dpp:lifeCycleStage` (token) | Lossless | Token ↔ IRDI via lookup table ([Appendix A](#appendix-a-lifecycle-stage-irdi-token-mapping)) |
| [OperatorIdentifier](#operatoridentifier) | `BatteryNameplateAPI` | `dpp:operatorIdentifier` (string) | Lossless | Direct string mapping |
| [ManufacturerIdentifier](#manufactureridentifier) | `BatteryNameplateAPI` | `sourceId:dpp:manufacturerIdentifier` (string) + `dpp:manufacturerIdentifier` (string) | Lossless | Source id entry is the primary cross-system identifier; `assetInfo["name"]` must not be used (display-name semantics, deprecation path) |
| [EUDeclarationOfConformity](#eudeclarationofconformity) | `BatteryNameplateAPI` | `sourceId:dpp:euDeclarationOfConformityIds` (string[]) primary; `dpp:euDeclarationOfConformity` (asset[]) for URI/path cases | Lossless | Source id string array preserves verbatim AAS document identifiers; `asset[]` written additionally when identifiers are resolvable URIs |
| [ResultsOfTestReportsProvingCompliance](#resultsoftestreportsprovingcompliance) | `BatteryNameplateAPI` | `sourceId:dpp:testReportComplianceIds` (string[]) primary; `dpp:testReportCompliance` (asset[]) for URI/path cases | Lossless | Same as above |
| — | — | [Composition arcs](#composition-arcs) | Dropped | No DBP equivalent |
| — | — | [Time-varying attributes](#time-varying-attributes) | Dropped | No DBP equivalent |
| — | — | [Variant sets](#variant-sets) | Dropped | No DBP equivalent |
| — | — | [Relationships](#relationships) | Dropped | No DBP equivalent |

---

### BatteryNameplate (Submodel)

#### DBP → USD

A `BatteryNameplate` Submodel instance is encoded as a USD prim with both `DppNameplateAPI` and `BatteryNameplateAPI` applied. The AAS `semanticId` is stored in `customData`. See [`dpp_to_openusd_mapping.md § BatteryNameplate`](./dpp_to_openusd_mapping.md#batterynameplate-submodel) for the full schema definitions and usage example.

#### USD → DBP

To reconstruct a `BatteryNameplate` Submodel from a USD prim:

1. **Identify the prim**: The prim must have both `DppNameplateAPI` and `BatteryNameplateAPI` in its applied schemas. A prim with only `DppNameplateAPI` produces an IDTA-02006 nameplate, not a `BatteryNameplate`.
2. **Construct the Submodel envelope**:
   - `idShort`: `BatteryNameplate`
   - `semanticId`: `https://admin-shell.io/idta/digitalbatterypassport/nameplate/1/0/Nameplate` (from `customData["aas:submodelSemanticId:battery"]` if present; otherwise use the fixed value)
3. **Populate SubmodelElements** from prim attributes per the per-field mappings below.
4. **AAS envelope** (Asset, AssetAdministrationShell): cannot be reconstructed from USD alone. The receiving AAS system must supply this.

#### Round-trip Fidelity

| AAS Element | Survives Round-trip? | Notes |
|---|---|---|
| Submodel idShort | Yes | Fixed value `BatteryNameplate` |
| Submodel semanticId | Yes | Stored in `customData`; survives if not stripped |
| SubmodelElement values | See per-field table | — |
| Asset, AAS hierarchy | No | Not encoded in USD |

---

### URIOfTheProduct

#### DBP → USD

`URIOfTheProduct` is written to three locations, in order of preference:

1. **`sourceId:dpp:uriOfTheProduct`** (string) — the primary cross-system identifier entry. Stores the URI verbatim as a plain string, free from SdfAssetPath resolution semantics.
2. **`dpp:uriOfTheProduct`** (asset) — the domain-specific attribute, kept for schema completeness and USD tools that resolve asset paths.
3. **`assetInfo["identifier"]`** — written as a fallback for USD tools that predate source id support. `assetInfo["identifier"]` is limited to model-root prims and its keys are oriented toward Pixar's asset management workflows; it is not the authoritative location.

#### USD → DBP

Read in priority order: `sourceId:dpp:uriOfTheProduct` → `dpp:uriOfTheProduct` → `assetInfo["identifier"]`. Write to AAS `Property URIOfTheProduct` with `valueType = xs:anyURI`.

#### Round-trip

| | DBP → USD | USD → DBP |
|---|---|---|
| Value | `xs:anyURI` → string (source id) + asset (attribute) | string value → `xs:anyURI` |
| Fidelity | Lossless | Lossless |
| Fallback chain | — | `sourceId:dpp:uriOfTheProduct` → `dpp:uriOfTheProduct` → `assetInfo["identifier"]` |

---

### ManufacturerName

#### DBP → USD

The primary language string value of the MLP is written to `dpp:manufacturerName`. If language variants are important, they are written to `customData["dpp:manufacturerName:i18n"]` as a dictionary keyed by ISO 639 language code.

#### USD → DBP

Read `dpp:manufacturerName` (string). Reconstruct as MLP with a single entry. If `customData["dpp:manufacturerName:i18n"]` is present, reconstruct full MLP from the dictionary.

#### Round-trip

| | DBP → USD | USD → DBP |
|---|---|---|
| Primary value | Lossless | Lossless |
| Language variants | Lossy — written to `customData` only | Recovered only if `customData` preserved |

```usda
# DBP → USD encoding with language variants preserved
string dpp:manufacturerName = "Muster AG"
customData = {
    dictionary "dpp:manufacturerName:i18n" = {
        string "de" = "Muster AG"
        string "en" = "Muster AG"
    }
}
```

---

### AddressInformation

#### DBP → USD

Address fields are written as `dpp:address:*` namespaced attributes on the prim (flat encoding) or as a child `Scope` prim. The flat encoding is recommended for round-trip; child prim encoding requires agreement on prim naming.

#### USD → DBP

Read `dpp:address:*` attributes. Reconstruct as SMC `AddressInformation` using the drop-in from IDTA 02002-1. Map each attribute to the corresponding MLP SubmodelElement.

#### Round-trip

| DBP Field | USD Attribute | Fidelity |
|---|---|---|
| Street | `dpp:address:street` | Lossless |
| Zipcode | `dpp:address:zipcode` | Lossless |
| CityTown | `dpp:address:cityTown` | Lossless |
| NationalCode | `dpp:address:nationalCode` | Lossless |
| Email | `dpp:address:email` | Lossless |
| AddressOfAdditionalLink | `dpp:address:additionalLink` | Lossless |
| Language variants (MLP) | `customData` | Lossy — same as ManufacturerName |

---

### SerialNumber

#### DBP → USD

Written to `dpp:serialNumber` (string).

#### USD → DBP

Read `dpp:serialNumber`. Write to AAS `Property SerialNumber` with `valueType = xs:string`.

#### Round-trip: Lossless

---

### DateOfManufacture

#### DBP → USD

Written to `dpp:dateOfManufacture` as ISO 8601 string `YYYY-MM-DD`.

#### USD → DBP

Read `dpp:dateOfManufacture`. Validate ISO 8601-1:2020 format. Write to AAS `Property DateOfManufacture` with `valueType = xs:date`.

#### Round-trip: Lossless (provided the string is valid ISO 8601)

---

### DateOfPuttingIntoService

#### DBP → USD

Written to `dpp:dateOfPuttingIntoService` as ISO 8601 string if present (cardinality 0..1). If absent in DBP, the attribute is not authored in USD.

#### USD → DBP

If `dpp:dateOfPuttingIntoService` is authored and non-empty, write to AAS `Property DateOfPuttingIntoService`. If absent or empty, omit the optional SubmodelElement.

#### Round-trip: Lossless

---

### UniqueFacilityIdentifier

#### DBP → USD

Written to `dpp:uniqueFacilityIdentifier` (string).

#### USD → DBP

Read `dpp:uniqueFacilityIdentifier`. Write to AAS `Property UniqueFacilityIdentifier` with `valueType = xs:string`.

#### Round-trip: Lossless

---

### Markings

#### DBP → USD

Each `Markings__NN__` SMC is written as a child prim under a `Markings` Scope, with `MarkingAPI` applied. Prim names are constructed as `Marking_NN` (zero-padded index) to preserve original SML ordering.

```usda
def Scope "Markings" {
    def Scope "Marking_00" (prepend apiSchemas = ["MarkingAPI"]) { ... }
    def Scope "Marking_01" (prepend apiSchemas = ["MarkingAPI"]) { ... }
}
```

#### USD → DBP

1. Find the child prim named `Markings` (Scope).
2. Collect all child prims that have `MarkingAPI` applied.
3. **Sort by prim name** to recover the original SML order (relies on the `Marking_NN` naming convention).
4. For each, construct a `Markings__NN__` SMC with the fields below.

#### Round-trip

| DBP Field | USD Attribute | Fidelity |
|---|---|---|
| MarkingName | `marking:name` (token) | Lossless if IRDI token; lossy if free-text token normalised |
| DesignationOfCertificateOrApproval | `marking:certificateDesignation` (string) | Lossless |
| IssueDate | `marking:issueDate` (string) | Lossless |
| ExpiryDate | `marking:expiryDate` (string) | Lossless |
| MarkingFile | `marking:file` (asset) | Lossless (path preserved) |
| MarkingAdditionalText | `marking:additionalText` (string[]) | Lossless |
| SML ordering | Child prim sort by `Marking_NN` name | Lossless if naming convention respected; otherwise ordering lost |

---

### LifeCycleStage

> **Schema:** `BatteryNameplateAPI`

#### DBP → USD

Map the ECLASS IRDI value to the corresponding USD token using the table in [Appendix A](#appendix-a-lifecycle-stage-irdi-token-mapping). Write to `dpp:lifeCycleStage`.

#### USD → DBP

Read `dpp:lifeCycleStage` (token). Reverse-map to the ECLASS IRDI using [Appendix A](#appendix-a-lifecycle-stage-irdi-token-mapping). Write to AAS `Property LifeCycleStage` with `valueType = xs:string` and the IRDI as the value.

#### Round-trip: Lossless (via lookup table)

---

### OperatorIdentifier

> **Schema:** `BatteryNameplateAPI`

#### DBP → USD

Written to `dpp:operatorIdentifier` (string) if present (cardinality 0..1).

#### USD → DBP

If `dpp:operatorIdentifier` is authored and non-empty, write to AAS `Property OperatorIdentifier`. If absent, omit the optional SubmodelElement.

#### Round-trip: Lossless

---

### ManufacturerIdentifier

> **Schema:** `BatteryNameplateAPI`

#### DBP → USD

Written to two locations:

1. **`sourceId:dpp:manufacturerIdentifier`** (string) — the primary cross-system identifier entry, making the formal manufacturer identifier discoverable without prior knowledge of the `dpp:` schema.
2. **`dpp:manufacturerIdentifier`** (string) — the domain-specific attribute, kept for schema completeness.

Do **not** mirror to `assetInfo["name"]`. That field carries display-name semantics and is on a deprecation path following the UI Hints migration (`displayName` moved to `uiHints` dictionary). Using it to carry a formal manufacturer identifier conflates identification with presentation. Older content that used `assetInfo["name"]` as a workaround should be migrated to the source id entry.

#### USD → DBP

Read `dpp:manufacturerIdentifier` as the authoritative value. If absent, read `sourceId:dpp:manufacturerIdentifier`. Write to AAS `Property ManufacturerIdentifier` with `valueType = xs:string`.

#### Round-trip

| | DBP → USD | USD → DBP |
|---|---|---|
| Value | Direct string | Direct string |
| Fidelity | Lossless | Lossless |
| Fallback | — | `sourceId:dpp:manufacturerIdentifier` if `dpp:manufacturerIdentifier` absent |

---

### EUDeclarationOfConformity

> **Schema:** `BatteryNameplateAPI`

#### DBP → USD

AAS stores document identifiers as opaque strings referencing documents in the Handover Documentation submodel (IDTA-02035-2). These identifiers are not necessarily URIs or file paths — they may be internal AAS document reference keys.

Write to two locations:

1. **`sourceId:dpp:euDeclarationOfConformityIds`** (string[]) — the primary encoding. Stores the verbatim AAS document identifier strings, free from SdfAssetPath path-resolution semantics.
2. **`dpp:euDeclarationOfConformity`** (asset[]) — written additionally only when the identifiers are resolvable URIs or file paths, so that USD tools can follow the asset reference. If the identifiers are opaque keys, this attribute is omitted or left empty to avoid false path resolution.

#### USD → DBP

Read `sourceId:dpp:euDeclarationOfConformityIds` (string[]) as the authoritative source. If absent, fall back to `dpp:euDeclarationOfConformity` (asset[]) and extract the string value of each SdfAssetPath. Write to AAS `SML EUDeclarationOfConformity` as a list of `Property DocumentIdentifier` elements.

#### Round-trip

| | Fidelity | Notes |
|---|---|---|
| Document identifier values | Lossless | Verbatim strings preserved via `sourceId:dpp:euDeclarationOfConformityIds` |
| Document identifier values (fallback path) | Lossy | If only `asset[]` is present, opaque AAS keys may be mangled by SdfAssetPath resolution |
| List length | Lossless | Array length preserved |

---

### ResultsOfTestReportsProvingCompliance

> **Schema:** `BatteryNameplateAPI`

Identical encoding and round-trip behaviour to [EUDeclarationOfConformity](#eudeclarationofconformity). Primary attribute: `sourceId:dpp:testReportComplianceIds` (string[]); fallback: `dpp:testReportCompliance` (asset[]) for resolvable URI/path cases.

---

## USD-Native Concepts

These concepts exist in USD but have no equivalent in the DBP/AAS metamodel. They are dropped when exporting from USD to DBP.

### Composition Arcs

USD supports `references`, `payloads`, `inherits`, `specializes`, and `over` composition arcs. These define how layer stacks are assembled into a scene. DBP has no equivalent; AAS Submodels are monolithic documents.

**On USD → DBP export:** Flatten the composed prim (resolve all composition arcs) before reading attribute values. The flattened values are exported; the composition structure is dropped.

### Time-Varying Attributes

USD attributes can carry time samples (values at specific time codes). DBP properties are static.

**On USD → DBP export:** Use the default value (`UsdAttribute::Get()` with `UsdTimeCode::Default()`). If no default value is authored, use the value at `UsdTimeCode(0)`. If neither is present, the field is treated as unset.

### Variant Sets

USD variant sets allow a prim to carry multiple alternative representations selectable at runtime. DBP has no equivalent.

**On USD → DBP export:** Export the currently selected variant only. Other variants are dropped.

### Relationships

USD relationships are typed connections between prims. DBP uses `ReferenceElement` for inter-submodel links, but the DBP Nameplate submodel contains no relationship-type SubmodelElements.

**On USD → DBP export:** Dropped. If a USD relationship encodes information that should map to a DBP field, it must be modelled as an attribute instead.

---

## Appendices

### Appendix A: LifeCycleStage IRDI ↔ Token Mapping

This table is required for lossless round-trip of `LifeCycleStage`.

| ECLASS IRDI (DBP value) | USD Token (`dpp:lifeCycleStage`) |
|---|---|
| `0173-1#07-ACC020#001` | `original` |
| `0173-1#07-ACC021#001` | `repurposed` |
| `0173-1#07-ACC022#001` | `re-used` |
| `0173-1#07-ACC023#001` | `remanufactured` |
| `0173-1#07-ACC024#001` | `waste` |

**DBP → USD**: look up IRDI, write token.  
**USD → DBP**: look up token, write IRDI. If the token value is not in this table (e.g., a free-text value), the USD → DBP export must fail validation or write a best-effort string with a warning.

---

### Appendix B: Round-trip Fidelity Summary

| DBP Field | Direction | Fidelity | Loss / Condition |
|---|---|---|---|
| URIOfTheProduct | Both | Lossless | Primary: `sourceId:dpp:uriOfTheProduct`; fallback chain: `dpp:uriOfTheProduct` → `assetInfo["identifier"]` |
| ManufacturerName (primary value) | Both | Lossless | — |
| ManufacturerName (language variants) | Both | Lossy | Preserved only via `customData` convention |
| AddressInformation (all fields) | Both | Lossless | — |
| SerialNumber | Both | Lossless | — |
| DateOfManufacture | Both | Lossless | String must be valid ISO 8601 |
| DateOfPuttingIntoService | Both | Lossless | Absent field handled correctly in both directions |
| UniqueFacilityIdentifier | Both | Lossless | — |
| Markings (field values) | Both | Lossless | — |
| Markings (SML ordering) | Both | Lossless | Requires `Marking_NN` naming convention |
| LifeCycleStage | Both | Lossless | Requires IRDI ↔ token lookup table (Appendix A) |
| OperatorIdentifier | Both | Lossless | Absent field handled correctly in both directions |
| ManufacturerIdentifier | Both | Lossless | Primary: `sourceId:dpp:manufacturerIdentifier`; `assetInfo["name"]` must not be used |
| EUDeclarationOfConformity | Both | Lossless | Verbatim identifiers via `sourceId:dpp:euDeclarationOfConformityIds`; fallback `asset[]` is lossy for opaque AAS keys |
| ResultsOfTestReportsProvingCompliance | Both | Lossless | Verbatim identifiers via `sourceId:dpp:testReportComplianceIds`; same fallback caveat |
| semanticIds | Both | Conditional | Survive only if `customData` is not stripped by USD tooling |
| AAS Asset / AAS hierarchy | DBP → USD | Dropped | Not encoded in USD |
| Composition arcs | USD → DBP | Dropped | Flatten before export |
| Time-varying attributes | USD → DBP | Dropped | Use default value |
| Variant sets | USD → DBP | Dropped | Export selected variant only |
| Relationships | USD → DBP | Dropped | No DBP Nameplate equivalent |

---

### Appendix C: AAS-to-USD and USD-to-AAS Type Mapping

| AAS Type | USD Type | DBP → USD | USD → DBP | Round-trip Fidelity |
|---|---|---|---|---|
| `xs:string` | `string` | Direct | Direct | Lossless |
| `xs:anyURI` | `asset` (SdfAssetPath) | URI as asset path string | Asset path string as URI | Lossless |
| `xs:date` | `string` | ISO 8601 string | Parse ISO 8601 string to `xs:date` | Lossless if valid ISO 8601 |
| `MLP` (primary value) | `string` | Primary string | Single-entry MLP | Lossless for primary value |
| `MLP` (all variants) | `string` + `customData` dict | Primary + i18n dict | Reconstruct from dict if present | Lossy if `customData` stripped |
| `File` | `asset` | File path as asset | Asset path as file path | Lossless |
| ECLASS IRDI (enum) | `token` | IRDI → token via lookup | Token → IRDI via lookup | Lossless with lookup table |
| `SMC` (flat fields) | Namespaced attributes | `ns:field` attributes | Read `ns:field` attributes | Lossless |
| `SML` (ordered, complex elements) | Child prims with index-based names | `Scope_NN` child prims | Sort child prims by name | Lossless if naming convention respected |
| `SML` (ordered, scalar list) | Array attribute | `type[]` attribute | Array to list of Properties | Lossless |
