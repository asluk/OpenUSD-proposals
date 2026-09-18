# PR comment — response to Dhruv-relayed feedback on Brep↔Mesh correlation

**Reply to:** https://github.com/PixarAnimationStudios/OpenUSD-proposals/pull/109#issuecomment-4556502142
**Posted as:** https://github.com/PixarAnimationStudios/OpenUSD-proposals/pull/109#issuecomment-4559346157 (2026-05-27)
**Authors:** Aaron Luk, Joe Umhoefer
**Status:** Posted. Draft below preserved for the record.

> Note on delivery: pasting via HTML rich-text into the GitHub composer dropped inline formatting (bullets, bold labels, italics, inline code). The clean path was pasting raw Markdown from `comment-paste.md` into the GitHub edit composer (clipboard pushed with `Get-Content -Raw -Encoding UTF8 … | Set-Clipboard` so UTF-8 chars like em-dash and ↔ survived).

---

Hi Dhruv — thanks for surfacing this. Responding for whoever raised it:

Correlation isn't deferred — it's a separate concern from the Brep schema. The companion problem statement's [Coexistence with meshes principle](https://github.com/aousd/OpenUSD-proposals/blob/p1-exact-geometry-problem-statement/proposals/cad_geometry/README.md#principles) already says Brep and Mesh "should be relatable… but neither should require the other," and the mechanism is "separable from the core Brep schema." This proposal's [Open Questions](https://github.com/aousd/OpenUSD-proposals/blob/p2-usdsolid-schema/proposals/UsdSolid/README.md#open-questions) section has a "Brep↔Mesh correlation" entry sketching a candidate from Steve Ghee: an applied schema on the *derived* gprim that back-references the source Brep — the active follow-on path.

Two reasons it sits there:

- **Broader than Brep↔Mesh.** Source/derived pairs aren't unique to CAD — subdivision cages and limit surfaces, sim results and viz meshes, LoD chains. A mechanism designed only for UsdSolid would need rework when the next pair appears. It belongs in its own proposal, seeded by prior discussions.
- **USD composition supports the separation.** The correlation mechanism sits outside UsdSolid's domain entirely; the core Brep schema stays self-contained.

On the two specific concerns:

**Vendor divergence.** The Ghee sketch signals direction. Vendor-prefixed proposals exploring variations are welcome — AOUSD's vendor → multi-vendor → core pattern (cf. PR #105) converges rather than fragments. Symmetric risk: continuing to block the Brep schema leaves vendor-specific Brep encodings hardening in `customData` and opaque payloads — a divergence we're already paying for.

**Brep without companion mesh.** The problem statement frames this as a desired direction, not a worse outcome — see ["'Derive on demand' is replacing pre-tessellation"](https://github.com/aousd/OpenUSD-proposals/blob/p1-exact-geometry-problem-statement/proposals/cad_geometry/README.md#why-this-matters-now) and [Hero Use Case 2](https://github.com/aousd/OpenUSD-proposals/blob/p1-exact-geometry-problem-statement/proposals/cad_geometry/README.md#hero-use-case-2-consumer-controlled-data-quality) (consumer-controlled data quality). The schema doesn't preclude shipping both; the question is whether the correlation *contract* must land in v1, and we don't think so. Real data on real stages is how the community converges on the right mechanism.

Best,
Aaron and Joe

---

## Drafting notes (not for posting)

- Opens by acknowledging Dhruv as the relay (not the author of the feedback); directs the response at the substance for whoever raised it internally.
- Reframes "deferred" → "separate-but-related" per the slack alignment, without implying personal disagreement with Dhruv.
- Cites the problem statement's Coexistence-with-meshes principle directly (linked to the rendered section) because the position is already on the record there.
- Two structural reasons mirror Joe's framing, adjusted: (a) source/derived is broader, separate-proposal-with-seed-prior-discussions, (b) USD composition supports the separation.
- Vendor-divergence response: Ghee sketch already signals direction; AOUSD vendor→core pattern converges; symmetric counter made *concrete* (customData/opaque payloads we're already paying for) rather than left as a hypothetical "stakeholders making non-standard Brep schemas."
- "Brep without companion mesh" response: cites the problem statement directly to reverse the framing — the relayed feedback calls it "arguably worse," the problem statement explicitly identifies it as a desired trend ("'Derive on demand' is replacing pre-tessellation", Hero Use Case 2). Original heading "Brep-only authoring" was ambiguous (could be read as authoring CAD in USD); renamed for clarity.
- No process commitment at the end (deliberately): spinning up a parallel proposal track in the comment would risk pulling focus from getting UsdSolid itself moving. The position on the comment thread, plus the existing Open Question entry, is enough.
- Avoids naming the source behind the relayed feedback.
- Avoids speaking for Pixar or any specific vendor.
- Final length ~280 words — substantive, dense, no throat-clearing.
