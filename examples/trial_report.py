#!/usr/bin/env python3
"""Trial landscape report for any topic: one CSV per section, plus design benchmarks from comparable trials.
Read-only, deterministic, no model calls.

  python examples/trial_report.py --cache tl_cache --topic examples/topics/lumbar_fusion.json --out OUT \
      [--full-record full_record.parquet] [--history history.jsonl]

Inputs
  --cache        trial_landscape.py's Parquet cache of a release (built with `trial_landscape.py --build-cache`).
  --topic        topic spec (JSON): selection routes, optional restriction, optional subset. Examples in
                 examples/topics/. Every term list and the count each route contributes is printed to
                 01_selection_routes.csv.
  --full-record  optional: one row per trial with the ClinicalTrials.gov full-record fields (official_title,
                 intervention_names, primary outcomes, primary_completion_date, why_stopped, design, eligibility,
                 results_first_posted_date ...). Build it from a release that carries them with
                 examples/extract_full_record.py. Without it those fields are reported as MISSING.
  --history      optional: JSON lines of record versions per trial ({"nct_id", "versions": [{"date",
                 "enrollment", "enrollment_type", "overall_status", "sites": [{"name","city","country","status"}]}]})
                 for planned-vs-actual enrollment and site activation timing. Without it those sections are MISSING.

Benchmarks compare trials in the same topic by phase x lead-sponsor class (median and IQR). All keyword maps,
weights and definitions are written next to the numbers they produce.
"""
import argparse, csv, datetime as dt, importlib.util, json, os, re, statistics, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("trial_landscape", os.path.join(HERE, "trial_landscape.py"))
TL = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TL)

ACTIVE = ("RECRUITING", "NOT_YET_RECRUITING", "ENROLLING_BY_INVITATION", "ACTIVE_NOT_RECRUITING")
CLOSED = ("COMPLETED", "TERMINATED", "WITHDRAWN")
STUB = "ctgov_identity_only"
MISSING = "MISSING (not in input)"
TEXT_FIELDS = ("brief_title", "official_title", "intervention_names")
FULL_FIELDS = ["official_title", "enrollment_type", "primary_completion_date", "primary_completion_date_type",
               "start_date_type", "completion_date_type", "why_stopped", "allocation", "intervention_model", "masking",
               "primary_purpose", "results_first_posted_date", "eligibility_sex", "eligibility_minimum_age",
               "eligibility_maximum_age", "eligibility_healthy_volunteers", "eligibility_criteria",
               "intervention_names", "intervention_types", "primary_outcome_measures", "primary_outcome_time_frames",
               "secondary_outcome_measures", "secondary_outcome_time_frames"]
NOT_AVAILABLE = [  # registry fields no input carries yet
    ("overall_officials / investigators", "not in the release or the full-record input"),
    ("arm_groups", "not in the release or the full-record input"),
    ("site_contacts", "internal-only by policy; never read or exported"),
]

