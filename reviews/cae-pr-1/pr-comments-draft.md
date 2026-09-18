# PR 1 (SchultzC/OpenUSD-proposals) — comment drafts

Target: Chris Schultz's draft of *OpenUSD for Scientific Data* on his fork, pre-upstream. **Posted 2026-05-27** as review id 4376356354 (`https://github.com/SchultzC/OpenUSD-proposals/pull/1#pullrequestreview-4376356354`), event=COMMENT, five inline comments anchored to README.md lines 30 / 59 / 171 / 231 / 605, plus one-sentence summary body. Head SHA at submission: `1b8c43507d25965dbe12afa647bd0672fd1e3142`.

**Review intent: light-touch pre-external-share.** Chris is planning to share this draft with external CAE/EDA partners before upstreaming. AOUSD TAC review is further downstream, not imminent — there's runway between the partner share and the TAC submission. Aaron's role at this stage is to make the draft legible to that immediate audience, not to pre-resolve the scope and design questions external partners (and later TAC reviewers) will surface more credibly. Two lenses: (a) clarity of problem statement, (b) separation of concerns. Each comment body is self-contained — no references to staging structure (out-of-scope items, future rounds, etc.) in the text Chris reads.

Goal: friendly, short, one clear ask per comment.

No-cross-reference hygiene: avoid `org/repo#N` notation and PR URLs in this WIP file and in posted comments here. Repo URLs (no PR number) are fine. PR numbers as plain text ("PR 107") are fine — only the `#N` parse or the trailing `/pull/N` URL would auto-cross-reference.

---

## Comment 1 — Friendly onboarding for non-CAE readers

**Anchor:** top of `proposals/cae_scientific_datasets/README.md` (Introduction).

**Status:** ready to post pending sign-off.

---

The proposal moves between "scientific data" (title) and CAE (the worked vertical) without naming the relationship. A short bridge — why "scientific data" rather than "OpenUSD for CAE" — plus one-line expansions for CAE/CFD/FEA/EDA, "solver-native," "field," and "association" would help reviewers from M&E or non-simulation PLM.

