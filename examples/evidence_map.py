#!/usr/bin/env python3
"""Evidence map for a MeSH descriptor, from the published Lunas Clinical Evidence KG files.

  pip install duckdb
  python examples/evidence_map.py --input ckg --condition "Heart Failure"        # name or D006333 / MESH:D006333
  python examples/evidence_map.py --input ckg --condition D001943 --exclude-stubs --out out/breast
  python examples/evidence_map.py --input ckg --condition D012516 --expansion none --major-only

For the descriptor (and, by default, every narrower descriptor) it counts the indexed Articles by study
design, then asks which primary studies (randomized and other clinical trials) are cited by an in-graph
guideline, systematic review or meta-analysis. Output: summary.json, design.csv, primary_studies.csv,
citing_reviews.csv, recent_reviews.csv (guidelines and SR/MA from 2022-2026 with PMID, title and year),
expansion.csv, a self-contained report.html and a GitHub-readable README.md.

Only the files listed in manifest.json (Hugging Face) or zenodo_manifest.json (Zenodo) are read; without
either (e.g. the sample subgraph) every nodes/edges file is read.

Definitions (all from the released files):
  Articles      (Article)-[:HAS_MESH]->(MeSHConcept) to any descriptor in the expansion; --major-only keeps
                is_major_topic = true edges only.
  Expansion     full (default): the descriptor plus every HAS_BROADER_ANCESTOR subject whose object is the
                descriptor (HAS_BROADER_ANCESTOR points narrower -> broader and follows MeSH tree numbers);
                none: the descriptor only. The 40 MeSH check tags (Humans, Female, Aged, ...) are never used.
  Design        one per Article, first match in this order, from NLM publication types (pub_types):
                guideline      Guideline, Practice Guideline
                sr_or_ma       Systematic Review, Meta-Analysis, Network Meta-Analysis
                rct            Randomized Controlled Trial (incl. Veterinary)
                other_trial    Clinical Trial, Clinical Trial Phase I-IV, Controlled Clinical Trial, Pragmatic
                               Clinical Trial, Equivalence Trial, Adaptive Clinical Trial, Clinical Trial Veterinary
                observational  Observational Study (incl. Veterinary)
                other          everything else (Clinical Trial Protocol is a protocol, not a trial report: other)
  Primary study design rct or other_trial.
  Citing review any in-graph Article with a guideline, systematic review or meta-analysis publication type
                (it does not have to be in the map). CITES edges from an Article to itself are dropped.
  Stubs         --exclude-stubs removes identity-only Articles (lunasai_layer = ctgov_identity_only) from the
                map and from the citing reviews. In v0.2.x stubs carry no pub_types, MeSH or CITES edges,
                so for MeSH-based maps both populations give the same numbers.

The first run reads the node and edge files once (about a minute on 16+ cores for the full release) and
caches what it needs as Parquet in <input>/evidence_map_cache; later runs take seconds.
"""
import argparse, json, os, re, sys, time

try:
    import duckdb
except ImportError:
    sys.exit("pip install duckdb")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trial_landscape import glob_for  # noqa: E402  (same manifest-only file selection)

CACHE_VERSION = 1
STUB_LAYER = "ctgov_identity_only"
GUIDELINE = ["Guideline", "Practice Guideline"]
SR_OR_MA = ["Systematic Review", "Meta-Analysis", "Network Meta-Analysis"]
RCT = ["Randomized Controlled Trial", "Randomized Controlled Trial, Veterinary"]
OTHER_TRIAL = ["Clinical Trial", "Clinical Trial, Phase I", "Clinical Trial, Phase II", "Clinical Trial, Phase III",
               "Clinical Trial, Phase IV", "Controlled Clinical Trial", "Pragmatic Clinical Trial", "Equivalence Trial",
               "Adaptive Clinical Trial", "Clinical Trial, Veterinary"]
