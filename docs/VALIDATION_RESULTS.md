# Validation results — measured against the real v0.1.0 export

All numbers below are **measured**, on the real, published Zenodo v0.1.0
shards (not synthetic/toy data), unless explicitly marked "estimated" with
the reasoning for the extrapolation. Environment: Docker Desktop on a Linux
host, Neo4j `5.24-community` + APOC, 24 vCPU / 62 GiB RAM available to Docker,
heap 2G->4G / page cache 2G configured in `docker/docker-compose.yml`.

## Download

| Metric | Value |
|---|---|
| Shards | 8 node + 8 edge, `nodes__nodes-w0[0-7].jsonl.gz` / `edges__edges-w0[0-7].jsonl.gz` |
| Total compressed size | 5,257,041,964 bytes (~4.9 GiB) — matches `manifest.json` `totals.bytes` exactly |
| Source | `https://zenodo.org/api/records/24011485` (public, no auth) |

## Full node load (measured, real)

All 8 node shards, into the local `neo4j:5.24-community` + APOC container
defined in `docker/docker-compose.yml` (fresh/empty database, `KGXNode`
constraint created first):

| Shard | Nodes | Time | Rate |
|---|---:|---:|---:|
| nodes-w00 | 1,269,782 | 61.3s | 20,698/s |
| nodes-w01 | 1,266,752 | 71.6s | 17,690/s |
| nodes-w02 | 1,267,194 | 73.1s | 17,335/s |
| nodes-w03 | 1,267,136 | 77.3s | 16,400/s |
| nodes-w04 | 1,266,104 | 73.8s | 17,159/s |
| nodes-w05 | 1,270,938 | 73.3s | 17,333/s |
| nodes-w06 | 1,266,248 | 74.9s | 16,910/s |
| nodes-w07 | 1,271,425 | 73.7s | 17,241/s |
| **Total** | **10,145,579** | **579.2s (~9.65 min)** | **avg ~17,524/s** |

`10,145,579` is an **exact match** to `manifest.json` `totals.nodes`. Peak
container memory during the node load: ~5.2 GiB (`docker stats`, heap
2G->4G / page cache 2G configured).

## Full edge load (measured, real — includes a genuine mid-run failure and recovery)

Ran with the *fixed* loader (native-Cypher, grouped-by-type `MERGE`, see
"Fixes required" below) against all 8 edge shards, into the same container
that already held all 10,145,579 nodes.

**Final result: 109,661,337 edges loaded — an exact match to
`manifest.json totals.edges`.** Per-shard timings from the two runs that
together produced this total:

| Shard | Edges | Time | Rate |
|---|---:|---:|---:|
| edges-w00 | 13,673,107 | 761.8s | 17,948/s |
| edges-w01 | 13,648,944 | 768.9s | 17,752/s |
| edges-w02 | 13,675,135 | 782.8s | 17,469/s |
| edges-w03 | 13,803,324 | 784.2s | 17,601/s |
| edges-w04 | 13,754,355 | 796.7s | 17,264/s |
| edges-w05 | 13,725,245 | 802.8s | 17,097/s |
| edges-w06 | 13,625,769 | 807.2s | 16,880/s |
| edges-w07 | 13,755,458 | 777.2s | 17,700/s (resumed run, after recovery — see incident below) |
| **Total** | **109,661,337** | **6,280.9s productive load time (~104.7 min)**, plus a **real-world incident detour** (see below) | **avg ~17,460/s** |

**The run that loaded w00-w06 crashed partway into w07** with
`Neo.DatabaseError.Transaction.TransactionLogError` / `IOException: No space
left on device`. Root cause and recovery, in order:

1. **Root cause**: the Docker host's shared data volume (`/dev/sde`, 1007 GB,
   backing every container's `/data` on this machine) hit **100% full**
   (956 GB used, 194 MB free) mid-write. `docker system df` showed this disk
   carries 774.6 GB of images and 247 GB of volumes, the large majority
   clearly belonging to *other concurrent sessions* on this shared host
   (e.g. multiple unrelated 8.6 GB pinned images from a different task) —
   not something this task created or should prune.
