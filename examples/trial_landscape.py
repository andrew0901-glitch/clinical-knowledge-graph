#!/usr/bin/env python3
"""Clinical trial landscape for a condition, from the published Lunas Clinical Evidence KG files.

  pip install duckdb
  python examples/trial_landscape.py --input ckg --condition "Asthma"          # name or D001249 / MESH:D001249
  python examples/trial_landscape.py --input ckg --condition D001249 --out out/asthma
  python examples/trial_landscape.py --input ckg --condition D006333 --merge-sites   # merge facility spellings
  python examples/trial_landscape.py --input ckg --data-check                   # field completeness table only

For a MeSH condition descriptor it reports the competitive trial landscape (sponsors, sponsor class,
phase, status, start-year timeline), where the trials run (sites and countries, with how many matching
trials are recruiting at each -- the competing-trial density a site-selection team cares about), and
which trials have published results (VALIDATED_BY) and how often those results papers are cited
in-graph by guidelines or systematic reviews. Output: CSVs plus one self-contained report.html.

How a trial is linked to a condition (verified against the v0.2.x files):
  (ClinicalTrial)-[:HAS_MESH {study_aspect:'condition', mesh_type:'mesh-list'}]->(MeSHConcept)
  These edges carry ClinicalTrials.gov's own condition browse terms (its published condition -> MeSH
  mapping). mesh_type 'mesh-ancestor' edges are the ancestors ClinicalTrials.gov adds itself; this
  script ignores them and does its own expansion so direct and narrower matches can be told apart.
  study_aspect 'intervention' edges (the intervention browse terms) are never used.

Hierarchy expansion: HAS_BROADER is subject=narrower, object=broader, so the query descriptor is
matched as the OBJECT and the walk goes to its subjects. Each step follows the edge's tree numbers
(child_tree_numbers must sit directly under the parent tree number reached), which is PubMed's
"explode": a descriptor that also sits in an unrelated branch does not drag that branch in.

The first run reads every node and edge file once (about a minute on 16+ cores) and caches the
trial subgraph as Parquet in <input>/trial_landscape_cache; later runs take seconds.
"""
import argparse, csv, glob, gzip, html, json, os, re, shutil, sys, time, unicodedata
from collections import defaultdict
from multiprocessing import Pool

try:
    import duckdb
except ImportError:
    sys.exit("pip install duckdb")

CACHE_VERSION = 1
GUIDELINE_TYPES = {"Guideline", "Practice Guideline"}
SYSTEMATIC_REVIEW_TYPES = {"Systematic Review"}
META_ANALYSIS_TYPES = {"Meta-Analysis"}
RECRUITING = "RECRUITING"
# ClinicalTrials.gov agency_class (on the SPONSORED_BY edge) folded into four display groups.
# CT.gov has no "academic" class: universities and hospitals are filed under OTHER.
CLASS_GROUP = {"INDUSTRY": "Industry", "OTHER": "Academic / hospital / other",
               "NIH": "Government", "FED": "Government", "OTHER_GOV": "Government",
               "NETWORK": "Network / individual / unknown", "INDIV": "Network / individual / unknown",
               "UNKNOWN": "Network / individual / unknown", "AMBIG": "Network / individual / unknown"}
# v0.2.x: the newest registrations (about 22.6K trials) have no SPONSORED_BY or CONDUCTED_AT edges at all;
# they are kept apart from CT.gov's own UNKNOWN class.
NO_SPONSOR = "No sponsor record in release"
CLASS_ORDER = ["Industry", "Academic / hospital / other", "Government", "Network / individual / unknown", NO_SPONSOR]
PHASE_ORDER = ["EARLY_PHASE1", "PHASE1", "PHASE1/PHASE2", "PHASE2", "PHASE2/PHASE3", "PHASE3", "PHASE4",
               "NA", "(missing)"]
STATUS_ORDER = ["RECRUITING", "NOT_YET_RECRUITING", "ENROLLING_BY_INVITATION", "ACTIVE_NOT_RECRUITING",
                "SUSPENDED", "COMPLETED", "TERMINATED", "WITHDRAWN", "UNKNOWN", "AVAILABLE",
                "TEMPORARILY_NOT_AVAILABLE", "NO_LONGER_AVAILABLE", "APPROVED_FOR_MARKETING", "WITHHELD",
                "(missing)"]

# ---------------------------------------------------------------------------------------------
# Extraction: one streaming pass over nodes, two over edges, each file in its own process.
# Workers write gzipped CSV per shard; DuckDB folds them into one Parquet file per table.
# ---------------------------------------------------------------------------------------------
TABLES = {
    "trials": ["id", "nct_id", "title", "overall_status", "phase", "study_type", "start_date",
               "completion_date", "enrollment", "invalid_reason"],
    "sites": ["id", "name", "city", "state", "country"],
    "sponsors": ["id", "name"],
    "mesh": ["id", "mesh_id", "name"],
    "articles": ["id", "pmid", "title", "year", "journal", "layer", "cited_by_count",
                 "is_guideline", "is_systematic_review", "is_meta_analysis"],
    "trial_mesh": ["trial", "mesh", "mesh_type", "study_aspect", "mesh_term"],
    "sponsored_by": ["trial", "sponsor", "agency_class", "lead_or_collaborator"],
    "conducted_at": ["trial", "site", "site_status"],
    "trial_pubs": ["article", "trial", "rel", "publication_role"],
    "broader": ["child", "parent", "child_tree_numbers", "parent_tree_numbers"],
    "broader_ancestor": ["descendant", "ancestor", "depth"],
    "result_citations": ["cited", "n_cites"],
    "result_citers": ["citer", "cited"],
}
NODE_TABLE = {"ClinicalTrial": "trials", "TrialSite": "sites", "Sponsor": "sponsors",
              "MeSHConcept": "mesh", "Article": "articles"}
TRIAL_PUB_RELS = {"VALIDATED_BY", "CITES_BACKGROUND", "HAS_DERIVED_PUBLICATION"}
SUBJ_RE = re.compile(r'"subject":\s*"([^"]+)"')
OBJ_RE = re.compile(r'"object":\s*"([^"]+)"')
_W = {}


def _writers(tmp, shard, names):
    out = {}
    for t in names:
        os.makedirs(os.path.join(tmp, t), exist_ok=True)
        fh = gzip.open(os.path.join(tmp, t, shard + ".csv.gz"), "wt", newline="", compresslevel=1)
        w = csv.writer(fh)
        w.writerow(TABLES[t])
        out[t] = (fh, w)
    return out


def _close(ws):
    for fh, _ in ws.values():
        fh.close()


def _rel(r):
    return (r.get("original_predicate") or "").rsplit(".", 1)[-1]


def _node_worker(args):
    path, tmp = args
    ws = _writers(tmp, "n_" + os.path.basename(path), NODE_TABLE.values())
    with gzip.open(path, "rt") as fh:
        for line in fh:
            if not any(f'"{l}"' in line for l in NODE_TABLE):
                continue
            r = json.loads(line)
            t = NODE_TABLE.get((r.get("lunasai_labels") or [None])[0])
            if t == "trials":
                ws[t][1].writerow([r["id"], r.get("nct_id"), r.get("name"), r.get("overall_status"),
                                   r.get("phase"), r.get("study_type"), r.get("start_date"),
                                   r.get("completion_date"), r.get("enrollment"), r.get("invalid_reason")])
            elif t == "sites":
                ws[t][1].writerow([r["id"], r.get("name"), r.get("city"), r.get("state"), r.get("country")])
            elif t == "sponsors":
                ws[t][1].writerow([r["id"], r.get("name")])
            elif t == "mesh":
                ws[t][1].writerow([r["id"], r.get("mesh_id"), r.get("name")])
            elif t == "articles":
                pt = set(r.get("pub_types") or [])
                ws[t][1].writerow([r["id"], r.get("pmid"), r.get("name"), r.get("year"), r.get("journal"),
                                   r.get("lunasai_layer"), r.get("cited_by_count"),
                                   bool(pt & GUIDELINE_TYPES), bool(pt & SYSTEMATIC_REVIEW_TYPES),
                                   bool(pt & META_ANALYSIS_TYPES)])
    _close(ws)


