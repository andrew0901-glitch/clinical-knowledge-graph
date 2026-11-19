# Data issues — v0.2.0 audit (graph files identical in v0.2.1)

> **Scope.** These documents report the audit of release **v0.2.0** (Zenodo 10.5281/zenodo.24091964, HF tag `clinical-v0.2.0`). All 107 node/edge files of release v0.2.1 (Zenodo 10.5281/zenodo.24108692) are **byte-identical** (same SHA-256) to the v0.2.0 files, so every statement about graph content holds for v0.2.1. Statements about the *release metadata files* (dataset card, citation file, exporter commit) describe v0.2.0. Comparisons with earlier releases and with the unreleased pre-correction build were removed from this copy; see `../EXCLUDED.md`.

Read-only independent findings against DOI [10.5281/zenodo.24091964](https://doi.org/10.5281/zenodo.24091964). Complete-population unless explicitly marked as examples.


1. *[Removed: comparison with the unreleased pre-correction build; see EXCLUDED.md.]* Measured on the release itself: 578,177 canonical identity-only Articles; titled stubs 0; stubs with publication types 0.
2. *[Removed: comparison with the unreleased pre-correction build; see EXCLUDED.md.]* Measured on the release itself: extra same NCT-PMID-role edges beyond one per role-pair: 0.

3. **Journal identities remain mostly fallback strings.** Only 376/2,734 have NLM IDs; ISSN/ISSN-L/source IDs are absent and 2,358 have no exported source URL. Zero exact abbreviation collisions does not resolve aliases.
4. **PMC routes are not verified full-text/OA availability.** Access/deposit/figure/table metadata is absent; a graph route can exist without an Article PMCID property.
5. **Provenance gaps remain.** See the per-type completeness table. Release-linked IDs, primary source identifiers, direct source URLs and agent classes answer different questions.
6. **Selection and semantic limitations remain.** Removing true stubs selects for observable bibliography/citations. Registry RESULT/BACKGROUND/DERIVED roles are not clinical-quality adjudications; citations are not endorsement and exact-name/hierarchy trial mapping is not proof of equivalent populations.
7. **Analytics currentness remains unresolved.** The published README states that PageRank/community runs can predate the source snapshot. No analytics property enters the transparent ranking.
8. **Publication metadata has residual inconsistencies.** The README citation still uses a TBD DOI despite the valid published DOI; broad VALIDATED_BY wording appears before the explicit role split and the HAS_MESH direction list omits trial/topic uses. The recorded exporter commit has dirty=true; exact published file hashes, not that commit alone, define this resource. Source registry/shard manifests are available on HF; Zenodo uses the separately verified bundles.
9. **Exact major-label strings do not always link.** Unmatched labels and PMC records with multiple PubMed endpoints are measured, not assigned an unobserved cause or repaired.
10. **Self-citation sensitivity is explicit.** Primary paper chains exclude self-links; historical self-inclusive controls are retained.
11. **Protocol labels overlap source RESULT roles.** The exact NLM-label join is a metadata-bounded lower bound and requires clinical/source adjudication; it does not prove a registry-role error.

The data support descriptive source-integrated resource and connectivity claims. They do not establish expert validation, causal benefit, clinical retrieval quality, complete literature recall, perfect identity resolution, verified OA/full text, or a novel ranking algorithm. Six query examples are purposive, not a representative benchmark.

## Candidates for a subsequent release

- Add stable journal identifiers (ISSN-L/NLM ID), full titles, abbreviations and aliases with provenance.
- Export explicit PMC access/OA/deposit metadata and figure/table counts where licensed and available; distinguish identifier presence from accessible full text.
- Improve structured provenance completeness, unmatched major-topic linkage, identity ambiguity reporting and analytics run dates.
- Replace citation DOI placeholders and clarify all relationship directions and source-role semantics in documentation.
