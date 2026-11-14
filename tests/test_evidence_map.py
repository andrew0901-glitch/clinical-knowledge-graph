"""Tests for examples/evidence_map.py on the bundled sample subgraph (sample_out/).

  pip install duckdb pytest
  pytest tests/test_evidence_map.py

The expected numbers are recomputed here in plain Python straight from the sample's gzipped KGX files,
independently of the tool's DuckDB SQL, for the sample descriptor with the most primary studies. The
sample keeps too few CITES edges for any sample map to contain a review-cited primary study, so the
citation, self-link, stub and check-tag rules are also tested on a tiny synthetic graph with hand-computed
answers (test_synthetic_rules).
"""
import gzip, json, os, shutil, subprocess, sys
from collections import defaultdict

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE = os.path.join(ROOT, "sample_out")
sys.path.insert(0, os.path.join(ROOT, "examples"))
import evidence_map as em  # noqa: E402


def _read(kind):
    with gzip.open(os.path.join(SAMPLE, f"{kind}__sample.jsonl.gz"), "rt") as fh:
        for line in fh:
            yield json.loads(line)


def _rel(r):
    return (r.get("original_predicate") or "").rsplit(".", 1)[-1]


def _design(pub_types):
    pt = set(pub_types or [])
    for name, types in (("guideline", em.GUIDELINE), ("sr_or_ma", em.SR_OR_MA), ("rct", em.RCT),
                        ("other_trial", em.OTHER_TRIAL), ("observational", em.OBSERVATIONAL)):
        if pt & set(types):
            return name
    return "other"


@pytest.fixture(scope="module")
def sample():
    articles, mesh = {}, {}
    for r in _read("nodes"):
        label = (r.get("lunasai_labels") or [None])[0]
        if label == "Article":
            articles[r["id"]] = dict(design=_design(r.get("pub_types")), year=r.get("year"),
                                     stub=r.get("lunasai_layer") == em.STUB_LAYER,
                                     review=bool(set(r.get("pub_types") or []) & set(em.GUIDELINE + em.SR_OR_MA)))
        elif label == "MeSHConcept":
            mesh[r["id"]] = r.get("name")
    am, cites, desc = defaultdict(set), defaultdict(set), defaultdict(set)
    for r in _read("edges"):
        rel, s, o = _rel(r), r["subject"], r["object"]
        if rel == "HAS_MESH" and s in articles:
            am[o].add((s, bool(r.get("is_major_topic"))))
        elif rel == "CITES" and s != o:
            cites[o].add(s)
        elif rel == "HAS_BROADER_ANCESTOR":
            desc[o].add(s)
    return articles, mesh, am, cites, desc


def expected(sample, root, expansion="full", exclude_stubs=False, major_only=False):
    articles, mesh, am, cites, desc = sample
    exp = {root} | (desc[root] if expansion == "full" else set())
    exp = {d for d in exp if mesh.get(d) not in em.CHECK_TAGS}
    ok = lambda a: not (exclude_stubs and articles[a]["stub"])
    mp = {a for d in exp for a, major in am[d] if (major or not major_only) and ok(a)}
    primary = {a for a in mp if articles[a]["design"] in ("rct", "other_trial")}
    citing = {p: {c for c in cites[p] if c in articles and articles[c]["review"] and ok(c)} for p in primary}
    cited = {p for p, cs in citing.items() if cs}
    reviews = set().union(*citing.values()) if citing else set()
    design = {d: sum(articles[a]["design"] == d for a in mp) for d in em.DESIGNS}
    return {
        "descriptors_in_expansion": len(exp), "articles": len(mp), "by_design": design,
        "primary_studies": len(primary), "primary_cited_by_review": len(cited),
        "primary_not_cited_by_review": len(primary) - len(cited),
        "rct_cited_by_review": sum(articles[p]["design"] == "rct" for p in cited),
        "other_trial_cited_by_review": sum(articles[p]["design"] == "other_trial" for p in cited),
        "distinct_citing_reviews": len(reviews), "distinct_citing_reviews_in_map": len(reviews & mp),
        "sr_or_ma_2022_2026": sum(articles[a]["design"] == "sr_or_ma" and 2022 <= int(articles[a]["year"] or 0) <= 2026
                                  for a in mp),
        "guideline_2022_2026": sum(articles[a]["design"] == "guideline" and 2022 <= int(articles[a]["year"] or 0) <= 2026
                                   for a in mp),
    }


