# PR #81 comment drafts

Goal: very friendly, short, one clear ask per comment. The author shouldn't feel buried under a writeup posted in response to their own writeup. Issue #7 link demoted to a single optional pointer in the anchor comment, framed as for-the-curious.

The Issue #7 link will, on posting, create the *intended* upstream cross-reference. That is fine; the no-cross-reference scrubbing only applies to the WIP Issue body itself.

---

## Anchor comment (top-level on PR)

The proposal lands a real gap in OpenUSD, and the multi-domain decomposition (independent activation per domain over a shared hierarchy, with the parent-active and domain-independence axioms) is a meaningful step beyond what FBX, Maya, Unreal LODGroups, glTF MSFT_lod, or X3D LOD have offered.

A few small framing suggestions inline — they cluster around scoping the schema's slot in the broader LOD landscape so adjacent paradigms (industrial streaming, AECO, geographic, splats) have clear room to land later as peer schemas, and tightening one example that overlaps with AECO terminology.

(Side note for anyone curious about the cross-paradigm context — how 3D Tiles, Nanite, Gaussian-splat octree LOD, CityGML 3.0, BIMForum LOD, and ISO 19650 LOIN sit relative to this proposal — there's a longer writeup at [asluk/OpenUSD-proposals#7](https://github.com/asluk/OpenUSD-proposals/issues/7). Optional reading; the inline comments stand on their own.)

---

## Comment 1 — Summary

**Anchor:** `proposals/level-of-detail/README.md`, the Summary paragraph beginning *"This proposal defines an API schema for managing Level of Detail..."*

---

Since the Summary sets the mental model for readers arriving from BIM, GIS, or streaming/capture backgrounds, naming the schema's category up front (something like *view-driven runtime LOD*) might help avoid the unqualified "LOD" being read as universal. One possible shape:

> This proposal defines an API schema for **view-driven runtime LOD** in USD compositions — the category of LOD in which engines and applications switch between mutually-exclusive asset representations based on configurable criteria such as distance, screen size, performance heuristics, or explicit authoring. The schema standardizes this category, enabling runtime composition, hierarchical evaluation, and multi-domain decoupling within the M&E / runtime-engine vertical, while maintaining deterministic behavior. Other LOD verticals (industrial streaming/refinement, AECO information-maturity, geographic-semantic) are addressed by separate peer schemas and are out of scope here.

Just one option among several.

---

## Comment 2 — Problem Statement

**Anchor:** `proposals/level-of-detail/README.md`, the Problem Statement bullet list beginning *"USD lacks a standardized runtime LOD representation..."*

---

Pairs with the Summary suggestion: scoping the gap explicitly to the M&E / runtime-engine vertical, and introducing a two-level taxonomy — *vertical* (industry axis: M&E, industrial, AECO, geographic) and *domain* (within-vertical subsystems: graphics, physics, audio). The proposal's existing "domain" language stays clean, and "vertical" gives a vocabulary for cross-industry scoping. Possible shape:

> Within the M&E / runtime-engine **vertical**, USD lacks a standardized LOD representation. Current workarounds (variants, payloads, custom schemas) do not provide:
> - Standardized interchange of LOD data within the vertical.
> - Multiple LOD **domains** (graphics, physics, audio, ...) within the vertical simultaneously composed — e.g., cross-fading geometry while switching physics LOD.
> - Runtime evaluation and deterministic selection.
>
> Other LOD verticals (industrial streaming/refinement, AECO information-maturity, geographic-semantic) have their own gaps and are addressed by separate peer schemas — see Excluded Topics.

---

## Comment 3 — CAD/Engineering use case

**Anchor:** `proposals/level-of-detail/use-cases.md`, the "CAD/Engineering Visualization" section.

---

The CAD/Engineering example uses distance-based switching of mechanical assemblies, which doesn't quite exercise the schema's strengths (multi-domain coordination, hierarchical heterogeneous evaluation), and overlaps with the BIMForum Level of Development reading that BIM-side readers may default to on a `MechanicalAssembly`. The two flagship examples (City→Buildings→Rooms; multi-domain vehicle) carry the illustrative weight without that exposure — could be worth dropping this one.

Pairs with one possible addition to "Excluded Topics" — naming AECO model maturity explicitly as out of scope so the AECO IG has clean room for a peer schema later:

> **AECO/BIM model maturity**: This proposal addresses the M&E / runtime vertical of LOD. AECO/BIM "Level of Development" (per [BIMForum's 2025 LOD Specification](https://bimforum.org/resource/lod-level-of-development-lod-specification/)) and "Level of Information Need" (per [ISO 19650 / DIN EN 17412-1](https://www.symetri.co.uk/insights/blog/iso-19650-level-of-information-need-the-elephant-in-the-room/)) are different categories of "LOD" that exist as active industry standards. They are out of scope of this schema and are expected to be addressed by separate peer schemas via the AECO IG.

---

## §6.3 — dropped

The "Renderer-agnostic" → "Engine-agnostic within vertical" bullet rewrite is the smallest-leverage of the four §6 items, and posting a fourth comment risks tipping the volume over the friendly-feedback line. Skipped here. If the author lands the Summary and Problem Statement reframes, the "renderer-agnostic" line becomes inconsistent on its own and is a likely natural fix as part of that pass.