def _edge_worker(args):
    path, tmp = args
    names = ["trial_mesh", "sponsored_by", "conducted_at", "trial_pubs", "broader", "broader_ancestor"]
    ws = _writers(tmp, "e_" + os.path.basename(path), names)
    with gzip.open(path, "rt") as fh:
        for line in fh:
            if "clinicaltrials:" not in line and "HAS_BROADER" not in line:
                continue
            r = json.loads(line)
            rel, s, o = _rel(r), r["subject"], r["object"]
            if rel == "HAS_MESH" and s.startswith("clinicaltrials:"):
                ws["trial_mesh"][1].writerow([s, o, r.get("mesh_type"), r.get("study_aspect"), r.get("mesh_term")])
            elif rel == "SPONSORED_BY":
                ws["sponsored_by"][1].writerow([s, o, r.get("agency_class"), r.get("lead_or_collaborator")])
            elif rel == "CONDUCTED_AT":
                ws["conducted_at"][1].writerow([s, o, r.get("status")])
            elif rel in TRIAL_PUB_RELS:
                ws["trial_pubs"][1].writerow([s, o, rel, r.get("publication_role") or r.get("reference_type")])
            elif rel == "HAS_BROADER":
                ws["broader"][1].writerow([s, o, "|".join(r.get("child_tree_numbers") or []),
                                           "|".join(r.get("parent_tree_numbers") or [])])
            elif rel == "HAS_BROADER_ANCESTOR":
                ws["broader_ancestor"][1].writerow([s, o, r.get("depth")])
    _close(ws)


def _init_cites(results, gsr):
    _W["results"], _W["gsr"] = results, gsr


def _cites_worker(args):
    path, tmp = args
    results, gsr, counts = _W["results"], _W["gsr"], defaultdict(int)
    ws = _writers(tmp, "c_" + os.path.basename(path), ["result_citations", "result_citers"])
    with gzip.open(path, "rt") as fh:
        for line in fh:
            if 'vocab.CITES"' not in line:
                continue
            o = OBJ_RE.search(line).group(1)
            if o not in results:
                continue
            counts[o] += 1
            s = SUBJ_RE.search(line).group(1)
            if s in gsr:
                ws["result_citers"][1].writerow([s, o])
    for o, n in counts.items():
        ws["result_citations"][1].writerow([o, n])
    _close(ws)


def glob_for(root, kind):
    for pat in (os.path.join(root, kind, "*.jsonl.gz"), os.path.join(root, f"{kind}__*.jsonl.gz")):
        files = sorted(glob.glob(pat))
        if files:
            return files
    sys.exit(f"no {kind} files found under {root}")


def build_cache(input_dir, cache, workers):
    t0 = time.time()
    tmp = os.path.join(cache, "_tmp")
    shutil.rmtree(tmp, ignore_errors=True)
    nodes, edges = glob_for(input_dir, "nodes"), glob_for(input_dir, "edges")
    con = duckdb.connect()

    def fold(table, dtypes):
        cols = "{" + ", ".join(f"'{c}': '{dtypes.get(c, 'VARCHAR')}'" for c in TABLES[table]) + "}"
        src = os.path.join(tmp, table, "*.csv.gz")
        con.sql(f"COPY (SELECT * FROM read_csv('{src}', header=true, columns={cols}, quote='\"', escape='\"')) "
                f"TO '{os.path.join(cache, table + '.parquet')}' (FORMAT parquet)")

    print(f"[cache] pass 1/3: {len(nodes)} node files", flush=True)
    with Pool(workers) as p:
        list(p.imap_unordered(_node_worker, [(f, tmp) for f in nodes]))
    fold("trials", {"enrollment": "BIGINT"})
    for t in ("sites", "sponsors", "mesh"):
        fold(t, {})
    fold("articles", {"year": "INTEGER", "cited_by_count": "BIGINT", "is_guideline": "BOOLEAN",
                      "is_systematic_review": "BOOLEAN", "is_meta_analysis": "BOOLEAN"})

    print(f"[cache] pass 2/3: {len(edges)} edge files (trial, sponsor, site, MeSH-tree edges)", flush=True)
    with Pool(workers) as p:
        list(p.imap_unordered(_edge_worker, [(f, tmp) for f in edges]))
    for t in ("trial_mesh", "sponsored_by", "conducted_at", "trial_pubs", "broader"):
        fold(t, {})
    fold("broader_ancestor", {"depth": "INTEGER"})

    print("[cache] pass 3/3: CITES edges pointing at trial results articles", flush=True)
    results = {r[0] for r in con.sql(f"SELECT DISTINCT article FROM '{cache}/trial_pubs.parquet' "
                                     f"WHERE rel = 'VALIDATED_BY'").fetchall()}
    gsr = {r[0] for r in con.sql(f"SELECT id FROM '{cache}/articles.parquet' "
                                 f"WHERE is_guideline OR is_systematic_review OR is_meta_analysis").fetchall()}
    with Pool(workers, initializer=_init_cites, initargs=(results, gsr)) as p:
        list(p.imap_unordered(_cites_worker, [(f, tmp) for f in edges]))
    cols = "{'cited': 'VARCHAR', 'n_cites': 'BIGINT'}"
    con.sql(f"COPY (SELECT cited, sum(n_cites) AS n_cites FROM read_csv('{tmp}/result_citations/*.csv.gz', "
            f"header=true, columns={cols}) GROUP BY cited) TO '{cache}/result_citations.parquet' (FORMAT parquet)")
    fold("result_citers", {})
    shutil.rmtree(tmp)
    meta = {"cache_version": CACHE_VERSION, "input": os.path.abspath(input_dir), "built_seconds": round(time.time() - t0, 1),
            "node_files": [os.path.basename(f) for f in nodes], "edge_files": [os.path.basename(f) for f in edges]}
    json.dump(meta, open(os.path.join(cache, "meta.json"), "w"), indent=1)
    print(f"[cache] built in {meta['built_seconds']}s -> {cache}", flush=True)


def open_cache(cache):
    con = duckdb.connect()
    for t in TABLES:
        con.sql(f"CREATE VIEW {t} AS SELECT * FROM read_parquet('{os.path.join(cache, t + '.parquet')}')")
    return con