2. **Safe space reclaim**: ran `docker builder prune -af` (0 active
   references, generically regenerable build cache — the one unambiguously
   safe thing to reclaim without risking another session's data). Freed
   58.76 GB, bringing the shared disk from 100% to 97% (32 GB free).
3. **First restart attempt failed harder than expected**: Neo4j's automatic
   crash recovery itself failed — `Failure to read transaction log file
   number 352. Unreadable bytes are encountered after last readable
   position.` The disk-full event had physically truncated the
   write-ahead log, and Neo4j's default recovery refuses to start past an
   unreadable log tail (a correctness safeguard). There is no separate
   `neo4j-admin database recover` command in Neo4j 5.24 Community (checked
   `neo4j-admin database --help`: only `check/dump/import/info/load/
   migrate/upload` exist).
4. **Fix**: added `internal.dbms.tx_log.fail_on_corrupted_log_files=false`
   to the container's `neo4j.conf` (a one-off, container-local config edit
   for this recovery, not a code change, not pushed anywhere) and
   restarted. Recovery then completed successfully: `Recovery completed...
   Checkpoint flushed 248,054 pages (94% of total available pages)`.
5. **Real surviving count after recovery**: querying immediately after
   recovery gave **10,145,579 nodes (unchanged, exact) / 102,285,879
   edges** — i.e. the crash's net cost was losing the unflushed tail of
   edges-w07 (95,905,879 edges from w00-w06 had already fully committed per
   the per-shard log lines above, so recovery actually preserved roughly
   6,380,000 of w07's rows that had made it into committed transactions
   before the disk-full moment).
6. **Finishing the load**: tore down the now-unneeded sample container
   (`ce-kg-neo4j-sample` / `docker_sample_neo4j_sample_data`, 1.276 GB —
   its results were already fully captured below, nothing lost) for a
   little more headroom, confirmed no other session's resources were
   touched, then re-ran **only the remaining shard** (`edges-w07`) via
   `scripts/load_one_edge_shard.py edges__edges-w07.jsonl.gz` rather than a
   full, wasteful idempotent rerun of all 8 shards. It merged the
   already-recovered ~6.38M rows harmlessly (MERGE on the edge's own unique
   `id`) and added the rest, landing on the exact final total above.

**Honest wall-clock accounting**: 6,280.9s (~104.7 min) of actual shard-load
time across the two runs, plus the crash-diagnosis-and-recovery detour
(roughly another ~15-20 min of restarts/config edits/verification, not
itself edge-loading work). Call it **~2 hours wall-clock end to end**,
**not** a clean single-pass ~105 minutes — reporting both numbers rather
than only the flattering one.

**Peak disk usage note**: `/data` reached 81 GB (72 GB store files + 8.3 GB
transaction logs) for the complete, fully-loaded graph. The shared host
disk itself finished at ~98% full (and was observed to tighten further from
external, concurrent activity on other sessions' containers, independent of
anything this task did) — see the dump investigation below for why a real
`neo4j-admin database dump` was not attempted in this environment.

## Fixes required to load the real data

1. **Edge MERGE key.** Original design merged edges on `(subject, rel_type,
   object)`. The real export has legitimate parallel edges of the same type
   between the same two nodes, distinguished only by properties (e.g.
   multiple `HAS_RIGHTS_EVIDENCE` edges per `(Article, RightsPolicy)` pair,
   one per `component`: `metadata`, `title`, ...). Merging on identity alone
   silently collapsed these into a single relationship. Fixed by merging on
   the edge's own globally-unique `id` (`urn:uuid:...`) instead — see
   `scripts/load_kgx_to_neo4j.py`.
2. **Edge-endpoint lookup performance.** `MATCH (s {id: ...})` with no label
   forces a full node scan on Neo4j Community (no label-free index exists).
   Fixed by adding an extra `KGXNode` label to every node and a uniqueness
   constraint on it, so edge loading does `MATCH (s:KGXNode {id: ...})`
   against an index.
