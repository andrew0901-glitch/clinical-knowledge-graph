"""trial_report.py on a tiny synthetic cache: routes, restriction, subset, benchmarks, missing fields."""
import csv, json, os, sys

import duckdb
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "examples"))
import trial_report as TR  # noqa: E402

TRIALS = [  # id, nct, title, status, phase, study_type, start, completion, enrollment
    ("clinicaltrials:NCT1", "NCT1", "Lumbar fusion with cage", "COMPLETED", "NA", "INTERVENTIONAL", "2018-01-01", "2020-01-01", 120),
    ("clinicaltrials:NCT2", "NCT2", "Spine study", "RECRUITING", "NA", "INTERVENTIONAL", "2024-01-01", "2027-01-01", 200),
    ("clinicaltrials:NCT3", "NCT3", "PD-L1 fusion protein", "TERMINATED", "PHASE1", "INTERVENTIONAL", "2019-01-01", "2020-06-01", 5),
    ("clinicaltrials:NCT4", "NCT4", "Knee trial", "COMPLETED", "NA", "INTERVENTIONAL", "2015-01-01", "2016-01-01", 50),
]
FULL = [
    dict(nct_id="NCT1", official_title="TLIF in the lumbar spine", enrollment_type="ACTUAL", primary_completion_date="2019-07-01",
         primary_completion_date_type="ACTUAL", start_date_type="ACTUAL", why_stopped=None, intervention_names=["Cage X"],
         intervention_types=["DEVICE"], primary_outcome_measures=["Oswestry Disability Index"], primary_outcome_time_frames=["6 months"],
         eligibility_minimum_age="18 Years", eligibility_sex="ALL", eligibility_criteria="Inclusion: x\nExclusion Criteria:\n- pregnancy\n- smoking"),
    dict(nct_id="NCT2", official_title="Posterior lumbar interbody fusion versus decompression", enrollment_type="ESTIMATED",
         primary_completion_date="2026-12-01", primary_completion_date_type="ESTIMATED", intervention_names=["PLIF"],
         intervention_types=["PROCEDURE"], primary_outcome_measures=["VAS back pain"], primary_outcome_time_frames=["two years"]),
    dict(nct_id="NCT3", official_title="Bintrafusp, a PD-L1 fusion protein", why_stopped="Slow accrual", enrollment_type="ACTUAL"),
    dict(nct_id="NCT4", official_title="Total knee arthroplasty", enrollment_type="ACTUAL"),
]
SPEC = {
    "label": "Lumbar fusion",
    "routes": [{"id": "A1", "label": "brief title", "kind": "text", "field": "brief_title", "terms": ["fusion", "cage"]},
               {"id": "A2", "label": "official title", "kind": "text", "field": "official_title", "terms": ["fusion", "TLIF"]}],
    "restrict": [{"id": "B1", "label": "lumbar text", "kind": "text", "field": "official_title", "regex": r"\blumbar\b"}],
    "subset": {"label": "interbody", "routes": [{"id": "C1", "label": "interbody", "kind": "text", "field": "official_title",
                                                  "terms": ["interbody", "TLIF"]}]},
}


@pytest.fixture()
def cache(tmp_path):
    c = tmp_path / "cache"
    c.mkdir()
    con = duckdb.connect()

    def table(name, cols, rows):
        typ = {"enrollment": "BIGINT"}   # as trial_landscape.build_cache types it
        con.sql(f"CREATE OR REPLACE TABLE t ({', '.join(f'{x} ' + typ.get(x, 'VARCHAR') for x in cols)})")
        for r in rows:
            con.execute(f"INSERT INTO t VALUES ({', '.join('?' for _ in cols)})",
                        [None if v is None else (v if c in typ else str(v)) for c, v in zip(cols, r)])
        con.sql(f"COPY t TO '{c / (name + '.parquet')}' (FORMAT parquet)")

    table("trials", TR.TL.TABLES["trials"], [r + (None,) for r in TRIALS])
    table("sites", TR.TL.TABLES["sites"], [("s1", "Spine Center", "Boston", "Massachusetts", "United States"),
                                           ("s2", "Spine Centre", "Boston", "Massachusetts", "United States")])
    table("sponsors", TR.TL.TABLES["sponsors"], [("sp1", "Acme Spine")])
    table("mesh", TR.TL.TABLES["mesh"], [])
    table("articles", TR.TL.TABLES["articles"], [])
    table("trial_mesh", TR.TL.TABLES["trial_mesh"], [])
    table("sponsored_by", TR.TL.TABLES["sponsored_by"], [("clinicaltrials:NCT1", "sp1", "INDUSTRY", "LEAD"),
                                                         ("clinicaltrials:NCT2", "sp1", "INDUSTRY", "LEAD")])
    table("conducted_at", TR.TL.TABLES["conducted_at"], [("clinicaltrials:NCT1", "s1", "COMPLETED"),
                                                         ("clinicaltrials:NCT2", "s2", "RECRUITING")])
    for t in ("trial_pubs", "broader", "broader_ancestor", "result_citations", "result_citers"):
        table(t, TR.TL.TABLES[t], [])
    return str(c)


@pytest.fixture()
def full_record(tmp_path):
    p = tmp_path / "fr.jsonl"
    with open(p, "w") as fh:
        for r in FULL:
            fh.write(json.dumps({**{f: None for f in TR.FULL_FIELDS}, **r}) + "\n")
    out = tmp_path / "fr.parquet"
    duckdb.sql(f"COPY (SELECT * FROM read_json('{p}', format='newline_delimited')) TO '{out}' (FORMAT parquet)")
    return str(out)


