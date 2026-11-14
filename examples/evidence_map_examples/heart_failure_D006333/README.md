# Evidence map: Heart Failure

MeSH D006333, 6 descriptors. Source: Lunas Clinical Evidence KG v0.2.1 (snapshot 2026-11-07). Built by `examples/evidence_map.py`; `report.html` has the same content with a chart.

| measure | value |
|---|---|
| Articles | 13,500 |
| Guideline | 25 |
| Systematic review or meta-analysis | 410 |
| Randomized controlled trial | 1,653 |
| Other clinical trial | 329 |
| Observational study | 413 |
| Other | 10,670 |
| Primary studies (RCT + other clinical trial) | 1,982 |
| Primary studies cited by an in-graph guideline or review | 954 |
| Primary studies not cited within the graph | 1,028 |
| Randomized controlled trials cited | 863 |
| Other clinical trials cited | 91 |
| Distinct citing guidelines and reviews | 1,134 |
| ... of which in this map | 290 |
| Systematic reviews or meta-analyses, 2022-2026 | 162 |
| Guidelines, 2022-2026 | 15 |

## Definitions

- **Articles.** Articles indexed (HAS_MESH) to the descriptor or a narrower descriptor in the expansion with is_major_topic = true. The 40 MeSH check tags (Humans, Female, Aged, ...) are never used.
- **Expansion.** The descriptor plus every narrower descriptor reached by HAS_BROADER_ANCESTOR, which follows MeSH tree numbers (PubMed-style explode).
- **Design class.** One class per Article, the first that matches in this order, from NLM publication types: Guideline (Guideline, Practice Guideline); Systematic review or meta-analysis (Systematic Review, Meta-Analysis, Network Meta-Analysis); Randomized controlled trial (Randomized Controlled Trial, incl. Veterinary); Other clinical trial (Clinical Trial, Clinical Trial Phase I-IV, Controlled Clinical Trial, Pragmatic Clinical Trial, Equivalence Trial, Adaptive Clinical Trial, Clinical Trial Veterinary); Observational study (Observational Study, incl. Veterinary); Other (everything else, including Clinical Trial Protocol and no types).
- **Primary studies.** Articles in the Randomized controlled trial or Other clinical trial class.
- **Cited / not cited.** A primary study is cited when at least one Article anywhere in the graph whose publication types include Guideline, Practice Guideline, Systematic Review, Meta-Analysis or Network Meta-Analysis cites it (CITES edge). An Article citing itself is not counted. Only citations between Articles in the graph are counted, so cited counts are lower bounds: a study not cited within the graph may be cited elsewhere.
- **2022-2026.** The Article's publication year (integer `year`) from 2022 to 2026 inclusive.
- **Population.** All Articles, including identity-only Articles (in this release they have no publication types, MeSH or CITES edges, so they do not enter MeSH-based maps).

## Descriptors in the expansion

| mesh_id | name | depth |
|---|---|---|
| D006333 | Heart Failure | 0 |
| D059347 | Cardio-Renal Syndrome | 1 |
| D004418 | Dyspnea, Paroxysmal | 1 |
| D004489 | Edema, Cardiac | 1 |
| D054144 | Heart Failure, Diastolic | 1 |
| D054143 | Heart Failure, Systolic | 1 |

## Guidelines, 2022-2026 (15)

