# Clinical trial landscape: Heart Failure

MeSH D006333 and 5 narrower descriptors. Source: Lunas Clinical Evidence KG v0.2.1 (snapshot 2026-11-07). Built by `examples/trial_landscape.py`; the same content with charts is in `report.html` (download and open it in a browser).

A trial matches when ClinicalTrials.gov lists the descriptor, or one of its narrower descriptors, among the trial's condition browse terms (`ClinicalTrial -HAS_MESH {study_aspect:'condition', mesh_type:'mesh-list'}-> MeSHConcept`). Status is the registry status at the snapshot date.

| measure | value |
|---|---|
| matching trials | 5,828 |
| direct on the descriptor | 5,560 |
| via narrower descriptors only | 268 |
| recruiting (registry status) | 688 |
| not yet recruiting | 247 |
| interventional | 3,932 |
| lead sponsors | 1,853 |
| trials with sites | 5,071 |
| sites | 29,720 |
| countries | 127 |
| trials with a results article | 467 |
| results trial-article links (rows) | 1,845 |
| distinct results Articles | 1,738 |
| distinct results Articles with a PubMed record | 563 |
| distinct results Articles cited by a guideline or SR | 305 |
| ... of which with a PubMed record | 305 |
| results trial-article links cited by a guideline or SR | 329 |

**Records not in this release:** 173 matching trials (the newest registrations) have no sponsor or site records, including 47 recruiting ones. They are counted in trial totals, phase and status, and are missing from sponsor, site and country figures.

## Results articles and citations within the graph

A results article is an Article linked to the trial with the RESULT role (`VALIDATED_BY`, Article -> ClinicalTrial). Identity-only Articles (`lunasai_layer` = `ctgov_identity_only`) carry a PMID but no bibliographic data.

**Cited by a guideline or SR** means at least one Article in the graph whose NLM publication types include Guideline, Practice Guideline or Systematic Review cites the results article (CITES edge; an Article citing itself is not counted; Meta-Analysis alone does not qualify). Only citations between Articles in the graph are counted, so cited counts are lower bounds; an article not cited within the graph may be cited elsewhere.

Top 25 of 1,845 trial-article links (all in `results_publications.csv`):