OBSERVATIONAL = ["Observational Study", "Observational Study, Veterinary"]
DESIGNS = ["guideline", "sr_or_ma", "rct", "other_trial", "observational", "other"]
CHECK_TAGS = [
    "Adolescent", "Adult", "Aged", "Aged, 80 and over", "Animals", "Bees", "Cats", "Cattle", "Chick Embryo", "Child",
    "Child, Preschool", "Chlorocebus aethiops", "Cricetinae", "Dogs", "Female", "Guinea Pigs", "History of Medicine",
    "History, 15th Century", "History, 16th Century", "History, 17th Century", "History, 18th Century",
    "History, 19th Century", "History, 20th Century", "History, 21st Century", "History, Ancient", "History, Medieval",
    "Horses", "Humans", "Infant", "Infant, Newborn", "Male", "Mice", "Middle Aged", "Pregnancy", "Rabbits", "Rats",
    "Sheep", "Swine", "United States", "Young Adult"]


def lst(values):
    return "[" + ", ".join("'" + v.replace("'", "''") + "'" for v in values) + "]"


DESIGN_SQL = (f"CASE WHEN list_has_any(pub_types, {lst(GUIDELINE)}) THEN 'guideline' "
              f"WHEN list_has_any(pub_types, {lst(SR_OR_MA)}) THEN 'sr_or_ma' "
              f"WHEN list_has_any(pub_types, {lst(RCT)}) THEN 'rct' "
              f"WHEN list_has_any(pub_types, {lst(OTHER_TRIAL)}) THEN 'other_trial' "
              f"WHEN list_has_any(pub_types, {lst(OBSERVATIONAL)}) THEN 'observational' ELSE 'other' END")


def build_cache(input_dir, cache):
    t0 = time.time()
    nodes, edges = glob_for(input_dir, "nodes"), glob_for(input_dir, "edges")
    con = duckdb.connect()
    ncols = "{'id': 'VARCHAR', 'lunasai_labels': 'VARCHAR[]', 'lunasai_layer': 'VARCHAR', 'name': 'VARCHAR', " \
            "'mesh_id': 'VARCHAR', 'pmid': 'VARCHAR', 'year': 'VARCHAR', 'pub_types': 'VARCHAR[]'}"
    ecols = "{'subject': 'VARCHAR', 'object': 'VARCHAR', 'original_predicate': 'VARCHAR', " \
            "'is_major_topic': 'BOOLEAN', 'depth': 'INTEGER'}"
    print(f"[cache] reading {len(nodes)} node files", flush=True)
    con.execute(f"CREATE TABLE n AS SELECT id, lunasai_labels[1] AS label, lunasai_layer AS layer, name, mesh_id, pmid, "
                f"try_cast(year AS INTEGER) AS year, coalesce(pub_types, []) AS pub_types "
                f"FROM read_json(?, format='newline_delimited', columns={ncols}) "
                f"WHERE lunasai_labels[1] IN ('Article', 'MeSHConcept')", [nodes])
    con.execute(f"COPY (SELECT id, pmid, name AS title, year, layer = '{STUB_LAYER}' AS stub, {DESIGN_SQL} AS design, "
                f"list_has_any(pub_types, {lst(GUIDELINE + SR_OR_MA)}) AS review, pub_types "
                f"FROM n WHERE label = 'Article') TO '{cache}/articles.parquet' (FORMAT parquet)")
    con.execute(f"COPY (SELECT id, mesh_id, name, name IN (SELECT unnest(?::VARCHAR[])) AS check_tag FROM n "
                f"WHERE label = 'MeSHConcept') TO '{cache}/mesh.parquet' (FORMAT parquet)", [CHECK_TAGS])
    print(f"[cache] reading {len(edges)} edge files (HAS_MESH, CITES, HAS_BROADER_ANCESTOR)", flush=True)
    con.execute(f"CREATE TABLE e AS SELECT subject, object, split_part(original_predicate, '.', -1) AS type, "
                f"is_major_topic, depth FROM read_json(?, format='newline_delimited', columns={ecols}) "
                f"WHERE split_part(original_predicate, '.', -1) IN ('HAS_MESH', 'CITES', 'HAS_BROADER_ANCESTOR')", [edges])
    con.execute(f"COPY (SELECT e.subject AS article, e.object AS descriptor, coalesce(e.is_major_topic, false) AS major "
                f"FROM e WHERE e.type = 'HAS_MESH' AND e.subject IN (SELECT id FROM n WHERE label = 'Article')) "
                f"TO '{cache}/article_mesh.parquet' (FORMAT parquet)")
    self_links = con.execute("SELECT count(*) FROM e WHERE type = 'CITES' AND subject = object").fetchone()[0]
    con.execute(f"COPY (SELECT subject AS citer, object AS cited FROM e WHERE type = 'CITES' AND subject <> object) "
                f"TO '{cache}/cites.parquet' (FORMAT parquet)")
    con.execute(f"COPY (SELECT subject AS child, object AS parent, depth FROM e WHERE type = 'HAS_BROADER_ANCESTOR') "
                f"TO '{cache}/broader_ancestor.parquet' (FORMAT parquet)")
    meta = {"cache_version": CACHE_VERSION, "input": os.path.abspath(input_dir), "built_seconds": round(time.time() - t0, 1),
            "cites_self_links_dropped": self_links,
            "node_files": [os.path.basename(f) for f in nodes], "edge_files": [os.path.basename(f) for f in edges]}
    json.dump(meta, open(os.path.join(cache, "meta.json"), "w"), indent=1)
    print(f"[cache] built in {meta['built_seconds']}s -> {cache}", flush=True)


