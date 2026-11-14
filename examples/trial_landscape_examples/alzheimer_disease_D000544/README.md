# Clinical trial landscape: Alzheimer Disease

MeSH D000544 and 0 narrower descriptors. Source: Lunas Clinical Evidence KG v0.2.1 (snapshot 2026-11-07). Built by `examples/trial_landscape.py`; the same content with charts is in `report.html` (download and open it in a browser).

A trial matches when ClinicalTrials.gov lists the descriptor, or one of its narrower descriptors, among the trial's condition browse terms (`ClinicalTrial -HAS_MESH {study_aspect:'condition', mesh_type:'mesh-list'}-> MeSHConcept`). Status is the registry status at the snapshot date.

| measure | value |
|---|---|
| matching trials | 3,853 |
| direct on the descriptor | 3,853 |
| via narrower descriptors only | 0 |
| recruiting (registry status) | 536 |
| not yet recruiting | 168 |
| interventional | 3,037 |
| lead sponsors | 1,265 |
| trials with sites | 3,333 |
| sites | 18,423 |
| countries | 72 |
| trials with a results article | 244 |
| results trial-article links (rows) | 714 |
| distinct results Articles | 692 |
| distinct results Articles with a PubMed record | 188 |
| distinct results Articles cited by a guideline or SR | 65 |
| ... of which with a PubMed record | 65 |
| results trial-article links cited by a guideline or SR | 68 |

**Records not in this release:** 122 matching trials (the newest registrations) have no sponsor or site records, including 58 recruiting ones. They are counted in trial totals, phase and status, and are missing from sponsor, site and country figures.

## Results articles and citations within the graph

A results article is an Article linked to the trial with the RESULT role (`VALIDATED_BY`, Article -> ClinicalTrial). Identity-only Articles (`lunasai_layer` = `ctgov_identity_only`) carry a PMID but no bibliographic data.

**Cited by a guideline or SR** means at least one Article in the graph whose NLM publication types include Guideline, Practice Guideline or Systematic Review cites the results article (CITES edge; an Article citing itself is not counted; Meta-Analysis alone does not qualify). Only citations between Articles in the graph are counted, so cited counts are lower bounds; an article not cited within the graph may be cited elsewhere.

Top 25 of 714 trial-article links (all in `results_publications.csv`):