| nct_id | pmid | article_title | year | identity_only | cited_in_graph | cited_by_guidelines | cited_by_systematic_reviews |
|---|---|---|---|---|---|---|---|
| NCT04513964 | 31986264 | Clinical features of patients infected with 2019 novel coronavirus in Wuhan, China. | 2,020 | False | 2674.0 | 18 | 98 |
| NCT04513964 | 32031570 | Clinical Characteristics of 138 Hospitalized Patients With 2019 Novel Coronavirus-Infected Pneumonia in Wuhan, China. | 2,020 | False | 1272.0 | 14 | 62 |
| NCT04717986 | 26378978 | Empagliflozin, Cardiovascular Outcomes, and Mortality in Type 2 Diabetes. | 2,015 | False | 1104.0 | 25 | 44 |
| NCT04739215 | 26378978 | Empagliflozin, Cardiovascular Outcomes, and Mortality in Type 2 Diabetes. | 2,015 | False | 1104.0 | 25 | 44 |
| NCT05424315 | 26378978 | Empagliflozin, Cardiovascular Outcomes, and Mortality in Type 2 Diabetes. | 2,015 | False | 1104.0 | 25 | 44 |
| NCT01206062 | 26551272 | A Randomized Trial of Intensive versus Standard Blood-Pressure Control. | 2,015 | False | 870.0 | 35 | 31 |
| NCT04717986 | 28605608 | Canagliflozin and Cardiovascular and Renal Events in Type 2 Diabetes. | 2,017 | False | 784.0 | 25 | 41 |
| NCT05424315 | 28605608 | Canagliflozin and Cardiovascular and Renal Events in Type 2 Diabetes. | 2,017 | False | 784.0 | 25 | 41 |
| NCT05042622 | 28101605 | Surviving Sepsis Campaign: International Guidelines for Management of Sepsis and Septic Shock: 2016. | 2,017 | False | 544.0 | 11 | 44 |
| NCT04717986 | 30990260 | Canagliflozin and Renal Outcomes in Type 2 Diabetes and Nephropathy. | 2,019 | False | 657.0 | 16 | 27 |
| NCT04717986 | 31535829 | Dapagliflozin in Patients with Heart Failure and Reduced Ejection Fraction. | 2,019 | False | 637.0 | 16 | 23 |
| NCT05424315 | 31535829 | Dapagliflozin in Patients with Heart Failure and Reduced Ejection Fraction. | 2,019 | False | 637.0 | 16 | 23 |
| NCT05759000 | 31535829 | Dapagliflozin in Patients with Heart Failure and Reduced Ejection Fraction. | 2,019 | False | 637.0 | 16 | 23 |
| NCT06812546 | 31535829 | Dapagliflozin in Patients with Heart Failure and Reduced Ejection Fraction. | 2,019 | False | 637.0 | 16 | 23 |
| NCT05424315 | 32865377 | Cardiovascular and Renal Outcomes with Empagliflozin in Heart Failure. | 2,020 | False | 471.0 | 15 | 24 |
| NCT05580510 | 32865377 | Cardiovascular and Renal Outcomes with Empagliflozin in Heart Failure. | 2,020 | False | 471.0 | 15 | 24 |
| NCT02635477 | 18029834 | Using pedometers to increase physical activity and improve health: a systematic review. | 2,007 | False | 276.0 | 4 | 32 |
| NCT06812546 | 34449189 | Empagliflozin in Heart Failure with a Preserved Ejection Fraction. | 2,021 | False | 418.0 | 19 | 16 |
| NCT00218933 | 17548726 | Superior cardiovascular effect of aerobic interval training versus moderate continuous training in heart failure patients: a randomized study. | 2,007 | False | 203.0 | 2 | 28 |
| NCT04513964 | 32217556 | Clinical characteristics of 113 deceased patients with coronavirus disease 2019: retrospective study. | 2,020 | False | 272.0 | 1 | 28 |
| NCT02436317 | 22681860 | Radiation exposure from CT scans in childhood and subsequent risk of leukaemia and brain tumours: a retrospective cohort study. | 2,012 | False | 492.0 | 9 | 19 |
| NCT06074887 | 35379503 | 2022 AHA/ACC/HFSA Guideline for the Management of Heart Failure: A Report of the American College of Cardiology/American Heart Association Joint Committee on Clinical Practice Guidelines. | 2,022 | False | 267.0 | 19 | 9 |
| NCT04513964 | 32125362 | Epidemiologic Features and Clinical Course of Patients Infected With SARS-CoV-2 in Singapore. | 2,020 | False | 152.0 | 2 | 26 |
| NCT07567378 | 32154773 | The Image Biomarker Standardization Initiative: Standardized Quantitative Radiomics for High-Throughput Image-based Phenotyping. | 2,020 | False | 344.0 | 2 | 24 |
| NCT04853758 | 25176015 | Angiotensin-neprilysin inhibition versus enalapril in heart failure. | 2,014 | False | 524.0 | 13 | 11 |

## Lead sponsor class

| sponsor_class | trials | recruiting |
|---|---|---|
| Academic / hospital / other | 4,002 | 502 |
| Industry | 1,332 | 112 |
| Government | 287 | 24 |
| No sponsor record in release | 173 | 47 |
| Network / individual / unknown | 34 | 3 |

ClinicalTrials.gov has no academic class: universities and hospitals are filed as OTHER.

## Lead sponsors (top 25 by trials led; all in `by_sponsor.csv`)