def open_cache(cache):
    con = duckdb.connect()
    for t in ("articles", "mesh", "article_mesh", "cites", "broader_ancestor"):
        con.execute(f"CREATE VIEW {t} AS SELECT * FROM read_parquet('{os.path.join(cache, t + '.parquet')}')")
    return con


def resolve(con, condition):
    m = re.fullmatch(r"(?:MESH:)?(D\d{6,9})", condition.strip(), re.I)
    if m:
        rows = con.execute("SELECT id, mesh_id, name FROM mesh WHERE mesh_id = ?", [m.group(1).upper()]).fetchall()
    else:
        rows = con.execute("SELECT id, mesh_id, name FROM mesh WHERE lower(name) = lower(?)", [condition.strip()]).fetchall()
    if not rows:
        sys.exit(f"no MeSH descriptor named or with ID '{condition}'")
    return rows[0]


def evidence_map(con, root_id, expansion="full", exclude_stubs=False, major_only=False):
    """Returns (summary dict, {table name: (columns, rows)}). Pure SQL over the cache views."""
    con.execute("CREATE OR REPLACE TEMP TABLE exp AS SELECT ? AS descriptor, 0 AS depth"
                + (" UNION SELECT child, min(depth) FROM broader_ancestor WHERE parent = ? GROUP BY child"
                   if expansion == "full" else ""), [root_id, root_id] if expansion == "full" else [root_id])
    con.execute("DELETE FROM exp WHERE descriptor IN (SELECT id FROM mesh WHERE check_tag)")
    stub_filter = "AND NOT a.stub" if exclude_stubs else ""
    con.execute(f"""CREATE OR REPLACE TEMP TABLE map AS
        SELECT DISTINCT a.id, a.pmid, a.title, a.year, a.design FROM article_mesh am JOIN exp USING (descriptor)
        JOIN articles a ON a.id = am.article WHERE {'am.major' if major_only else 'true'} {stub_filter}""")
    con.execute(f"""CREATE OR REPLACE TEMP TABLE pc AS
        SELECT m.id AS primary_id, m.design, c.citer FROM map m JOIN cites c ON c.cited = m.id
        JOIN articles a ON a.id = c.citer AND a.review WHERE m.design IN ('rct', 'other_trial') {stub_filter}""")
    q = lambda s: con.execute(s).fetchone()[0]
    design = {d: q(f"SELECT count(*) FROM map WHERE design = '{d}'") for d in DESIGNS}
    primary = design["rct"] + design["other_trial"]
    cited = q("SELECT count(DISTINCT primary_id) FROM pc")
    summary = {
        "descriptors_in_expansion": q("SELECT count(*) FROM exp"),
        "articles": q("SELECT count(*) FROM map"),
        "by_design": design,
        "primary_studies": primary,
        "primary_cited_by_review": cited,
        "primary_not_cited_by_review": primary - cited,
        "rct_cited_by_review": q("SELECT count(DISTINCT primary_id) FROM pc WHERE design = 'rct'"),
        "other_trial_cited_by_review": q("SELECT count(DISTINCT primary_id) FROM pc WHERE design = 'other_trial'"),
        "distinct_citing_reviews": q("SELECT count(DISTINCT citer) FROM pc"),
        "distinct_citing_reviews_in_map": q("SELECT count(DISTINCT citer) FROM pc WHERE citer IN (SELECT id FROM map)"),
        "sr_or_ma_2022_2026": q("SELECT count(*) FROM map WHERE design = 'sr_or_ma' AND year BETWEEN 2022 AND 2026"),
        "guideline_2022_2026": q("SELECT count(*) FROM map WHERE design = 'guideline' AND year BETWEEN 2022 AND 2026"),
    }
    tables = {}
    for name, sql in {
        "design": "SELECT d.design, count(m.id) AS articles FROM (SELECT unnest(?::VARCHAR[]) AS design) d "
                  "LEFT JOIN map m USING (design) GROUP BY d.design ORDER BY list_position(?::VARCHAR[], d.design)",
        "primary_studies": "SELECT m.pmid, m.title, m.year, m.design, count(DISTINCT pc.citer) AS citing_reviews "
                           "FROM map m LEFT JOIN pc ON pc.primary_id = m.id WHERE m.design IN ('rct', 'other_trial') "
                           "GROUP BY ALL ORDER BY citing_reviews DESC, m.year DESC NULLS LAST, m.pmid",
        "citing_reviews": "SELECT a.pmid, a.title, a.year, a.design, a.id IN (SELECT id FROM map) AS in_map, "
                          "count(DISTINCT pc.primary_id) AS primary_studies_cited FROM pc JOIN articles a ON a.id = pc.citer "
                          "GROUP BY ALL ORDER BY primary_studies_cited DESC, a.year DESC NULLS LAST, a.pmid",
        "recent_reviews": "SELECT design, pmid, title, year FROM map WHERE design IN ('guideline', 'sr_or_ma') "
                          "AND year BETWEEN 2022 AND 2026 ORDER BY design, year DESC, pmid",
        "expansion": "SELECT m.mesh_id, m.name, e.depth FROM exp e JOIN mesh m ON m.id = e.descriptor ORDER BY e.depth, m.name",
    }.items():
        cur = con.execute(sql, [DESIGNS, DESIGNS] if name == "design" else [])
        tables[name] = ([d[0] for d in cur.description], cur.fetchall())
    assert summary["primary_cited_by_review"] + summary["primary_not_cited_by_review"] == summary["primary_studies"]
    return summary, tables


