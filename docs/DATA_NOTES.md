# Data notes — Lunas Clinical Evidence KG v0.1.0

Source of truth: the dataset's own `README.md` / `NOTICE.md` / `manifest.json`
on Zenodo (https://doi.org/10.5281/zenodo.24011485) and Hugging Face
(`lunas-health/clinical-evidence-kg`). This file only summarizes what the
loader in this repo needs to know; always defer to the dataset's own docs for
anything licensing- or provenance-related.

## Scope (v0.1.0)

Five source families only: **PubMed, OpenAlex, MeSH, ClinicalTrials.gov,
MedlinePlus**. Everything else in the broader LunasAI graph (RxNorm/NDC/FDA
drugs, ICD-10/CPT/HCPCS/MS-DRG coding, devices, NPPES providers, CMS coverage
policy, LunasAI-computed communities/co-citation) is explicitly **withheld**
from this release regardless of its own license status — see each dataset's
`README.md` "What is not included" section.

Two populations are shipped but are **not part of the CC0 core graph**:
- `ctgov_publications.jsonl` — a separate CC0 sidecar for independent
  integrity verification, not meant to be loaded as graph nodes/edges.
- The **JEV evidence-annotation sidecar** (`jev_manifest.json`,
  `jev_evidence_annotations.jsonl`) — explicitly **NOT CC0**, rights reserved,
  "must never be used to train, fine-tune, distill, or fit thresholds for any
  model." This repo's loader never touches it.

## Real shipped counts (manifest.json, 2026-11-03 snapshot)

| Kind | Count |
|---|---:|
| Nodes | 10,145,579 |
| Edges | 109,661,337 |
| Compressed shard bytes | 5,257,041,964 (~4.9 GiB) |

Node labels present: Article (3,139,339), Author (5,134,220), ClinicalTrial
(606,482), ExternalResource (38,751), License (76), MeSHConcept (31,110),
MedlinePlus (2,033), MedlinePlusGroup (88), RightsPolicy (11), Sponsor
(101,306), TrialSite (1,092,163).

Edge types present: AUTHORED_BY (21,135,333), CITES (30,203,219), HAS_MESH
(42,629,950), HAS_RIGHTS_EVIDENCE (7,218,698), HAS_USE_GRANT (4,026,032),
SPONSORED_BY (931,156), CONDUCTED_AT (3,153,344), PARENT_OF (42,519),
ANCESTOR_OF (185,654), VALIDATED_BY (45,314), plus six smaller MedlinePlus/
resource types (HAS_LANGUAGE_RESOURCE, IN_TOPIC_GROUP, LINKS_TO_RESOURCE,
RELATED_TOPIC, RESOURCE_TRANSLATION_OF, TRANSLATION_OF).

## KGX record shape actually observed

**Node** (`id` is a globally-unique CURIE across the *entire* export, not
just within one shard):
```json
{
  "id": "PMID:10203632",
  "category": ["biolink:Article"],
  "name": "...",
  "lunasai_labels": ["Article"],
  "lunasai_layer": "pubmed",
  "...": "many more flat scalar/list properties"
}
```

**Edge** (`id` is a per-edge `urn:uuid:...`, globally unique; `original_predicate`
carries the native LunasAI/Neo4j relationship type as `lunasai:vocab.<TYPE>`):
```json
{
  "id": "urn:uuid:2fe34fbc-...",
  "subject": "PMID:10021452",
  "predicate": "biolink:related_to",
  "object": "lunasai:rights_policy.rp_05deb3b92d11e92a",
  "original_predicate": "lunasai:vocab.HAS_RIGHTS_EVIDENCE",
  "...": "provenance / evidence properties"
}
```

**Important correctness gotcha found during validation**: the real export
legitimately has *parallel edges* of the same `original_predicate` between
the same `(subject, object)` pair, distinguished only by properties — e.g.
multiple `HAS_RIGHTS_EVIDENCE` edges per `(Article, RightsPolicy)` pair, one
per `component` (`metadata`, `title`, ...). A loader that MERGEs edges on
`(subject, rel_type, object)` alone will silently collapse these into a
single relationship and lose data. This repo's loader MERGEs on the edge's
own `id` instead (see `scripts/load_kgx_to_neo4j.py` docstring and
`docs/VALIDATION_RESULTS.md`).

## File layout on Zenodo

The published record exposes **8 node shards + 8 edge shards** as
`nodes__nodes-w0N.jsonl.gz` / `edges__edges-w0N.jsonl.gz` (each a
concatenation of several smaller gzip members from the original 56+56-part
internal layout — transparent to any gzip-aware reader, including Python's
`gzip` module, since gzip streams concatenate). `manifest.json` lists per-part
`sha256` for the internal parts; this repo's `download_shards.py` verifies
shard *size* against the Zenodo API listing and leaves deeper per-part
checksum verification to anyone who needs it (the shard-level sha256 values
used in this repo's own checksums, where quoted, are computed directly over
the downloaded shard files — see `docs/VALIDATION_RESULTS.md`).