| sponsor | agency_class | sponsor_class | trials_as_lead | trials_as_collaborator | recruiting_as_lead |
|---|---|---|---|---|---|
| abbott medical devices | INDUSTRY | Industry | 104 | 19 | 4 |
| medtronic cardiac rhythm and heart failure | INDUSTRY | Industry | 98 | 3 | 2 |
| mayo clinic | OTHER | Academic / hospital / other | 64 | 19 | 8 |
| duke university | OTHER | Academic / hospital / other | 58 | 8 | 2 |
| astrazeneca | INDUSTRY | Industry | 54 | 29 | 4 |
| boston scientific corporation | INDUSTRY | Industry | 52 | 23 | 1 |
| national heart, lung, and blood institute (nhlbi) | NIH | Government | 48 | 173 | 2 |
| novartis pharmaceuticals | INDUSTRY | Industry | 47 | 5 | 3 |
| brigham and women's hospital | OTHER | Academic / hospital / other | 39 | 12 | 4 |
| va office of research and development | FED | Government | 37 | 1 | 2 |
| massachusetts general hospital | OTHER | Academic / hospital / other | 36 | 11 | 4 |
| university of pennsylvania | OTHER | Academic / hospital / other | 34 | 14 | 1 |
| biotronik se & co. kg | INDUSTRY | Industry | 34 | 9 | 3 |
| bayer | INDUSTRY | Industry | 32 | 12 | 4 |
| yale university | OTHER | Academic / hospital / other | 32 | 6 | 9 |
| imperial college london | OTHER | Academic / hospital / other | 28 | 3 | 5 |
| university of aarhus | OTHER | Academic / hospital / other | 27 | 4 | 3 |
| emory university | OTHER | Academic / hospital / other | 26 | 5 | 0 |
| us department of veterans affairs | FED | Government | 25 | 4 | 0 |
| assistance publique - hôpitaux de paris | OTHER | Academic / hospital / other | 25 | 2 | 5 |
| university of sao paulo general hospital | OTHER | Academic / hospital / other | 25 | 1 | 2 |
| university medical center groningen | OTHER | Academic / hospital / other | 24 | 5 | 4 |
| university of texas southwestern medical center | OTHER | Academic / hospital / other | 24 | 2 | 5 |
| university of colorado, denver | OTHER | Academic / hospital / other | 23 | 7 | 1 |
| university of alberta | OTHER | Academic / hospital / other | 23 | 6 | 5 |

## Phase by overall status

| phase | RECRUITING | NOT_YET_RECRUITING | ENROLLING_BY_INVITATION | ACTIVE_NOT_RECRUITING | SUSPENDED | COMPLETED | TERMINATED | WITHDRAWN | UNKNOWN | NO_LONGER_AVAILABLE | APPROVED_FOR_MARKETING |
|---|---|---|---|---|---|---|---|---|---|---|---|
| EARLY_PHASE1 | 4 | 1 | 0 | 1 | 0 | 21 | 2 | 3 | 4 | 0 | 0 |
| PHASE1 | 19 | 3 | 1 | 1 | 2 | 118 | 16 | 12 | 18 | 0 | 0 |
| PHASE1/PHASE2 | 6 | 6 | 0 | 6 | 1 | 54 | 10 | 9 | 21 | 0 | 0 |
| PHASE2 | 33 | 9 | 2 | 7 | 1 | 232 | 54 | 22 | 35 | 0 | 0 |
| PHASE2/PHASE3 | 5 | 1 | 0 | 0 | 2 | 49 | 12 | 2 | 21 | 0 | 0 |
| PHASE3 | 38 | 11 | 2 | 6 | 1 | 194 | 43 | 8 | 38 | 0 | 0 |
| PHASE4 | 31 | 14 | 5 | 9 | 1 | 229 | 53 | 21 | 86 | 0 | 0 |
| NA | 277 | 137 | 29 | 92 | 7 | 1,148 | 162 | 102 | 362 | 0 | 0 |
| (missing) | 275 | 65 | 36 | 73 | 5 | 894 | 78 | 51 | 414 | 3 | 2 |

NA means phase not applicable; (missing) is mostly observational studies.

## Sites (top 25 by matching trials; all 29,720 in `sites.csv`)

A site is one facility name + city + state + country as registered; spellings are not merged.