DESIGN_LABEL = {"guideline": "Guideline", "sr_or_ma": "Systematic review or meta-analysis", "rct": "Randomized controlled trial",
                "other_trial": "Other clinical trial", "observational": "Observational study", "other": "Other"}
DEFINITIONS = [
    ("Articles", "Articles indexed (HAS_MESH) to the descriptor or a narrower descriptor in the expansion{major}. The 40 MeSH "
                 "check tags (Humans, Female, Aged, ...) are never used."),
    ("Expansion", "{expansion}"),
    ("Design class", "One class per Article, the first that matches in this order, from NLM publication types: Guideline "
                     "(Guideline, Practice Guideline); Systematic review or meta-analysis (Systematic Review, Meta-Analysis, "
                     "Network Meta-Analysis); Randomized controlled trial (Randomized Controlled Trial, incl. Veterinary); Other "
                     "clinical trial (Clinical Trial, Clinical Trial Phase I-IV, Controlled Clinical Trial, Pragmatic Clinical Trial, "
                     "Equivalence Trial, Adaptive Clinical Trial, Clinical Trial Veterinary); Observational study (Observational "
                     "Study, incl. Veterinary); Other (everything else, including Clinical Trial Protocol and no types)."),
    ("Primary studies", "Articles in the Randomized controlled trial or Other clinical trial class."),
    ("Cited / not cited", "A primary study is cited when at least one Article anywhere in the graph whose publication types include "
                          "Guideline, Practice Guideline, Systematic Review, Meta-Analysis or Network Meta-Analysis cites it "
                          "(CITES edge). An Article citing itself is not counted. Only citations between Articles in the graph are "
                          "counted, so cited counts are lower bounds: a study not cited within the graph may be cited elsewhere."),
    ("2022-2026", "The Article's publication year (integer `year`) from 2022 to 2026 inclusive."),
    ("Population", "{population}"),
]


