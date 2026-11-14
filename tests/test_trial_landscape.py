"""examples/trial_landscape.py on the bundled sample subgraph: summary fields and report files.

  pip install duckdb pytest
  pytest tests/test_trial_landscape.py
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_cli_summary_and_reports(tmp_path):
    out = tmp_path / "out"
    subprocess.run([sys.executable, os.path.join(ROOT, "examples", "trial_landscape.py"), "--input",
                    os.path.join(ROOT, "sample_out"), "--cache", str(tmp_path / "cache"), "--condition", "D001943",
                    "--out", str(out)], check=True, stdout=subprocess.DEVNULL)
    s = json.loads((out / "summary.json").read_text())
    assert s["trials"] > 0
    assert s["results_article_rows"] == s["results_articles"]
    assert s["results_articles_distinct_not_identity_only"] <= s["results_articles_distinct"] <= s["results_article_rows"]
    assert (s["results_articles_distinct_cited_by_guideline_or_sr_not_identity_only"]
            <= s["results_articles_distinct_cited_by_guideline_or_sr"] <= s["results_articles_cited_by_guideline_or_sr"])
    for f in ("report.html", "README.md", "trials.csv", "results_publications.csv", "sites.csv", "countries.csv",
              "by_sponsor.csv", "by_sponsor_class.csv", "by_phase_status.csv", "timeline_start_year.csv", "descriptors.csv"):
        assert (out / f).exists(), f
    html = (out / "report.html").read_text()
    assert "<script" not in html.lower()
    assert "Practice Guideline or Systematic Review" in html and "lower bounds" in html
    md = (out / "README.md").read_text()
    assert "distinct results Articles" in md and "lower bounds" in md
