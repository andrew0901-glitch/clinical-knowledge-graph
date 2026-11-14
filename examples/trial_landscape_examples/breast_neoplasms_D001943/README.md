# Clinical trial landscape: Breast Neoplasms

MeSH D001943 and 8 narrower descriptors. Source: Lunas Clinical Evidence KG v0.2.1 (snapshot 2026-11-07). Built by `examples/trial_landscape.py`; the same content with charts is in `report.html` (download and open it in a browser).

A trial matches when ClinicalTrials.gov lists the descriptor, or one of its narrower descriptors, among the trial's condition browse terms (`ClinicalTrial -HAS_MESH {study_aspect:'condition', mesh_type:'mesh-list'}-> MeSHConcept`). Status is the registry status at the snapshot date.

| measure | value |
|---|---|
| matching trials | 14,321 |
| direct on the descriptor | 13,445 |
| via narrower descriptors only | 876 |
| recruiting (registry status) | 1,992 |
| not yet recruiting | 645 |
| interventional | 11,198 |
| lead sponsors | 3,040 |
| trials with sites | 12,611 |
| sites | 60,591 |
| countries | 119 |
| trials with a results article | 1,006 |
| results trial-article links (rows) | 3,258 |
| distinct results Articles | 3,087 |
| distinct results Articles with a PubMed record | 1,211 |
| distinct results Articles cited by a guideline or SR | 646 |
| ... of which with a PubMed record | 646 |
| results trial-article links cited by a guideline or SR | 735 |

**Records not in this release:** 437 matching trials (the newest registrations) have no sponsor or site records, including 163 recruiting ones. They are counted in trial totals, phase and status, and are missing from sponsor, site and country figures.

## Results articles and citations within the graph

A results article is an Article linked to the trial with the RESULT role (`VALIDATED_BY`, Article -> ClinicalTrial). Identity-only Articles (`lunasai_layer` = `ctgov_identity_only`) carry a PMID but no bibliographic data.

**Cited by a guideline or SR** means at least one Article in the graph whose NLM publication types include Guideline, Practice Guideline or Systematic Review cites the results article (CITES edge; an Article citing itself is not counted; Meta-Analysis alone does not qualify). Only citations between Articles in the graph are counted, so cited counts are lower bounds; an article not cited within the graph may be cited elsewhere.

Top 25 of 3,258 trial-article links (all in `results_publications.csv`):