# ---------------------------------------------------------------------------------------------
# Data check: field completeness with denominators.
# ---------------------------------------------------------------------------------------------
def data_check(con):
    rows = []

    def add(entity, field, n, d, note=""):
        rows.append((entity, field, n, d, round(100.0 * n / d, 2) if d else None, note))

    q = lambda s: con.execute(s).fetchall()[0][0]
    n_trials = q("SELECT count(*) FROM trials")
    n_full = q("SELECT count(*) FROM trials WHERE title IS NOT NULL")
    add("ClinicalTrial", "(node has registry record: title present)", n_full, n_trials,
        "the rest are identity-only stubs created for publication edges")
    for f in ("overall_status", "phase", "study_type", "start_date", "completion_date", "enrollment"):
        add("ClinicalTrial", f, q(f"SELECT count(*) FROM trials WHERE {f} IS NOT NULL"), n_full)
    add("ClinicalTrial", "phase (excluding 'NA' = not applicable)",
        q("SELECT count(*) FROM trials WHERE phase IS NOT NULL AND phase <> 'NA'"), n_full)
    n_int = q("SELECT count(*) FROM trials WHERE study_type = 'INTERVENTIONAL'")
    add("ClinicalTrial", "phase, interventional trials only",
        q("SELECT count(*) FROM trials WHERE study_type='INTERVENTIONAL' AND phase IS NOT NULL"), n_int)
    add("ClinicalTrial", "start_date day = last day of month (month-precision date padded)",
        q("SELECT count(*) FROM trials WHERE start_date IS NOT NULL AND "
          "try_cast(start_date AS DATE) = last_day(try_cast(start_date AS DATE))"),
        q("SELECT count(*) FROM trials WHERE start_date IS NOT NULL"),
        "use start year, not day")
    add("ClinicalTrial", "enrollment = 0", q("SELECT count(*) FROM trials WHERE enrollment = 0"), n_full)
    add("ClinicalTrial", "invalid_reason set (deleted in source)",
        q("SELECT count(*) FROM trials WHERE invalid_reason IS NOT NULL"), n_trials)
    add("ClinicalTrial", "conditions / MeSH as node properties", 0, n_trials,
        "no such property; condition linkage is the HAS_MESH edge below")

    for aspect in ("condition", "intervention"):
        add("ClinicalTrial", f"has >=1 HAS_MESH {aspect} edge (mesh-list, direct browse term)",
            q(f"SELECT count(DISTINCT trial) FROM trial_mesh WHERE study_aspect='{aspect}' AND mesh_type='mesh-list'"),
            n_full)
    add("ClinicalTrial", "has >=1 HAS_MESH condition edge (any mesh_type)",
        q("SELECT count(DISTINCT trial) FROM trial_mesh WHERE study_aspect='condition'"), n_full)
    for mt in ("mesh-list", "mesh-ancestor"):
        for aspect in ("condition", "intervention"):
            add("HAS_MESH (trial)", f"edges: {aspect} / {mt}",
                q(f"SELECT count(*) FROM trial_mesh WHERE study_aspect='{aspect}' AND mesh_type='{mt}'"),
                q("SELECT count(*) FROM trial_mesh"))
    add("HAS_MESH (trial)", "object resolves to a MeSHConcept node",
        q("SELECT count(*) FROM trial_mesh tm JOIN mesh m ON m.id = tm.mesh"), q("SELECT count(*) FROM trial_mesh"))

    n_sites = q("SELECT count(*) FROM sites")
    for f in ("name", "city", "state", "country"):
        add("TrialSite", f, q(f"SELECT count(*) FROM sites WHERE {f} IS NOT NULL"), n_sites,
            "facility = name; no postcode or coordinates" if f == "name" else "")
    add("TrialSite", "state, sites in United States",
        q("SELECT count(*) FROM sites WHERE country='United States' AND state IS NOT NULL"),
        q("SELECT count(*) FROM sites WHERE country='United States'"))
    keys = {site_merge_key(n, c, k) for n, c, k in con.sql("SELECT name, city, country FROM sites").fetchall()}
    add("TrialSite", "distinct sites after --merge-sites spelling merge", len(keys), n_sites,
        "basic merge within city and country; coverage = after / before")
    add("ClinicalTrial", "has >=1 CONDUCTED_AT site", q("SELECT count(DISTINCT trial) FROM conducted_at"), n_full)
    n_ca = q("SELECT count(*) FROM conducted_at")
    add("CONDUCTED_AT", "site-level recruitment status on edge",
        q("SELECT count(*) FROM conducted_at WHERE site_status IS NOT NULL"), n_ca)
    add("CONDUCTED_AT", "site-level status, edges of RECRUITING trials",
        q("SELECT count(*) FROM conducted_at c JOIN trials t ON t.id=c.trial "
          "WHERE t.overall_status='RECRUITING' AND c.site_status IS NOT NULL"),
        q("SELECT count(*) FROM conducted_at c JOIN trials t ON t.id=c.trial WHERE t.overall_status='RECRUITING'"))

    n_sp = q("SELECT count(*) FROM sponsors")
    add("Sponsor", "name", q("SELECT count(*) FROM sponsors WHERE name IS NOT NULL"), n_sp, "lower-cased in source")
    add("Sponsor", "class as a node property", 0, n_sp, "class is agency_class on the SPONSORED_BY edge")
    n_sb = q("SELECT count(*) FROM sponsored_by")
    add("SPONSORED_BY", "agency_class", q("SELECT count(*) FROM sponsored_by WHERE agency_class IS NOT NULL"), n_sb)
    add("SPONSORED_BY", "agency_class known (not UNKNOWN/AMBIG/missing)",
        q("SELECT count(*) FROM sponsored_by WHERE agency_class NOT IN ('UNKNOWN','AMBIG')"), n_sb)
    add("SPONSORED_BY", "lead_or_collaborator", q("SELECT count(*) FROM sponsored_by WHERE lead_or_collaborator IS NOT NULL"), n_sb)
    add("ClinicalTrial", "has a LEAD sponsor", q("SELECT count(DISTINCT trial) FROM sponsored_by WHERE lead_or_collaborator='LEAD'"), n_full)
    add("ClinicalTrial", "has >1 LEAD sponsor",
        q("SELECT count(*) FROM (SELECT trial FROM sponsored_by WHERE lead_or_collaborator='LEAD' GROUP BY trial HAVING count(*)>1)"),
        n_full)

    for rel in ("VALIDATED_BY", "CITES_BACKGROUND", "HAS_DERIVED_PUBLICATION"):
        add("ClinicalTrial", f"has >=1 {rel} article", q(f"SELECT count(DISTINCT trial) FROM trial_pubs WHERE rel='{rel}'"), n_full)
    n_res = q("SELECT count(DISTINCT article) FROM trial_pubs WHERE rel='VALIDATED_BY'")
    add("VALIDATED_BY article", "has PubMed record (not ctgov_identity_only stub)",
        q("SELECT count(DISTINCT p.article) FROM trial_pubs p JOIN articles a ON a.id=p.article "
          "WHERE p.rel='VALIDATED_BY' AND a.layer <> 'ctgov_identity_only'"), n_res)
    add("VALIDATED_BY article", "cited >=1 time in-graph (CITES)", q("SELECT count(*) FROM result_citations"), n_res)
    add("VALIDATED_BY article", "cited by >=1 guideline or systematic review in-graph",
        q("SELECT count(DISTINCT c.cited) FROM result_citers c JOIN articles a ON a.id=c.citer "
          "WHERE a.is_guideline OR a.is_systematic_review"), n_res)
    n_art = q("SELECT count(*) FROM articles WHERE layer <> 'ctgov_identity_only'")
    for f, lab in (("is_guideline", "Guideline / Practice Guideline"), ("is_systematic_review", "Systematic Review"),
                   ("is_meta_analysis", "Meta-Analysis")):
        add("Article", f"pub_types includes {lab}", q(f"SELECT count(*) FROM articles WHERE {f}"), n_art)
    return rows


# ---------------------------------------------------------------------------------------------
# Condition resolution and tree-precise hierarchy expansion.
# ---------------------------------------------------------------------------------------------
def resolve(con, condition):
    m = re.fullmatch(r"(?:MESH:)?(D\d{6,9})", condition.strip(), re.I)
    if m:
        rows = con.execute("SELECT id, mesh_id, name FROM mesh WHERE mesh_id = ?", [m.group(1).upper()]).fetchall()
    else:
        rows = con.execute("SELECT id, mesh_id, name FROM mesh WHERE lower(name) = lower(?)", [condition.strip()]).fetchall()
    if not rows:
        near = con.execute("SELECT mesh_id, name FROM mesh WHERE name ILIKE ? ORDER BY length(name) LIMIT 10",
                           [f"%{condition.strip()}%"]).fetchall()
        sys.exit(f"no MeSH descriptor named or with ID '{condition}'. Close matches: "
                 + ("; ".join(f"{i} {n}" for i, n in near) or "none"))
    return rows[0]