# ---------------------------------------------------------------- printed keyword maps (first match wins)
OUTCOME_KEYWORDS = [
    ("ODI (Oswestry)", r"\boswestry\b|\bODI\b"),
    ("VAS / NRS pain", r"\bVAS\b|visual analog|\bNRS\b|numeric(al)? (pain )?rating"),
    ("fusion rate", r"\bfusion\b|arthrodesis|bony union|bone union"),
    ("SF-36 / SF-12", r"\bSF-?36\b|\bSF-?12\b|short form"),
    ("EQ-5D", r"EQ-?5D"),
    ("JOA", r"\bJOA\b"),
    ("survival (OS / EFS / PFS / DFS)", r"surviv|\bOS\b|\bEFS\b|\bPFS\b|\bDFS\b|event[- ]free|progression[- ]free"),
    ("response (ORR / histologic)", r"response|\bORR\b|remission|necrosis"),
    ("dose-finding (MTD / DLT / RP2D)", r"maximum tolerated|\bMTD\b|\bDLT\b|dose[- ]limiting|recommended phase"),
    ("adverse events / safety", r"adverse|toxicit|safety|complication"),
    ("reoperation / revision", r"reoperation|re-operation|revision"),
    ("pharmacokinetics", r"pharmacokinetic|\bPK\b|\bAUC\b|\bCmax\b"),
    ("function score (MSTS / TESS / other)", r"\bMSTS\b|\bTESS\b|function"),
    ("pain (other)", r"\bpain\b"),
    ("blood loss / perioperative", r"blood loss|transfusion|operative time|length of (hospital )?stay"),
    ("radiographic", r"radiograph|\bCT\b|subsidence|alignment|lordosis"),
]
STOP_REASONS = [  # applied in this order; first match wins
    ("safety", r"safety|toxicit|adverse|death|harm|\bSAE"),
    ("enrollment or accrual", r"accru|enrol|recruit|inclusion|slow|participants?|patients?|subjects?|eligible|target number|difficult(y|ies)? (to|in) find"),
    ("funding", r"fund|financ|budget|grant|money|resourc|cost|study support"),
    ("sponsor decision", r"sponsor|business|strateg|company|portfolio|commercial|decision|priorit|terminated by|supply|development program|no longer (on the market|available)"),
    ("other", r".*"),
]
EXCLUSION_KEYWORDS = [
    ("pregnancy / breastfeeding", r"pregnan|breast-?feeding|lactat|nursing"),
    ("prior surgery at the site", r"prior (spin|surg|fusion|lumbar)|previous (spin|surg|fusion|lumbar)|revision"),
    ("infection", r"infect|sepsis|osteomyelitis"),
    ("malignancy / tumour", r"malignan|cancer|tumou?r|metasta"),
    ("osteoporosis / bone disease", r"osteopor|osteopeni|metabolic bone|paget"),
    ("smoking / nicotine", r"smok|nicotin|tobacco"),
    ("BMI / obesity", r"\bBMI\b|body mass|obes"),
    ("renal impairment", r"renal|kidney|creatinine"),
    ("hepatic impairment", r"hepat|liver|bilirubin|\bALT\b|\bAST\b"),
    ("cardiac disease", r"cardiac|heart|myocard|QTc"),
    ("HIV / hepatitis", r"\bHIV\b|hepatitis"),
    ("prior chemotherapy / radiotherapy", r"chemotherap|radiotherap|radiation therapy|prior (systemic )?therapy"),
    ("psychiatric / substance use", r"psychiatr|depress|substance|alcohol|drug abuse"),
    ("other trial participation", r"other (clinical )?(trial|study)|investigational"),
    ("allergy / hypersensitivity", r"allerg|hypersensitiv"),
    ("diabetes", r"diabet"),
    ("steroids / immunosuppression", r"steroid|immunosuppress|corticoster"),
    ("litigation / workers' compensation", r"litigation|compensation|disability claim"),
]
SITE_SHORTLIST_WEIGHTS = [  # (criterion, weight, definition)
    ("completed_trials_in_topic", 3, "topic trials with overall_status COMPLETED at the site"),
    ("accrual_terminations_in_topic", -3, "topic trials TERMINATED / WITHDRAWN at the site whose why_stopped is grouped 'enrollment or accrual'"),
    ("competing_active_trials_in_topic", -1, "topic trials currently active at the site (competition for the same patients)"),
    ("recruiting_now", 2, "1 if the site's CONDUCTED_AT status is RECRUITING for any topic trial, else 0"),
]
NUM_WORDS = {w: i for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve".split())}
UNIT_MONTHS = {"hour": 1 / 730.5, "day": 1 / 30.4375, "week": 7 / 30.4375, "month": 1.0, "year": 12.0}
TF_RE = re.compile(r"(\d+(?:\.\d+)?|" + "|".join(NUM_WORDS) + r")[\s-]*(hour|day|week|month|year)s?", re.I)
TF_BINS = [(1, "<=1 month"), (3, ">1-3 months"), (6, ">3-6 months"), (12, ">6-12 months"), (24, ">12-24 months"),
           (60, ">24-60 months"), (float("inf"), ">60 months")]
STOPWORDS = set("""a an and are as at be by for from has have in is it its of on or that the this to with without
were was will who which not no any other than within prior previous patients patient subjects subject participants
participant study history known current evidence including e g i e etc years year age criteria exclusion inclusion
must may more less use used who have had following one two any all""".split())


def words_re(terms):
    return re.compile(r"\b(?:" + "|".join(re.escape(t) + ("s?" if t.islower() else "") for t in terms) + r")\b", re.I)


def route_regex(r):
    return re.compile(r["regex"], re.I) if r.get("regex") else words_re(r["terms"])


def months_between(a, b):
    try:
        da, db = dt.date.fromisoformat(str(a)[:10]), dt.date.fromisoformat(str(b)[:10])
    except (TypeError, ValueError):
        return None
    return (db - da).days / 30.4375


def max_time_frame_months(frames):
    """Longest duration written in any time-frame string, in months (None if nothing parses)."""
    best = None
    for f in frames or []:
        for n, unit in TF_RE.findall(f or ""):
            v = NUM_WORDS.get(n.lower(), None)
            v = float(n) if v is None else float(v)
            m = v * UNIT_MONTHS[unit.lower()]
            best = m if best is None or m > best else best
    return best


def age_years(s):
    if not s:
        return None
    m = re.match(r"\s*(\d+(?:\.\d+)?)\s*(year|month|week|day|hour|minute)", s, re.I)
    if not m:
        return None
    return float(m.group(1)) * {"year": 1, "month": 1 / 12, "week": 1 / 52, "day": 1 / 365, "hour": 1 / 8760,
                                "minute": 1 / 525600}[m.group(2).lower()]


def age_band(mn, mx):
    a, b = age_years(mn), age_years(mx)
    if b is not None and b < 18:
        return "children only (max age < 18)"
    if a is not None and a >= 65:
        return "older adults only (min age >= 65)"
    if a is not None and a >= 18:
        return "adults (min age >= 18)"
    return "children and adults (min age < 18 or none, max age >= 18 or none)"


def exclusion_text(criteria):
    if not criteria:
        return ""
    m = re.search(r"exclusion criteria\s*:?", criteria, re.I)
    return criteria[m.end():] if m else ""


def first_group(text, groups):
    for g, rx in groups:
        if re.search(rx, text or "", re.I):
            return g
    return None


def quantiles(xs):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return (0, None, None, None)
    if len(xs) == 1:
        return (1, xs[0], xs[0], xs[0])
    q = statistics.quantiles(xs, n=4, method="inclusive")
    return (len(xs), q[1], q[0], q[2])


def r1(x):
    return None if x is None else round(x, 1)


class Writer:
    def __init__(self, out, release):
        self.out, self.release = out, release
        os.makedirs(out, exist_ok=True)

    def __call__(self, name, header, rows, note=None):
        with open(os.path.join(self.out, name), "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(header + ["release"])
            for r in rows:
                w.writerow(list(r) + [self.release])
            if note:
                w.writerow(["# " + note] + [""] * len(header))


# ---------------------------------------------------------------- data
def load_inputs(cache, full_record=None, history=None):
    con = TL.open_cache(cache)
    trials = {}
    for r in con.sql("SELECT id, nct_id, title, overall_status, phase, study_type, start_date, completion_date, "
                     "enrollment FROM trials").fetchall():
        trials[r[0]] = dict(zip(["id", "nct", "brief_title", "status", "phase", "study_type", "start", "completion",
                                 "enrollment"], r))
    fr = {}
    if full_record:
        rel = con.sql(f"SELECT * FROM read_parquet('{full_record}')")
        cols = rel.columns
        for row in rel.fetchall():
            d = dict(zip(cols, row))
            fr[d["nct_id"]] = d
    for t in trials.values():
        d = fr.get(t["nct"], {})
        for f in FULL_FIELDS:
            v = d.get(f)
            t[f] = (list(v) if isinstance(v, (list, tuple)) else v) if d else None
        for f in ("primary_completion_date", "results_first_posted_date"):
            if t[f] is not None:
                t[f] = str(t[f])[:10]
    hist = {}
    if history:
        with open(history) as fh:
            for line in fh:
                h = json.loads(line)
                hist[h["nct_id"]] = sorted(h["versions"], key=lambda v: v["date"])
    return con, trials, bool(fr), hist


def trial_text(t, field):
    v = t.get(field)
    return " | ".join(v) if isinstance(v, list) else (v or "")


def select(con, trials, spec, have_full):
    """Returns (selected ids, subset ids, route rows)."""
    tm = con.sql("SELECT trial, mesh, mesh_type, study_aspect FROM trial_mesh").fetchall()
    mesh_name = dict(con.sql("SELECT id, name FROM mesh").fetchall())
    tree_cache = {}

    def tree(d):
        if d not in tree_cache:
            tree_cache[d] = set(TL.expand(con, "MESH:" + d)[0])
        return tree_cache[d]

    def run_route(r):
        if r["kind"] == "mesh":
            ids = set().union(*[tree(d) for d in r["mesh"]]) - set().union(set(), *[tree(d) for d in r.get("exclude_mesh", [])])
            asp, mt = r.get("study_aspect", "any"), r.get("mesh_type", "any")
            hit = {t for t, m, mty, sa in tm if m in ids and asp in ("any", sa) and mt in ("any", mty)}
            terms = "; ".join(f"{d.split(':')[1]} {mesh_name.get(d, '')}" for d in sorted(ids))
            return hit, terms, True
        field = r["field"]
        if field != "brief_title" and not have_full:
            return set(), ", ".join(r.get("terms", [])) or r.get("regex"), False
        rx = route_regex(r)
        hit = {i for i, t in trials.items() if rx.search(trial_text(t, field))}
        return hit, ", ".join(r.get("terms", [])) or r["regex"], True

    rows, sel, seen = [], set(), set()
    results = []
    for r in spec["routes"]:
        hit, terms, ok = run_route(r)
        results.append((r, hit, terms, ok))
        sel |= hit
    restrict_hits = None
    if spec.get("restrict"):
        restrict_hits = set()
        rres = []
        for r in spec["restrict"]:
            hit, terms, ok = run_route(r)
            rres.append((r, hit, terms, ok))
            restrict_hits |= hit
        cand = sel
        sel = cand & restrict_hits
    for r, hit, terms, ok in results:
        kept = hit & sel
        new = kept - seen
        seen |= kept
        rows.append([r["id"], r["label"], terms, len(hit) if ok else MISSING, len(kept) if ok else MISSING,
                     len(new) if ok else MISSING,
                     len(kept - set().union(set(), *[h for rr, h, _, _ in results if rr is not r])) if ok else MISSING])
    if restrict_hits is not None:
        rows.append(["candidates", "any inclusion route", "", len(cand), "", "", ""])
        for r, hit, terms, ok in rres:
            rows.append([r["id"], "restriction: " + r["label"], terms, len(hit & cand) if ok else MISSING,
                         len(hit & sel) if ok else MISSING, "",
                         len((hit - set().union(set(), *[h for rr, h, _, _ in rres if rr is not r])) & sel) if ok else MISSING])
    rows.append(["selected", spec["label"], "", len(sel), len(sel), "", ""])
    sub = set()
    if spec.get("subset"):
        for r in spec["subset"]["routes"]:
            hit, terms, ok = run_route(r)
            sub |= hit & sel
            rows.append([r["id"], f"subset '{spec['subset']['label']}': " + r["label"], terms, len(hit & sel) if ok else MISSING,
                         len(hit & sel) if ok else MISSING, "", ""])
        rows.append(["subset", spec["subset"]["label"], "", len(sub), len(sub), "", ""])
    return sel, sub, rows


# ---------------------------------------------------------------- report
def build(cache, spec, out, full_record=None, history=None, release=""):
    con, trials, have_full, hist = load_inputs(cache, full_record, history)
    W = Writer(out, release)
    sel, sub, route_rows = select(con, trials, spec, have_full)
    sub_label = spec.get("subset", {}).get("label", "subset")
    W("01_selection_routes.csv", ["route_id", "route", "terms", "trials_matched", "trials_kept", "trials_added_in_route_order",
                                  "trials_only_via_this_route"], route_rows,
      note="trials_matched: before any restriction; trials_kept: in the final selection; added_in_route_order: kept and not already "
           "kept by an earlier route; only_via_this_route: kept trials no other route of the same block matched. Text match: "
           "whole word, case-insensitive, plural s allowed on lower-case terms. MISSING = the field is not in the input.")

    lead, sp_name = {}, dict(con.sql("SELECT id, name FROM sponsors").fetchall())
    for t, s, ac, lc in con.sql("SELECT trial, sponsor, agency_class, lead_or_collaborator FROM sponsored_by").fetchall():
        if t in sel and (lc or "").lower() == "lead":
            lead[t] = (s, ac)
    sponsor = lambda t: sp_name.get(lead[t][0], lead[t][0]) if t in lead else TL.NO_SPONSOR
    sclass = lambda t: TL.CLASS_GROUP.get((lead[t][1] or "").upper(), "Network / individual / unknown") if t in lead else TL.NO_SPONSOR
    sites = {r[0]: r[1:] for r in con.sql("SELECT id, name, city, state, country FROM sites").fetchall()}
    tsites, site_status, keyinfo = defaultdict(set), {}, {}
    for t, s, st in con.sql("SELECT trial, site, site_status FROM conducted_at").fetchall():
        if t in sel:
            n, c, stt, ctry = sites.get(s, ("", "", "", ""))
            k = TL.site_merge_key(n, c, ctry)
            tsites[t].add(k)
            if site_status.get((t, k)) != "RECRUITING":
                site_status[(t, k)] = st
            keyinfo.setdefault(k, Counter())[(n, c, stt, ctry)] += 1
    kname = {k: v.most_common(1)[0][0] for k, v in keyinfo.items()}
    site_tr = defaultdict(set)
    for t, ks in tsites.items():
        for k in ks:
            site_tr[k].add(t)
    res = defaultdict(list)
    for art, t in con.sql("SELECT article, trial FROM trial_pubs WHERE rel = 'VALIDATED_BY'").fetchall():
        if t in sel:
            res[t].append(art)
    layer = dict(con.sql("SELECT id, layer FROM articles WHERE id IN (SELECT article FROM trial_pubs WHERE rel='VALIDATED_BY')").fetchall())
    cited = defaultdict(set)
    srg = dict(con.sql("SELECT id, layer FROM articles WHERE is_guideline OR is_systematic_review OR is_meta_analysis").fetchall())
    for c, d in con.sql("SELECT citer, cited FROM result_citers").fetchall():
        if srg.get(c) != STUB:
            cited[d].add(c)

    T = lambda t: trials[t]
    active = lambda t: T(t)["status"] in ACTIVE
    flag = lambda t: "yes" if t in sub else ""
    M = lambda v: MISSING if not have_full else ("" if v is None else v)
    J = lambda v: MISSING if not have_full else " | ".join(v or [])
    stop_group = lambda t: first_group(T(t)["why_stopped"], STOP_REASONS) if T(t)["why_stopped"] else None
    countries = lambda t: sorted({kname[k][3] for k in tsites[t] if kname[k][3]})

    def pc_months(t):
        return months_between(T(t)["start"], T(t)["primary_completion_date"])

    def recruit_months(t):
        """start -> primary completion minus the longest primary-outcome time frame; both dates ACTUAL."""
        if T(t)["start_date_type"] != "ACTUAL" or T(t)["primary_completion_date_type"] != "ACTUAL":
            return None
        span, fu = pc_months(t), max_time_frame_months(T(t)["primary_outcome_time_frames"])
        if span is None or fu is None:
            return None
        v = span - fu
        return v if v > 0 else None

    # 02 active trials
    act = sorted((t for t in sel if active(t)), key=lambda t: (T(t)["status"], -(int(T(t)["enrollment"] or 0)), T(t)["nct"]))
    W("02_active_trials.csv",
      ["nct_id", "brief_title", "official_title", sub_label, "lead_sponsor", "lead_sponsor_class", "phase", "status", "enrollment",
       "enrollment_type", "start_date", "primary_completion_date", "primary_completion_date_type", "completion_date",
       "intervention_names", "intervention_types", "primary_outcomes", "primary_outcome_time_frames", "sites", "countries", "url"],
      [[T(t)["nct"], T(t)["brief_title"], M(T(t)["official_title"]), flag(t), sponsor(t), sclass(t), T(t)["phase"] or "", T(t)["status"],
        T(t)["enrollment"], M(T(t)["enrollment_type"]), T(t)["start"], M(T(t)["primary_completion_date"]),
        M(T(t)["primary_completion_date_type"]), T(t)["completion"], J(T(t)["intervention_names"]), J(T(t)["intervention_types"]),
        J(T(t)["primary_outcome_measures"]), J(T(t)["primary_outcome_time_frames"]), len(tsites[t]), " | ".join(countries(t)),
        f"https://clinicaltrials.gov/study/{T(t)['nct']}"] for t in act],
      note=f"active = overall_status in {', '.join(ACTIVE)}; enrollment_type ESTIMATED = target, ACTUAL = enrolled")

    # 03 / 29 industry competitors
    ind = defaultdict(list)
    for t in sel:
        if sclass(t) == "Industry":
            ind[sponsor(t)].append(t)
    rows, prof = [], []
    for s, ts in ind.items():
        a_ts = sorted(t for t in ts if active(t))
        names = sorted({n for t in ts for n in (T(t)["intervention_names"] or []) if n and not re.search(r"placebo|standard of care|sham", n, re.I)})
        ks = set().union(set(), *[tsites[t] for t in ts])
        rows.append([s, len(a_ts), len(ts), sum(t in sub for t in ts), " | ".join(T(t)["nct"] for t in a_ts),
                     J(sorted({n for t in a_ts for n in (T(t)["intervention_names"] or [])})) if have_full else MISSING,
                     sum(int(T(t)["enrollment"] or 0) for t in a_ts)])
        prof.append([s, len(ts), len(a_ts), " | ".join(T(t)["nct"] for t in sorted(ts)), J(names) if have_full else MISSING,
                     len(ks), len({kname[k][3] for k in ks if kname[k][3]}), sum(int(T(t)["enrollment"] or 0) for t in ts),
                     sum(int(T(t)["enrollment"] or 0) for t in a_ts),
                     " | ".join(f"{T(t)['nct']}: {T(t)['primary_completion_date'] or '?'} ({T(t)['primary_completion_date_type'] or '?'})"
                                for t in sorted(a_ts, key=lambda t: T(t)["primary_completion_date"] or "9999")) if have_full else MISSING])
    rows.sort(key=lambda r: (-r[1], -r[2], r[0]))
    prof.sort(key=lambda r: (-r[2], -r[1], r[0]))
    W("03_industry_competitors.csv", ["industry_lead_sponsor", "active_trials", "all_trials", f"all_trials_{sub_label}",
                                      "active_nct_ids", "active_intervention_names", "active_total_enrollment"], rows)
    W("29_competitor_profiles.csv", ["industry_lead_sponsor", "trials", "active_trials", "nct_ids", "intervention_and_product_names",
                                     "sites_merged", "countries", "enrollment_all_trials", "enrollment_active_trials",
                                     "expected_readouts_active (primary completion, type)"], prof,
      note="intervention names exclude placebo / sham / standard of care; readouts = primary_completion_date of active trials")

    # 04-07 sites
    rows = []
    for k, ts in site_tr.items():
        n, c, stt, ctry = kname[k]
        a_ts = {t for t in ts if active(t)}
        rows.append([n, c, stt, ctry, len(a_ts), sum(site_status.get((t, k)) == "RECRUITING" for t in a_ts), len(ts),
                     sum(t in sub for t in ts), len({sponsor(t) for t in a_ts})])
    rows.sort(key=lambda r: (-r[4], -r[6], r[0]))
    W("04_top_sites_by_active_trials.csv", ["site", "city", "state", "country", "active_trials", "active_trials_site_recruiting",
                                            "all_trials", f"all_trials_{sub_label}", "active_lead_sponsors"], rows,
      note="sites merged as trial_landscape.py --merge-sites")
    top_sites = sorted(site_tr, key=lambda k: (-len(site_tr[k]), kname[k][0]))[:25]
    top_sp = [s for s, _ in Counter(sponsor(t) for k in top_sites for t in site_tr[k]).most_common(12)]
    W("05_site_x_sponsor_overlap.csv", ["site", "country", "all_trials"] + top_sp,
      [[kname[k][0], kname[k][3], len(site_tr[k])] + [sum(sponsor(t) == s for t in site_tr[k]) for s in top_sp] for k in top_sites])
    st = defaultdict(lambda: [set(), set(), set()])
    for k, ts in site_tr.items():
        if kname[k][3] == "United States":
            v = st[kname[k][2] or "(missing)"]
            v[0].add(k); v[1].update(ts); v[2].update(t for t in ts if active(t))
    W("06_us_sites_by_state.csv", ["state", "sites", "trials", "active_trials"],
      sorted(([s, len(v[0]), len(v[1]), len(v[2])] for s, v in st.items()), key=lambda r: (-r[2], r[0])))
    W("07_completed_trials_per_site.csv", ["site", "city", "country", "completed_trials", "all_trials"],
      [r for r in sorted(([kname[k][0], kname[k][1], kname[k][3], sum(T(t)["status"] == "COMPLETED" for t in ts), len(ts)]
                          for k, ts in site_tr.items()), key=lambda r: (-r[3], -r[4], r[0])) if r[3] > 0])
    W("08_investigators.csv", ["field", "status"], [["overall_officials / investigators", MISSING]])

    # 09 readout pipeline
    yrs = defaultdict(lambda: [0, 0, 0, 0])
    for t in sel:
        pcd = T(t)["primary_completion_date"]
        y = (pcd or "")[:4] or "(missing)"
        yrs[y][0] += 1
        if active(t):
            yrs[y][1] += 1; yrs[y][2] += t in sub; yrs[y][3] += T(t)["primary_completion_date_type"] == "ESTIMATED"
    W("09_readout_pipeline.csv", ["primary_completion_year", "all_trials", "active_trials", f"active_{sub_label}", "active_estimated"],
      [[y, *v] for y, v in sorted(yrs.items())] if have_full else [[MISSING, "", "", "", ""]])

    # 10 / 25 endpoints
    eg, unmatched, n_po = Counter(), 0, 0
    for t in sel:
        pm = T(t)["primary_outcome_measures"] or []
        if not pm:
            continue
        n_po += 1
        gs = {first_group(m, OUTCOME_KEYWORDS) for m in pm} - {None}
        eg.update(gs)
        unmatched += not gs
    W("10_primary_outcomes.csv", ["outcome_group", "keyword_regex", "trials", "share_of_trials_with_primary_outcome"],
      ([[g, rx, eg[g], r1(100 * eg[g] / n_po) if n_po else None] for g, rx in OUTCOME_KEYWORDS] +
       [["(no group matched)", "", unmatched, r1(100 * unmatched / n_po) if n_po else None]]) if have_full else
      [[g, rx, MISSING, ""] for g, rx in OUTCOME_KEYWORDS],
      note=f"each primary outcome measure gets the first matching group (order as listed); a trial counts once per group; "
           f"{n_po} trials have >=1 primary outcome")
    tfb = Counter()
    for t in sel:
        m = max_time_frame_months(T(t)["primary_outcome_time_frames"])
        tfb["(not parseable / missing)" if m is None else next(lbl for ub, lbl in TF_BINS if m <= ub)] += 1
    W("25_primary_followup_time_frames.csv", ["longest_primary_time_frame", "trials"],
      [[lbl, tfb[lbl]] for _, lbl in TF_BINS] + [["(not parseable / missing)", tfb["(not parseable / missing)"]]],
      note="longest duration written in any primary-outcome time frame (number + hour/day/week/month/year; number words one-twelve)")

    # 11 / 24 termination
    stp = sorted((t for t in sel if T(t)["status"] in ("TERMINATED", "WITHDRAWN", "SUSPENDED")), key=lambda t: (T(t)["status"], T(t)["nct"]))
    W("11_why_stopped.csv", ["nct_id", "brief_title", "status", "lead_sponsor", "lead_sponsor_class", "why_stopped", "stop_reason_group"],
      [[T(t)["nct"], T(t)["brief_title"], T(t)["status"], sponsor(t), sclass(t), M(T(t)["why_stopped"]),
        (stop_group(t) or "(no reason given)") if have_full else MISSING] for t in stp])
    closed = [t for t in sel if T(t)["status"] in CLOSED]
    term = [t for t in closed if T(t)["status"] in ("TERMINATED", "WITHDRAWN")]
    rg = Counter((stop_group(t) or "(no reason given)") for t in term)
    rows = [["termination_rate_pct", r1(100 * len(term) / len(closed)) if closed else None,
             f"TERMINATED or WITHDRAWN / closed trials (COMPLETED + TERMINATED + WITHDRAWN) = {len(term)} / {len(closed)}"],
            ["terminated_only_rate_pct", r1(100 * sum(T(t)['status'] == 'TERMINATED' for t in closed) / len(closed)) if closed else None,
             "TERMINATED / closed trials"]]
    for g, rx in STOP_REASONS + [("(no reason given)", "")]:
        rows.append([f"stop_reason: {g}", rg[g] if have_full else MISSING, f"regex: {rx}" if rx else "why_stopped empty"])
    W("24_termination.csv", ["metric", "value", "definition"], rows,
      note="stop reasons grouped by the first matching regex, in the order listed")

    # 12 design
    rows = []
    for f in ("allocation", "intervention_model", "masking", "primary_purpose"):
        c = Counter(T(t)[f] or "(missing)" for t in sel)
        rows += [[f, k, v] for k, v in c.most_common()] if have_full else [[f, MISSING, ""]]
    rows += [["study_type", k, v] for k, v in Counter(T(t)["study_type"] or "(missing)" for t in sel).most_common()]
    W("12_allocation_masking.csv", ["field", "value", "trials"], rows)

    # 13 results
    rows = []
    for t in sorted(sel, key=lambda t: T(t)["nct"]):
        rs = res[t]
        full = [x for x in rs if layer.get(x) != STUB]
        cit = set().union(set(), *[cited[x] for x in full])
        if rs or T(t)["results_first_posted_date"]:
            rows.append([T(t)["nct"], T(t)["brief_title"], flag(t), T(t)["status"], M(T(t)["results_first_posted_date"]),
                         len(rs), len(full), len(cit)])
    W("13_results.csv", ["nct_id", "brief_title", sub_label, "status", "results_first_posted_on_ctgov", "results_articles_incl_stubs",
                         "results_articles_full_record", "citing_reviews_or_guidelines"], rows)

    # 14-18
    cc = defaultdict(lambda: [set(), set(), set()])
    for t in sel:
        for c in countries(t):
            cc[c][0].add(t); cc[c][1].update([t] if active(t) else []); cc[c][2].update([t] if t in sub else [])
    W("14_countries.csv", ["country", "trials", "active_trials", f"trials_{sub_label}"],
      sorted(([c, len(v[0]), len(v[1]), len(v[2])] for c, v in cc.items()), key=lambda r: (-r[1], r[0])))
    sc, scs = Counter(sclass(t) for t in sel), Counter(sclass(t) for t in sub)
    W("15_lead_sponsor_class.csv", ["lead_sponsor_class", "trials", sub_label, "active"],
      [[c, n, scs[c], sum(sclass(t) == c and active(t) for t in sel)] for c, n in sc.most_common()])
    tsp = Counter(sponsor(t) for t in sel)
    W("16_top_lead_sponsors.csv", ["lead_sponsor", "class", "trials", sub_label, "active"],
      [[s, next(sclass(t) for t in sel if sponsor(t) == s), n, sum(sponsor(t) == s for t in sub),
        sum(sponsor(t) == s and active(t) for t in sel)] for s, n in tsp.most_common(25)])
    ph, phs = Counter(T(t)["phase"] or "(missing)" for t in sel), Counter(T(t)["phase"] or "(missing)" for t in sub)
    W("17_phase.csv", ["phase", "trials", sub_label], [[p, ph[p], phs[p]] for p in list(TL.PHASE_ORDER) + ["(missing)"] if ph.get(p)])
    sy, sys_ = Counter((T(t)["start"] or "")[:4] or "(missing)" for t in sel), Counter((T(t)["start"] or "")[:4] or "(missing)" for t in sub)
    W("18_started_per_year.csv", ["start_year", "trials", sub_label], [[y, sy[y], sys_[y]] for y in sorted(sy)])

    # 20 design benchmarks / 21 enrollment rate
    def bench_groups(ts):
        g = defaultdict(list)
        for t in ts:
            g[("all", "all")].append(t)
            g[(T(t)["phase"] or "(missing)", "all")].append(t)
            g[("all", sclass(t))].append(t)
            g[(T(t)["phase"] or "(missing)", sclass(t))].append(t)
        return g
    metrics = [
        ("sites_per_trial", lambda t: len(tsites[t]) or None, "merged sites per trial (trials with >=1 site)"),
        ("target_enrollment", lambda t: T(t)["enrollment"] if T(t)["enrollment_type"] == "ESTIMATED" else None,
         "enrollment where enrollment_type = ESTIMATED (the current target)"),
        ("actual_enrollment", lambda t: T(t)["enrollment"] if T(t)["enrollment_type"] == "ACTUAL" and T(t)["status"] == "COMPLETED" else None,
         "enrollment where enrollment_type = ACTUAL, completed trials"),
        ("start_to_primary_completion_months", lambda t: pc_months(t) if (pc_months(t) or 0) > 0 else None,
         "start_date to primary_completion_date (actual or anticipated), months"),
        ("recruitment_months", recruit_months,
         "derived: start to primary completion (both ACTUAL) minus the longest primary-outcome time frame, months; positive only"),
    ]
    rows = []
    for (p, c), ts in sorted(bench_groups(sel).items(), key=lambda kv: (kv[0][0] != "all", kv[0][0], kv[0][1] != "all", kv[0][1])):
        for name, f, d in metrics:
            n, med, q1, q3 = quantiles([f(t) for t in ts])
            if n:
                rows.append([p, c, name, n, r1(med), r1(q1), r1(q3), d])
    W("20_design_benchmarks.csv", ["phase", "lead_sponsor_class", "metric", "n_trials", "median", "q1", "q3", "definition"], rows,
      note="comparable trials = same topic selection, grouped by phase x lead-sponsor class ('all' = pooled); median and IQR (inclusive quartiles)")
    rate_rows, rates = [], {}
    for t in sel:
        rm = recruit_months(t)
        if T(t)["status"] == "COMPLETED" and T(t)["enrollment_type"] == "ACTUAL" and T(t)["enrollment"] and tsites[t] and rm:
            rates[t] = T(t)["enrollment"] / len(tsites[t]) / rm
    for (p, c), ts in sorted(bench_groups(list(rates)).items(), key=lambda kv: (kv[0][0] != "all", kv[0][0], kv[0][1] != "all", kv[0][1])):
        n, med, q1, q3 = quantiles([rates[t] for t in ts])
        rate_rows.append([p, c, n, None if med is None else round(med, 2), None if q1 is None else round(q1, 2),
                          None if q3 is None else round(q3, 2)])
    W("21_enrollment_rate.csv", ["phase", "lead_sponsor_class", "n_trials", "median_patients_per_site_month", "q1", "q3"], rate_rows,
      note="actual enrollment / merged sites / recruitment_months (see 20_design_benchmarks.csv); COMPLETED trials with ACTUAL enrollment")
    W("21b_enrollment_rate_trials.csv", ["nct_id", "phase", "lead_sponsor_class", "actual_enrollment", "sites", "recruitment_months",
                                         "patients_per_site_month"],
      [[T(t)["nct"], T(t)["phase"], sclass(t), T(t)["enrollment"], len(tsites[t]), r1(recruit_months(t)), round(v, 3)]
       for t, v in sorted(rates.items(), key=lambda kv: T(kv[0])["nct"])])

    # 22 planned vs actual / 23 site activation (record history)
    if hist:
        rows, act_rows = [], []
        for t in sorted(sel, key=lambda t: T(t)["nct"]):
            vs = hist.get(T(t)["nct"])
            if not vs:
                continue
            first = next((v for v in vs if v.get("enrollment") is not None), None)
            last = vs[-1]
            if first and last.get("enrollment_type") == "ACTUAL" and first.get("enrollment_type") == "ESTIMATED":
                rows.append([T(t)["nct"], T(t)["status"], first["date"], first["enrollment"], last["date"], last["enrollment"],
                             r1(100 * last["enrollment"] / first["enrollment"]) if first["enrollment"] else None])
            seen = {}
            for v in vs:
                for s in v.get("sites", []):
                    k = TL.site_merge_key(s.get("name", ""), s.get("city", ""), s.get("country", ""))
                    if k not in seen:
                        seen[k] = (v["date"], s)
            first_date = vs[0]["date"]
            for k, (d, s) in seen.items():
                if d > first_date:
                    act_rows.append([T(t)["nct"], s.get("name"), s.get("city"), s.get("country"), d, s.get("status"),
                                     r1(months_between(T(t)["start"], d))])
        n, med, q1, q3 = quantiles([r[6] for r in rows])
        W("22_planned_vs_actual_enrollment.csv", ["nct_id", "status", "first_version_date", "planned_enrollment", "last_version_date",
                                                  "actual_enrollment", "actual_pct_of_planned"], rows,
          note=f"planned = first version in the history with enrollment_type ESTIMATED; actual = latest version with ACTUAL; "
               f"n={n}, median {r1(med)}% (IQR {r1(q1)}-{r1(q3)})")
        n2, med2, q12, q32 = quantiles([r[6] for r in act_rows])
        W("23_site_activation.csv", ["nct_id", "site", "city", "country", "first_listed_in_version_dated", "status_when_listed",
                                     "months_after_trial_start"], act_rows,
          note=f"sites first appearing after the earliest version in the history; n={n2}, median {r1(med2)} months after trial start "
               f"(IQR {r1(q12)}-{r1(q32)}). Sites present in the earliest version are not dated.")
    else:
        for name in ("22_planned_vs_actual_enrollment.csv", "23_site_activation.csv"):
            W(name, ["field", "status"], [["record version history", MISSING]])

    # 26 eligibility
    rows = []
    for t_set, lbl in ((sel, "all"), (sub, sub_label)):
        if have_full:
            for b, n in Counter(age_band(T(t)["eligibility_minimum_age"], T(t)["eligibility_maximum_age"]) for t in t_set).most_common():
                rows.append([lbl, "age_band", b, n])
            for s, n in Counter(T(t)["eligibility_sex"] or "(missing)" for t in t_set).most_common():
                rows.append([lbl, "sex", s, n])
            for s, n in Counter(str(T(t)["eligibility_healthy_volunteers"]) for t in t_set).most_common():
                rows.append([lbl, "healthy_volunteers", s, n])
    W("26_eligibility_norms.csv", ["trials", "field", "value", "n"], rows or [["all", "eligibility", MISSING, ""]])
    rows, bigr = [], Counter()
    n_ex = 0
    for t in sel:
        ex = exclusion_text(T(t)["eligibility_criteria"])
        if not ex:
            continue
        n_ex += 1
        for g, rx in EXCLUSION_KEYWORDS:
            if re.search(rx, ex, re.I):
                bigr[("keyword", g)] += 1
        toks = [w for w in re.findall(r"[a-z][a-z\-]+", ex.lower()) if w not in STOPWORDS]
        bigr.update({("bigram", f"{a} {b}") for a, b in zip(toks, toks[1:])})
    for g, rx in EXCLUSION_KEYWORDS:
        rows.append(["keyword", g, rx, bigr[("keyword", g)], r1(100 * bigr[("keyword", g)] / n_ex) if n_ex else None])
    for (kind, g), n in sorted(((k, n) for k, n in bigr.items() if k[0] == "bigram"), key=lambda kv: (-kv[1], kv[0][1]))[:30]:
        rows.append(["frequent bigram", g, "", n, r1(100 * n / n_ex)])
    W("27_exclusion_terms.csv", ["kind", "term", "regex", "trials", "pct_of_trials_with_exclusion_text"],
      rows if have_full else [["exclusion criteria", MISSING, "", "", ""]],
      note=f"exclusion text = eligibility_criteria after 'Exclusion Criteria'; {n_ex} trials have it; a trial counts once per term; "
           "bigrams: lower-cased words, stopwords removed, top 30")

    # 28 site shortlist
    rows = []
    wts = {c: w for c, w, _ in SITE_SHORTLIST_WEIGHTS}
    for k, ts in site_tr.items():
        crit = {"completed_trials_in_topic": sum(T(t)["status"] == "COMPLETED" for t in ts),
                "accrual_terminations_in_topic": sum(T(t)["status"] in ("TERMINATED", "WITHDRAWN") and stop_group(t) == "enrollment or accrual" for t in ts),
                "competing_active_trials_in_topic": sum(active(t) for t in ts),
                "recruiting_now": int(any(site_status.get((t, k)) == "RECRUITING" for t in ts))}
        score = sum(wts[c] * v for c, v in crit.items())
        n, c, stt, ctry = kname[k]
        rows.append([n, c, stt, ctry, score, *crit.values(), len(ts)])
    rows.sort(key=lambda r: (-r[4], -r[5], r[0]))
    W("28_site_shortlist.csv", ["site", "city", "state", "country", "score"] + [c for c, _, _ in SITE_SHORTLIST_WEIGHTS] + ["all_topic_trials"],
      rows[:100], note="score = " + " + ".join(f"({w}) x {c}" for c, w, _ in SITE_SHORTLIST_WEIGHTS) + ". " +
      "; ".join(f"{c}: {d}" for c, _, d in SITE_SHORTLIST_WEIGHTS) + ". Ties: more completed trials, then name. Top 100.")
    W("28b_site_shortlist_criteria.csv", ["criterion", "weight", "definition"], [list(x) for x in SITE_SHORTLIST_WEIGHTS])

    # 30 active timeline
    W("30_active_timeline.csv", ["nct_id", "brief_title", sub_label, "lead_sponsor", "lead_sponsor_class", "phase", "status", "start_date",
                                 "start_date_type", "primary_completion_date", "primary_completion_date_type", "months_start_to_primary_completion"],
      [[T(t)["nct"], T(t)["brief_title"], flag(t), sponsor(t), sclass(t), T(t)["phase"] or "", T(t)["status"], T(t)["start"],
        M(T(t)["start_date_type"]), M(T(t)["primary_completion_date"]), M(T(t)["primary_completion_date_type"]), r1(pc_months(t))]
       for t in sorted(act, key=lambda t: (T(t)["start"] or "", T(t)["nct"]))])

    # 00 headline, 19 coverage
    def headline(ts):
        ks = set().union(set(), *[tsites[t] for t in ts])
        cl = [t for t in ts if T(t)["status"] in CLOSED]
        return dict(trials=len(ts), active=sum(active(t) for t in ts), recruiting=sum(T(t)["status"] == "RECRUITING" for t in ts),
                    merged_sites=len(ks), countries=len({kname[k][3] for k in ks if kname[k][3]}),
                    industry_lead=sum(sclass(t) == "Industry" for t in ts),
                    results_posted_on_ctgov=sum(bool(T(t)["results_first_posted_date"]) for t in ts) if have_full else MISSING,
                    trials_with_results_article_incl_stubs=sum(bool(res[t]) for t in ts),
                    trials_with_full_record_results_article=sum(any(layer.get(x) != STUB for x in res[t]) for t in ts),
                    trials_results_cited_by_review_or_guideline=sum(any(cited[x] for x in res[t] if layer.get(x) != STUB) for t in ts),
                    terminated_or_withdrawn=sum(T(t)["status"] in ("TERMINATED", "WITHDRAWN") for t in ts),
                    termination_rate_pct=r1(100 * sum(T(t)["status"] in ("TERMINATED", "WITHDRAWN") for t in cl) / len(cl)) if cl else None)
    H, Hs = headline(sel), headline(sub)
    W("00_headline.csv", ["metric", spec["label"], sub_label], [[k, H[k], Hs[k]] for k in H])
    cov = []
    for f in FULL_FIELDS:
        n = sum(T(t)[f] not in (None, [], "") for t in sel)
        cov.append([f, n if have_full else MISSING, len(sel), r1(100 * n / len(sel)) if have_full and sel else ""])
    cov += [[f, MISSING, len(sel), why] for f, why in NOT_AVAILABLE]
    cov.append(["record version history", len({T(t)['nct'] for t in sel} & set(hist)) if hist else MISSING, len(sel), ""])
    W("19_field_coverage.csv", ["field", "trials_with_value", "trials_selected", "pct_or_note"], cov)
    with open(os.path.join(out, "trials_selected.txt"), "w") as fh:
        fh.write("\n".join(sorted(T(t)["nct"] for t in sel)))
    with open(os.path.join(out, "trials_subset.txt"), "w") as fh:
        fh.write("\n".join(sorted(T(t)["nct"] for t in sub)))
    return dict(headline=H, subset=Hs, routes=route_rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cache", required=True)
    ap.add_argument("--topic", required=True, help="topic spec JSON")
    ap.add_argument("--out", required=True)
    ap.add_argument("--full-record")
    ap.add_argument("--history")
    ap.add_argument("--release-label", default="")
    a = ap.parse_args()
    spec = json.load(open(a.topic))
    out = build(a.cache, spec, a.out, a.full_record, a.history, a.release_label)
    print(json.dumps(dict(topic=spec["label"], headline=out["headline"], subset=out["subset"]), indent=1, default=str))


if __name__ == "__main__":
    main()