@pytest.fixture(scope="module")
def con(tmp_path_factory):
    cache = str(tmp_path_factory.mktemp("evidence_map_cache"))
    em.build_cache(SAMPLE, cache)
    return em.open_cache(cache)


@pytest.fixture(scope="module")
def busiest(sample):
    """Sample descriptor (with narrower descriptors) whose map has the most primary studies."""
    articles, mesh, am, cites, desc = sample
    scored = {d: expected(sample, d) for d in desc if mesh.get(d) and mesh[d] not in em.CHECK_TAGS}
    best = max(scored, key=lambda d: (scored[d]["primary_studies"], scored[d]["articles"], d))
    e = scored[best]
    assert e["primary_studies"] > 0 and e["descriptors_in_expansion"] > 1
    return best


@pytest.mark.parametrize("expansion,exclude_stubs,major_only",
                         [("full", False, False), ("full", True, False), ("none", False, False), ("full", False, True)])
def test_matches_independent_python(con, sample, busiest, expansion, exclude_stubs, major_only):
    got, tables = em.evidence_map(con, busiest, expansion, exclude_stubs, major_only)
    assert got == expected(sample, busiest, expansion, exclude_stubs, major_only)
    assert sum(r[1] for r in tables["design"][1]) == got["articles"]
    assert len(tables["primary_studies"][1]) == got["primary_studies"]
    assert len(tables["citing_reviews"][1]) == got["distinct_citing_reviews"]


def test_invariants(con, busiest):
    s, _ = em.evidence_map(con, busiest)
    assert sum(s["by_design"].values()) == s["articles"]
    assert s["primary_studies"] == s["by_design"]["rct"] + s["by_design"]["other_trial"]
    assert s["rct_cited_by_review"] + s["other_trial_cited_by_review"] == s["primary_cited_by_review"]
    assert s["distinct_citing_reviews_in_map"] <= s["distinct_citing_reviews"]
    none, _ = em.evidence_map(con, busiest, expansion="none")
    assert none["articles"] <= s["articles"] and none["descriptors_in_expansion"] == 1


def test_reads_only_manifest_files(tmp_path, busiest):
    """A stray shard next to the listed files must be ignored when manifest.json is present."""
    for kind in ("nodes", "edges"):
        shutil.copy(os.path.join(SAMPLE, f"{kind}__sample.jsonl.gz"), tmp_path / f"{kind}__sample.jsonl.gz")
    stray = {"subject": busiest, "object": busiest, "original_predicate": "lunasai:vocab.HAS_BROADER_ANCESTOR"}
    with gzip.open(tmp_path / "edges__stray.jsonl.gz", "wt") as fh:
        fh.write(json.dumps(stray) + "\n")
    (tmp_path / "manifest.json").write_text(json.dumps({"nodes": [{"path": "nodes/sample.jsonl.gz"}],
                                                        "edges": [{"path": "edges/sample.jsonl.gz"}]}))
    cache = tmp_path / "cache"
    cache.mkdir()
    em.build_cache(str(tmp_path), str(cache))
    meta = json.loads((cache / "meta.json").read_text())
    assert meta["edge_files"] == ["edges__sample.jsonl.gz"]


def test_cli(tmp_path, busiest):
    out = tmp_path / "out"
    subprocess.run([sys.executable, os.path.join(ROOT, "examples", "evidence_map.py"), "--input", SAMPLE,
                    "--cache", str(tmp_path / "cache"), "--condition", busiest.split(":")[1], "--out", str(out)],
                   check=True, stdout=subprocess.DEVNULL)
    s = json.loads((out / "summary.json").read_text())
    assert s["self_citations"] == "excluded" and s["article_population"] == "with_stubs"
    for f in ("design.csv", "primary_studies.csv", "citing_reviews.csv"):
        assert (out / f).exists()


def _write(path, rows):
    with gzip.open(path, "wt") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")


