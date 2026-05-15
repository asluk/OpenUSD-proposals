# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

This directory contains an **OpenUSD Enhancement Proposal (OEP)** titled "Separation of Concerns for Identifiers in USD" (version 0.1, DRAFT). It is not a software project — there are no build systems, tests, or package managers. Work here is exclusively editing Markdown documents and `.usda` (USD ASCII) files.

The proposal is submitted as PR #105 to the upstream `PixarAnimationStudios/OpenUSD-proposals` repository. The git remote points to a fork at `perfectproducts/OpenUSD-proposals`.

## Core Problem Being Addressed

USD uses **namespace paths** (e.g., `/World/Building/Floor1`) as its only identifier mechanism. External systems (manufacturing PLM, BIM, robotics, M&E) have their own identifier schemes that conflict with USD path syntax, causing data loss on ingest and forcing ad-hoc workarounds. The proposal advocates **separation of concerns**: keep USD paths for composition, add a standardized mechanism for co-storing external/source identifiers.

Two candidate mechanisms are under discussion:
- **Approach A** — Extend `assetInfo` with stratified sub-dictionaries (e.g., `assetInfo["sourceId"]["dpp"]["serial"]`)
- **Approach B** — Applied schema with typed properties (enables validation, discovery, schema versioning)

## File Map

| File | Role |
|------|------|
| `README.md` | The proposal itself — problem statement, use cases, design principles, open questions, candidate mechanisms, next steps |
| `dpp_openusd_bidirectional_mapping.md` | Concrete technical example: bidirectional mapping between OpenUSD and the IDTA 02035-1 Digital Battery Passport (AAS standard). Defines `DppNameplateAPI` and `BatteryNameplateAPI` applied schemas. |
| `dpp_sample.usda` | Working USDA example file showing the proposed `sourceId:dpp:*` encoding on a fictional battery unit (`Battery_A12345X75EN`), with illustrative schema class definitions |
| `product_passport_1775058840764.pdf` | Reference: IDTA 02035-1 Digital Battery Passport specification |

## Proposal Architecture

The README is structured in deliberate layers:

1. **Problem framing** — why the namespace-path-as-identifier conflation exists and why it matters now (displayName deprecation, USD expanding beyond VFX)
2. **Cross-industry validation** — AECO (room numbers, IFC GlobalIds), Manufacturing/PLM (part numbers, serial numbers, BOMs), M&E (asset DB IDs, shot IDs), Robotics (URDF/ROS provenance, OPC UA NodeIds)
3. **Design principles** (8) and **open questions** (8) — the criteria any solution must satisfy
4. **Candidate mechanisms** with explicit trade-offs — deliberately left unresolved pending community consensus
5. **Relationship to other proposals** — Unicode Identifiers, Transcoding, Revise Layer Metadata, UI Hints (displayName deprecation)

The `dpp_openusd_bidirectional_mapping.md` and `dpp_sample.usda` are companion artifacts that ground the abstract proposal in a real regulatory standard (EU Battery Regulation 2023/1542).

## Key Concepts and Terminology

- **Source identifier** — an identifier assigned by an external system (PLM, BIM, etc.) to track an asset; may be opaque, composite, or contain characters invalid in USD paths
- **USD namespace identifier** — a prim path used for composition and hierarchy navigation; must follow USD naming rules; unique per stage instance
- **`assetInfo`** — existing USD prim metadata dictionary (under `UsdModelAPI`) already used for asset tracking; Approach A proposes extending this
- **Applied schema** — a USD schema that can be applied to any prim at runtime; Approach B proposes introducing one for source identifiers
- **`sourceId`** — the proposed custom attribute namespace prefix used in the USDA example (e.g., `sourceId:dpp:serialNumber`)
- **AAS** — Asset Administration Shell, IEC 63278 standard used in manufacturing digital twins; the DPP mapping document translates between AAS submodels and USD

## Governance Context

The proposal follows the OpenUSD proposal lifecycle: **Draft → Finalizing → Published → Implemented**. Editing should preserve the DRAFT status and the 8 core design principles unless explicitly advancing toward a solution. The "Likely direction" and "Open questions" sections are intentionally open — do not resolve them without explicit instruction. Appendix A discloses AI-assisted drafting; maintain that transparency.