| pmid | title | year |
|---|---|---|
| [41171219](https://pubmed.ncbi.nlm.nih.gov/41171219/) | Transthyretin Cardiac Amyloidosis Evaluation and Management: 2025 ACC Concise Clinical Guidance. | 2,026 |
| [41791738](https://pubmed.ncbi.nlm.nih.gov/41791738/) | Kidney disease and heart failure: recent advances and current challenges: conclusions from a Kidney Disease: Improving Global Outcomes (KDIGO) Controversies Conference. | 2,026 |
| [42263157](https://pubmed.ncbi.nlm.nih.gov/42263157/) | 2026 AHA/ACC/ADA/ASN Guideline for the Prevention, Detection, Evaluation, and Management of Cardiovascular-Kidney-Metabolic Syndrome: A Report of the American College of Cardiology/American Heart Association Joint Committee on Clinical Practice Guidelines. | 2,026 |
| [42265997](https://pubmed.ncbi.nlm.nih.gov/42265997/) | 2026 AHA/ACC/ADA/ASN Guideline for the Prevention, Detection, Evaluation, and Management of Cardiovascular-Kidney-Metabolic Syndrome: A Report of the American College of Cardiology/American Heart Association Joint Committee on Clinical Practice Guidelines. | 2,026 |
| [42684397](https://pubmed.ncbi.nlm.nih.gov/42684397/) | ASN Kidney Health Guidance on the Cardiovascular-Kidney-Metabolic Syndrome. | 2,026 |
| [40409892](https://pubmed.ncbi.nlm.nih.gov/40409892/) | ACR Appropriateness Criteria® Suspected and Known Heart Failure: 2024 Update. | 2,025 |
| [40512113](https://pubmed.ncbi.nlm.nih.gov/40512113/) | 2025 ACC Scientific Statement on the Management of Obesity in Adults With Heart Failure: A Report of the American College of Cardiology. | 2,025 |
| [38453571](https://pubmed.ncbi.nlm.nih.gov/38453571/) | Acute heart failure - an EFIM guideline critical appraisal and adaptation for internists. | 2,024 |
| [38526578](https://pubmed.ncbi.nlm.nih.gov/38526578/) | British societies guideline on the management of emergencies in implantable left ventricular assist device recipients in transplant centres. | 2,024 |
| [39127953](https://pubmed.ncbi.nlm.nih.gov/39127953/) | 2024 Update to the 2020 ACC/AHA Clinical Performance and Quality Measures for Adults With Heart Failure: A Report of the American Heart Association/American College of Cardiology Joint Committee on Performance Measures. | 2,024 |
| [39253806](https://pubmed.ncbi.nlm.nih.gov/39253806/) | Evaluation and Management of Kidney Dysfunction in Advanced Heart Failure: A Scientific Statement From the American Heart Association. | 2,024 |
| [36958952](https://pubmed.ncbi.nlm.nih.gov/36958952/) | Supervised Exercise Training for Chronic Heart Failure With Preserved Ejection Fraction: A Scientific Statement From the American Heart Association and American College of Cardiology. | 2,023 |
| [35363499](https://pubmed.ncbi.nlm.nih.gov/35363499/) | 2022 AHA/ACC/HFSA Guideline for the Management of Heart Failure: A Report of the American College of Cardiology/American Heart Association Joint Committee on Clinical Practice Guidelines. | 2,022 |
| [35379503](https://pubmed.ncbi.nlm.nih.gov/35379503/) | 2022 AHA/ACC/HFSA Guideline for the Management of Heart Failure: A Report of the American College of Cardiology/American Heart Association Joint Committee on Clinical Practice Guidelines. | 2,022 |
| [35379504](https://pubmed.ncbi.nlm.nih.gov/35379504/) | 2022 AHA/ACC/HFSA Guideline for the Management of Heart Failure: Executive Summary: A Report of the American College of Cardiology/American Heart Association Joint Committee on Clinical Practice Guidelines. | 2,022 |

## Systematic reviews and meta-analyses, 2022-2026 (162)

| pmid | title | year |
|---|---|---|
| [41287923](https://pubmed.ncbi.nlm.nih.gov/41287923/) | GLP-1 Receptor Agonists for the Prevention of New-Onset Heart Failure: A Systematic Review and Meta-Analysis of Placebo-Controlled Randomized Clinical Trials. | 2,026 |
| [41314931](https://pubmed.ncbi.nlm.nih.gov/41314931/) | Robustness of randomized controlled trial evidence for SGLT2 inhibitors in heart failure with preserved and mildly reduced ejection fraction. | 2,026 |
| [41565332](https://pubmed.ncbi.nlm.nih.gov/41565332/) | Risk prediction models for detecting a new diagnosis of heart failure within 5 years in the community: a systematic review. | 2,026 |
| [41825469](https://pubmed.ncbi.nlm.nih.gov/41825469/) | Guidelines and tools to assess appropriateness of diuretic prescribing and aid deprescribing: a systematic review. | 2,026 |
| [41875203](https://pubmed.ncbi.nlm.nih.gov/41875203/) | Effects of Virtual Reality-Based Interventions for Promoting Physical Activity in Patients With Heart Failure: Systematic Review. | 2,026 |
| [42074120](https://pubmed.ncbi.nlm.nih.gov/42074120/) | Cardiorenal Associations in Preclinical Modeling: A Systematic Review and Meta-Analysis. | 2,026 |
| [42106991](https://pubmed.ncbi.nlm.nih.gov/42106991/) | Efficacy and Safety of Digitalis Glycosides in Heart Failure: A Meta-Analysis. | 2,026 |
| [42406570](https://pubmed.ncbi.nlm.nih.gov/42406570/) | Comparative Efficacy of Various Exercise Modes on Inflammatory Markers in Patients with Heart Failure: A Pairwise and Network Meta-Analysis. | 2,026 |
| [42406878](https://pubmed.ncbi.nlm.nih.gov/42406878/) | Patients' Experiences of Nurse-Led eHealth Interventions for Chronic Heart Failure: Qualitative Systematic Review and Meta-Synthesis. | 2,026 |
| [42552200](https://pubmed.ncbi.nlm.nih.gov/42552200/) | Prevalence of orthostatic hypotension in heart failure: a systematic review and meta-analysis. | 2,026 |
| [42594378](https://pubmed.ncbi.nlm.nih.gov/42594378/) | Digital Health Technology for Improving Physical Function in Adults With Chronic Heart Failure: Systematic Review and Meta-Analysis of Randomized Controlled Trials. | 2,026 |
| [42637254](https://pubmed.ncbi.nlm.nih.gov/42637254/) | Patients' experiences of mobile health tools for chronic heart failure self-management: a qualitative meta-synthesis. | 2,026 |
| [42722677](https://pubmed.ncbi.nlm.nih.gov/42722677/) | Multi-ancestry genetic architecture of heart failure subtypes. | 2,026 |
| [38862032](https://pubmed.ncbi.nlm.nih.gov/38862032/) | High-Intensity Interval Training Programs Versus Moderate-Intensity Continuous Training for Individuals With Heart Failure: A Systematic Review and Meta-analysis. | 2,025 |
| [39162139](https://pubmed.ncbi.nlm.nih.gov/39162139/) | Point-of-care ultrasound to assess left ventricular ejection fraction in heart failure in unselected patients in primary care: a systematic review. | 2,025 |
| [39215750](https://pubmed.ncbi.nlm.nih.gov/39215750/) | A systematic review and meta-analysis of Nordic walking for chronic heart failure with low left ventricular ejection fraction. | 2,025 |
| [39487697](https://pubmed.ncbi.nlm.nih.gov/39487697/) | Effects of new hypoglycemic drugs on patients with heart failure: a systematic review and network meta-analysis. | 2,025 |
| [39566897](https://pubmed.ncbi.nlm.nih.gov/39566897/) | GH Therapy in Chronic Heart Failure: A Systematic Review and Meta-analysis of Randomized Controlled Trials. | 2,025 |
| [39745404](https://pubmed.ncbi.nlm.nih.gov/39745404/) | Systolic Blood Pressure and Pulse Pressure in Heart Failure: Pooled Participant-Level Analysis of 4 Trials. | 2,025 |
| [39786850](https://pubmed.ncbi.nlm.nih.gov/39786850/) | Use of mHealth Technology for Improving Exercise Adherence in Patients With Heart Failure: Systematic Review. | 2,025 |
| [39843332](https://pubmed.ncbi.nlm.nih.gov/39843332/) | Safety and efficacy of early initiation of sodium-glucose co-transporter inhibitors 2 in patients hospitalized for acute heart failure: A meta-analysis of randomized controlled trials. | 2,025 |
| [39939263](https://pubmed.ncbi.nlm.nih.gov/39939263/) | Characterization of ischemic etiology in heart failure with reduced ejection fraction randomized clinical trials: A systematic review and meta-analysis. | 2,025 |
| [40025422](https://pubmed.ncbi.nlm.nih.gov/40025422/) | Patient participation in self-monitoring regarding healthcare of heart failure: an integrated systematic review. | 2,025 |
| [40089313](https://pubmed.ncbi.nlm.nih.gov/40089313/) | Association between cardiac cachexia and adverse outcomes in patients with heart failure: a meta-analysis of cohort studies. | 2,025 |
| [40106427](https://pubmed.ncbi.nlm.nih.gov/40106427/) | Predictors of successful weaning from veno-arterial extracorporeal membrane oxygenation (V-A ECMO): A systematic review and meta-analysis. | 2,025 |
| [40138616](https://pubmed.ncbi.nlm.nih.gov/40138616/) | Clinical and Imaging Markers of Cardiac Function and Brain Health: A Meta-Analysis of Community-Based Studies. | 2,025 |
| [40159279](https://pubmed.ncbi.nlm.nih.gov/40159279/) | Systematic review and meta-analysis of intravenous iron therapy for patients with heart failure and iron deficiency. | 2,025 |
| [40187783](https://pubmed.ncbi.nlm.nih.gov/40187783/) | What are the experiences of people with heart failure regarding participation in physical activity? A systematic review, meta-aggregation and development of a logic model. | 2,025 |
| [40444781](https://pubmed.ncbi.nlm.nih.gov/40444781/) | Heart failure: assessment of the global economic burden. | 2,025 |
| [40450575](https://pubmed.ncbi.nlm.nih.gov/40450575/) | Prescribed in-hospital sodium intake for decompensated heart failure: A systematic review and meta-analysis. | 2,025 |
| [40497591](https://pubmed.ncbi.nlm.nih.gov/40497591/) | Evaluation of the risk of heart failure with tumour necrosis factor inhibitors: A large-scale meta-analysis in immune-mediated inflammatory diseases. | 2,025 |
| [40531895](https://pubmed.ncbi.nlm.nih.gov/40531895/) | Prevalence of the depression among heart failure patients in Ethiopia, 2024: A systematic review and meta-analysis. | 2,025 |
| [40541431](https://pubmed.ncbi.nlm.nih.gov/40541431/) | Barriers and facilitators to offering palliative care to patients with heart failure: a mixed-methods systematic review using the COM-B model and theoretical domains framework. | 2,025 |
| [40624658](https://pubmed.ncbi.nlm.nih.gov/40624658/) | Prognostic and predictive microRNA panels for heart failure patients with reduced or preserved ejection fraction: a meta-analysis of Kaplan-Meier-based individual patient data. | 2,025 |
| [40750285](https://pubmed.ncbi.nlm.nih.gov/40750285/) | Comorbidities and incidence of heart failure with preserved ejection fraction: a systematic review and meta-analysis of cohort studies. | 2,025 |
| [40884036](https://pubmed.ncbi.nlm.nih.gov/40884036/) | Dapagliflozin in Patients Hospitalized for Heart Failure: Primary Results of the DAPA ACT HF-TIMI 68 Randomized Clinical Trial and Meta-Analysis of Sodium-Glucose Cotransporter-2 Inhibitors in Patients Hospitalized for Heart Failure. | 2,025 |
| [40892608](https://pubmed.ncbi.nlm.nih.gov/40892608/) | Pharmacologic Treatment of Heart Failure With Reduced Ejection Fraction: An Updated Systematic Review and Network Meta-Analysis. | 2,025 |
| [41052919](https://pubmed.ncbi.nlm.nih.gov/41052919/) | Frequent premature ventricular complexes and risk of atrial fibrillation, heart failure, stroke and mortality: a meta-analysis. | 2,025 |
| [41096770](https://pubmed.ncbi.nlm.nih.gov/41096770/) | Pharmacokinetic Alterations in Patients with Chronic Heart Failure: A Systematic Review. | 2,025 |
| [41184235](https://pubmed.ncbi.nlm.nih.gov/41184235/) | Genome-wide analysis of heart failure yields insights into disease heterogeneity and enables prognostic prediction in the Japanese population. | 2,025 |
| [41303536](https://pubmed.ncbi.nlm.nih.gov/41303536/) | Exploring the Clinical Utility of Osteoprotegerin in Heart Failure-A Systematic Review and Meta-Analysis. | 2,025 |
| [41370315](https://pubmed.ncbi.nlm.nih.gov/41370315/) | GV effects of diabetes mellitus on clinical outcomes of patients with acute heart failure: A systematic review and meta-analysis. | 2,025 |
| [37499852](https://pubmed.ncbi.nlm.nih.gov/37499852/) | Non-Pharmacological Interventions in Patients With Heart Failure With Reduced Ejection Fraction: A Systematic Review and Network Meta-analysis. | 2,024 |
| [37648583](https://pubmed.ncbi.nlm.nih.gov/37648583/) | Novel potassium binders to optimize RAASi therapy in heart failure: A systematic review and meta-analysis. | 2,024 |
| [37993005](https://pubmed.ncbi.nlm.nih.gov/37993005/) | Exercise-based cardiac rehabilitation for left ventricular function in patients with heart failure: A systematic review and meta-analysis. | 2,024 |
| [38122973](https://pubmed.ncbi.nlm.nih.gov/38122973/) | A Systematic Review Exploring the Impact of Arteriovenous Fistula Ligature on High-Output Heart Failure in Renal Transplant Recipients. | 2,024 |
| [38163367](https://pubmed.ncbi.nlm.nih.gov/38163367/) | Development and Validation of a Protein Risk Score for Mortality in Heart Failure : A Community Cohort Study. | 2,024 |
| [38195054](https://pubmed.ncbi.nlm.nih.gov/38195054/) | Mineralocorticoid receptor antagonists and atrial fibrillation: a meta-analysis of clinical trials. | 2,024 |
| [38273315](https://pubmed.ncbi.nlm.nih.gov/38273315/) | Proteomics for heart failure risk stratification: a systematic review. | 2,024 |
| [38316960](https://pubmed.ncbi.nlm.nih.gov/38316960/) | Association of weight loss with cardiovascular or all-cause mortality in patients with heart failure: A meta-analysis. | 2,024 |
| [38325994](https://pubmed.ncbi.nlm.nih.gov/38325994/) | Implantable Hemodynamic Monitors Improve Survival in Patients With Heart Failure and Reduced Ejection Fraction. | 2,024 |
| [38381449](https://pubmed.ncbi.nlm.nih.gov/38381449/) | Interventions for Optimization of Guideline-Directed Medical Therapy: A Systematic Review. | 2,024 |
| [38382766](https://pubmed.ncbi.nlm.nih.gov/38382766/) | Association between estrogen replacement therapy and heart failure in postmenopausal women: A systematic review and meta-analysis. | 2,024 |
| [38451843](https://pubmed.ncbi.nlm.nih.gov/38451843/) | Exercise-based cardiac rehabilitation for adults with heart failure. | 2,024 |
| [38573633](https://pubmed.ncbi.nlm.nih.gov/38573633/) | SGLT2 Inhibitors, Functional Capacity, and Quality of Life in Patients With Heart Failure: A Systematic Review and Meta-Analysis. | 2,024 |
| [38613991](https://pubmed.ncbi.nlm.nih.gov/38613991/) | Comparative effectiveness of ehealth self-management interventions for patients with heart failure: A Bayesian network meta-analysis. | 2,024 |
| [38656292](https://pubmed.ncbi.nlm.nih.gov/38656292/) | Atrial Fibrillation Ablation in Heart Failure With Reduced vs Preserved Ejection Fraction: A Systematic Review and Meta-Analysis. | 2,024 |
| [38687991](https://pubmed.ncbi.nlm.nih.gov/38687991/) | Economic Evaluations of Digital Health Interventions for Patients With Heart Failure: Systematic Review. | 2,024 |
| [38692445](https://pubmed.ncbi.nlm.nih.gov/38692445/) | Mineralocorticoid receptor antagonists in heart failure with reduced ejection fraction: a systematic review and network meta-analysis of 32 randomized trials. | 2,024 |
| [38768620](https://pubmed.ncbi.nlm.nih.gov/38768620/) | Effect of SGLT2 inhibitors on heart failure outcomes and cardiovascular death across the cardiometabolic disease spectrum: a systematic review and meta-analysis. | 2,024 |
| [38792942](https://pubmed.ncbi.nlm.nih.gov/38792942/) | The Role of Oxidative Stress and Inflammatory Parameters in Heart Failure. | 2,024 |
| [38804781](https://pubmed.ncbi.nlm.nih.gov/38804781/) | Vasodilators for Acute Heart Failure - A Systematic Review with Meta-Analysis. | 2,024 |
| [38805436](https://pubmed.ncbi.nlm.nih.gov/38805436/) | Blood urea nitrogen/creatinine ratio in heart failure: Systematic review and meta-analysis. | 2,024 |
| [38809561](https://pubmed.ncbi.nlm.nih.gov/38809561/) | Revisiting Race and the Benefit of RAS Blockade in Heart Failure: A Meta-Analysis of Randomized Clinical Trials. | 2,024 |
| [38891881](https://pubmed.ncbi.nlm.nih.gov/38891881/) | Metabolomics and Cardiovascular Risk in Patients with Heart Failure: A Systematic Review and Meta-Analysis. | 2,024 |
| [38928341](https://pubmed.ncbi.nlm.nih.gov/38928341/) | The Use of Hematopoietic Stem Cells for Heart Failure: A Systematic Review. | 2,024 |
| [39125696](https://pubmed.ncbi.nlm.nih.gov/39125696/) | Viral Myocarditis as a Factor Leading to the Development of Heart Failure Symptoms, Including the Role of Parvovirus B19 Infection-Systematic Review. | 2,024 |
| [39174318](https://pubmed.ncbi.nlm.nih.gov/39174318/) | Long-term risk of heart failure in adult cancer survivors: a systematic review and meta-analysis. | 2,024 |
| [39232490](https://pubmed.ncbi.nlm.nih.gov/39232490/) | Mineralocorticoid receptor antagonists in heart failure: an individual patient level meta-analysis. | 2,024 |
| [39462344](https://pubmed.ncbi.nlm.nih.gov/39462344/) | Effects of education based on teach-back methods on self‑care and quality of life of the patients with heart failure: a systematic review. | 2,024 |
| [39602122](https://pubmed.ncbi.nlm.nih.gov/39602122/) | Heart Failure and All-Cause Hospitalizations in Patients With Heart Failure: A Meta-Analysis. | 2,024 |
| [39700173](https://pubmed.ncbi.nlm.nih.gov/39700173/) | Impact of shock index (SI), modified SI, and age-derivative indices on acute heart failure prognosis; A systematic review and meta-analysis. | 2,024 |
| [36261102](https://pubmed.ncbi.nlm.nih.gov/36261102/) | Prolactin Inhibition in Peripartum Cardiomyopathy: Systematic Review and Meta-analysis. | 2,023 |
| [36303404](https://pubmed.ncbi.nlm.nih.gov/36303404/) | Growth differentiation factor 15 and cardiovascular risk: individual patient meta-analysis. | 2,023 |
| [36326565](https://pubmed.ncbi.nlm.nih.gov/36326565/) | Management of atrial flutter and atrial fibrillation with rapid ventricular response in patients with acute decompensated heart failure: A systematic review. | 2,023 |
| [36411152](https://pubmed.ncbi.nlm.nih.gov/36411152/) | Effectiveness of discharge education using teach-back method on readmission among heart failure patients: A systematic review and meta-analysis. | 2,023 |
| [36456204](https://pubmed.ncbi.nlm.nih.gov/36456204/) | Methamphetamine-associated heart failure: a systematic review of observational studies. | 2,023 |
| [36522146](https://pubmed.ncbi.nlm.nih.gov/36522146/) | Efficacy of implantable haemodynamic monitoring in heart failure across ranges of ejection fraction: a systematic review and meta-analysis. | 2,023 |
| [36537288](https://pubmed.ncbi.nlm.nih.gov/36537288/) | Prospective Association of Daily Steps With Cardiovascular Disease: A Harmonized Meta-Analysis. | 2,023 |
| [36781285](https://pubmed.ncbi.nlm.nih.gov/36781285/) | Prevalence, outcomes and costs of a contemporary, multinational population with heart failure. | 2,023 |
| [36811901](https://pubmed.ncbi.nlm.nih.gov/36811901/) | Association of Dapagliflozin Use With Clinical Outcomes and the Introduction of Uric Acid-Lowering Therapy and Colchicine in Patients With Heart Failure With and Without Gout: A Patient-Level Pooled Meta-analysis of DAPA-HF and DELIVER. | 2,023 |
| [36849238](https://pubmed.ncbi.nlm.nih.gov/36849238/) | Habitual physical activity levels of adults with heart failure: systematic review and meta-analysis. | 2,023 |
| [36878671](https://pubmed.ncbi.nlm.nih.gov/36878671/) | Effect of opioids for breathlessness in heart failure: a systematic review and meta-analysis. | 2,023 |
| [36898704](https://pubmed.ncbi.nlm.nih.gov/36898704/) | Prognostic models for heart failure in patients with type 2 diabetes: a systematic review and meta-analysis. | 2,023 |
| [36902318](https://pubmed.ncbi.nlm.nih.gov/36902318/) | Proenkephalin as a Novel Prognostic Marker in Heart Failure Patients: A Systematic Review and Meta-Analysis. | 2,023 |
| [36952483](https://pubmed.ncbi.nlm.nih.gov/36952483/) | Prevalence of depression and its association with health-related quality of life in people with heart failure in low- and middle-income countries: A systematic review and meta-analysis. | 2,023 |
| [36982265](https://pubmed.ncbi.nlm.nih.gov/36982265/) | miRNA Dysregulation in Cardiovascular Diseases: Current Opinion and Future Perspectives. | 2,023 |
| [36982717](https://pubmed.ncbi.nlm.nih.gov/36982717/) | Markers of Iron Metabolism and Outcomes in Patients with Heart Failure: A Systematic Review. | 2,023 |
| [37024129](https://pubmed.ncbi.nlm.nih.gov/37024129/) | Benefits and harms of drug treatment for type 2 diabetes: systematic review and network meta-analysis of randomised controlled trials. | 2,023 |
| [37062643](https://pubmed.ncbi.nlm.nih.gov/37062643/) | The effect of sodium-glucose cotransporter-2 inhibitors on cardiac structure remodeling and function: A meta-analysis of randomized controlled trials. | 2,023 |
| [37146072](https://pubmed.ncbi.nlm.nih.gov/37146072/) | Clinical effect of Danshen decoction in patients with heart failure: A systematic review and meta-analysis of randomized controlled trials. | 2,023 |
| [37191040](https://pubmed.ncbi.nlm.nih.gov/37191040/) | Racial Differences in Quality of Life in Patients With Heart Failure Treated With Sodium-Glucose Cotransporter 2 Inhibitors: A Patient-Level Meta-Analysis of the CHIEF-HF, DEFINE-HF, and PRESERVED-HF Trials. | 2,023 |
| [37210750](https://pubmed.ncbi.nlm.nih.gov/37210750/) | Efficacy of pulmonary artery pressure monitoring in patients with chronic heart failure: a meta-analysis of three randomized controlled trials. | 2,023 |
| [37216272](https://pubmed.ncbi.nlm.nih.gov/37216272/) | Telemonitoring for heart failure: a meta-analysis. | 2,023 |
| [37220172](https://pubmed.ncbi.nlm.nih.gov/37220172/) | Heart failure, peripheral artery disease, and dapagliflozin: a patient-level meta-analysis of DAPA-HF and DELIVER. | 2,023 |
| [37220263](https://pubmed.ncbi.nlm.nih.gov/37220263/) | Cardiovascular and Renal Benefits of Novel Diabetes Drugs by Baseline Cardiovascular Risk: A Systematic Review, Meta-analysis, and Meta-regression. | 2,023 |
| [37328640](https://pubmed.ncbi.nlm.nih.gov/37328640/) | The prognostic value of myocardial salvage index by cardiac magnetic resonance in ST-segment elevation myocardial infarction patients: a systematic review and meta-analysis. | 2,023 |
| [37344038](https://pubmed.ncbi.nlm.nih.gov/37344038/) | Effect of SGLT2 Inhibitors on Cardiovascular Outcomes Across Various Patient Populations. | 2,023 |
| [37358785](https://pubmed.ncbi.nlm.nih.gov/37358785/) | Stroke in patients with heart failure and reduced or preserved ejection fraction. | 2,023 |
| [37429843](https://pubmed.ncbi.nlm.nih.gov/37429843/) | Genome-wide association analysis and Mendelian randomization proteomics identify drug targets for heart failure. | 2,023 |
| [37446137](https://pubmed.ncbi.nlm.nih.gov/37446137/) | Meta-Analysis of Mechano-Sensitive Ion Channels in Human Hearts: Chamber- and Disease-Preferential mRNA Expression. | 2,023 |
| [37467015](https://pubmed.ncbi.nlm.nih.gov/37467015/) | Video-Based Educational Interventions for Patients With Chronic Illnesses: Systematic Review. | 2,023 |
| [37495280](https://pubmed.ncbi.nlm.nih.gov/37495280/) | Global Comparison of Readmission Rates for Patients With Heart Failure. | 2,023 |
| [37511587](https://pubmed.ncbi.nlm.nih.gov/37511587/) | A Systematic Review of the Effect of Vericiguat on Patients with Heart Failure. | 2,023 |
| [37590312](https://pubmed.ncbi.nlm.nih.gov/37590312/) | Effects of high intensity interval training versus moderate intensity continuous training on exercise capacity and quality of life in patients with heart failure: A systematic review and meta-analysis. | 2,023 |
| [37605637](https://pubmed.ncbi.nlm.nih.gov/37605637/) | Mineralocorticoid receptor antagonists with sodium-glucose co-transporter-2 inhibitors in heart failure: a meta-analysis. | 2,023 |
| [37611019](https://pubmed.ncbi.nlm.nih.gov/37611019/) | Adherence to self-care practices and associated factors among heart failure patients in Ethiopia: A systematic review and meta-analysis. | 2,023 |
| [37615988](https://pubmed.ncbi.nlm.nih.gov/37615988/) | Time to Benefit of Sodium-Glucose Cotransporter-2 Inhibitors Among Patients With Heart Failure. | 2,023 |
| [37632415](https://pubmed.ncbi.nlm.nih.gov/37632415/) | Efficacy of ferric carboxymaltose in heart failure with iron deficiency: an individual patient data meta-analysis. | 2,023 |
| [37708836](https://pubmed.ncbi.nlm.nih.gov/37708836/) | Effect and usability of mobile health applications for medication adherence in patients with heart failure: A systematic review. | 2,023 |
| [37762592](https://pubmed.ncbi.nlm.nih.gov/37762592/) | Non-Alcoholic Fatty Liver Disease and Echocardiographic Parameters of Left Ventricular Diastolic Function: A Systematic Review and Meta-Analysis. | 2,023 |
| [37811703](https://pubmed.ncbi.nlm.nih.gov/37811703/) | Combinatorial Effect of Biomaterials and Extracellular Vesicle Therapy for Heart Failure with Reduced Ejection Fraction: A Systematic Review of Preclinical Studies. | 2,023 |
| [37997105](https://pubmed.ncbi.nlm.nih.gov/37997105/) | Impact of the COVID-19 pandemic on delayed care of cardiovascular diseases in Europe: a systematic review. | 2,023 |
| [38019892](https://pubmed.ncbi.nlm.nih.gov/38019892/) | The effect of sodium-glucose cotransporter 2 inhibitors in patients with chronic kidney disease with or without type 2 diabetes mellitus on cardiovascular and renal outcomes: A systematic review and meta-analysis. | 2,023 |
| [38048301](https://pubmed.ncbi.nlm.nih.gov/38048301/) | Effect of pueraria on left ventricular remodelling in HFrEF: A systematic review and meta-analysis. | 2,023 |
| [38070901](https://pubmed.ncbi.nlm.nih.gov/38070901/) | Non-pharmacological interventions in primary care to improve the quality of life of older patients with palliative care needs: a systematic review of randomised controlled trials. | 2,023 |
| [38072478](https://pubmed.ncbi.nlm.nih.gov/38072478/) | Self-care behaviour and associated factors among heart failure patients in Ethiopia: a systematic review and meta-analysis. | 2,023 |
| [33789068](https://pubmed.ncbi.nlm.nih.gov/33789068/) | Combined aerobic and strength training for fitness outcomes in heart failure: meta-analysis and meta-regression. | 2,022 |
| [33789973](https://pubmed.ncbi.nlm.nih.gov/33789973/) | Telomere length is independently associated with all-cause mortality in chronic heart failure. | 2,022 |
| [33972360](https://pubmed.ncbi.nlm.nih.gov/33972360/) | Benefits of sodium glucose cotransporter 2 inhibitors across the spectrum of cardiovascular diseases. | 2,022 |
| [34607811](https://pubmed.ncbi.nlm.nih.gov/34607811/) | Prediction of incident atrial fibrillation in community-based electronic health records: a systematic review with meta-analysis. | 2,022 |
| [34789473](https://pubmed.ncbi.nlm.nih.gov/34789473/) | Ivabradine added to usual care in patients with heart failure: a systematic review with meta-analysis and trial sequential analysis. | 2,022 |
| [34791312](https://pubmed.ncbi.nlm.nih.gov/34791312/) | Beneficial Effect of Sodium-Glucose Co-transporter 2 Inhibitors on Left Ventricular Function. | 2,022 |
| [34966917](https://pubmed.ncbi.nlm.nih.gov/34966917/) | Kidney function assessment and endpoint ascertainment in clinical trials. | 2,022 |
| [35020750](https://pubmed.ncbi.nlm.nih.gov/35020750/) | Effects of SGLT2 inhibitors on cardiovascular outcomes in patients with stage 3/4 CKD: A meta-analysis. | 2,022 |
| [35042750](https://pubmed.ncbi.nlm.nih.gov/35042750/) | Prevalence, incidence and survival of heart failure: a systematic review. | 2,022 |
| [35081164](https://pubmed.ncbi.nlm.nih.gov/35081164/) | Role of sacubitril-valsartan in the prevention of atrial fibrillation occurrence in patients with heart failure: A systematic review and meta-analysis of randomized controlled trials. | 2,022 |
| [35098748](https://pubmed.ncbi.nlm.nih.gov/35098748/) | Burden of hospitalization for heart failure in the United States: a systematic literature review. | 2,022 |
| [35100355](https://pubmed.ncbi.nlm.nih.gov/35100355/) | Primary Prevention of Cardiovascular and Heart Failure Events With SGLT2 Inhibitors, GLP-1 Receptor Agonists, and Their Combination in Type 2 Diabetes. | 2,022 |
| [35166680](https://pubmed.ncbi.nlm.nih.gov/35166680/) | Posthospitalization Follow-Up of Patients With Heart Failure Using eHealth Solutions: Restricted Systematic Review. | 2,022 |
| [35243488](https://pubmed.ncbi.nlm.nih.gov/35243488/) | Bariatric surgery and cardiovascular disease: a systematic review and meta-analysis. | 2,022 |
| [35278525](https://pubmed.ncbi.nlm.nih.gov/35278525/) | Etiologies of In-hospital cardiac arrest: A systematic review and meta-analysis. | 2,022 |
| [35300523](https://pubmed.ncbi.nlm.nih.gov/35300523/) | Therapeutic Targets for Heart Failure Identified Using Proteomics and Mendelian Randomization. | 2,022 |
| [35332595](https://pubmed.ncbi.nlm.nih.gov/35332595/) | Network meta-analysis of medical therapy efficacy in more than 90,000 patients with heart failure and reduced ejection fraction. | 2,022 |
| [35404670](https://pubmed.ncbi.nlm.nih.gov/35404670/) | Sodium-Glucose Cotransporter-2 Inhibitors in Patients With Heart Failure : A Systematic Review and Meta-analysis. | 2,022 |
| [35439243](https://pubmed.ncbi.nlm.nih.gov/35439243/) | Temporal trends in associations between severe mental illness and risk of cardiovascular disease: A systematic review and meta-analysis. | 2,022 |
| [35443059](https://pubmed.ncbi.nlm.nih.gov/35443059/) | Data standards for heart failure: the European Unified Registries for Heart Care Evaluation and Randomized Trials (EuroHeart). | 2,022 |
| [35644712](https://pubmed.ncbi.nlm.nih.gov/35644712/) | Safety and efficacy of ultrafiltration versus diuretics in patients with decompensated heart failure: A systematic review and meta-analysis. | 2,022 |
| [35697365](https://pubmed.ncbi.nlm.nih.gov/35697365/) | Development and validation of a decision support tool for the diagnosis of acute heart failure: systematic review, meta-analysis, and modelling study. | 2,022 |
| [35711614](https://pubmed.ncbi.nlm.nih.gov/35711614/) | Adverse cardiovascular events and mortality in men during testosterone treatment: an individual patient and aggregate data meta-analysis. | 2,022 |
| [35763296](https://pubmed.ncbi.nlm.nih.gov/35763296/) | Comparison of Mortality and Hospital Readmissions Among Patients Receiving Virtual Ward Transitional Care vs Usual Postdischarge Care: A Systematic Review and Meta-analysis. | 2,022 |
| [35763619](https://pubmed.ncbi.nlm.nih.gov/35763619/) | Implications of fetal premature atrial contractions: systematic review. | 2,022 |
| [35778278](https://pubmed.ncbi.nlm.nih.gov/35778278/) | Epidemiology of persistent postoperative opioid use after cardiac surgery: a systematic review and meta-analysis. | 2,022 |
| [35878651](https://pubmed.ncbi.nlm.nih.gov/35878651/) | Blood pressure-lowering treatment for prevention of major cardiovascular diseases in people with and without type 2 diabetes: an individual participant-level data meta-analysis. | 2,022 |
| [35938489](https://pubmed.ncbi.nlm.nih.gov/35938489/) | Heart Failure Caregiver Burden and Outcomes: A Systematic Review. | 2,022 |
| [36006944](https://pubmed.ncbi.nlm.nih.gov/36006944/) | Effects of cardiac rehabilitation on elderly patients with Chronic heart failure: A meta-analysis and systematic review. | 2,022 |
| [36018711](https://pubmed.ncbi.nlm.nih.gov/36018711/) | Telehealth for the Longitudinal Management of Chronic Conditions: Systematic Review. | 2,022 |
| [36028290](https://pubmed.ncbi.nlm.nih.gov/36028290/) | Efficacy of telemedicine for the management of cardiovascular disease: a systematic review and meta-analysis. | 2,022 |
| [36030328](https://pubmed.ncbi.nlm.nih.gov/36030328/) | Dapagliflozin across the range of ejection fraction in patients with heart failure: a patient-level, pooled meta-analysis of DAPA-HF and DELIVER. | 2,022 |
| [36041474](https://pubmed.ncbi.nlm.nih.gov/36041474/) | SGLT-2 inhibitors in patients with heart failure: a comprehensive meta-analysis of five randomised controlled trials. | 2,022 |
| [36125813](https://pubmed.ncbi.nlm.nih.gov/36125813/) | Optimal Pharmacologic Treatment of Heart Failure With Preserved and Mildly Reduced Ejection Fraction: A Meta-analysis. | 2,022 |
| [36155484](https://pubmed.ncbi.nlm.nih.gov/36155484/) | Effectiveness of eHealth Self-management Interventions in Patients With Heart Failure: Systematic Review and Meta-analysis. | 2,022 |
| [36172637](https://pubmed.ncbi.nlm.nih.gov/36172637/) | Factors associated with hospitalisations of patients with chronic heart failure approaching the end of life: A systematic review. | 2,022 |
| [36223967](https://pubmed.ncbi.nlm.nih.gov/36223967/) | Burden of atrial fibrillation among adults with heart failure in sub-Saharan Africa: a systematic review and meta-analysis. | 2,022 |
| [36224587](https://pubmed.ncbi.nlm.nih.gov/36224587/) | Effectiveness of early rhythm control in improving clinical outcomes in patients with atrial fibrillation: a systematic review and meta-analysis. | 2,022 |
| [36241355](https://pubmed.ncbi.nlm.nih.gov/36241355/) | Cardiovascular and renal efficacy and safety of sodium-glucose cotransporter-2 inhibitors in patients without diabetes: a systematic review and meta-analysis of randomised placebo-controlled trials. | 2,022 |
| [36351458](https://pubmed.ncbi.nlm.nih.gov/36351458/) | Impact of diabetes on the effects of sodium glucose co-transporter-2 inhibitors on kidney outcomes: collaborative meta-analysis of large placebo-controlled trials. | 2,022 |
| [36376295](https://pubmed.ncbi.nlm.nih.gov/36376295/) | Genome-wide association and multi-trait analyses characterize the common genetic architecture of heart failure. | 2,022 |
| [36490252](https://pubmed.ncbi.nlm.nih.gov/36490252/) | Abnormalities of hippocampus and frontal lobes in heart failure patients and animal models with cognitive impairment or depression: A systematic review. | 2,022 |
| [36499336](https://pubmed.ncbi.nlm.nih.gov/36499336/) | Crosstalk between microRNA and Oxidative Stress in Heart Failure: A Systematic Review. | 2,022 |
| [36527023](https://pubmed.ncbi.nlm.nih.gov/36527023/) | Effect of sacubitril/valsartan and ACEI/ARB on glycaemia and the development of diabetes: a systematic review and meta-analysis of randomised controlled trials. | 2,022 |
| [36584227](https://pubmed.ncbi.nlm.nih.gov/36584227/) | Impact of type of dialyzable beta-blockers on subsequent risk of mortality in patients receiving dialysis: A systematic review and meta-analysis. | 2,022 |

Primary studies with their number of citing guidelines and reviews are in `primary_studies.csv`; the citing guidelines and reviews in `citing_reviews.csv`. PubMed, MeSH: U.S. National Library of Medicine; citations: OpenAlex. Graph files: CC0.