| site | city | state | country | trials | recruiting_trials | recruiting_site_confirmed | not_yet_recruiting | recruiting_lead_sponsors |
|---|---|---|---|---|---|---|---|---|
| Massachusetts General Hospital | Boston | Massachusetts | United States | 97 | 11 | 11 | 0 | 8 |
| Mayo Clinic | Rochester | Minnesota | United States | 81 | 14 | 10 | 0 | 12 |
| Duke University Medical Center | Durham | North Carolina | United States | 72 | 4 | 3 | 0 | 4 |
| Brigham and Women's Hospital | Boston | Massachusetts | United States | 69 | 9 | 6 | 1 | 5 |
| Cleveland Clinic | Cleveland | Ohio | United States | 65 | 16 | 11 | 1 | 13 |
| Montreal Heart Institute | Montreal | Quebec | Canada | 59 | 7 | 6 | 0 | 7 |
| Medical University of South Carolina | Charleston | South Carolina | United States | 57 | 8 | 4 | 0 | 8 |
| Vanderbilt University Medical Center | Nashville | Tennessee | United States | 53 | 7 | 6 | 0 | 5 |
| Hospital of the University of Pennsylvania | Philadelphia | Pennsylvania | United States | 50 | 2 | 2 | 0 | 2 |
| University of Michigan | Ann Arbor | Michigan | United States | 49 | 8 | 6 | 0 | 7 |
| University of Pennsylvania | Philadelphia | Pennsylvania | United States | 45 | 7 | 7 | 0 | 6 |
| Tufts Medical Center | Boston | Massachusetts | United States | 44 | 9 | 8 | 0 | 6 |
| Northwestern University | Chicago | Illinois | United States | 41 | 5 | 5 | 0 | 4 |
| Henry Ford Hospital | Detroit | Michigan | United States | 40 | 3 | 3 | 0 | 3 |
| Montefiore Medical Center | The Bronx | New York | United States | 38 | 2 | 1 | 1 | 2 |
| University of Utah | Salt Lake City | Utah | United States | 36 | 5 | 4 | 0 | 5 |
| Emory University Hospital | Atlanta | Georgia | United States | 36 | 3 | 3 | 0 | 3 |
| Virginia Commonwealth University | Richmond | Virginia | United States | 35 | 6 | 6 | 0 | 5 |
| Emory University | Atlanta | Georgia | United States | 34 | 2 | 2 | 0 | 2 |
| Washington University School of Medicine | St Louis | Missouri | United States | 34 | 2 | 1 | 0 | 2 |
| University of Minnesota | Minneapolis | Minnesota | United States | 33 | 4 | 3 | 0 | 4 |
| University of Ottawa Heart Institute | Ottawa | Ontario | Canada | 33 | 4 | 3 | 1 | 4 |
| Cleveland Clinic Foundation | Cleveland | Ohio | United States | 33 | 3 | 3 | 0 | 3 |
| University of Pittsburgh Medical Center | Pittsburgh | Pennsylvania | United States | 32 | 4 | 3 | 0 | 4 |
| The Ohio State University | Columbus | Ohio | United States | 32 | 3 | 3 | 0 | 3 |

## Countries (top 25; all 128 in `countries.csv`)

| country | trials | sites | recruiting_trials | sites_with_recruiting_trial |
|---|---|---|---|---|
| United States | 1,952 | 8,333 | 218 | 1,521 |
| Germany | 498 | 2,230 | 67 | 315 |
| United Kingdom | 420 | 1,000 | 57 | 240 |
| Canada | 390 | 1,015 | 53 | 232 |
| Italy | 367 | 1,989 | 58 | 265 |
| France | 354 | 1,711 | 48 | 250 |
| Spain | 274 | 927 | 42 | 214 |
| China | 264 | 850 | 55 | 311 |
| Netherlands | 250 | 620 | 27 | 107 |
| Poland | 221 | 954 | 34 | 185 |
| Denmark | 190 | 335 | 30 | 79 |
| Brazil | 185 | 634 | 26 | 186 |
| Belgium | 158 | 359 | 22 | 52 |
| Australia | 139 | 396 | 16 | 72 |
| Israel | 137 | 264 | 14 | 39 |
| Sweden | 136 | 279 | 26 | 54 |
| Czechia | 133 | 502 | 21 | 114 |
| Austria | 111 | 189 | 19 | 51 |
| Switzerland | 111 | 163 | 9 | 16 |
| Taiwan | 110 | 128 | 17 | 43 |
| South Korea | 101 | 292 | 25 | 105 |
| Turkey (Türkiye) | 101 | 290 | 15 | 75 |
| Hungary | 99 | 373 | 16 | 84 |
| Russia | 99 | 475 | 11 | 12 |
| Japan | 90 | 875 | 10 | 206 |

## Condition expansion

6 descriptors: the query plus everything below it in its own MeSH tree branches (a walk that ignored tree numbers would reach 6). ClinicalTrials.gov's own ancestor terms put 5,828 trials under Heart Failure; 5,828 of them are in this report.

| mesh_id | name | depth | trials_direct_on_descriptor |
|---|---|---|---|
| D006333 | Heart Failure | 0 | 5,560 |
| D054143 | Heart Failure, Systolic | 1 | 222 |
| D054144 | Heart Failure, Diastolic | 1 | 195 |
| D059347 | Cardio-Renal Syndrome | 1 | 82 |
| D004489 | Edema, Cardiac | 1 | 9 |
| D004418 | Dyspnea, Paroxysmal | 1 | 7 |

All 5,828 matching trials are in `trials.csv`; start-year counts by lead sponsor class in `timeline_start_year.csv`.

Trial data originate from ClinicalTrials.gov; MeSH from the U.S. National Library of Medicine. Graph files: CC0.