def expand(con, root_id):
    """Descendants of root_id walking HAS_BROADER object -> subject, tree-number by tree-number.
    Returns {descriptor_id: depth} (root at depth 0) and the descriptor-level closure size for comparison."""
    by_parent = defaultdict(list)
    tree_numbers = defaultdict(set)
    for child, parent, ctn, ptn in con.sql("SELECT * FROM broader").fetchall():
        ctn, ptn = [x for x in (ctn or "").split("|") if x], [x for x in (ptn or "").split("|") if x]
        by_parent[parent].append((child, ctn))
        tree_numbers[child].update(ctn)
        tree_numbers[parent].update(ptn)
    depth = {root_id: 0}
    frontier = [(root_id, tn) for tn in sorted(tree_numbers[root_id])]
    while frontier:
        nxt = []
        for node, tn in frontier:
            for child, ctns in by_parent[node]:
                for ctn in ctns:
                    if ctn.rsplit(".", 1)[0] == tn:
                        d = depth.get(node, 0) + 1
                        if child not in depth or d < depth[child]:
                            depth[child] = d
                        nxt.append((child, ctn))
        frontier = nxt
    seen, stack = {root_id}, [root_id]
    while stack:
        for child, _ in by_parent[stack.pop()]:
            if child not in seen:
                seen.add(child)
                stack.append(child)
    return depth, len(seen)


# ---------------------------------------------------------------------------------------------
# Landscape queries.
# ---------------------------------------------------------------------------------------------
def class_case(col):
    return f"CASE WHEN {col} IS NULL THEN '{NO_SPONSOR}' " + \
           " ".join(f"WHEN {col} = '{k}' THEN '{v}'" for k, v in CLASS_GROUP.items()) + \
           " ELSE 'Network / individual / unknown' END"


# --merge-sites: a basic, deterministic merge of facility spellings within one city and country
# ("Dana-Farber Cancer Institute" / "Dana Farber Cancer Institute", "M D Anderson" / "MD Anderson").
# It does not resolve different names for the same place ("University of Texas MD Anderson ...").
SITE_ABBREVIATIONS = {"ctr": "center", "centre": "center", "cntr": "center", "hosp": "hospital",
                      "univ": "university", "med": "medical", "inst": "institute", "natl": "national",
                      "dept": "department", "and": "", "the": "", "of": ""}
SITE_SUFFIXES = {"inc", "llc", "ltd", "limited", "pc", "pa", "pllc", "llp", "corp", "corporation", "co",
                 "company", "gmbh", "mbh", "ag", "sa", "sas", "sarl", "srl", "spa", "bv", "nv", "ab", "oy",
                 "as", "aps", "plc", "pty", "kk", "sl", "slu"}


def _norm(text):
    text = unicodedata.normalize("NFKD", (text or "").lower())
    text = "".join(ch for ch in text if not unicodedata.combining(ch)).replace("&", " and ")
    return re.sub(r"[^a-z0-9]+", " ", text).split()


def site_merge_key(name, city, country):
    tokens = [SITE_ABBREVIATIONS.get(w, w) for w in _norm(name)]
    tokens = [w for w in tokens if w]
    while len(tokens) > 1 and tokens[-1] in SITE_SUFFIXES:
        tokens.pop()
    # Join runs of single letters: "m d anderson" -> "md anderson".
    joined = re.sub(r"\b(?:[a-z] )+[a-z]\b", lambda m: m.group(0).replace(" ", ""), " ".join(tokens))
    return f"{joined}|{' '.join(_norm(city))}|{' '.join(_norm(country))}"