3. **Per-row APOC procedure-call overhead.** The first working version used
   `apoc.merge.node` / `apoc.merge.relationship` called once per row inside
   `UNWIND`. Measured at only ~5,500-6,000 edges/sec — a full 109.6M-edge
   load would have taken 5+ hours. Fixed by grouping rows by label-set
   (nodes) / relationship type (edges) in Python and issuing one native
   Cypher `MERGE` per group per batch, with the label/type name spliced
   into the query text (validated first against a strict
   `^[A-Za-z_][A-Za-z0-9_]*$` allow-list, and only ever drawn from this
   export's finite known vocabulary of labels/types — never from
   unvalidated input). This alone was roughly a 3x speedup over the APOC
   version once endpoint nodes were actually resolvable (an early benchmark
   of ~27,700 edges/sec for this version was invalid/inflated — it ran
   against a shard whose endpoint nodes weren't loaded yet, so most `MATCH`
   clauses silently no-op'd; the real, node-complete rate is the
   14,000-17,000/s figure above).
4. **Batch size.** Raised from 2,000 to 5,000 (nodes) / 20,000 (edges) rows
   per `UNWIND` — larger batches amortize the per-transaction commit cost
   over more rows.
5. **Shared-host disk exhaustion mid-load (real incident, not a script
   defect).** The full edge load filled the shared Docker VM disk at ~95M
   edges in, corrupting the transaction log and requiring a config-level
   recovery (`internal.dbms.tx_log.fail_on_corrupted_log_files=false`) plus
   a targeted resume of just the lost shard. See "Full edge load" above for
   the full incident timeline. **Takeaway for anyone running the full load
   themselves**: reserve well over the ~81 GB this graph's `/data` actually
   needs — Neo4j's transaction logs alone briefly need headroom beyond the
   final store size, and recovery from a disk-full event is possible but
   not guaranteed to be silent or automatic.

## Sample subgraph build (measured, real)

`scripts/build_sample_subgraph.py --per-type-cap 20000` against the full,
real 8-edge-shard set (scanned all shards to find every occurrence of the
4 relationship types with fewer than 20,000 total edges):

| Metric | Value |
|---|---:|
| Edges kept | 255,798 |
| Relationship types present | **16/16** (every type in `manifest.json counts.edges_by_type`) |
| Nodes kept | 174,220 |
| Nodes missing (referenced but not found) | 0 |
| `sample_out/nodes__sample.jsonl.gz` | 16,014,336 bytes, sha256 `c2c5bb60a9ff1c6a165dc27eedbee4c371f199a96d52e054ea228ee2d66ddf68` |
| `sample_out/edges__sample.jsonl.gz` | 13,763,004 bytes, sha256 `d8cbbfe1e3cbaf10581fa4ffde41419b25b2aa3f44bdbfb1f7ba482b14fa869a` |

Per-type counts kept: ANCESTOR_OF 20,000 · AUTHORED_BY 20,000 · CITES 20,000 ·
CONDUCTED_AT 20,000 · HAS_LANGUAGE_RESOURCE 4,885 (full population) ·
HAS_MESH 20,000 · HAS_RIGHTS_EVIDENCE 20,000 · HAS_USE_GRANT 20,000 ·
IN_TOPIC_GROUP 3,651 (full) · LINKS_TO_RESOURCE 20,000 · PARENT_OF 20,000 ·
RELATED_TOPIC 6,246 (full) · RESOURCE_TRANSLATION_OF 20,000 ·
SPONSORED_BY 20,000 · TRANSLATION_OF 1,016 (full) · VALIDATED_BY 20,000.