cf. *Separation of Concerns for IP Protection in USD* (PR 107 on the upstream [PixarAnimationStudios/OpenUSD-proposals](https://github.com/PixarAnimationStudios/OpenUSD-proposals) repo) — Spiff requested similar onboarding and a short glossary landed it.

---

## Comment 2 — SVG readability in dark mode

**Anchor:** `proposals/cae_scientific_datasets/architecture-diagram.svg` (or the README image reference to it).

**Status:** ready to post pending sign-off.

---

`architecture-diagram.svg` doesn't render readably in GitHub dark mode — section titles, footer captions, and the connector arrows disappear against a dark background.

---

## Comment 5 — Name provenance, units and physical meaning, and ensembles as separated concerns first

**Anchor:** §"Key questions" (the conceptual-separation section) or §"Design considerations / Principles" (a new principle for separated concerns). Chris's choice.

**Status:** ready to post pending sign-off.

**Promoted from "extend PR 105 pattern" framing**, sharpened by the user's correction that PR 105's actual discipline is conceptual-separation-first (no schema-mechanism prescription). Uses the proposal's exact terms ("Provenance," "Units and physical meaning," "Ensembles" within "Time and ensembles"). Subsumes the original provenance-seam parking-lot item; complements Comment 3's §Risks ask.

---

The *Separation of Concerns for Identifiers in USD* pattern (PR 105 on the upstream [PixarAnimationStudios/OpenUSD-proposals](https://github.com/PixarAnimationStudios/OpenUSD-proposals) repo) is to win conceptual alignment on separation *before* proposing schema solutions. The proposal does this for the big data-model-vs-runtime split, but three within-model concerns aren't yet treated that way in the prose:

- **Provenance** (vocabulary table + Principle 6 / Source fidelity), with the multi-source seam noted in §"How should scientific files participate in composition?"
- **Units and physical meaning** (Open Question 5), with the cross-layer composition tension
- **Ensembles** — bundled with time in the "Time and ensembles" vocabulary row, but iterations, operating points, ensemble members, and model variants aren't covered by USD's `.timeSamples`

Naming each as a distinct concern — independent of any future schema-mechanism decision — would let each mature on its own track, mirroring how PR 105 separated USD identifiers from external system identifiers.

---

## Comment 4 — Field association vs. primvars

**Anchor:** §"Existing OpenUSD mechanisms / UsdGeom" (the existing primvar discussion is the natural place to extend).

**Status:** ready to post pending sign-off.

**Promoted from parking lot.** Reversed the earlier "leave alone" call — the inheritance-correctness argument is substantive enough that pre-empting the question is worth one short comment, and the existing topology-shape argument in the proposal is defensible-but-not-the-strongest answer.

---

An OpenUSD reviewer will ask "why aren't these primvars?" — the existing language in §"Existing OpenUSD mechanisms / UsdGeom" answers it as a topology-shape argument (UsdGeom is for renderable geometry), but a stronger answer is available. Primvars bundle three things: a topology-location index space, hierarchical inheritance down the namespace (with resolution cost), and renderer-binding semantics. Field association answers only the first and would be actively wrong if it carried the others — a `pressure` field's array length is tied to a Zone's cell count, so inheriting it to a child prim with a different cell count would silently produce wrong-sized arrays bound to the wrong topology.

One sentence on this scoping (location-only, no inheritance, no renderer binding) plus `UsdVol`'s field-asset model as precedent would pre-empt the question cleanly.

---

## Comment 3 — Cross-layer unit resolution: risk + call for examples

**Anchor:** §Risks (or anchored to Open Question 5 in §Design considerations).

**Status:** ready to post pending sign-off.

**Why post:** external CAE/EDA partners with broad solver and format coverage will hit this on first reading. Naming it as a risk + partner-input ask is light-touch (matches the proposal's existing incubation tone) and helpful, vs. letting a partner's first reaction be "you didn't think about this."

---

Open Question 5 names units as "first proposal vs follow-up?" Worth promoting the composition dimension into the Risks section separately: USD's stronger-opinion-wins resolution is editorial, but units are facts about what was stored — a stronger layer overriding only `:unit` (without overriding the value array) silently reinterprets numbers in a way no other USD attribute composition does. Not a first-proposal design ask, but naming it as a known risk and calling for partner-contributed worst-case examples (mixed-source datasets with divergent unit contexts; reference+payload composition where the strong-opinion author can't see the weak-opinion unit basis) would help the eventual design land on something CAE/EDA partners can actually use.

---

## Out of scope for this round

Items considered and not posting. Lens: this review focuses on (a) clarity of problem statement and (b) separation of concerns. Items that don't materially advance either lens, or that add work to Chris without proportional clarity gain, are held here. Analysis retained so we don't relitigate.

**Subsumed by staged comments:**
- *Provenance seam* — subsumed by Comment 5; per-field-placement is now the concern's own design space.
- *Field association vs. primvars* — promoted to Comment 4.
- *`:name` redundancy in examples* — UsdVol's `fieldName` convention; established pattern, no concern.

**Downstream of Comment 5 (per PR 105's conceptual-first discipline):**
- *Typed-prim vs applied-API for `ScientificDataset`* — mechanism question; becomes more urgent once concerns are separated, but Comment 5 deliberately avoids mechanism prescription. Belongs to Chris's response cycle.
- *Field/array 1:1 split justification* — mechanism question. If concerns are separated, the question of whether field and array are one concern or two falls out naturally.
- *Mechanism-shaped items surfaced on first read* (`custom` keyword vs schema-declared attributes; multi-apply instance-name conventions; `SdfFileFormat` / `SdfAbstractData` value-resolution; discovery without authored-property enumeration) — same family, mechanism territory downstream of conceptual separation.

**Doesn't serve either lens:**
- *Scope umbrella / peer-schemas framing* — proposal already flags as Open Question 1 ("vocabulary boundary"). External partners will surface on their own data.
- *Topology-kind token governance* — within-topology detail, not a separated-concerns question. Belongs in the topology concern's own design once conceptual separation lands.
- *Field-to-topology binding integrity* — within-field-concern semantic question. Real but narrow.
- *NVIDIA implementation asymmetry* — §"Relationship to implementation work" is already labeled as reference-implementation-not-standardization-target. Ask would be tone, not substance.
- *AOUSD relevance* — naming the Industrial Engineering Digital Twins IG via review comment would assert external-party engagement (see [external-party-commitments](../../memory/feedback_external_party_commitments.md)). Route separately if/when it goes to AOUSD.

**Dropped earlier:**
- *Comment 4 / PR 105 identifier-separation cross-ref* — wrong grounding example (`:name` is UsdVol, not identifier-separation); PR 105's scope is external-system object identifiers, not source-asset field display names. Conflating over-reached.