def landscape(con, root, depth, out, top_n, merge_sites=False):
    con.execute("CREATE OR REPLACE TEMP TABLE expansion AS SELECT unnest(?::VARCHAR[]) AS mesh, unnest(?::INTEGER[]) AS depth",
                [list(depth), list(depth.values())])
    root_id = root[0]
    con.sql(f"""CREATE OR REPLACE TEMP TABLE matched AS
        SELECT tm.trial,
               bool_or(tm.mesh = '{root_id}') AS direct,
               string_agg(DISTINCT m.name, '; ' ORDER BY m.name) AS matched_descriptors
        FROM trial_mesh tm JOIN expansion e ON e.mesh = tm.mesh JOIN mesh m ON m.id = tm.mesh
        WHERE tm.study_aspect = 'condition' AND tm.mesh_type = 'mesh-list'
        GROUP BY tm.trial""")
    con.sql(f"""CREATE OR REPLACE TEMP TABLE lead AS
        SELECT trial, arg_min(sponsor, sponsor) AS sponsor, arg_min(agency_class, sponsor) AS agency_class
        FROM sponsored_by WHERE lead_or_collaborator = 'LEAD' GROUP BY trial""")
    con.sql(f"""CREATE OR REPLACE TEMP TABLE t AS
        SELECT t.nct_id, t.id, t.title, CASE WHEN m.direct THEN 'direct' ELSE 'narrower' END AS match,
               m.matched_descriptors,
               coalesce(t.overall_status, '(missing)') AS overall_status,
               coalesce(t.phase, '(missing)') AS phase, t.study_type,
               t.start_date, year(try_cast(t.start_date AS DATE)) AS start_year, t.completion_date, t.enrollment,
               s.name AS lead_sponsor, l.agency_class AS lead_agency_class,
               CASE WHEN l.trial IS NULL THEN '{NO_SPONSOR}' ELSE {class_case("coalesce(l.agency_class, 'UNKNOWN')")} END
                 AS lead_sponsor_class,
               (SELECT count(*) FROM conducted_at c WHERE c.trial = t.id) AS n_sites,
               (SELECT count(DISTINCT st.country) FROM conducted_at c JOIN sites st ON st.id = c.site
                 WHERE c.trial = t.id) AS n_countries,
               (SELECT count(*) FROM trial_pubs p WHERE p.trial = t.id AND p.rel = 'VALIDATED_BY') AS n_results_articles
        FROM matched m JOIN trials t ON t.id = m.trial
        LEFT JOIN lead l ON l.trial = t.id LEFT JOIN sponsors s ON s.id = l.sponsor""")

    def save(name, sql):
        con.sql(f"COPY ({sql}) TO '{os.path.join(out, name + '.csv')}' (HEADER)")
        rel = con.sql(sql)
        return rel.columns, rel.fetchall()

    r = {}
    r["trials"] = save("trials", "SELECT * EXCLUDE (id) FROM t ORDER BY start_date DESC NULLS LAST, nct_id")
    r["descriptors"] = save("descriptors", f"""
        SELECT m.mesh_id, m.name, e.depth,
               count(DISTINCT tm.trial) FILTER (WHERE tm.study_aspect='condition' AND tm.mesh_type='mesh-list') AS trials_direct_on_descriptor
        FROM expansion e JOIN mesh m ON m.id = e.mesh LEFT JOIN trial_mesh tm ON tm.mesh = e.mesh
        GROUP BY ALL ORDER BY e.depth, trials_direct_on_descriptor DESC, m.name""")
    r["by_sponsor"] = save("by_sponsor", f"""
        WITH x AS (
            SELECT sb.sponsor, sb.agency_class, sb.lead_or_collaborator, t.nct_id, t.overall_status
            FROM sponsored_by sb JOIN t ON t.id = sb.trial)
        SELECT s.name AS sponsor, mode(x.agency_class) AS agency_class, {class_case("coalesce(mode(x.agency_class), 'UNKNOWN')")} AS sponsor_class,
               count(DISTINCT nct_id) FILTER (WHERE lead_or_collaborator='LEAD') AS trials_as_lead,
               count(DISTINCT nct_id) FILTER (WHERE lead_or_collaborator='COLLABORATOR') AS trials_as_collaborator,
               count(DISTINCT nct_id) FILTER (WHERE lead_or_collaborator='LEAD' AND overall_status='{RECRUITING}') AS recruiting_as_lead
        FROM x JOIN sponsors s ON s.id = x.sponsor
        GROUP BY s.name ORDER BY trials_as_lead DESC, trials_as_collaborator DESC, sponsor""")
    r["by_sponsor_class"] = save("by_sponsor_class", f"""
        SELECT lead_sponsor_class AS sponsor_class, count(*) AS trials,
               count(*) FILTER (WHERE overall_status='{RECRUITING}') AS recruiting
        FROM t GROUP BY 1 ORDER BY trials DESC""")
    r["phase_status"] = save("by_phase_status", """
        SELECT phase, overall_status, count(*) AS trials FROM t GROUP BY ALL ORDER BY phase, overall_status""")
    r["timeline"] = save("timeline_start_year", """
        SELECT start_year, lead_sponsor_class, count(*) AS trials,
               count(*) FILTER (WHERE study_type='INTERVENTIONAL') AS interventional
        FROM t WHERE start_year IS NOT NULL GROUP BY ALL ORDER BY start_year, lead_sponsor_class""")
    # One row per site group: each TrialSite on its own, or merged by site_merge_key() with --merge-sites.
    site_rows = con.sql("SELECT DISTINCT s.id, s.name, s.city, s.country FROM conducted_at c JOIN t ON t.id = c.trial "
                        "JOIN sites s ON s.id = c.site").fetchall()
    con.execute("CREATE OR REPLACE TEMP TABLE site_group AS SELECT unnest(?::VARCHAR[]) AS id, unnest(?::VARCHAR[]) AS grp",
                [[i for i, *_ in site_rows], [site_merge_key(n, c, k) if merge_sites else i for i, n, c, k in site_rows]])
    # Display the spelling attached to the most trial links; list every spelling that was merged.
    site_sql = f"""
        SELECT mode(s.name) AS site, mode(s.city) AS city, mode(s.state) AS state, mode(s.country) AS country,
               count(DISTINCT t.id) AS trials,
               count(DISTINCT t.id) FILTER (WHERE t.overall_status='{RECRUITING}') AS recruiting_trials,
               count(DISTINCT t.id) FILTER (WHERE t.overall_status='{RECRUITING}' AND c.site_status='{RECRUITING}') AS recruiting_site_confirmed,
               count(DISTINCT t.id) FILTER (WHERE t.overall_status='NOT_YET_RECRUITING') AS not_yet_recruiting,
               count(DISTINCT t.lead_sponsor) FILTER (WHERE t.overall_status='{RECRUITING}') AS recruiting_lead_sponsors,
               count(DISTINCT s.id) AS site_records,
               string_agg(DISTINCT s.name, ' | ' ORDER BY s.name) AS name_variants
        FROM conducted_at c JOIN t ON t.id = c.trial JOIN sites s ON s.id = c.site JOIN site_group g ON g.id = s.id
        GROUP BY g.grp"""
    r["sites"] = save("sites", site_sql + " ORDER BY trials DESC, recruiting_trials DESC, site")
    r["sites_recruiting"] = con.sql(site_sql + " HAVING recruiting_trials > 0 ORDER BY recruiting_trials DESC, trials DESC, site "
                                    f"LIMIT {top_n}").fetchall()
    r["countries"] = save("countries", f"""
        SELECT coalesce(s.country, '(missing)') AS country, count(DISTINCT t.id) AS trials, count(DISTINCT g.grp) AS sites,
               count(DISTINCT t.id) FILTER (WHERE t.overall_status='{RECRUITING}') AS recruiting_trials,
               count(DISTINCT g.grp) FILTER (WHERE t.overall_status='{RECRUITING}') AS sites_with_recruiting_trial
        FROM conducted_at c JOIN t ON t.id = c.trial JOIN sites s ON s.id = c.site JOIN site_group g ON g.id = s.id
        GROUP BY 1 ORDER BY trials DESC, country""")
    r["results"] = save("results_publications", """
        WITH cit AS (
            SELECT c.cited, count(*) FILTER (WHERE a.is_guideline) AS cited_by_guidelines,
                   count(*) FILTER (WHERE a.is_systematic_review) AS cited_by_systematic_reviews,
                   count(*) FILTER (WHERE a.is_meta_analysis) AS cited_by_meta_analyses,
                   count(*) FILTER (WHERE a.is_guideline OR a.is_systematic_review) AS cited_by_guideline_or_sr
            FROM result_citers c JOIN articles a ON a.id = c.citer GROUP BY c.cited)
        SELECT t.nct_id, t.title AS trial_title, t.phase, t.lead_sponsor, a.pmid, a.title AS article_title, a.year, a.journal,
               (a.layer = 'ctgov_identity_only') AS article_is_stub,
               coalesce(rc.n_cites, 0) AS cited_in_graph, a.cited_by_count AS cited_by_count_openalex,
               coalesce(cit.cited_by_guidelines, 0) AS cited_by_guidelines,
               coalesce(cit.cited_by_systematic_reviews, 0) AS cited_by_systematic_reviews,
               coalesce(cit.cited_by_meta_analyses, 0) AS cited_by_meta_analyses,
               coalesce(cit.cited_by_guideline_or_sr, 0) AS cited_by_guideline_or_sr
        FROM trial_pubs p JOIN t ON t.id = p.trial LEFT JOIN articles a ON a.id = p.article
        LEFT JOIN result_citations rc ON rc.cited = p.article LEFT JOIN cit ON cit.cited = p.article
        WHERE p.rel = 'VALIDATED_BY'
        ORDER BY cited_by_guideline_or_sr DESC, cited_in_graph DESC, t.nct_id""")
    q = lambda s: con.execute(s).fetchall()[0][0]
    ctgov = q(f"SELECT count(DISTINCT trial) FROM trial_mesh WHERE study_aspect='condition' AND mesh='{root_id}'")
    both = q(f"SELECT count(*) FROM (SELECT DISTINCT trial FROM trial_mesh WHERE study_aspect='condition' AND mesh='{root_id}') "
             f"JOIN t ON t.id = trial")
    r["summary"] = {
        "trials": q("SELECT count(*) FROM t"),
        "trials_direct": q("SELECT count(*) FROM t WHERE match='direct'"),
        "trials_narrower_only": q("SELECT count(*) FROM t WHERE match='narrower'"),
        "recruiting": q(f"SELECT count(*) FROM t WHERE overall_status='{RECRUITING}'"),
        "not_yet_recruiting": q("SELECT count(*) FROM t WHERE overall_status='NOT_YET_RECRUITING'"),
        "interventional": q("SELECT count(*) FROM t WHERE study_type='INTERVENTIONAL'"),
        "lead_sponsors": q("SELECT count(DISTINCT lead_sponsor) FROM t"),
        "trials_with_sites": q("SELECT count(*) FROM t WHERE n_sites > 0"),
        "trials_without_sponsor_record": q(f"SELECT count(*) FROM t WHERE lead_sponsor_class = '{NO_SPONSOR}'"),
        "recruiting_without_sponsor_record": q(f"SELECT count(*) FROM t WHERE overall_status='{RECRUITING}' "
                                              f"AND lead_sponsor_class = '{NO_SPONSOR}'"),
        "site_merge": merge_sites,
        "sites_before_merge": len(site_rows),
        "sites": q("SELECT count(DISTINCT grp) FROM site_group"),
        "countries": q("SELECT count(DISTINCT s.country) FROM conducted_at c JOIN t ON t.id = c.trial JOIN sites s ON s.id = c.site"),
        "trials_with_results_article": q("SELECT count(*) FROM t WHERE n_results_articles > 0"),
        "results_articles": len(r["results"][1]),
        "results_articles_cited_by_guideline_or_sr": sum(1 for row in r["results"][1] if row[-1] > 0),
        "crosscheck_ctgov_ancestor_terms_trials": ctgov,
        "crosscheck_ctgov_trials_also_in_our_expansion": both,
    }
    return r