| nct_id | pmid | article_title | year | identity_only | cited_in_graph | cited_by_guidelines | cited_by_systematic_reviews |
|---|---|---|---|---|---|---|---|
| NCT06424652 | 11556941 | The PHQ-9: validity of a brief depression severity measure. | 2,001 | False | 3790.0 | 11 | 75 |
| NCT06669182 | 34998485 | Estimation of the global prevalence of dementia in 2019 and forecasted prevalence in 2050: an analysis for the Global Burden of Disease Study 2019. | 2,022 | False | 415.0 | 1 | 23 |
| NCT02685787 | 7991117 | The Neuropsychiatric Inventory: comprehensive assessment of psychopathology in dementia. | 1,994 | False | 525.0 | 3 | 13 |
| NCT05119114 | 16360788 | Global prevalence of dementia: a Delphi consensus study. | 2,005 | False | 313.0 | 0 | 14 |
| NCT00246896 | 16684985 | Effectiveness of collaborative care for older adults with Alzheimer disease in primary care: a randomized controlled trial. | 2,006 | False | 67.0 | 0 | 12 |
| NCT02685787 | 10605972 | Caregiving as a risk factor for mortality: the Caregiver Health Effects Study. | 1,999 | False | 246.0 | 1 | 10 |
| NCT02685787 | 24618967 | Caregiver burden: a clinical review. | 2,014 | False | 136.0 | 1 | 11 |
| NCT02303158 | 24849862 | Advancing research diagnostic criteria for Alzheimer's disease: the IWG-2 criteria. | 2,014 | False | 278.0 | 4 | 5 |
| NCT01430286 | 25967983 | A web-based psychoeducational program for informal caregivers of patients with Alzheimer's disease: a pilot randomized controlled trial. | 2,015 | False | 22.0 | 0 | 9 |
| NCT02303158 | 23637108 | Late-life depression and risk of vascular dementia and Alzheimer's disease: systematic review and meta-analysis of community-based cohort studies. | 2,013 | False | 73.0 | 0 | 8 |
| NCT06669182 | 33667416 | Alzheimer's disease. | 2,021 | False | 313.0 | 0 | 7 |
| NCT00857415 | 21245183 | Use of florbetapir-PET for imaging beta-amyloid pathology. | 2,011 | False | 163.0 | 4 | 2 |
| NCT00000177 | 10697060 | Estrogen replacement therapy for treatment of mild to moderate Alzheimer disease: a randomized controlled trial. Alzheimer's Disease Cooperative Study. | 2,000 | False | 61.0 | 1 | 5 |
| NCT00177489 | 17116917 | Enhancing the quality of life of dementia caregivers from different ethnic or racial groups: a randomized, controlled trial. | 2,006 | False | 34.0 | 0 | 6 |
| NCT03548883 | 22784036 | Clinical and biomarker changes in dominantly inherited Alzheimer's disease. | 2,012 | False | 450.0 | 0 | 5 |
| NCT06669182 | 12084879 | Phases of A beta-deposition in the human brain and its relevance for the development of AD. | 2,002 | False | 353.0 | 0 | 5 |
| NCT06631742 | 9153155 | The Neuropsychiatric Inventory: assessing psychopathology in dementia patients. | 1,997 | False | 134.0 | 2 | 3 |
| NCT00253201 | 10881250 | Galantamine in AD: A 6-month randomized, placebo-controlled trial with a 6-month extension. The Galantamine USA-1 Study Group. | 2,000 | False | 52.0 | 1 | 4 |
| NCT00253188 | 11110737 | Efficacy and safety of galantamine in patients with mild to moderate Alzheimer's disease: multicentre randomised controlled trial. Galantamine International-1 Study Group. | 2,000 | False | 32.0 | 0 | 5 |
| NCT00253227 | 11606667 | Effects of a flexible galantamine dose in Alzheimer's disease: a randomised, controlled trial. | 2,001 | False | 18.0 | 0 | 5 |
| NCT06852352 | 22896675 | A paravascular pathway facilitates CSF flow through the brain parenchyma and the clearance of interstitial solutes, including amyloid β. | 2,012 | False | 556.0 | 0 | 4 |
| NCT03136679 | 15817019 | The Montreal Cognitive Assessment, MoCA: a brief screening tool for mild cognitive impairment. | 2,005 | False | 146.0 | 1 | 3 |
| NCT06424652 | 15817019 | The Montreal Cognitive Assessment, MoCA: a brief screening tool for mild cognitive impairment. | 2,005 | False | 146.0 | 1 | 3 |
| NCT06852352 | 33004510 | Glymphatic failure as a final common pathway to dementia. | 2,020 | False | 120.0 | 0 | 4 |
| NCT00249145 | 10496251 | A randomized trial of risperidone, placebo, and haloperidol for behavioral symptoms of dementia. | 1,999 | False | 29.0 | 1 | 3 |

## Lead sponsor class

| sponsor_class | trials | recruiting |
|---|---|---|
| Academic / hospital / other | 2,313 | 389 |
| Industry | 1,221 | 71 |
| Government | 185 | 14 |
| No sponsor record in release | 122 | 58 |
| Network / individual / unknown | 12 | 4 |

ClinicalTrials.gov has no academic class: universities and hospitals are filed as OTHER.

## Lead sponsors (top 25 by trials led; all in `by_sponsor.csv`)