| nct_id | pmid | article_title | year | identity_only | cited_in_graph | cited_by_guidelines | cited_by_systematic_reviews |
|---|---|---|---|---|---|---|---|
| NCT04817813 | 15273542 | Classification of surgical complications: a new proposal with evaluation in a cohort of 6336 patients and results of a survey. | 2,004 | False | 5499.0 | 5 | 184 |
| NCT06433349 | 33069326 | Global burden of 369 diseases and injuries in 204 countries and territories, 1990-2019: a systematic analysis for the Global Burden of Disease Study 2019. | 2,020 | False | 1954.0 | 7 | 147 |
| NCT02964286 | 22818936 | Effect of physical inactivity on major non-communicable diseases worldwide: an analysis of burden of disease and life expectancy. | 2,012 | False | 782.0 | 2 | 86 |
| NCT07676591 | 8433390 | The European Organization for Research and Treatment of Cancer QLQ-C30: a quality-of-life instrument for use in international clinical trials in oncology. | 1,993 | False | 2445.0 | 6 | 69 |
| NCT06690320 | 33538338 | Global Cancer Statistics 2020: GLOBOCAN Estimates of Incidence and Mortality Worldwide for 36 Cancers in 185 Countries. | 2,021 | False | 1504.0 | 0 | 52 |
| NCT07238894 | 33538338 | Global Cancer Statistics 2020: GLOBOCAN Estimates of Incidence and Mortality Worldwide for 36 Cancers in 185 Countries. | 2,021 | False | 1504.0 | 0 | 52 |
| NCT02408393 | 16698416 | Persistent postsurgical pain: risk factors and prevention. | 2,006 | False | 668.0 | 0 | 52 |
| NCT05450016 | 28117445 | Dermatologist-level classification of skin cancer with deep neural networks. | 2,017 | False | 1148.0 | 2 | 42 |
| NCT01290835 | 12393820 | Twenty-year follow-up of a randomized trial comparing total mastectomy, lumpectomy, and lumpectomy plus irradiation for the treatment of invasive breast cancer. | 2,002 | False | 1057.0 | 9 | 33 |
| NCT02400190 | 12393820 | Twenty-year follow-up of a randomized trial comparing total mastectomy, lumpectomy, and lumpectomy plus irradiation for the treatment of invasive breast cancer. | 2,002 | False | 1057.0 | 9 | 33 |
| NCT06946238 | 12393820 | Twenty-year follow-up of a randomized trial comparing total mastectomy, lumpectomy, and lumpectomy plus irradiation for the treatment of invasive breast cancer. | 2,002 | False | 1057.0 | 9 | 33 |
| NCT07345026 | 19644246 | Development of a new patient-reported outcome measure for breast surgery: the BREAST-Q. | 2,009 | False | 541.0 | 1 | 39 |
| NCT01290835 | 16360786 | Effects of radiotherapy and of differences in the extent of surgery for early breast cancer on local recurrence and 15-year survival: an overview of the randomised trials. | 2,005 | False | 935.0 | 14 | 24 |
| NCT06946238 | 16360786 | Effects of radiotherapy and of differences in the extent of surgery for early breast cancer on local recurrence and 15-year survival: an overview of the randomised trials. | 2,005 | False | 935.0 | 14 | 24 |
| NCT07676591 | 23295957 | SPIRIT 2013 statement: defining standard protocol items for clinical trials. | 2,013 | False | 1462.0 | 6 | 30 |
| NCT01016665 | 15894097 | Effects of chemotherapy and hormonal therapy for early breast cancer on recurrence and 15-year survival: an overview of the randomised trials. | 2,005 | False | 959.0 | 11 | 23 |
| NCT02995772 | 15894097 | Effects of chemotherapy and hormonal therapy for early breast cancer on recurrence and 15-year survival: an overview of the randomised trials. | 2,005 | False | 959.0 | 11 | 23 |
| NCT05661656 | 15894097 | Effects of chemotherapy and hormonal therapy for early breast cancer on recurrence and 15-year survival: an overview of the randomised trials. | 2,005 | False | 959.0 | 11 | 23 |
| NCT04248998 | 30207593 | Global cancer statistics 2018: GLOBOCAN estimates of incidence and mortality worldwide for 36 cancers in 185 countries. | 2,018 | False | 924.0 | 0 | 30 |
| NCT04328194 | 30207593 | Global cancer statistics 2018: GLOBOCAN estimates of incidence and mortality worldwide for 36 cancers in 185 countries. | 2,018 | False | 924.0 | 0 | 30 |
| NCT05177432 | 30207593 | Global cancer statistics 2018: GLOBOCAN estimates of incidence and mortality worldwide for 36 cancers in 185 countries. | 2,018 | False | 924.0 | 0 | 30 |
| NCT07446868 | 30207593 | Global cancer statistics 2018: GLOBOCAN estimates of incidence and mortality worldwide for 36 cancers in 185 countries. | 2,018 | False | 924.0 | 0 | 30 |
| NCT00000611 | 16481635 | Calcium plus vitamin D supplementation and the risk of fractures. | 2,006 | False | 275.0 | 9 | 22 |
| NCT07676591 | 29395269 | Global surveillance of trends in cancer survival 2000-14 (CONCORD-3): analysis of individual records for 37 513 025 patients diagnosed with one of 18 cancers from 322 population-based registries in 71 countries. | 2,018 | False | 440.0 | 4 | 26 |
| NCT04248998 | 24529560 | Pathological complete response and long-term clinical benefit in breast cancer: the CTNeoBC pooled analysis. | 2,014 | False | 592.0 | 5 | 23 |

## Lead sponsor class

| sponsor_class | trials | recruiting |
|---|---|---|
| Academic / hospital / other | 10,072 | 1,414 |
| Industry | 2,870 | 335 |
| Government | 653 | 64 |
| No sponsor record in release | 437 | 163 |
| Network / individual / unknown | 289 | 16 |

ClinicalTrials.gov has no academic class: universities and hospitals are filed as OTHER.

## Lead sponsors (top 25 by trials led; all in `by_sponsor.csv`)