# ---------------------------------------------------------------------------------------------
# HTML report: inline SVG, no external assets, light and dark themes.
# ---------------------------------------------------------------------------------------------
E = lambda s: html.escape("" if s is None else str(s))
FMT = lambda n: f"{n:,}" if isinstance(n, int) else E(n)

CSS = """
:root{color-scheme:light;--surface:#fcfcfb;--panel:#ffffff;--border:#e4e3df;--text:#0b0b0b;--text2:#52514e;--muted:#8a8984;
--grid:#ecebe7;--s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;--s4:#eda100;--context:#c9c8c2;--seq0:#f4f8fd;--seq1:#cde2fb;--seq2:#86b6ef;--seq3:#2a78d6;--seq4:#184f95}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){color-scheme:dark;--surface:#1a1a19;--panel:#222220;--border:#383835;--text:#f0efec;
--text2:#c3c2b7;--muted:#8f8e86;--grid:#2e2e2b;--s1:#3987e5;--s2:#d95926;--s3:#199e70;--s4:#c98500;--context:#55544f;--seq0:#20242b;--seq1:#184f95;--seq2:#256abf;--seq3:#3987e5;--seq4:#9ec5f4}}
:root[data-theme="dark"]{color-scheme:dark;--surface:#1a1a19;--panel:#222220;--border:#383835;--text:#f0efec;--text2:#c3c2b7;--muted:#8f8e86;
--grid:#2e2e2b;--s1:#3987e5;--s2:#d95926;--s3:#199e70;--s4:#c98500;--context:#55544f;--seq0:#20242b;--seq1:#184f95;--seq2:#256abf;--seq3:#3987e5;--seq4:#9ec5f4}
*{box-sizing:border-box}body{margin:0;background:var(--surface);color:var(--text);font:14px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:1120px;margin:0 auto;padding:24px 16px 64px}h1{font-size:24px;margin:0 0 4px}h2{font-size:17px;margin:36px 0 4px}
.sub{color:var(--text2);margin:0 0 4px}.note{color:var(--text2);font-size:12.5px;margin:4px 0 10px;max-width:880px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:18px 0}
.tile{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:10px 12px}.tile b{display:block;font-size:22px;font-variant-numeric:tabular-nums}
.tile span{color:var(--text2);font-size:12px}.panel{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:12px;overflow-x:auto}
svg{display:block;max-width:100%;height:auto}svg text{fill:var(--text2);font-size:11px}svg .val{fill:var(--text)}svg .grid{stroke:var(--grid)}
svg rect.mark:hover{opacity:.8}.legend{display:flex;flex-wrap:wrap;gap:14px;font-size:12px;color:var(--text2);margin:2px 0 8px}
.legend i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:5px;vertical-align:-1px}
table{border-collapse:collapse;width:100%;font-size:12.5px}th,td{padding:5px 8px;border-bottom:1px solid var(--border);text-align:left;vertical-align:top}
th{color:var(--text2);font-weight:600}td.n,th.n{text-align:right;font-variant-numeric:tabular-nums}
td.h0{background:var(--seq0)}td.h1{background:var(--seq1)}td.h2{background:var(--seq2)}td.h3{background:var(--seq3);color:#fff}td.h4{background:var(--seq4);color:#fff}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) td.h4{color:#0b0b0b}}:root[data-theme="dark"] td.h4{color:#0b0b0b}
details{margin-top:8px}summary{cursor:pointer;color:var(--text2);font-size:12.5px}a{color:var(--s1)}
"""


def svg_hbars(rows, series, value_fmt=FMT, label_w=260, width=760):
    """rows: [(label, [v1, v2, ...], tooltip)], stacked left to right in series order."""
    if not rows:
        return "<p class='note'>No rows.</p>"
    bar_h, gap, top = 16, 8, 6
    vmax = max(sum(v) for _, v, _ in rows) or 1
    plot_w = width - label_w - 60
    h = top + len(rows) * (bar_h + gap) + 4
    out = [f"<svg viewBox='0 0 {width} {h}' role='img'>"]
    for i, (label, vals, tip) in enumerate(rows):
        y = top + i * (bar_h + gap)
        short = label if len(label) <= 42 else label[:40] + "…"
        out.append(f"<text x='{label_w - 8}' y='{y + 12}' text-anchor='end'><title>{E(label)}</title>{E(short)}</text>")
        x = label_w
        for (sname, color), v in zip(series, vals):
            w = plot_w * v / vmax
            if w > 0:
                out.append(f"<rect class='mark' x='{x:.1f}' y='{y}' width='{max(w - 2, 1):.1f}' height='{bar_h}' rx='3' "
                           f"fill='var({color})'><title>{E(label)} - {E(sname)}: {value_fmt(v)}{E(tip)}</title></rect>")
            x += w
        out.append(f"<text class='val' x='{x + 6:.1f}' y='{y + 12}'>{value_fmt(sum(vals))}</text>")
    out.append("</svg>")
    return "".join(out)


def svg_columns(years, stacks, series, width=1060, height=240):
    """stacks[year] = [v per series]; stacked columns with a single y axis."""
    if not years:
        return "<p class='note'>No start dates.</p>"
    left, bottom, top = 40, 22, 10
    plot_w, plot_h = width - left - 10, height - bottom - top
    vmax = max(sum(stacks[y]) for y in years) or 1
    step = 10 ** max(len(str(vmax)) - 1, 0)
    tick = next(s for s in (step, 2 * step, 5 * step, 10 * step) if vmax / s <= 5)
    col_w = plot_w / len(years)
    out = [f"<svg viewBox='0 0 {width} {height}' role='img'>"]
    for k in range(0, vmax + tick, tick):
        y = top + plot_h - plot_h * k / vmax
        if y < top - 1:
            break
        out.append(f"<line class='grid' x1='{left}' x2='{width - 10}' y1='{y:.1f}' y2='{y:.1f}'/>"
                   f"<text x='{left - 6}' y='{y + 4:.1f}' text-anchor='end'>{k:,}</text>")
    label_every = max(1, round(len(years) / 18))
    for i, yr in enumerate(years):
        x = left + i * col_w
        base = top + plot_h
        for (sname, color), v in zip(series, stacks[yr]):
            hgt = plot_h * v / vmax
            if hgt > 0:
                out.append(f"<rect class='mark' x='{x + 1:.1f}' y='{base - hgt:.1f}' width='{max(col_w - 2, 1):.1f}' "
                           f"height='{max(hgt - 1, 0.5):.1f}' rx='2' fill='var({color})'><title>{yr} - {E(sname)}: {v:,} "
                           f"(year total {sum(stacks[yr]):,})</title></rect>")
            base -= hgt
        if i % label_every == 0:
            out.append(f"<text x='{x + col_w / 2:.1f}' y='{height - 6}' text-anchor='middle'>{yr}</text>")
    out.append("</svg>")
    return "".join(out)


def legend(series):
    return "<div class='legend'>" + "".join(f"<span><i style='background:var({c})'></i>{E(n)}</span>" for n, c in series) + "</div>"