def _defs(summary):
    fill = dict(major=" with is_major_topic = true" if summary["indexing"] == "major_topic" else "",
                expansion=("The descriptor plus every narrower descriptor reached by HAS_BROADER_ANCESTOR, which follows MeSH tree "
                           "numbers (PubMed-style explode)." if summary["expansion"] == "full" else "The descriptor only."),
                population=("Identity-only Articles (lunasai_layer ctgov_identity_only) excluded." if summary["article_population"]
                            == "without_stubs" else "All Articles, including identity-only Articles (in this release they have "
                            "no publication types, MeSH or CITES edges, so they do not enter MeSH-based maps)."))
    return [(k, v.format(**fill)) for k, v in DEFINITIONS]


def _rows(summary):
    d = summary["by_design"]
    return [("Articles", summary["articles"])] + [(DESIGN_LABEL[k], d[k]) for k in DESIGNS] + [
        ("Primary studies (RCT + other clinical trial)", summary["primary_studies"]),
        ("Primary studies cited by an in-graph guideline or review", summary["primary_cited_by_review"]),
        ("Primary studies not cited within the graph", summary["primary_not_cited_by_review"]),
        ("Randomized controlled trials cited", summary["rct_cited_by_review"]),
        ("Other clinical trials cited", summary["other_trial_cited_by_review"]),
        ("Distinct citing guidelines and reviews", summary["distinct_citing_reviews"]),
        ("... of which in this map", summary["distinct_citing_reviews_in_map"]),
        ("Systematic reviews or meta-analyses, 2022-2026", summary["sr_or_ma_2022_2026"]),
        ("Guidelines, 2022-2026", summary["guideline_2022_2026"])]


