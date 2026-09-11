# PR 106 (Authorship Metadata) — comment drafts

Goal: three line-anchored comments on PR 106. Each is a single tradeoff-acknowledgment ask — not a redesign, not a new section. The author can drop each one into the proposal where the relevant material already lives.

Spiff has the schema mechanics covered in his inline review (10 comments + summary, 2026-05-08/09); Dhruv replied to all 10 on 2026-05-12 with concrete change intentions on several. Our angle is complementary: cross-vertical scope, and seams with two in-flight Aaron proposals (source-identifiers PR 105 and IP protection draft).

No top-level anchor comment; the three line-anchored comments stand alone. No companion Issue. No PDF build pipeline. Volume kept low per [[feedback_review_volume_author_empathy]].

---

## Comment 1 — Scope to creative authorship

**Anchor:** `proposals/authorship/README.md`, the **Non-Goals** section, immediately after the tamper-resistance paragraph.

---

Worth considering a scope statement here, alongside the tamper-resistance non-goal. The current shape of the schema — `producer` reverse-DNS, `attribution`, IPTC vocabulary — is well-suited to creative authorship: human artists, AI generators, DCC tools, photogrammetry-as-asset-creation. Naming that scope explicitly would reserve clean room for adjacent provenance work (sensor capture, engineering/PLM lineage, simulation provenance for synthetic data) to land later as peer schemas, rather than being pulled into `AuthorshipAPI` post-hoc with awkward field shaping.

One possible shape:

> **Provenance beyond creative authorship.** This proposal is scoped to **creative authorship** — who or what creatively authored a prim (human artists, AI generators, DCC tools, creative algorithmic tools like photogrammetry-as-asset-creation). Other forms of provenance — sensor-capture metadata (e.g., LiDAR / camera-rig data), engineering lineage from PLM/CAD systems, simulation runs producing synthetic data — are out of scope and are expected to be addressed by separate peer schemas in a future provenance family.

A scope paragraph here is probably enough; the schema name doesn't need to change.

---

## Comment 2 — Recombination / virality tradeoff

**Anchor:** `proposals/authorship/README.md`, the **Open Questions** section, on the *"What happens when an asset is referenced into another scene?"* paragraph (≈ L617–623).

---

The shape of this question — how authorship and responsibility flow when composed content becomes part of a larger composition — also appears in a parallel in-flight proposal on IP protection in USD, where it lives as the "recombination problem" (concern 4: provenance and compositional integrity). Both proposals are wrestling with the same compositional dynamic from different angles: this proposal from compliance and attribution, the IP-protection proposal from dissemination and ownership.

The discussion in this thread (compliance-pressure points and the counter about placeholders-replaced-by-human-work) is a concrete manifestation of that broader structural question. Worth naming the cross-proposal seam in the proposal itself, even before the virality question settles within this proposal — it gives downstream consumers and adjacent proposals a shared frame, and lets the conversation cohere across both efforts.

One possible shape (could live near this open question or in a Relationship-to-other-proposals subsection):

> Whether and how authorship records propagate through references and sublayers connects to a broader structural problem in USD composition: how do responsibility, attribution, and ownership flow when assets are recombined across vendor and pipeline boundaries? This proposal addresses one slice — creative authorship and AI-content compliance. The parallel IP-protection proposal addresses another (concern 4: provenance and compositional integrity). The resolution within this proposal does not need to wait on the broader question, but downstream tooling benefits from knowing the two are related.

---

## Comment 3 — Field overlap with source-identifiers proposal

**Anchor:** `proposals/authorship/README.md`, the **`producer` (required)** field definition (≈ L215). Comment text covers `identifier` as well.

---

The `producer` field's reverse-DNS naming convention, and the `identifier` field's role as an external-system identifier, overlap with the typed-external-identifier work being explored in a parallel in-flight proposal on identifier separation of concerns in USD (PR 105). The Profiles proposal independently adopts reverse-DNS with a canonical-vs-vendor extension model — three live efforts converging on similar convention shape. The plugin-sub-namespacing direction in the L356 thread (e.g., `org.blenderGenAI.hunyuan3d`) is the kind of convention work that benefits from cross-proposal alignment.

One possible shape for the acknowledgment:

> The fields that identify the producer and the generated artifact are typed external identifiers in the broader sense — they name systems and instances external to USD's namespace. Naming and extensibility conventions for them (reverse-DNS, vendor-extension prefixes, canonical-vs-vendor distinctions) are being worked out in parallel efforts on identifier separation of concerns and on capability profiles. Wherever these fields ultimately live (applied-schema attributes, layer metadata, or `assetInfo`), convergence on shared conventions is worth pursuing — the convention question is largely independent of the storage-mechanism question.

No structural change needed — a sentence or two acknowledging the seam is enough.

---

## Posting plan (when ready)

Three separate line-anchored review comments via `gh pr review 106 --comment` or the web UI. Each is self-contained; no preamble comment needed.

References to PR 105 and the IP-protection proposal: when these comments post on PR 106, the `#105` / proposal-name references become normal in-repo cross-references on the upstream timeline — that is the intended behavior. The no-cross-reference rule from [[feedback_github_cross_references]] applies to WIP draft Issue/PR bodies on the fork, not to comments posted directly on upstream PRs.