def test_synthetic_rules(tmp_path):
    """Hand-built graph: root R with narrower N; check tag H (Humans) also indexed. Expected values by hand."""
    A = lambda i, pt, **kw: dict(id=f"PMID:{i}", lunasai_labels=["Article"], lunasai_layer="pubmed", pmid=str(i),
                                 year=kw.get("year", 2020), pub_types=pt)
    M = lambda d, name: dict(id=f"MESH:{d}", lunasai_labels=["MeSHConcept"], mesh_id=d, name=name)
    nodes = [M("D1", "Root"), M("D2", "Narrower"), M("D3", "Unrelated"), M("D006801", "Humans"),
             A(1, ["Randomized Controlled Trial"]),                  # rct, cited by SR 5
             A(2, ["Clinical Trial, Phase II"]),                     # other_trial, cited only by itself
             A(3, ["Clinical Trial Protocol"]),                      # other (protocol)
             A(4, ["Observational Study"]),                          # observational
             A(5, ["Systematic Review", "Randomized Controlled Trial"], year=2023),  # sr_or_ma (beats rct), in map
             A(6, ["Practice Guideline", "Meta-Analysis"], year=2026),           # guideline, outside map, cites 1
             A(7, ["Randomized Controlled Trial"]),                  # rct only on unrelated D3
             A(8, ["Review"]),                                       # plain review: not a citing review
             dict(id="PMID:9", lunasai_labels=["Article"], lunasai_layer="ctgov_identity_only", pmid="9")]  # stub
    E = lambda s, o, p, **kw: dict(subject=s, object=o, original_predicate=f"lunasai:vocab.{p}", **kw)
    edges = [E("MESH:D2", "MESH:D1", "HAS_BROADER_ANCESTOR", depth=1),
             E("MESH:D006801", "MESH:D1", "HAS_BROADER_ANCESTOR", depth=1),   # check tag never expands
             E("PMID:1", "MESH:D1", "HAS_MESH", is_major_topic=True),
             E("PMID:2", "MESH:D2", "HAS_MESH", is_major_topic=False),
             E("PMID:3", "MESH:D2", "HAS_MESH", is_major_topic=True),
             E("PMID:4", "MESH:D1", "HAS_MESH", is_major_topic=False),
             E("PMID:5", "MESH:D1", "HAS_MESH", is_major_topic=True),
             E("PMID:6", "MESH:D3", "HAS_MESH", is_major_topic=True),
             E("PMID:7", "MESH:D3", "HAS_MESH", is_major_topic=True),
             E("PMID:7", "MESH:D006801", "HAS_MESH", is_major_topic=False),  # via check tag only: excluded
             E("PMID:8", "MESH:D1", "HAS_MESH", is_major_topic=False),
             E("PMID:5", "PMID:1", "CITES"), E("PMID:6", "PMID:1", "CITES"),
             E("PMID:2", "PMID:2", "CITES"),                         # self-link: dropped
             E("PMID:8", "PMID:2", "CITES"),                         # plain review: not counted
             E("PMID:9", "PMID:1", "CITES")]                         # stub citer (no pub types): not a review
    _write(tmp_path / "nodes__t.jsonl.gz", nodes)
    _write(tmp_path / "edges__t.jsonl.gz", edges)
    cache = tmp_path / "cache"
    cache.mkdir()
    em.build_cache(str(tmp_path), str(cache))
    assert json.loads((cache / "meta.json").read_text())["cites_self_links_dropped"] == 1
    con = em.open_cache(str(cache))
    s, tables = em.evidence_map(con, "MESH:D1")
    assert s["descriptors_in_expansion"] == 2
    assert s["articles"] == 6
    assert s["by_design"] == {"guideline": 0, "sr_or_ma": 1, "rct": 1, "other_trial": 1, "observational": 1, "other": 2}
    assert (s["primary_studies"], s["primary_cited_by_review"], s["primary_not_cited_by_review"]) == (2, 1, 1)
    assert (s["rct_cited_by_review"], s["other_trial_cited_by_review"]) == (1, 0)
    assert (s["distinct_citing_reviews"], s["distinct_citing_reviews_in_map"]) == (2, 1)
    assert (s["sr_or_ma_2022_2026"], s["guideline_2022_2026"]) == (1, 0)
    major, _ = em.evidence_map(con, "MESH:D1", major_only=True)
    assert major["articles"] == 3 and major["primary_studies"] == 1
    none, _ = em.evidence_map(con, "MESH:D1", expansion="none")
    assert none["articles"] == 4 and none["primary_studies"] == 1
    assert em.evidence_map(con, "MESH:D1", exclude_stubs=True)[0] == s