def render_markdown(summary, tables):
    c = summary["condition"]
    esc = lambda v: "" if v is None else (f"{v:,}" if isinstance(v, int) and not isinstance(v, bool) else str(v).replace("|", "\\|"))
    tbl = lambda cols, rows: "\n".join(["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
                                        + ["| " + " | ".join(esc(v) for v in r) + " |" for r in rows])
    rec_cols, rec = tables["recent_reviews"]
    link = lambda pmid: f"[{pmid}](https://pubmed.ncbi.nlm.nih.gov/{pmid}/)" if pmid else ""
    L = [f"# Evidence map: {c['name']}", "",
         f"MeSH {c['mesh_id']}, {summary['descriptors_in_expansion']} descriptors. Source: {summary['release']}. "
         "Built by `examples/evidence_map.py`; `report.html` has the same content with a chart.", "",
         tbl(["measure", "value"], _rows(summary)), "", "## Definitions", ""]
    L += [f"- **{k}.** {v}" for k, v in _defs(summary)]
    L += ["", "## Descriptors in the expansion", "", tbl(*tables["expansion"])]
    for design, title in (("guideline", "Guidelines"), ("sr_or_ma", "Systematic reviews and meta-analyses")):
        rows = [r for r in rec if r[0] == design]
        L += ["", f"## {title}, 2022-2026 ({len(rows):,})", "",
              tbl(["pmid", "title", "year"], [(link(r[1]), r[2], r[3]) for r in rows])]
    L += ["", "Primary studies with their number of citing guidelines and reviews are in `primary_studies.csv`; the citing "
          "guidelines and reviews in `citing_reviews.csv`. PubMed, MeSH: U.S. National Library of Medicine; citations: OpenAlex. "
          "Graph files: CC0."]
    return "\n".join(L) + "\n"


CSS = (":root{color-scheme:light;--bg:#fcfcfb;--panel:#fff;--border:#e4e3df;--text:#0b0b0b;--text2:#52514e;--a:#2a78d6;--b:#c9c8c2}"
       "@media (prefers-color-scheme:dark){:root{color-scheme:dark;--bg:#1a1a19;--panel:#222220;--border:#383835;--text:#f0efec;"
       "--text2:#c3c2b7;--a:#3987e5;--b:#55544f}}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);"
       "font:14px/1.45 system-ui,-apple-system,'Segoe UI',sans-serif}main{max-width:1040px;margin:0 auto;padding:24px 16px 64px}"
       "h1{font-size:24px;margin:0 0 4px}h2{font-size:17px;margin:32px 0 6px}.sub,.note,dd{color:var(--text2)}"
       ".panel{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:12px;overflow-x:auto}"
       "table{border-collapse:collapse;width:100%;font-size:12.5px}th,td{padding:5px 8px;border-bottom:1px solid var(--border);"
       "text-align:left;vertical-align:top}td.n,th.n{text-align:right;font-variant-numeric:tabular-nums}a{color:var(--a)}"
       "svg{display:block;max-width:100%;height:auto}svg text{fill:var(--text2);font-size:11px}dt{font-weight:600;margin-top:8px}"
       "dd{margin:2px 0 0 0}.legend span{margin-right:14px;font-size:12px;color:var(--text2)}"
       ".legend i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:5px}")


def render_html(summary, tables):
    import html
    E = lambda v: html.escape("" if v is None else (f"{v:,}" if isinstance(v, int) and not isinstance(v, bool) else str(v)))
    c, d = summary["condition"], summary["by_design"]
    cited = {"rct": summary["rct_cited_by_review"], "other_trial": summary["other_trial_cited_by_review"]}
    vmax = max(d.values()) or 1
    bars, y = [], 6
    for k in DESIGNS:
        w = 560 * d[k] / vmax
        cw = 560 * cited.get(k, 0) / vmax
        bars.append(f"<text x='232' y='{y + 12}' text-anchor='end'>{E(DESIGN_LABEL[k])}</text>"
                    f"<rect x='240' y='{y}' width='{max(w, 1):.1f}' height='16' rx='3' fill='var(--b)'><title>{E(DESIGN_LABEL[k])}: "
                    f"{E(d[k])}</title></rect>"
                    + (f"<rect x='240' y='{y}' width='{max(cw, 1):.1f}' height='16' rx='3' fill='var(--a)'><title>cited by an in-graph "
                       f"guideline or review: {E(cited[k])}</title></rect>" if k in cited else "")
                    + f"<text x='{246 + w:.1f}' y='{y + 12}'>{E(d[k])}</text>")
        y += 24
    svg = f"<svg viewBox='0 0 900 {y + 4}' role='img' aria-label='Articles by design class'>{''.join(bars)}</svg>"
    row = lambda r: "<tr>" + "".join(f"<td class='{'n' if isinstance(v, int) else ''}'>{E(v)}</td>" for v in r) + "</tr>"
    rec_cols, rec = tables["recent_reviews"]
    lists = ""
    for design, title in (("guideline", "Guidelines"), ("sr_or_ma", "Systematic reviews and meta-analyses")):
        rows = [r for r in rec if r[0] == design]
        body = "".join(f"<tr><td><a href='https://pubmed.ncbi.nlm.nih.gov/{E(r[1])}/'>{E(r[1])}</a></td><td>{E(r[2])}</td>"
                       f"<td class='n'>{E(r[3])}</td></tr>" for r in rows)
        lists += (f"<h2>{title}, 2022-2026 ({len(rows):,})</h2><div class='panel'><table><thead><tr><th>PMID</th><th>Title</th>"
                  f"<th class='n'>Year</th></tr></thead><tbody>{body}</tbody></table></div>")
    ex_cols, ex = tables["expansion"]
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Evidence map: {E(c['name'])}</title><style>{CSS}</style></head><body><main>
<h1>Evidence map: {E(c['name'])}</h1>
<p class="sub">MeSH {E(c['mesh_id'])} · {E(summary['descriptors_in_expansion'])} descriptors · source: {E(summary['release'])}</p>
<h2>Articles by design class</h2>
<p class="note">Grey: Articles in the class. Blue (trial classes only): primary studies cited by at least one in-graph guideline or review.
Cited counts are lower bounds.</p>
<div class="panel"><div class="legend"><span><i style="background:var(--b)"></i>Articles</span><span><i style="background:var(--a)"></i>cited by an in-graph guideline or review</span></div>{svg}</div>
<h2>Summary</h2><div class="panel"><table><tbody>{''.join(row(r) for r in _rows(summary))}</tbody></table></div>
<h2>Definitions</h2><dl>{''.join(f"<dt>{E(k)}</dt><dd>{E(v)}</dd>" for k, v in _defs(summary))}</dl>
<h2>Descriptors in the expansion</h2><div class="panel"><table><thead><tr>{''.join(f"<th>{E(x)}</th>" for x in ex_cols)}</tr></thead>
<tbody>{''.join(row(r) for r in ex)}</tbody></table></div>
{lists}
<p class="note" style="margin-top:28px">Built by examples/evidence_map.py from the published Lunas Clinical Evidence KG graph files (CC0).
PubMed and MeSH: U.S. National Library of Medicine; citations: OpenAlex. Full lists in the CSV files next to this report.</p>
</main></body></html>"""


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--input", required=True, help="release folder (Hugging Face or Zenodo layout) or sample_out")
    ap.add_argument("--condition", required=True, help="MeSH descriptor name (exact, case-insensitive) or ID")
    ap.add_argument("--expansion", choices=["full", "none"], default="full")
    ap.add_argument("--exclude-stubs", action="store_true", help="drop identity-only (ctgov_identity_only) Articles")
    ap.add_argument("--major-only", action="store_true", help="only is_major_topic HAS_MESH edges")
    ap.add_argument("--out", help="output folder (default evidence_map_out/<descriptor id>)")
    ap.add_argument("--cache", help="Parquet cache folder (default <input>/evidence_map_cache)")
    ap.add_argument("--rebuild-cache", action="store_true")
    a = ap.parse_args()
    cache = a.cache or os.path.join(a.input, "evidence_map_cache")
    meta_path = os.path.join(cache, "meta.json")
    if a.rebuild_cache or not os.path.exists(meta_path) or json.load(open(meta_path)).get("cache_version") != CACHE_VERSION:
        os.makedirs(cache, exist_ok=True)
        build_cache(a.input, cache)
    con = open_cache(cache)
    root = resolve(con, a.condition)
    t0 = time.time()
    summary, tables = evidence_map(con, root[0], a.expansion, a.exclude_stubs, a.major_only)
    out = a.out or os.path.join("evidence_map_out", root[1])
    os.makedirs(out, exist_ok=True)
    for name, (cols, rows) in tables.items():
        import csv
        with open(os.path.join(out, name + ".csv"), "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(cols)
            w.writerows(rows)
    release = "Lunas Clinical Evidence KG"
    if os.path.exists(os.path.join(a.input, "manifest.json")):
        m = json.load(open(os.path.join(a.input, "manifest.json")))
        release += f" v{m.get('version')} (snapshot {m.get('snapshot_date')})"
    summary = {"condition": {"id": root[0], "mesh_id": root[1], "name": root[2]}, "release": release,
               "expansion": a.expansion, "article_population": "without_stubs" if a.exclude_stubs else "with_stubs",
               "indexing": "major_topic" if a.major_only else "any", "self_citations": "excluded",
               **summary, "run_seconds": round(time.time() - t0, 2)}
    json.dump(summary, open(os.path.join(out, "summary.json"), "w"), indent=1)
    with open(os.path.join(out, "report.html"), "w") as fh:
        fh.write(render_html(summary, tables))
    with open(os.path.join(out, "README.md"), "w") as fh:
        fh.write(render_markdown(summary, tables))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
