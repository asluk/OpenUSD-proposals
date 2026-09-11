> Hi Aaron, I am just relaying some internal feedback:
> 
> Can we reconsider deferring the correlation between the BRep and the tessellated mesh? These are the two main concerns:
> 
> **Vendor divergence risk:** If we ship without a standardized correlation mechanism, individual CAD vendors might develop their own conventions to bridge the two representations. Once these conventions become widely adopted and assets rely on them, standardizing later becomes a migration issue rather than a design challenge. The cost of getting this right upfront is significantly lower than the cost of reconciling multiple vendor-specific schemes later.
> 
> **Tessellated mesh may not always be present:** CAD vendors might choose not to ship a tessellated mesh at all if the correlation path is unclear. If the contract for going BRep - mesh isn't clearly defined, the safest choice for a new vendor is to ship BRep only and let consumers tessellate. This is arguably a worse outcome than having a dual representation, and it's the default we'll end up with if we defer.

Hi @dgovil — thanks for surfacing this. Responding for whoever raised it:

Correlation isn't deferred — it's a separate concern from the Brep schema. The companion problem statement's [Coexistence with meshes principle](https://github.com/aousd/OpenUSD-proposals/blob/p1-exact-geometry-problem-statement/proposals/cad_geometry/README.md#principles) already says Brep and Mesh "should be relatable… but neither should require the other," and the mechanism is "separable from the core Brep schema." This proposal's [Open Questions](https://github.com/aousd/OpenUSD-proposals/blob/p2-usdsolid-schema/proposals/UsdSolid/README.md#open-questions) section has a "Brep↔Mesh correlation" entry sketching a candidate from Steve Ghee: an applied schema on the *derived* gprim that back-references the source Brep — the active follow-on path.

Two reasons it sits there:

- **Broader than Brep↔Mesh.** Source/derived pairs aren't unique to CAD — subdivision cages and limit surfaces, sim results and viz meshes, LoD chains. A mechanism designed only for UsdSolid would need rework when the next pair appears. It belongs in its own proposal, seeded by prior discussions.
- **USD composition supports the separation.** The correlation mechanism sits outside UsdSolid's domain entirely; the core Brep schema stays self-contained.

On the two specific concerns:

**Vendor divergence.** The Ghee sketch signals direction. Vendor-prefixed proposals exploring variations are welcome — AOUSD's vendor → multi-vendor → core pattern (cf. [PR #105](https://github.com/PixarAnimationStudios/OpenUSD-proposals/pull/105)) converges rather than fragments. Symmetric risk: continuing to block the Brep schema leaves vendor-specific Brep encodings hardening in `customData` and opaque payloads — a divergence we're already paying for.

**Brep without companion mesh.** The problem statement frames this as a desired direction, not a worse outcome — see ["'Derive on demand' is replacing pre-tessellation"](https://github.com/aousd/OpenUSD-proposals/blob/p1-exact-geometry-problem-statement/proposals/cad_geometry/README.md#why-this-matters-now) and [Hero Use Case 2](https://github.com/aousd/OpenUSD-proposals/blob/p1-exact-geometry-problem-statement/proposals/cad_geometry/README.md#hero-use-case-2-consumer-controlled-data-quality) (consumer-controlled data quality). The schema doesn't preclude shipping both; the question is whether the correlation *contract* must land in v1, and we don't think so. Real data on real stages is how the community converges on the right mechanism.

Best,
@asluk and @umhoefer