| sponsor | agency_class | sponsor_class | trials_as_lead | trials_as_collaborator | recruiting_as_lead |
|---|---|---|---|---|---|
| pfizer | INDUSTRY | Industry | 62 | 21 | 0 |
| eli lilly and company | INDUSTRY | Industry | 49 | 14 | 4 |
| avid radiopharmaceuticals | INDUSTRY | Industry | 42 | 6 | 0 |
| national institute on aging (nia) | NIH | Government | 41 | 410 | 1 |
| wyeth is now a wholly owned subsidiary of pfizer | INDUSTRY | Industry | 32 | 2 | 0 |
| glaxosmithkline | INDUSTRY | Industry | 31 | 4 | 2 |
| merck sharp & dohme llc | INDUSTRY | Industry | 31 | 3 | 1 |
| indiana university | OTHER | Academic / hospital / other | 31 | 2 | 6 |
| johns hopkins university | OTHER | Academic / hospital / other | 28 | 17 | 7 |
| massachusetts general hospital | OTHER | Academic / hospital / other | 28 | 8 | 6 |
| assistance publique - hôpitaux de paris | OTHER | Academic / hospital / other | 28 | 5 | 8 |
| chang gung memorial hospital | OTHER | Academic / hospital / other | 26 | 2 | 2 |
| washington university school of medicine | OTHER | Academic / hospital / other | 26 | 2 | 9 |
| centre hospitalier universitaire de nice | OTHER | Academic / hospital / other | 26 | 1 | 4 |
| hoffmann-la roche | INDUSTRY | Industry | 25 | 8 | 1 |
| university of washington | OTHER | Academic / hospital / other | 24 | 9 | 1 |
| emory university | OTHER | Academic / hospital / other | 24 | 6 | 2 |
| nyu langone health | OTHER | Academic / hospital / other | 22 | 1 | 2 |
| university of wisconsin, madison | OTHER | Academic / hospital / other | 22 | 1 | 2 |
| xuanwu hospital, beijing | OTHER | Academic / hospital / other | 21 | 4 | 7 |
| astrazeneca | INDUSTRY | Industry | 21 | 1 | 0 |
| mayo clinic | OTHER | Academic / hospital / other | 20 | 11 | 4 |
| university of pennsylvania | OTHER | Academic / hospital / other | 20 | 6 | 5 |
| bristol-myers squibb | INDUSTRY | Industry | 20 | 2 | 6 |
| novartis pharmaceuticals | INDUSTRY | Industry | 20 | 1 | 1 |

## Phase by overall status

| phase | RECRUITING | NOT_YET_RECRUITING | ENROLLING_BY_INVITATION | ACTIVE_NOT_RECRUITING | SUSPENDED | COMPLETED | TERMINATED | WITHDRAWN | UNKNOWN | AVAILABLE | NO_LONGER_AVAILABLE |
|---|---|---|---|---|---|---|---|---|---|---|---|
| EARLY_PHASE1 | 9 | 2 | 1 | 4 | 0 | 36 | 8 | 1 | 2 | 0 | 0 |
| PHASE1 | 27 | 17 | 0 | 12 | 1 | 339 | 44 | 7 | 17 | 0 | 0 |
| PHASE1/PHASE2 | 16 | 3 | 0 | 5 | 0 | 46 | 5 | 3 | 15 | 0 | 0 |
| PHASE2 | 53 | 18 | 7 | 23 | 0 | 333 | 68 | 16 | 40 | 0 | 0 |
| PHASE2/PHASE3 | 6 | 2 | 0 | 3 | 0 | 32 | 10 | 1 | 6 | 0 | 0 |
| PHASE3 | 30 | 7 | 0 | 14 | 1 | 161 | 55 | 5 | 13 | 0 | 0 |
| PHASE4 | 10 | 4 | 2 | 4 | 0 | 86 | 8 | 5 | 17 | 0 | 0 |
| NA | 206 | 83 | 21 | 53 | 3 | 714 | 62 | 39 | 196 | 0 | 0 |
| (missing) | 179 | 32 | 31 | 31 | 1 | 345 | 31 | 18 | 142 | 2 | 4 |

NA means phase not applicable; (missing) is mostly observational studies.

## Sites (top 25 by matching trials; all 18,423 in `sites.csv`)

A site is one facility name + city + state + country as registered; spellings are not merged.