| sponsor | agency_class | sponsor_class | trials_as_lead | trials_as_collaborator | recruiting_as_lead |
|---|---|---|---|---|---|
| national cancer institute (nci) | NIH | Government | 307 | 1,334 | 19 |
| m.d. anderson cancer center | OTHER | Academic / hospital / other | 239 | 22 | 30 |
| memorial sloan kettering cancer center | OTHER | Academic / hospital / other | 235 | 16 | 41 |
| fudan university | OTHER | Academic / hospital / other | 233 | 10 | 47 |
| hoffmann-la roche | INDUSTRY | Industry | 181 | 57 | 9 |
| astrazeneca | INDUSTRY | Industry | 178 | 127 | 13 |
| novartis pharmaceuticals | INDUSTRY | Industry | 173 | 49 | 13 |
| pfizer | INDUSTRY | Industry | 159 | 134 | 3 |
| mayo clinic | OTHER | Academic / hospital / other | 151 | 11 | 27 |
| dana-farber cancer institute | OTHER | Academic / hospital / other | 143 | 41 | 14 |
| alliance for clinical trials in oncology | OTHER | Academic / hospital / other | 93 | 6 | 3 |
| eli lilly and company | INDUSTRY | Industry | 92 | 39 | 9 |
| city of hope medical center | OTHER | Academic / hospital / other | 85 | 4 | 9 |
| washington university school of medicine | OTHER | Academic / hospital / other | 84 | 7 | 14 |
| sun yat-sen memorial hospital of sun yat-sen university | OTHER | Academic / hospital / other | 80 | 12 | 30 |
| unc lineberger comprehensive cancer center | OTHER | Academic / hospital / other | 80 | 4 | 21 |
| case comprehensive cancer center | OTHER | Academic / hospital / other | 70 | 1 | 2 |
| assiut university | OTHER | Academic / hospital / other | 69 | 3 | 0 |
| stanford university | OTHER | Academic / hospital / other | 66 | 8 | 5 |
| massachusetts general hospital | OTHER | Academic / hospital / other | 65 | 34 | 7 |
| northwestern university | OTHER | Academic / hospital / other | 65 | 4 | 4 |
| wake forest university health sciences | OTHER | Academic / hospital / other | 65 | 2 | 5 |
| duke university | OTHER | Academic / hospital / other | 64 | 15 | 4 |
| university of washington | OTHER | Academic / hospital / other | 63 | 10 | 3 |
| ohio state university comprehensive cancer center | OTHER | Academic / hospital / other | 63 | 3 | 10 |

## Phase by overall status

| phase | RECRUITING | NOT_YET_RECRUITING | ENROLLING_BY_INVITATION | ACTIVE_NOT_RECRUITING | SUSPENDED | COMPLETED | TERMINATED | WITHDRAWN | UNKNOWN | AVAILABLE | TEMPORARILY_NOT_AVAILABLE | NO_LONGER_AVAILABLE | APPROVED_FOR_MARKETING |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EARLY_PHASE1 | 26 | 5 | 2 | 5 | 0 | 103 | 18 | 20 | 23 | 0 | 0 | 0 | 0 |
| PHASE1 | 171 | 17 | 4 | 111 | 10 | 769 | 193 | 57 | 91 | 0 | 0 | 0 | 0 |
| PHASE1/PHASE2 | 128 | 38 | 3 | 63 | 2 | 287 | 133 | 36 | 74 | 0 | 0 | 0 | 0 |
| PHASE2 | 380 | 145 | 6 | 215 | 4 | 1,346 | 445 | 125 | 419 | 0 | 0 | 0 | 0 |
| PHASE2/PHASE3 | 14 | 4 | 1 | 9 | 1 | 43 | 15 | 4 | 34 | 0 | 0 | 0 | 0 |
| PHASE3 | 151 | 47 | 1 | 127 | 6 | 613 | 92 | 25 | 154 | 0 | 0 | 0 | 0 |
| PHASE4 | 32 | 20 | 0 | 7 | 0 | 136 | 18 | 10 | 60 | 0 | 0 | 0 | 0 |
| NA | 611 | 247 | 27 | 287 | 12 | 2,002 | 203 | 130 | 579 | 0 | 0 | 0 | 0 |
| (missing) | 479 | 122 | 35 | 151 | 16 | 1,450 | 144 | 73 | 631 | 6 | 1 | 10 | 7 |

NA means phase not applicable; (missing) is mostly observational studies.

## Sites (top 25 by matching trials; all 60,591 in `sites.csv`)

A site is one facility name + city + state + country as registered; spellings are not merged.

