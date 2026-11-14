# Evidence map: Alzheimer Disease

MeSH D000544, 1 descriptors. Source: Lunas Clinical Evidence KG v0.2.1 (snapshot 2026-11-07). Built by `examples/evidence_map.py`; `report.html` has the same content with a chart.

| measure | value |
|---|---|
| Articles | 11,925 |
| Guideline | 5 |
| Systematic review or meta-analysis | 240 |
| Randomized controlled trial | 340 |
| Other clinical trial | 176 |
| Observational study | 128 |
| Other | 11,036 |
| Primary studies (RCT + other clinical trial) | 516 |
| Primary studies cited by an in-graph guideline or review | 226 |
| Primary studies not cited within the graph | 290 |
| Randomized controlled trials cited | 182 |
| Other clinical trials cited | 44 |
| Distinct citing guidelines and reviews | 244 |
| ... of which in this map | 77 |
| Systematic reviews or meta-analyses, 2022-2026 | 107 |
| Guidelines, 2022-2026 | 2 |

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
| D000544 | Alzheimer Disease | 0 |

## Guidelines, 2022-2026 (2)

| pmid | title | year |
|---|---|---|
| [39713939](https://pubmed.ncbi.nlm.nih.gov/39713939/) | The Alzheimer's Association clinical practice guideline for the diagnostic evaluation, testing, counseling, and disclosure of suspected Alzheimer's disease and related disorders (DETeCD-ADRD): Validated clinical assessment instruments. | 2,025 |
| [39713957](https://pubmed.ncbi.nlm.nih.gov/39713957/) | The Alzheimer's Association clinical practice guideline for the Diagnostic Evaluation, Testing, Counseling, and Disclosure of Suspected Alzheimer's Disease and Related Disorders (DETeCD-ADRD): Executive summary of recommendations for specialty care. | 2,025 |

## Systematic reviews and meta-analyses, 2022-2026 (107)

| pmid | title | year |
|---|---|---|
| [41324928](https://pubmed.ncbi.nlm.nih.gov/41324928/) | Plasma Phosphorylated Tau 217 and Amyloid Burden in Older Adults Without Cognitive Impairment: A Meta-Analysis. | 2,026 |
| [41454494](https://pubmed.ncbi.nlm.nih.gov/41454494/) | Obesity Paradox in Alzheimer's Disease: A Systematic Review and Meta-Analysis of Anthropometric Measures and Age-Dependent Effects. | 2,026 |
| [41760397](https://pubmed.ncbi.nlm.nih.gov/41760397/) | Cumulative cognitive benefits and brain volume change with anti-amyloid therapies for Alzheimer's disease. | 2,026 |
| [41828511](https://pubmed.ncbi.nlm.nih.gov/41828511/) | Can IVIG Intervene in AD? Insights from Animal Experiments and Clinical Trials-A Systematic Review and Synthesis Without Meta-Analysis. | 2,026 |
| [41883140](https://pubmed.ncbi.nlm.nih.gov/41883140/) | Multimodal AI for Alzheimer Disease Diagnosis: Systematic Review of Datasets, Models, and Modalities. | 2,026 |
| [41893846](https://pubmed.ncbi.nlm.nih.gov/41893846/) | Racial and Ethnic Reporting and Representation in US Alzheimer Clinical Trials: A Systematic Review. | 2,026 |
| [42123553](https://pubmed.ncbi.nlm.nih.gov/42123553/) | The Role of Antidiabetic Therapies in Mild Cognitive Impairment and Alzheimer's Disease: A Systematic Review of Metformin, Pioglitazone, and GLP-1 Receptor Agonists. | 2,026 |
| [42196209](https://pubmed.ncbi.nlm.nih.gov/42196209/) | The Emerging Role of Dimethyl Fumarate in Alzheimer's Disease-A Systematic Review of Available Preclinical Studies. | 2,026 |
| [42441390](https://pubmed.ncbi.nlm.nih.gov/42441390/) | Amyloid PET Quantitation and Centiloid Thresholds in the Diagnosis of Alzheimer Disease: An Individual Participant Data Meta-Analysis. | 2,026 |
| [42492033](https://pubmed.ncbi.nlm.nih.gov/42492033/) | Efficacy Measures Used in Alzheimer Disease Clinical Trials Between 2015 and 2025: A Systematic Review. | 2,026 |
| [42589678](https://pubmed.ncbi.nlm.nih.gov/42589678/) | The Possible Association Between Bisphenol A (BPA) and the Neuropathological Processes Characteristic of Alzheimer's Disease-A Systematic Review of the Literature. | 2,026 |
| [42778253](https://pubmed.ncbi.nlm.nih.gov/42778253/) | Alzheimer's disease and related dementias in South and Southeast Asia: a systematic review and meta-analysis of epidemiology and associated factors. | 2,026 |
| [42883821](https://pubmed.ncbi.nlm.nih.gov/42883821/) | Plasma Neurofilament Light Chain as a Complementary Biomarker for Alzheimer's Disease and Mild Cognitive Impairment: A Systematic Review and Meta-Analysis. | 2,026 |
| [39778970](https://pubmed.ncbi.nlm.nih.gov/39778970/) | Updated Appropriate Use Criteria for Amyloid and Tau PET: A Report from the Alzheimer's Association and Society for Nuclear Medicine and Molecular Imaging Workgroup. | 2,025 |
| [39800395](https://pubmed.ncbi.nlm.nih.gov/39800395/) | Effects of aerobic exercise on cognitive function and quality of life in patients with Alzheimer's disease: a systematic review and meta-analysis. | 2,025 |
| [39859201](https://pubmed.ncbi.nlm.nih.gov/39859201/) | AdipoRon's Impact on Alzheimer's Disease-A Systematic Review and Meta-Analysis. | 2,025 |
| [39908541](https://pubmed.ncbi.nlm.nih.gov/39908541/) | Detection of Alzheimer Disease in Neuroimages Using Vision Transformers: Systematic Review and Meta-Analysis. | 2,025 |
| [39941125](https://pubmed.ncbi.nlm.nih.gov/39941125/) | Role of 11β-Hydroxysteroid Dehydrogenase and Mineralocorticoid Receptor on Alzheimer's Disease Onset: A Systematic Review. | 2,025 |
| [40029915](https://pubmed.ncbi.nlm.nih.gov/40029915/) | Prevalence and correlation of sarcopenia with Alzheimer's disease: A systematic review and meta-analysis. | 2,025 |
| [40112274](https://pubmed.ncbi.nlm.nih.gov/40112274/) | Incidence of Amyloid-Related Imaging Abnormalities in Phase III Clinical Trials of Anti-Amyloid-β Immunotherapy: An Updated Meta-Analysis. | 2,025 |
| [40159544](https://pubmed.ncbi.nlm.nih.gov/40159544/) | Diagnostic performance of deep learning-assisted [<sup>18</sup>F]FDG PET imaging for Alzheimer's disease: a systematic review and meta-analysis. | 2,025 |
| [40163534](https://pubmed.ncbi.nlm.nih.gov/40163534/) | Efficacy and safety of passive immunotherapies targeting amyloid beta in Alzheimer's disease: A systematic review and meta-analysis. | 2,025 |
| [40175353](https://pubmed.ncbi.nlm.nih.gov/40175353/) | Cross-ancestry genome-wide association study identifies implications of SORL1 in cerebral beta-amyloid deposition. | 2,025 |
| [40194268](https://pubmed.ncbi.nlm.nih.gov/40194268/) | Clinical Benefits and Risks of Antiamyloid Antibodies in Sporadic Alzheimer Disease: Systematic Review and Network Meta-Analysis With a Web Application. | 2,025 |
| [40198863](https://pubmed.ncbi.nlm.nih.gov/40198863/) | Objective Criteria for Subtle Cognitive Decline in Aging and Preclinical Alzheimer Disease: A Systematic Review. | 2,025 |
| [40332115](https://pubmed.ncbi.nlm.nih.gov/40332115/) | Evaluating the Bidirectional Causal Effects of Alzheimer's Disease Across Multiple Conditions: A Systematic Review and Meta-Analysis of Mendelian Randomization Studies. | 2,025 |
| [40818474](https://pubmed.ncbi.nlm.nih.gov/40818474/) | Blood phosphorylated tau for the diagnosis of Alzheimer's disease: a systematic review and meta-analysis. | 2,025 |
| [41096551](https://pubmed.ncbi.nlm.nih.gov/41096551/) | Molecular Biomarkers for Early Detection of Alzheimer's Disease and the Complementary Role of Engineered Nanomaterials: A Systematic Review. | 2,025 |
| [41226373](https://pubmed.ncbi.nlm.nih.gov/41226373/) | Blood-Based Tau as a Biomarker for Early Detection and Monitoring of Alzheimer's Disease: A Systematic Review and Meta-Analysis. | 2,025 |
| [41226670](https://pubmed.ncbi.nlm.nih.gov/41226670/) | Natural Products in Alzheimer's Disease: A Systematic Review of Clinical Trials and Underlying Molecular Mechanisms. | 2,025 |
| [41465389](https://pubmed.ncbi.nlm.nih.gov/41465389/) | Therapeutic Potential for Cannabidiol on Alzheimer's Disease-Related Neuroinflammation: A Systematic Review and Meta-Analysis. | 2,025 |
| [38042449](https://pubmed.ncbi.nlm.nih.gov/38042449/) | Radiation Therapy in Alzheimer's Disease: A Systematic Review. | 2,024 |
| [38141755](https://pubmed.ncbi.nlm.nih.gov/38141755/) | Deep Brain Stimulation as an Emerging Therapy for Cognitive Decline in Alzheimer Disease: Systematic Review of Evidence and Current Targets. | 2,024 |
| [38253509](https://pubmed.ncbi.nlm.nih.gov/38253509/) | Clinically Important Benefits and Harms of Monoclonal Antibodies Targeting Amyloid for the Treatment of Alzheimer Disease: A Systematic Review and Meta-Analysis. | 2,024 |
| [38256241](https://pubmed.ncbi.nlm.nih.gov/38256241/) | Salivary Biomarkers for Alzheimer's Disease: A Systematic Review with Meta-Analysis. | 2,024 |
| [38267189](https://pubmed.ncbi.nlm.nih.gov/38267189/) | Demographic, clinical, biomarker, and neuropathological correlates of posterior cortical atrophy: an international cohort study and individual participant data meta-analysis. | 2,024 |
| [38279266](https://pubmed.ncbi.nlm.nih.gov/38279266/) | Exploitation of Autophagy Inducers in the Management of Dementia: A Systematic Review. | 2,024 |
| [38290090](https://pubmed.ncbi.nlm.nih.gov/38290090/) | Association of Plasma YKL-40 With MRI, CSF, and Cognitive Markers of Brain Health and Dementia. | 2,024 |
| [38519775](https://pubmed.ncbi.nlm.nih.gov/38519775/) | Association between Mediterranean diet and dementia and Alzheimer disease: a systematic review with meta-analysis. | 2,024 |
| [38705542](https://pubmed.ncbi.nlm.nih.gov/38705542/) | Risk of Dementia and Alzheimer's Disease Associated With Antidiabetics: A Bayesian Network Meta-Analysis. | 2,024 |
| [38917167](https://pubmed.ncbi.nlm.nih.gov/38917167/) | Neutrophil to lymphocyte ratio in Alzheimer's disease: A systematic review and meta-analysis. | 2,024 |
| [38928248](https://pubmed.ncbi.nlm.nih.gov/38928248/) | Emerging Therapeutic Potential of Fluoxetine on Cognitive Decline in Alzheimer's Disease: Systematic Review. | 2,024 |
| [38986050](https://pubmed.ncbi.nlm.nih.gov/38986050/) | Blood Astrocyte Biomarkers in Alzheimer Disease: A Systematic Review and Meta-Analysis. | 2,024 |
| [39029377](https://pubmed.ncbi.nlm.nih.gov/39029377/) | A systematic literature review on the significance of deep learning and machine learning in predicting Alzheimer's disease. | 2,024 |
| [39126112](https://pubmed.ncbi.nlm.nih.gov/39126112/) | Human Leukocyte Antigen and microRNAs as Key Orchestrators of Mild Cognitive Impairment and Alzheimer's Disease: A Systematic Review. | 2,024 |
| [39141884](https://pubmed.ncbi.nlm.nih.gov/39141884/) | Blood Pressure, Antihypertensive Use, and Late-Life Alzheimer and Non-Alzheimer Dementia Risk: An Individual Participant Data Meta-Analysis. | 2,024 |
| [39206795](https://pubmed.ncbi.nlm.nih.gov/39206795/) | Parallel electrophysiological abnormalities due to COVID-19 infection and to Alzheimer's disease and related dementia. | 2,024 |
| [39226058](https://pubmed.ncbi.nlm.nih.gov/39226058/) | Case Definition for Diagnosed Alzheimer Disease and Related Dementias in Medicare. | 2,024 |
| [39250132](https://pubmed.ncbi.nlm.nih.gov/39250132/) | Role of the X Chromosome in Alzheimer Disease Genetics. | 2,024 |
| [39456775](https://pubmed.ncbi.nlm.nih.gov/39456775/) | The Association and Prognostic Implications of Long Non-Coding RNAs in Major Psychiatric Disorders, Alzheimer's Diseases and Parkinson's Diseases: A Systematic Review. | 2,024 |
| [39570963](https://pubmed.ncbi.nlm.nih.gov/39570963/) | Diagnostic value of arterial spin labeling for Alzheimer's disease: A systematic review and meta-analysis. | 2,024 |
| [39684623](https://pubmed.ncbi.nlm.nih.gov/39684623/) | Role of Blood P-Tau Isoforms (181, 217, 231) in Predicting Conversion from MCI to Dementia Due to Alzheimer's Disease: A Review and Meta-Analysis. | 2,024 |
| [35171074](https://pubmed.ncbi.nlm.nih.gov/35171074/) | Effectiveness of physical exercise at improving functional capacity in older adults living with Alzheimer's disease: a systematic review of randomized controlled trials. | 2,023 |
| [36096664](https://pubmed.ncbi.nlm.nih.gov/36096664/) | Clinical utility of cerebrospinal fluid biomarkers in the evaluation of cognitive impairment: a systematic review and meta-analysis. | 2,023 |
| [36375591](https://pubmed.ncbi.nlm.nih.gov/36375591/) | Risk of Subsequent Dementia or Alzheimer Disease Among Patients With Age-Related Macular Degeneration: A Systematic Review and Meta-analysis. | 2,023 |
| [36394831](https://pubmed.ncbi.nlm.nih.gov/36394831/) | Ocular Biomarkers for Alzheimer Disease Dementia: An Umbrella Review of Systematic Reviews and Meta-analyses. | 2,023 |
| [36629438](https://pubmed.ncbi.nlm.nih.gov/36629438/) | Probiotic supplements are effective in people with cognitive impairment: a meta-analysis of randomized controlled trials. | 2,023 |
| [36675177](https://pubmed.ncbi.nlm.nih.gov/36675177/) | Rationale for a Multi-Factorial Approach for the Reversal of Cognitive Decline in Alzheimer's Disease and MCI: A Review. | 2,023 |
| [36834617](https://pubmed.ncbi.nlm.nih.gov/36834617/) | Is Hormone Replacement Therapy a Risk Factor or a Therapeutic Option for Alzheimer's Disease? | 2,023 |
| [36868847](https://pubmed.ncbi.nlm.nih.gov/36868847/) | Predictors of cognitive deterioration in subjective cognitive decline: evidence from longitudinal studies and implications for SCD-plus criteria. | 2,023 |
| [36927883](https://pubmed.ncbi.nlm.nih.gov/36927883/) | Association of Mitochondrial DNA Copy Number With Brain MRI Markers and Cognitive Function: A Meta-analysis of Community-Based Cohorts. | 2,023 |
| [36947499](https://pubmed.ncbi.nlm.nih.gov/36947499/) | Circulating long non-coding RNAs as novel diagnostic biomarkers for Alzheimer's disease (AD): A systematic review and meta-analysis. | 2,023 |
| [36963821](https://pubmed.ncbi.nlm.nih.gov/36963821/) | Epigenetic clocks in neurodegenerative diseases: a systematic review. | 2,023 |
| [36973044](https://pubmed.ncbi.nlm.nih.gov/36973044/) | Accelerated Brain Volume Loss Caused by Anti-β-Amyloid Drugs: A Systematic Review and Meta-analysis. | 2,023 |
| [37043277](https://pubmed.ncbi.nlm.nih.gov/37043277/) | Serious Games for Learning Among Older Adults With Cognitive Impairment: Systematic Review and Meta-analysis. | 2,023 |
| [37047347](https://pubmed.ncbi.nlm.nih.gov/37047347/) | Non-Ceruloplasmin Copper Identifies a Subtype of Alzheimer's Disease (CuAD): Characterization of the Cognitive Profile and Case of a CuAD Patient Carrying an <i>RGS7</i> Stop-Loss Variant. | 2,023 |
| [37075703](https://pubmed.ncbi.nlm.nih.gov/37075703/) | Meta-analysis of published cerebrospinal fluid proteomics data identifies and validates metabolic enzyme panel as Alzheimer's disease biomarkers. | 2,023 |
| [37165483](https://pubmed.ncbi.nlm.nih.gov/37165483/) | Assessing adipokines as potential biomarkers of dementia, Alzheimer's disease, and mild cognitive impairment: A systematic review and meta-analysis. | 2,023 |
| [37183681](https://pubmed.ncbi.nlm.nih.gov/37183681/) | SARS-CoV-2 susceptibility and COVID-19 illness course and outcome in people with pre-existing neurodegenerative disorders: systematic review with frequentist and Bayesian meta-analyses. | 2,023 |
| [37224131](https://pubmed.ncbi.nlm.nih.gov/37224131/) | Gut microbiome dysbiosis in Alzheimer's disease and mild cognitive impairment: A systematic review and meta-analysis. | 2,023 |
| [37225432](https://pubmed.ncbi.nlm.nih.gov/37225432/) | Alzheimer Disease and Epilepsy: A Mendelian Randomization Study. | 2,023 |
| [37322115](https://pubmed.ncbi.nlm.nih.gov/37322115/) | Clonal hematopoiesis is associated with protection from Alzheimer's disease. | 2,023 |
| [37358841](https://pubmed.ncbi.nlm.nih.gov/37358841/) | Cholinesterase Inhibitors for Treatment of Psychotic Symptoms in Alzheimer Disease and Parkinson Disease: A Meta-analysis. | 2,023 |
| [37373304](https://pubmed.ncbi.nlm.nih.gov/37373304/) | The Importance of Subjective Cognitive Decline Recognition and the Potential of Molecular and Neurophysiological Biomarkers-A Systematic Review. | 2,023 |
| [37373321](https://pubmed.ncbi.nlm.nih.gov/37373321/) | A Systematic Review of the Effects of Capsaicin on Alzheimer's Disease. | 2,023 |
| [37379265](https://pubmed.ncbi.nlm.nih.gov/37379265/) | Outcomes and clinical implications of intranasal insulin on cognition in humans: A systematic review and meta-analysis. | 2,023 |
| [37446135](https://pubmed.ncbi.nlm.nih.gov/37446135/) | Phototherapy of Alzheimer's Disease: Photostimulation of Brain Lymphatics during Sleep: A Systematic Review. | 2,023 |
| [37446396](https://pubmed.ncbi.nlm.nih.gov/37446396/) | Neurodegenerative Disease Associated Pathways in the Brains of Triple Transgenic Alzheimer's Model Mice Are Reversed Following Two Weeks of Peripheral Administration of Fasudil. | 2,023 |
| [37511037](https://pubmed.ncbi.nlm.nih.gov/37511037/) | Targeting Protein Aggregates with Natural Products: An Optional Strategy for Neurodegenerative Diseases. | 2,023 |
| [37834128](https://pubmed.ncbi.nlm.nih.gov/37834128/) | The Role of Adipokines in the Pathologies of the Central Nervous System. | 2,023 |
| [37878635](https://pubmed.ncbi.nlm.nih.gov/37878635/) | Atopic dermatitis and cognitive dysfunction in middle-aged and older adults: A systematic review and meta-analysis. | 2,023 |
| [37895161](https://pubmed.ncbi.nlm.nih.gov/37895161/) | Mechanistic Intimate Insights into the Role of Hydrogen Sulfide in Alzheimer's Disease: A Recent Systematic Review. | 2,023 |
| [37932666](https://pubmed.ncbi.nlm.nih.gov/37932666/) | Understanding barriers to and facilitators of clinician-patient conversations about brain health and cognitive concerns in primary care: a systematic review and practical considerations for the clinician. | 2,023 |
| [38003723](https://pubmed.ncbi.nlm.nih.gov/38003723/) | Topical Cellular/Tissue and Molecular Aspects Regarding Nonpharmacological Interventions in Alzheimer's Disease-A Systematic Review. | 2,023 |
| [38033098](https://pubmed.ncbi.nlm.nih.gov/38033098/) | The association between bullous pemphigoid and cognitive outcomes in middle-aged and older adults: A systematic review and meta-analysis. | 2,023 |
| [38042608](https://pubmed.ncbi.nlm.nih.gov/38042608/) | A comprehensive review on federated learning based models for healthcare applications. | 2,023 |
| [38055651](https://pubmed.ncbi.nlm.nih.gov/38055651/) | The effect of light therapy on sleep disorders and psychobehavioral symptoms in patients with Alzheimer's disease: A meta-analysis. | 2,023 |
| [34375545](https://pubmed.ncbi.nlm.nih.gov/34375545/) | Effectiveness of gait aid prescription for improving spatiotemporal gait parameters and associated outcomes in community-dwelling older people: a systematic review. | 2,022 |
| [34870696](https://pubmed.ncbi.nlm.nih.gov/34870696/) | Research Criteria for the Behavioral Variant of Alzheimer Disease: A Systematic Review and Meta-analysis. | 2,022 |
| [35099507](https://pubmed.ncbi.nlm.nih.gov/35099507/) | Amyloid-Related Imaging Abnormalities and β-Amyloid-Targeting Antibodies: A Systematic Review. | 2,022 |
| [35241627](https://pubmed.ncbi.nlm.nih.gov/35241627/) | Plasma Aβ as a biomarker for predicting Aβ-PET status in Alzheimer's disease：a systematic review with meta-analysis. | 2,022 |
| [35301183](https://pubmed.ncbi.nlm.nih.gov/35301183/) | Physical activity as a protective factor for dementia and Alzheimer's disease: systematic review, meta-analysis and quality assessment of cohort and case-control studies. | 2,022 |
| [35388616](https://pubmed.ncbi.nlm.nih.gov/35388616/) | Transcriptional landscape of human microglia implicates age, sex, and APOE-related immunometabolic pathway perturbations. | 2,022 |
| [35473731](https://pubmed.ncbi.nlm.nih.gov/35473731/) | Comparative safety and efficacy of cognitive enhancers for Alzheimer's dementia: a systematic review with individual patient data network meta-analysis. | 2,022 |
| [35507052](https://pubmed.ncbi.nlm.nih.gov/35507052/) | Diagnostic performance of hippocampal volumetry in Alzheimer's disease or mild cognitive impairment: a meta-analysis. | 2,022 |
| [35523585](https://pubmed.ncbi.nlm.nih.gov/35523585/) | Positive Airway Pressure and Cognitive Disorders in Adults With Obstructive Sleep Apnea: A Systematic Review of the Literature. | 2,022 |
| [35604690](https://pubmed.ncbi.nlm.nih.gov/35604690/) | Association of Alzheimer Disease With Life Expectancy in People With Down Syndrome. | 2,022 |
| [35737623](https://pubmed.ncbi.nlm.nih.gov/35737623/) | Predictive Accuracy of Digital Biomarker Technologies for Detection of Mild Cognitive Impairment and Pre-Frailty Amongst Older Adults: A Systematic Review and Meta-Analysis. | 2,022 |
| [35899678](https://pubmed.ncbi.nlm.nih.gov/35899678/) | Association between Human Blood Metabolome and the Risk of Alzheimer's Disease. | 2,022 |
| [35948447](https://pubmed.ncbi.nlm.nih.gov/35948447/) | Leisure Activities and the Risk of Dementia: A Systematic Review and Meta-analysis. | 2,022 |
| [35982059](https://pubmed.ncbi.nlm.nih.gov/35982059/) | Cross-tissue analysis of blood and brain epigenome-wide association studies in Alzheimer's disease. | 2,022 |
| [36028322](https://pubmed.ncbi.nlm.nih.gov/36028322/) | Progression of Subjective Cognitive Decline to MCI or Dementia in Relation to Biomarkers for Alzheimer Disease: A Meta-analysis. | 2,022 |
| [36038268](https://pubmed.ncbi.nlm.nih.gov/36038268/) | Incidence of Amyloid-Related Imaging Abnormalities in Patients With Alzheimer Disease Treated With Anti-β-Amyloid Immunotherapy: A Meta-analysis. | 2,022 |
| [36077520](https://pubmed.ncbi.nlm.nih.gov/36077520/) | Tear Biomarkers in Alzheimer's and Parkinson's Diseases, and Multiple Sclerosis: Implications for Diagnosis (Systematic Review). | 2,022 |
| [36499562](https://pubmed.ncbi.nlm.nih.gov/36499562/) | Disease-Modifying Activity of Huperzine A on Alzheimer's Disease: Evidence from Preclinical Studies on Rodent Models. | 2,022 |
| [36499656](https://pubmed.ncbi.nlm.nih.gov/36499656/) | Is Periodontitis Associated with Age-Related Cognitive Impairment? The Systematic Review, Confounders Assessment and Meta-Analysis of Clinical Studies. | 2,022 |
| [36520433](https://pubmed.ncbi.nlm.nih.gov/36520433/) | Transferability of Alzheimer Disease Polygenic Risk Score Across Populations and Its Association With Alzheimer Disease-Related Phenotypes. | 2,022 |

Primary studies with their number of citing guidelines and reviews are in `primary_studies.csv`; the citing guidelines and reviews in `citing_reviews.csv`. PubMed, MeSH: U.S. National Library of Medicine; citations: OpenAlex. Graph files: CC0.