def rows(out, name):
    """data rows only (a trailing '# ...' row carries the section note)"""
    return [r for r in csv.DictReader(open(os.path.join(out, name))) if not next(iter(r.values()), "").startswith("#")]


def test_without_full_record_text_routes_on_other_fields_are_missing(cache, tmp_path):
    out = str(tmp_path / "o1")
    TR.build(cache, SPEC, out)
    r = {x["route_id"]: x for x in rows(out, "01_selection_routes.csv")}
    assert r["A2"]["trials_matched"] == TR.MISSING
    assert r["selected"]["trials_matched"] == "0"            # the lumbar restriction needs the official title
    cov = {x["field"]: x for x in rows(out, "19_field_coverage.csv")}
    assert cov["why_stopped"]["trials_with_value"] == TR.MISSING


def test_routes_restriction_subset_and_sections(cache, full_record, tmp_path):
    out = str(tmp_path / "o2")
    res = TR.build(cache, SPEC, out, full_record=full_record)
    assert res["headline"]["trials"] == 2                     # NCT1, NCT2; NCT3 (PD-L1 fusion protein) fails lumbar
    assert res["subset"]["trials"] == 2                       # TLIF + interbody
    r = {x["route_id"]: x for x in rows(out, "01_selection_routes.csv")}
    assert r["A1"]["trials_matched"] == "2" and r["A1"]["trials_kept"] == "1"
    assert r["A2"]["trials_added_in_route_order"] == "1"     # NCT2 only via official title
    assert r["candidates"]["trials_matched"] == "3"
    oc = {x["outcome_group"]: x["trials"] for x in rows(out, "10_primary_outcomes.csv")}
    assert oc["ODI (Oswestry)"] == "1" and oc["VAS / NRS pain"] == "1"
    tf = {x["longest_primary_time_frame"]: x["trials"] for x in rows(out, "25_primary_followup_time_frames.csv")}
    assert tf[">3-6 months"] == "1" and tf[">12-24 months"] == "1"
    rate = rows(out, "21b_enrollment_rate_trials.csv")
    # NCT1: start 2018-01-01 -> primary completion 2019-07-01 = 18 months, minus 6-month follow-up = 12 months
    assert rate[0]["nct_id"] == "NCT1" and float(rate[0]["recruitment_months"]) == pytest.approx(12.0, abs=0.1)
    assert float(rate[0]["patients_per_site_month"]) == pytest.approx(10.0, rel=0.02)
    ex = {x["term"]: x["trials"] for x in rows(out, "27_exclusion_terms.csv") if x["kind"] == "keyword"}
    assert ex["pregnancy / breastfeeding"] == "1" and ex["smoking / nicotine"] == "1"
    sl = rows(out, "28_site_shortlist.csv")
    assert len(sl) == 1 and sl[0]["score"] == str(3 * 1 - 1 * 1 + 2 * 1)   # Spine Center / Centre merged
    prof = rows(out, "29_competitor_profiles.csv")
    assert prof[0]["industry_lead_sponsor"] == "Acme Spine" and "NCT2: 2026-12-01 (ESTIMATED)" in prof[0]["expected_readouts_active (primary completion, type)"]
    assert len(rows(out, "30_active_timeline.csv")) == 1


def test_history_planned_vs_actual_and_site_activation(cache, full_record, tmp_path):
    h = tmp_path / "h.jsonl"
    h.write_text(json.dumps({"nct_id": "NCT1", "versions": [
        {"date": "2018-01-05", "enrollment": 200, "enrollment_type": "ESTIMATED", "sites": [{"name": "Spine Center", "city": "Boston", "country": "United States"}]},
        {"date": "2018-07-01", "enrollment": 200, "enrollment_type": "ESTIMATED", "sites": [{"name": "Spine Center", "city": "Boston", "country": "United States"},
                                                                                         {"name": "Other Hospital", "city": "Lyon", "country": "France", "status": "RECRUITING"}]},
        {"date": "2020-02-01", "enrollment": 120, "enrollment_type": "ACTUAL", "sites": []}]}) + "\n")
    out = str(tmp_path / "o3")
    TR.build(cache, SPEC, out, full_record=full_record, history=str(h))
    pv = rows(out, "22_planned_vs_actual_enrollment.csv")
    assert pv[0]["planned_enrollment"] == "200" and pv[0]["actual_enrollment"] == "120" and pv[0]["actual_pct_of_planned"] == "60.0"
    sa = rows(out, "23_site_activation.csv")
    assert sa[0]["site"] == "Other Hospital" and sa[0]["first_listed_in_version_dated"] == "2018-07-01"


def test_helpers():
    assert TR.max_time_frame_months(["Baseline, 6 weeks, 12 months", "two years"]) == pytest.approx(24)
    assert TR.max_time_frame_months(["at discharge"]) is None
    assert TR.age_band("18 Years", None) == "adults (min age >= 18)"
    assert TR.age_band(None, "17 Years").startswith("children only")
    assert TR.first_group("Slow accrual", TR.STOP_REASONS) == "enrollment or accrual"
    assert TR.first_group("Drug supply issues", TR.STOP_REASONS) == "sponsor decision"
    assert TR.first_group("PI left", TR.STOP_REASONS) == "other"