def table(cols, rows, numeric=(), limit=None, link_nct=False):
    head = "".join(f"<th class='{'n' if c in numeric else ''}'>{E(c)}</th>" for c in cols)
    body = []
    for row in rows[:limit]:
        cells = []
        for c, v in zip(cols, row):
            if link_nct and c == "nct_id" and v:
                cells.append(f"<td><a href='https://clinicaltrials.gov/study/{E(v)}'>{E(v)}</a></td>")
            elif c == "pmid" and v:
                cells.append(f"<td><a href='https://pubmed.ncbi.nlm.nih.gov/{E(v)}/'>{E(v)}</a></td>")
            else:
                cells.append(f"<td class='{'n' if c in numeric else ''}'>{FMT(v)}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def heat_table(cells, rows_order, cols_order):
    rows = [r for r in rows_order if any(cells.get((r, c)) for c in cols_order)]
    cols = [c for c in cols_order if any(cells.get((r, c)) for r in rows_order)]
    vmax = max(cells.values() or [1])
    head = "<th>phase \\ status</th>" + "".join(f"<th class='n'>{E(c)}</th>" for c in cols) + "<th class='n'>total</th>"
    body = []
    for r in rows:
        tds = []
        for c in cols:
            v = cells.get((r, c), 0)
            lvl = 0 if not v else min(4, 1 + int(3.999 * v / vmax))
            tds.append(f"<td class='n h{lvl}' title='{E(r)} / {E(c)}: {v:,}'>{v:,}</td>" if v else "<td class='n'></td>")
        body.append(f"<tr><th>{E(r)}</th>{''.join(tds)}<td class='n'><b>{sum(cells.get((r, c), 0) for c in cols):,}</b></td></tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def ancestor_gap_note(s, root):
    """Warn when ClinicalTrials.gov's own ancestor terms place more trials under the condition than its
    explicit terms reach: the usual cause is a narrower browse term the release failed to link to MeSH
    (v0.2.x matched CT.gov's inverted-form names such as 'Pain, Postoperative' against natural-form
    descriptor names, so those descriptors have no trial edges)."""
    missed = s["crosscheck_ctgov_ancestor_terms_trials"] - s["crosscheck_ctgov_trials_also_in_our_expansion"]
    if missed <= 0:
        return ""
    return (f"<p class='note'><b>Possible missing trials:</b> ClinicalTrials.gov's own ancestor terms place {missed:,} more trials "
            f"under {E(root[2])} than this report finds through explicit condition terms. Their narrower browse term most likely "
            f"did not link to a MeSH descriptor in this release (a known name-form mismatch; for example Major Depressive Disorder "
            f"and Postoperative Pain have no trial edges in v0.2.x). They are not included here.</p>")


def site_merge_note(s):
    if s["site_merge"]:
        return (f"Facility spellings are merged within each city and country (--merge-sites: case, punctuation and common "
                f"suffixes): {s['sites_before_merge']:,} registered sites become {s['sites']:,}. Different names for the same place "
                f"are not merged; sites.csv lists the spellings behind each row.")
    return ("A site is one facility name + city + state + country as registered, so the same hospital spelled two ways counts "
            "twice; rerun with --merge-sites to merge spellings.")


def render_html(root, r, depth_n, closure_n, run_s, top_n, release):
    s = r["summary"]
    cls_series = list(zip(CLASS_ORDER, ["--s1", "--s2", "--s3", "--s4", "--context"]))
    _, tl = r["timeline"]
    stacks = defaultdict(lambda: [0] * len(CLASS_ORDER))
    for yr, cls, n, _ in tl:
        stacks[yr][CLASS_ORDER.index(cls)] += n
    dated = sum(sum(v) for v in stacks.values())
    # Drop the sparse tails (years under 1% of the peak year) so the busy decades get the width.
    peak = max((sum(v) for v in stacks.values()), default=0)
    kept = [y for y, v in stacks.items() if sum(v) >= 0.01 * peak]
    years = list(range(min(kept), max(kept) + 1)) if kept else []
    outside = dated - sum(sum(stacks[y]) for y in years)
    scols, srows = r["by_sponsor"]
    top_sponsors = [(row[0], [row[3]], f" | class {row[1]} | recruiting {row[5]:,} | collaborator on {row[4]:,}")
                    for row in srows if row[3] > 0][:top_n]
    sponsor_rows = [row for row in srows if row[3] > 0]
    _, cls_rows = r["by_sponsor_class"]
    rec = ("Recruiting", "--s1"), ("Other statuses", "--context")
    sites_cols, sites = r["sites"]
    top_sites = [(f"{row[0]} ({row[1] or '?'}, {row[3] or '?'})", [row[5], row[4] - row[5]],
                  f" | site-confirmed recruiting {row[6]:,} | not yet recruiting {row[7]:,}") for row in sites[:top_n]]
    dens = [(f"{row[0]} ({row[1] or '?'}, {row[3] or '?'})", [row[5]], f" | of {row[4]:,} matching trials here")
            for row in r["sites_recruiting"]]
    ccols, countries = r["countries"]
    top_countries = [(row[0], [row[3], row[1] - row[3]], f" | {row[2]:,} sites") for row in countries[:top_n]]
    phase_cells = {(p, st): n for p, st, n in r["phase_status"][1]}
    res_cols, res = r["results"]
    tcols, trials = r["trials"]
    dcols, drows = r["descriptors"]
    tiles = [("matching trials", s["trials"]), ("direct on the descriptor", s["trials_direct"]),
             ("via narrower descriptors only", s["trials_narrower_only"]), ("recruiting now", s["recruiting"]),
             ("lead sponsors", s["lead_sponsors"]), ("sites", s["sites"]), ("countries", s["countries"]),
             ("trials with results articles", s["trials_with_results_article"])]
    parts = [f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Trial landscape: {E(root[2])}</title><style>{CSS}</style></head><body><main>
<h1>Clinical trial landscape: {E(root[2])}</h1>
<p class="sub">MeSH {E(root[1])} and {depth_n - 1:,} narrower descriptors · source: {E(release)} · generated in {run_s:.1f}s</p>
<p class="note">A trial matches when ClinicalTrials.gov lists the descriptor, or one of its narrower descriptors, among the trial's
condition browse terms (graph edge ClinicalTrial -HAS_MESH {{study_aspect:'condition', mesh_type:'mesh-list'}}-> MeSHConcept).
"Recruiting" is the trial's overall status in the registry snapshot, not a live feed. Hover any bar for exact values.</p>
<div class="tiles">{''.join(f"<div class='tile'><b>{v:,}</b><span>{E(k)}</span></div>" for k, v in tiles)}</div>
<p class="note"><b>Coverage gap in this release:</b> {s['trials_without_sponsor_record']:,} matching trials (the newest registrations)
have no sponsor or site records, including {s['recruiting_without_sponsor_record']:,} of the {s['recruiting']:,} recruiting ones. They are counted
in trial totals, phase and status, shown as "{NO_SPONSOR}" in the timeline, and missing from every sponsor, site and country figure.</p>
{ancestor_gap_note(s, root)}

<h2>Trials started per year, by lead sponsor class</h2>
<p class="note">Start year from the registry start date (month-precision dates are stored as the last day of the month, so use years).
Years after the snapshot are planned starts. Not shown: {s['trials'] - dated:,} trials with no start date and {outside:,} in sparse
years outside {years[0] if years else ''}–{years[-1] if years else ''} (all in timeline_start_year.csv).</p>
<div class="panel">{legend(cls_series)}{svg_columns(years, stacks, cls_series)}</div>

<h2>Lead sponsors</h2>
<p class="note">Top {top_n} sponsors by number of matching trials they lead. Sponsor names are lower-cased in the source.</p>
<div class="panel">{svg_hbars(top_sponsors, [('Trials as lead', '--s1')])}</div>
<details><summary>All {len(sponsor_rows):,} lead sponsors (table)</summary>{table(scols, sponsor_rows, numeric=scols[3:])}</details>

<h2>Sponsor class</h2>
<p class="note">ClinicalTrials.gov agency class of the lead sponsor. It has no "academic" class: universities and hospitals are filed as OTHER.</p>
<div class="panel">{table(["sponsor_class", "trials", "recruiting"], cls_rows, numeric=("trials", "recruiting"))}</div>

<h2>Phase by overall status</h2>
<p class="note">NA means phase not applicable (device, behavioural and most other non-drug trials); (missing) is mostly observational studies.</p>
<div class="panel">{heat_table(phase_cells, PHASE_ORDER, STATUS_ORDER)}</div>

<h2>Where the trials run: top sites</h2>
<p class="note">Top {top_n} sites by number of matching trials; the blue part is trials recruiting now. {site_merge_note(s)}</p>
<div class="panel">{legend(rec)}{svg_hbars(top_sites, rec)}</div>

<h2>Competing-trial density: sites with the most recruiting trials</h2>
<p class="note">Matching trials currently recruiting at each site. The CSV adds site_confirmed (the registry's own per-site status also says
RECRUITING) and the number of distinct lead sponsors competing there.</p>
<div class="panel">{svg_hbars(dens, [('Recruiting trials', '--s1')])}</div>
<details><summary>Top {top_n} sites (table; all {len(sites):,} in sites.csv)</summary>{table(sites_cols, sites[:top_n], numeric=sites_cols[4:10])}</details>

<h2>Countries</h2>
<div class="panel">{legend(rec)}{svg_hbars(top_countries, rec, label_w=180)}</div>
<details><summary>All {len(countries):,} countries (table)</summary>{table(ccols, countries, numeric=ccols[1:])}</details>

<h2>Published results and their uptake</h2>
<p class="note">{s['trials_with_results_article']:,} of {s['trials']:,} matching trials have at least one results article (VALIDATED_BY, the
RESULT role: Article -> ClinicalTrial). {s['results_articles']:,} results-article links; {s['results_articles_cited_by_guideline_or_sr']:,} of them are
cited in-graph by at least one guideline or systematic review (NLM publication types Guideline / Practice Guideline / Systematic Review;
in-graph CITES only, so citations from papers outside the graph are not counted). Top 25 below; all in results_publications.csv.</p>
<div class="panel">{table(['nct_id', 'pmid', 'article_title', 'year', 'cited_in_graph', 'cited_by_guidelines', 'cited_by_systematic_reviews', 'cited_by_meta_analyses'],
                         [[row[0], row[4], row[5], row[6], row[9], row[11], row[12], row[13]] for row in res], numeric=('year', 'cited_in_graph', 'cited_by_guidelines', 'cited_by_systematic_reviews', 'cited_by_meta_analyses'), limit=25, link_nct=True)}</div>

<h2>Condition expansion</h2>
<p class="note">{depth_n:,} descriptors (the query plus everything below it in its own MeSH tree branches; a descriptor-level walk that ignored
tree numbers would have reached {closure_n:,}). Cross-check: ClinicalTrials.gov's own ancestor terms put {s['crosscheck_ctgov_ancestor_terms_trials']:,}
trials under {E(root[2])}; {s['crosscheck_ctgov_trials_also_in_our_expansion']:,} of them are in this report.</p>
<details><summary>Descriptors (table)</summary>{table(dcols, drows, numeric=('depth', 'trials_direct_on_descriptor'))}</details>

<h2>Trials</h2>
<details><summary>Newest 200 of {len(trials):,} matching trials (all in trials.csv)</summary>
{table(['nct_id', 'title', 'match', 'overall_status', 'phase', 'start_year', 'enrollment', 'lead_sponsor', 'n_sites'],
       [[row[tcols.index(c)] for c in ['nct_id', 'title', 'match', 'overall_status', 'phase', 'start_year', 'enrollment', 'lead_sponsor', 'n_sites']] for row in trials],
       numeric=('start_year', 'enrollment', 'n_sites'), limit=200, link_nct=True)}</details>
<p class="note" style="margin-top:28px">Built by examples/trial_landscape.py from the published Lunas Clinical Evidence KG files (CC0). Trial data
originate from ClinicalTrials.gov; MeSH from the U.S. National Library of Medicine.</p>
</main></body></html>"""]
    return "".join(parts)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", required=True, help="release folder (Hugging Face or Zenodo layout)")
    ap.add_argument("--condition", help="MeSH descriptor name (exact, case-insensitive) or ID (D001249 / MESH:D001249)")
    ap.add_argument("--out", help="output folder (default trial_landscape_out/<descriptor id>)")
    ap.add_argument("--cache", help="Parquet cache folder (default <input>/trial_landscape_cache)")
    ap.add_argument("--rebuild-cache", action="store_true")
    ap.add_argument("--workers", type=int, default=min(16, os.cpu_count() or 4))
    ap.add_argument("--top", type=int, default=25, help="rows shown in the report's ranked charts")
    ap.add_argument("--merge-sites", action="store_true",
                    help="merge facility spellings within a city and country (case, punctuation, common suffixes); "
                         "reports site counts before and after")
    ap.add_argument("--data-check", action="store_true", help="write data_check.csv (field, coverage, denominator) and exit")
    a = ap.parse_args()
    if not a.condition and not a.data_check:
        ap.error("give --condition or --data-check")
    cache = a.cache or os.path.join(a.input, "trial_landscape_cache")
    meta_path = os.path.join(cache, "meta.json")
    if a.rebuild_cache or not os.path.exists(meta_path) or json.load(open(meta_path)).get("cache_version") != CACHE_VERSION:
        os.makedirs(cache, exist_ok=True)
        build_cache(a.input, cache, a.workers)
    con = open_cache(cache)
    release = "Lunas Clinical Evidence KG"
    man = os.path.join(a.input, "manifest.json")
    if os.path.exists(man):
        m = json.load(open(man))
        release += f" v{m.get('version')} (snapshot {m.get('snapshot_date')})"

    if a.data_check:
        out = a.out or "trial_landscape_out"
        os.makedirs(out, exist_ok=True)
        rows = data_check(con)
        with open(os.path.join(out, "data_check.csv"), "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["entity", "field", "count", "denominator", "coverage_pct", "note"])
            w.writerows(rows)
        for e, f, n, d, p, note in rows:
            print(f"{e:22} {f:72} {n:>11,} / {d:>11,}  {'' if p is None else f'{p:6.2f}%'}  {note}")
        print(f"\nwrote {os.path.join(out, 'data_check.csv')}")
        return

    t0 = time.time()
    root = resolve(con, a.condition)
    depth, closure_n = expand(con, root[0])
    out = a.out or os.path.join("trial_landscape_out", root[1])
    os.makedirs(out, exist_ok=True)
    r = landscape(con, root, depth, out, a.top, a.merge_sites)
    run_s = time.time() - t0
    with open(os.path.join(out, "report.html"), "w") as fh:
        fh.write(render_html(root, r, len(depth), closure_n, run_s, a.top, release))
    summary = {"condition": {"id": root[0], "mesh_id": root[1], "name": root[2]}, "release": release,
               "descriptors_in_expansion": len(depth), "descriptor_level_closure": closure_n,
               **r["summary"], "csv_rows": {k: len(v[1]) for k, v in r.items() if isinstance(v, tuple)},
               "run_seconds": round(run_s, 2)}
    json.dump(summary, open(os.path.join(out, "summary.json"), "w"), indent=1)
    print(json.dumps(summary, indent=1))
    print(f"\nwrote {out}/report.html and CSVs")


if __name__ == "__main__":
    main()