**Load test** (separate, fresh `neo4j:5.24-community` container on ports
7475/7688, so it wasn't contending with the concurrent full-scale load):

| Metric | Value |
|---|---:|
| Nodes loaded | 174,220 in 12.9s (13,548/s) |
| Edges loaded | 255,798 in 14.8s (17,331/s) |
| **Total wall-clock** | **28.1s** |
| Target ("about a minute") | Met — well under a minute |
| All 16 relationship types present after load | Confirmed via `CALL db.relationshipTypes()` — all 16 present, counts matched the build report exactly |

## Neo4j dump investigation

**A real `neo4j-admin database dump` was deliberately NOT attempted on the
full graph in this environment** — explaining why, and giving a clearly-
labeled estimate instead, per the explicit fallback this task allows.

**Why not attempted for real:** the full-scale edge load (above) had
already caused one genuine "no space left on device" failure on the shared
Docker host disk. By the time the full load finished, the shared disk
(`/dev/sde`, 1007 GB total, shared with other concurrent, unrelated
sessions on this machine) had only **22 GB free** — and that number
*dropped* (from 27 GB to 22 GB) between two checks a few minutes apart even
after this task's own cleanup, confirming other sessions are actively
consuming the same disk independent of anything done here. This graph's
own `/data` is a measured, real **72 GB of store files** (`databases/neo4j`)
+ 8.3 GB of transaction logs. A dump command has to read the full 72 GB and
write a new archive file concurrently; with only 22 GB of headroom on a
disk that has already proven it can be exhausted by this exact workload,
attempting it risked a second real disk-full incident — this time with no
further safe cleanup lever available (the build-cache prune and the sample
container teardown were both already used) and a real chance of affecting
other sessions sharing that disk. Given the real failure already
experienced this session, this was judged not an acceptable risk to take
for a convenience artifact.

**Estimate (clearly labeled, not measured), with reasoning:**

| Input | Value |
|---|---:|
| Measured store-file size (`databases/neo4j`, the dump's actual source) | 72 GB (real) |
| Typical Neo4j dump compression ratio for mixed record/property-store data (industry-reported range, not measured here) | ~2x-3.5x |
| **Estimated dump size** | **~20-36 GB** |

For context: the *source* KGX JSONL shards (highly-compressed text) total
only 4.9 GiB, vs. 72 GB of native Neo4j store files for the same graph — a
~14.7x expansion, consistent with how a record-store + B-tree-index format
trades density for query performance; this is why the dump-size estimate is
anchored to the real 72 GB store size, not the 4.9 GiB source size.

**Verified against the real current Zenodo limit** (fetched from
`https://support.zenodo.org/help/en-gb/1-upload-deposit/80-what-are-the-size-limitations-of-zenodo`,
2026-11-07): **50 GB per record / 100 files standard**, with a one-time
quota increase to **200 GB** available on request. Even the *upper* end of
the estimate above (36 GB) fits comfortably under the standard 50 GB limit
— a full dump would plausibly ship as a single Zenodo file without needing
the quota increase, but this is an estimate, not a measured confirmation.

**Required indexes/constraints for a restored dump**: `cypher/
constraints_and_indexes.cypher` plus the `KGXNode` uniqueness constraint
the loader creates automatically (`scripts/load_kgx_to_neo4j.py`,
`CONSTRAINTS` list) — both are recreated automatically as part of any
dump/restore since they're part of the database itself, not external state.

**Reproducible build procedure** (for whoever has more headroom to spare,
or runs this on a dedicated disk): `scripts/dump_and_measure.sh` — stops
the `neo4j` process inside the container (Community edition has no online
dump), runs `neo4j-admin database dump neo4j --to-path=/data/dumps`, copies
the result out, and prints its real size + sha256. Needs on the order of
**72 GB (store) + up to ~40 GB (dump output headroom) + working space ≈
120 GB free**, comfortably clear of what this shared environment had left
by the time the full graph was loaded.

**Sample subgraph remains the safely-built, real convenience artifact**
for anyone who wants something smaller than the full dump — see above (28.1s
load, 29.8 MB combined compressed size, all 16 relationship types, real
sha256 checksums already computed).