| site | city | state | country | trials | recruiting_trials | recruiting_site_confirmed | not_yet_recruiting | recruiting_lead_sponsors |
|---|---|---|---|---|---|---|---|---|
| Memorial Sloan Kettering Cancer Center | New York | New York | United States | 293 | 34 | 27 | 0 | 17 |
| Dana-Farber Cancer Institute | Boston | Massachusetts | United States | 284 | 44 | 35 | 3 | 31 |
| Massachusetts General Hospital | Boston | Massachusetts | United States | 228 | 40 | 32 | 1 | 30 |
| Washington University School of Medicine | St Louis | Missouri | United States | 184 | 34 | 29 | 2 | 17 |
| Dana Farber Cancer Institute | Boston | Massachusetts | United States | 160 | 35 | 33 | 1 | 26 |
| Beth Israel Deaconess Medical Center | Boston | Massachusetts | United States | 150 | 16 | 13 | 0 | 15 |
| MD Anderson Cancer Center | Houston | Texas | United States | 147 | 34 | 27 | 0 | 29 |
| Fudan University Shanghai Cancer Center | Shanghai | Shanghai Municipality | China | 146 | 40 | 37 | 12 | 14 |
| Mayo Clinic | Rochester | Minnesota | United States | 146 | 16 | 13 | 0 | 16 |
| M D Anderson Cancer Center | Houston | Texas | United States | 143 | 25 | 24 | 0 | 4 |
| Roswell Park Cancer Institute | Buffalo | New York | United States | 131 | 15 | 13 | 0 | 9 |
| Samsung Medical Center | Seoul |  | South Korea | 128 | 27 | 22 | 1 | 17 |
| Seoul National University Hospital | Seoul |  | South Korea | 123 | 23 | 18 | 0 | 15 |
| Memorial Sloan-Kettering Cancer Center | New York | New York | United States | 119 | 4 | 2 | 0 | 4 |
| Asan Medical Center | Seoul |  | South Korea | 117 | 22 | 15 | 0 | 17 |
| Centre Oscar Lambret | Lille |  | France | 114 | 16 | 15 | 0 | 11 |
| University of Texas MD Anderson Cancer Center | Houston | Texas | United States | 114 | 9 | 7 | 0 | 6 |
| Duke University Medical Center | Durham | North Carolina | United States | 114 | 5 | 4 | 0 | 5 |
| Ohio State University Comprehensive Cancer Center | Columbus | Ohio | United States | 113 | 18 | 17 | 1 | 5 |
| Hospital Universitario 12 de Octubre | Madrid |  | Spain | 112 | 35 | 27 | 0 | 22 |
| Moffitt Cancer Center | Tampa | Florida | United States | 99 | 33 | 30 | 0 | 22 |
| Institut Curie | Paris |  | France | 98 | 16 | 13 | 0 | 10 |
| Institut Gustave Roussy | Villejuif |  | France | 91 | 15 | 10 | 0 | 13 |
| Northwestern University | Chicago | Illinois | United States | 91 | 12 | 11 | 0 | 8 |
| Fox Chase Cancer Center | Philadelphia | Pennsylvania | United States | 91 | 5 | 4 | 0 | 4 |

## Countries (top 25; all 120 in `countries.csv`)

| country | trials | sites | recruiting_trials | sites_with_recruiting_trial |
|---|---|---|---|---|
| United States | 6,034 | 21,458 | 723 | 4,680 |
| China | 1,629 | 2,605 | 436 | 977 |
| France | 1,144 | 3,313 | 151 | 711 |
| Canada | 886 | 1,351 | 111 | 251 |
| Spain | 866 | 2,904 | 115 | 609 |
| Italy | 810 | 3,061 | 142 | 594 |
| United Kingdom | 727 | 2,219 | 78 | 389 |
| Germany | 634 | 4,559 | 91 | 1,001 |
| South Korea | 574 | 895 | 96 | 251 |
| Belgium | 538 | 958 | 63 | 176 |
| Australia | 415 | 1,255 | 77 | 267 |
| Netherlands | 368 | 819 | 53 | 165 |
| Taiwan | 361 | 472 | 44 | 114 |
| Turkey (Türkiye) | 345 | 757 | 36 | 180 |
| Brazil | 319 | 1,119 | 38 | 231 |
| Japan | 277 | 1,137 | 49 | 305 |
| Poland | 264 | 776 | 27 | 152 |
| Israel | 256 | 381 | 30 | 82 |
| Russia | 231 | 1,087 | 10 | 94 |
| Sweden | 223 | 433 | 40 | 105 |
| Switzerland | 219 | 506 | 27 | 105 |
| Denmark | 214 | 338 | 24 | 59 |
| Austria | 208 | 647 | 18 | 95 |
| Egypt | 204 | 204 | 18 | 18 |
| Hungary | 199 | 422 | 14 | 41 |

## Condition expansion

9 descriptors: the query plus everything below it in its own MeSH tree branches (a walk that ignored tree numbers would reach 11). ClinicalTrials.gov's own ancestor terms put 14,321 trials under Breast Neoplasms; 14,321 of them are in this report.

| mesh_id | name | depth | trials_direct_on_descriptor |
|---|---|---|---|
| D001943 | Breast Neoplasms | 0 | 13,445 |
| D064726 | Triple Negative Breast Neoplasms | 1 | 1,191 |
| D018567 | Breast Neoplasms, Male | 1 | 285 |
| D000071960 | Breast Carcinoma In Situ | 1 | 190 |
| D058922 | Inflammatory Breast Neoplasms | 1 | 112 |
| D018270 | Carcinoma, Ductal, Breast | 1 | 86 |
| D018275 | Carcinoma, Lobular | 1 | 67 |
| D061325 | Hereditary Breast and Ovarian Cancer Syndrome | 1 | 60 |
| D000069584 | Unilateral Breast Neoplasms | 1 | 16 |

All 14,321 matching trials are in `trials.csv`; start-year counts by lead sponsor class in `timeline_start_year.csv`.

Trial data originate from ClinicalTrials.gov; MeSH from the U.S. National Library of Medicine. Graph files: CC0.