| site | city | state | country | trials | recruiting_trials | recruiting_site_confirmed | not_yet_recruiting | recruiting_lead_sponsors |
|---|---|---|---|---|---|---|---|---|
| Brain Matters Research | Delray Beach | Florida | United States | 76 | 2 | 2 | 0 | 2 |
| Banner Alzheimer's Institute | Phoenix | Arizona | United States | 74 | 3 | 3 | 0 | 3 |
| Banner Sun Health Research Institute | Sun City | Arizona | United States | 49 | 2 | 2 | 0 | 2 |
| Renstar Medical Research | Ocala | Florida | United States | 48 | 3 | 3 | 0 | 3 |
| Butler Hospital | Providence | Rhode Island | United States | 47 | 4 | 4 | 0 | 2 |
| Yale University School of Medicine | New Haven | Connecticut | United States | 46 | 2 | 2 | 0 | 1 |
| Progressive Medical Research | Port Orange | Florida | United States | 44 | 3 | 3 | 0 | 2 |
| Sunnybrook Health Sciences Centre | Toronto | Ontario | Canada | 42 | 10 | 8 | 0 | 5 |
| University of Pittsburgh | Pittsburgh | Pennsylvania | United States | 42 | 6 | 6 | 0 | 4 |
| Emory University | Atlanta | Georgia | United States | 42 | 3 | 3 | 0 | 2 |
| University of Pennsylvania | Philadelphia | Pennsylvania | United States | 42 | 3 | 3 | 0 | 1 |
| Syrentis Clinical Research | Santa Ana | California | United States | 42 | 1 | 1 | 0 | 1 |
| Toronto Memory Program | Toronto | Ontario | Canada | 41 | 3 | 3 | 0 | 3 |
| Neuropsychiatric Research Center of SouthWest Florida | Fort Myers | Florida | United States | 40 | 2 | 2 | 0 | 2 |
| Washington University School of Medicine | St Louis | Missouri | United States | 39 | 8 | 8 | 0 | 3 |
| MD Clinical | Hallandale | Florida | United States | 39 | 0 | 0 | 0 | 0 |
| Premiere Research Institute | West Palm Beach | Florida | United States | 39 | 0 | 0 | 0 | 0 |
| JEM Research Institute | Atlantis | Florida | United States | 38 | 4 | 4 | 0 | 4 |
| Massachusetts General Hospital | Boston | Massachusetts | United States | 37 | 8 | 8 | 1 | 4 |
| Johns Hopkins University | Baltimore | Maryland | United States | 37 | 1 | 1 | 0 | 1 |
| The Memory Clinic | Bennington | Vermont | United States | 37 | 1 | 1 | 0 | 1 |
| Institute for Neurodegenerative Disorders | New Haven | Connecticut | United States | 36 | 0 | 0 | 0 | 0 |
| University of Kentucky | Lexington | Kentucky | United States | 36 | 0 | 0 | 0 | 0 |
| Indiana University | Indianapolis | Indiana | United States | 35 | 2 | 2 | 0 | 2 |
| Boston Center for Memory | Newton | Massachusetts | United States | 34 | 4 | 4 | 0 | 2 |

## Countries (top 25; all 73 in `countries.csv`)

| country | trials | sites | recruiting_trials | sites_with_recruiting_trial |
|---|---|---|---|---|
| United States | 1,794 | 7,695 | 208 | 791 |
| France | 397 | 1,136 | 54 | 113 |
| Canada | 281 | 764 | 40 | 91 |
| Spain | 244 | 723 | 25 | 89 |
| United Kingdom | 222 | 758 | 26 | 70 |
| China | 206 | 649 | 66 | 238 |
| Germany | 181 | 675 | 19 | 67 |
| Italy | 176 | 574 | 30 | 78 |
| South Korea | 153 | 345 | 18 | 70 |
| Australia | 147 | 469 | 14 | 39 |
| Netherlands | 113 | 146 | 11 | 16 |
| Sweden | 110 | 194 | 9 | 13 |
| Japan | 105 | 848 | 15 | 100 |
| Poland | 96 | 400 | 10 | 55 |
| Taiwan | 94 | 127 | 13 | 25 |
| Belgium | 81 | 152 | 9 | 15 |
| Finland | 56 | 69 | 3 | 7 |
| Argentina | 55 | 216 | 14 | 51 |
| Brazil | 55 | 126 | 9 | 42 |
| Czechia | 55 | 222 | 7 | 28 |
| Switzerland | 54 | 70 | 8 | 9 |
| Turkey (Türkiye) | 53 | 104 | 5 | 17 |
| Denmark | 52 | 68 | 4 | 6 |
| Israel | 48 | 78 | 6 | 17 |
| Austria | 45 | 84 | 2 | 5 |

## Condition expansion

1 descriptors: the query plus everything below it in its own MeSH tree branches (a walk that ignored tree numbers would reach 1). ClinicalTrials.gov's own ancestor terms put 3,853 trials under Alzheimer Disease; 3,853 of them are in this report.

| mesh_id | name | depth | trials_direct_on_descriptor |
|---|---|---|---|
| D000544 | Alzheimer Disease | 0 | 3,853 |

All 3,853 matching trials are in `trials.csv`; start-year counts by lead sponsor class in `timeline_start_year.csv`.

Trial data originate from ClinicalTrials.gov; MeSH from the U.S. National Library of Medicine. Graph files: CC0.
