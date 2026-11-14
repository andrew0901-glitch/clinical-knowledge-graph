# Evidence map: Breast Neoplasms

MeSH D001943, 9 descriptors. Source: Lunas Clinical Evidence KG v0.2.1 (snapshot 2026-11-07). Built by `examples/evidence_map.py`; `report.html` has the same content with a chart.

| measure | value |
|---|---|
| Articles | 47,004 |
| Guideline | 180 |
| Systematic review or meta-analysis | 1,101 |
| Randomized controlled trial | 3,031 |
| Other clinical trial | 1,823 |
| Observational study | 370 |
| Other | 40,499 |
| Primary studies (RCT + other clinical trial) | 4,854 |
| Primary studies cited by an in-graph guideline or review | 2,297 |
| Primary studies not cited within the graph | 2,557 |
| Randomized controlled trials cited | 1,706 |
| Other clinical trials cited | 591 |
| Distinct citing guidelines and reviews | 1,874 |
| ... of which in this map | 750 |
| Systematic reviews or meta-analyses, 2022-2026 | 397 |
| Guidelines, 2022-2026 | 46 |

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
| D001943 | Breast Neoplasms | 0 |
| D000071960 | Breast Carcinoma In Situ | 1 |
| D018567 | Breast Neoplasms, Male | 1 |
| D018270 | Carcinoma, Ductal, Breast | 1 |
| D018275 | Carcinoma, Lobular | 1 |
| D061325 | Hereditary Breast and Ovarian Cancer Syndrome | 1 |
| D058922 | Inflammatory Breast Neoplasms | 1 |
| D064726 | Triple Negative Breast Neoplasms | 1 |
| D000069584 | Unilateral Breast Neoplasms | 1 |

## Guidelines, 2022-2026 (46)

| pmid | title | year |
|---|---|---|
| [40707174](https://pubmed.ncbi.nlm.nih.gov/40707174/) | Anticancer Agents and Their Impact on Breast Reconstruction: A Guide for Plastic Surgeons Based on Systematic Review and Expert Consensus. | 2,026 |
| [40856739](https://pubmed.ncbi.nlm.nih.gov/40856739/) | ESR Essentials: artificial intelligence in breast imaging-practice recommendations by the European Society of Breast Imaging. | 2,026 |
| [41885663](https://pubmed.ncbi.nlm.nih.gov/41885663/) | ACR Appropriateness Criteria® Breast Imaging During Lactation. | 2,026 |
| [41996183](https://pubmed.ncbi.nlm.nih.gov/41996183/) | Screening for Breast Cancer in Asymptomatic, Average-Risk Adult Females: A Guidance Statement From the American College of Physicians (Version 2). | 2,026 |
| [42462191](https://pubmed.ncbi.nlm.nih.gov/42462191/) | Breast Cancer Follow-Up and Surveillance After Primary Treatment: ASCO Guideline Update. | 2,026 |
| [42616513](https://pubmed.ncbi.nlm.nih.gov/42616513/) | American Society of Breast Surgeons, Society of Breast Imaging, and College of American Pathology 2026 Guidelines for the Management of Proliferative Lesions With Atypia and Lobular Carcinoma In Situ. | 2,026 |
| [39085641](https://pubmed.ncbi.nlm.nih.gov/39085641/) | ESR Essentials: diagnostic work-up in patients with symptomatic breast disease-practice recommendations by the European Society of Breast Imaging. | 2,025 |
| [39388713](https://pubmed.ncbi.nlm.nih.gov/39388713/) | Age to Initiate Routine Breast Cancer Screening: ACOG Clinical Practice Update. | 2,025 |
| [40209128](https://pubmed.ncbi.nlm.nih.gov/40209128/) | Sentinel Lymph Node Biopsy in Early-Stage Breast Cancer: ASCO Guideline Update. | 2,025 |
| [40409882](https://pubmed.ncbi.nlm.nih.gov/40409882/) | ACR Appropriateness Criteria® Imaging of Ductal Carcinoma in Situ (DCIS). | 2,025 |
| [40409891](https://pubmed.ncbi.nlm.nih.gov/40409891/) | ACR Appropriateness Criteria® Supplemental Breast Cancer Screening Based on Breast Density: 2024 Update. | 2,025 |
| [40674730](https://pubmed.ncbi.nlm.nih.gov/40674730/) | Recommendations From the Women's Preventive Services Initiative on Breast Cancer Screening for Women at Average Risk and Patient Navigation Services for Breast and Cervical Cancer Screening. | 2,025 |
| [40955654](https://pubmed.ncbi.nlm.nih.gov/40955654/) | Postmastectomy Radiation Therapy: An ASTRO-ASCO-SSO Clinical Practice Guideline. | 2,025 |
| [40956255](https://pubmed.ncbi.nlm.nih.gov/40956255/) | Postmastectomy Radiation Therapy: An ASTRO/ASCO/SSO Clinical Practice Guideline. | 2,025 |
| [41123921](https://pubmed.ncbi.nlm.nih.gov/41123921/) | American Society of Breast Surgeons and Society of Breast Imaging 2025 Guidelines for the Management of Benign Breast Fibroepithelial Lesions. | 2,025 |
| [41193040](https://pubmed.ncbi.nlm.nih.gov/41193040/) | ACR Appropriateness Criteria® Breast Imaging During Pregnancy. | 2,025 |
| [41193041](https://pubmed.ncbi.nlm.nih.gov/41193041/) | ACR Appropriateness Criteria® Female Breast Cancer Screening: 2025 Update. | 2,025 |
| [41193045](https://pubmed.ncbi.nlm.nih.gov/41193045/) | ACR Appropriateness Criteria® Male Breast Cancer Screening. | 2,025 |
| [37977261](https://pubmed.ncbi.nlm.nih.gov/37977261/) | Partial Breast Irradiation for Patients With Early-Stage Invasive Breast Cancer or Ductal Carcinoma In Situ: An ASTRO Clinical Practice Guideline. | 2,024 |
| [38175972](https://pubmed.ncbi.nlm.nih.gov/38175972/) | Germline Testing in Patients With Breast Cancer: ASCO-Society of Surgical Oncology Guideline. | 2,024 |
| [38206277](https://pubmed.ncbi.nlm.nih.gov/38206277/) | Systemic Treatment of Patients With Metastatic Breast Cancer: ASCO Resource-Stratified Guideline. | 2,024 |
| [38656711](https://pubmed.ncbi.nlm.nih.gov/38656711/) | ESR Essentials: screening for breast cancer - general recommendations by EUSOBI. | 2,024 |
| [38687503](https://pubmed.ncbi.nlm.nih.gov/38687503/) | Screening for Breast Cancer: US Preventive Services Task Force Recommendation Statement. | 2,024 |
| [38740576](https://pubmed.ncbi.nlm.nih.gov/38740576/) | Joint EANM-SNMMI guideline on the role of 2-[<sup>18</sup>F]FDG PET/CT in no special type breast cancer : (endorsed by the ACR, ESSO, ESTRO, EUSOBI/ESR, and EUSOMA). | 2,024 |
| [38768407](https://pubmed.ncbi.nlm.nih.gov/38768407/) | Optimal Adjuvant Chemotherapy and Targeted Therapy for Early Breast Cancer-Cyclin-Dependent Kinase 4 and 6 Inhibitors: ASCO Guideline Rapid Recommendation Update. | 2,024 |
| [38823941](https://pubmed.ncbi.nlm.nih.gov/38823941/) | ACR Appropriateness Criteria® Female Breast Cancer Screening: 2023 Update. | 2,024 |
| [38823943](https://pubmed.ncbi.nlm.nih.gov/38823943/) | ACR Appropriateness Criteria® Imaging of Invasive Breast Cancer. | 2,024 |
| [39835453](https://pubmed.ncbi.nlm.nih.gov/39835453/) | Contemporary management of phyllodes tumours of the breast: proposal for recommendations from the UK Association of Breast Surgery. | 2,024 |
| [36626701](https://pubmed.ncbi.nlm.nih.gov/36626701/) | Chemotherapy and Targeted Therapy for Endocrine-Pretreated or Hormone Receptor-Negative Metastatic Breast Cancer: ASCO Guideline Rapid Recommendation Update. | 2,023 |
| [36990615](https://pubmed.ncbi.nlm.nih.gov/36990615/) | Multinational Association of Supportive Care in Cancer (MASCC) clinical practice guidelines for the prevention and management of acute radiation dermatitis: international Delphi consensus-based recommendations. | 2,023 |
| [37196213](https://pubmed.ncbi.nlm.nih.gov/37196213/) | Testing for <i>ESR1</i> Mutations to Guide Therapy for Hormone Receptor-Positive, Human Epidermal Growth Factor Receptor 2-Negative Metastatic Breast Cancer: ASCO Guideline Rapid Recommendation Update. | 2,023 |
| [37236739](https://pubmed.ncbi.nlm.nih.gov/37236739/) | ACR Appropriateness Criteria® Monitoring Response to Neoadjuvant Systemic Therapy for Breast Cancer: 2022 Update. | 2,023 |
| [37236740](https://pubmed.ncbi.nlm.nih.gov/37236740/) | ACR Appropriateness Criteria® Palpable Breast Masses: 2022 Update. | 2,023 |
| [37284804](https://pubmed.ncbi.nlm.nih.gov/37284804/) | Human Epidermal Growth Factor Receptor 2 Testing in Breast Cancer: ASCO-College of American Pathologists Guideline Update. | 2,023 |
| [37301263](https://pubmed.ncbi.nlm.nih.gov/37301263/) | ESTRO-ACROP guideline: Recommendations on implementation of breath-hold techniques in radiotherapy. | 2,023 |
| [37490054](https://pubmed.ncbi.nlm.nih.gov/37490054/) | Management of individuals with germline pathogenic/likely pathogenic variants in CHEK2: A clinical practice resource of the American College of Medical Genetics and Genomics (ACMG). | 2,023 |
| [34878801](https://pubmed.ncbi.nlm.nih.gov/34878801/) | Abemaciclib With Endocrine Therapy in the Treatment of High-Risk Early Breast Cancer: ASCO Optimal Adjuvant Chemotherapy and Targeted Therapy Guideline Rapid Recommendation Update. | 2,022 |
| [35417251](https://pubmed.ncbi.nlm.nih.gov/35417251/) | Use of Immune Checkpoint Inhibitor Pembrolizumab in the Treatment of High-Risk, Early-Stage Triple-Negative Breast Cancer: ASCO Guideline Rapid Recommendation Update. | 2,022 |
| [35439025](https://pubmed.ncbi.nlm.nih.gov/35439025/) | Biomarkers for Adjuvant Endocrine and Chemotherapy in Early-Stage Breast Cancer: ASCO Guideline Update. | 2,022 |
| [35640075](https://pubmed.ncbi.nlm.nih.gov/35640075/) | Management of Advanced Human Epidermal Growth Factor Receptor 2-Positive Breast Cancer and Brain Metastases: ASCO Guideline Update. | 2,022 |
| [35738413](https://pubmed.ncbi.nlm.nih.gov/35738413/) | Clinical Diagnoses and Outcomes After Diagnostic Breast Ultrasound by Nurses and General Practitioner Physicians in Rural Rwanda. | 2,022 |
| [35759724](https://pubmed.ncbi.nlm.nih.gov/35759724/) | Biomarkers for Systemic Therapy in Metastatic Breast Cancer: ASCO Guideline Update. | 2,022 |
| [35926153](https://pubmed.ncbi.nlm.nih.gov/35926153/) | Chemotherapy and Targeted Therapy for Human Epidermal Growth Factor Receptor 2-Negative Metastatic Breast Cancer That Is Either Endocrine-Pretreated or Hormone Receptor-Negative: ASCO Guideline Rapid Recommendation Update. | 2,022 |
| [36436958](https://pubmed.ncbi.nlm.nih.gov/36436958/) | ACR Appropriateness Criteria® Evaluation of Nipple Discharge: 2022 Update. | 2,022 |
| [36436961](https://pubmed.ncbi.nlm.nih.gov/36436961/) | ACR Appropriateness Criteria® Imaging After Breast Surgery. | 2,022 |
| [36436962](https://pubmed.ncbi.nlm.nih.gov/36436962/) | ACR Appropriateness Criteria® Imaging of Deep Inferior Epigastric Arteries for Surgical Planning (Breast Reconstruction Surgery): 2022 Update. | 2,022 |

## Systematic reviews and meta-analyses, 2022-2026 (397)

| pmid | title | year |
|---|---|---|
| [40570265](https://pubmed.ncbi.nlm.nih.gov/40570265/) | Efficacy of Multimodal Psychological Interventions on Pain After Surgery in Breast Cancer Survivors: A Systematic Review. | 2,026 |
| [40745968](https://pubmed.ncbi.nlm.nih.gov/40745968/) | Physical exercise and breast cancer-related lymphedema: an umbrella review, systematic review and meta-analysis. | 2,026 |
| [40960690](https://pubmed.ncbi.nlm.nih.gov/40960690/) | Artificial intelligence-assisted PET imaging for predicting neoadjuvant chemotherapy response in breast cancer: a systematic review and meta-analysis. | 2,026 |
| [40962960](https://pubmed.ncbi.nlm.nih.gov/40962960/) | Immediate Lymphatic Reconstruction (ILR) for the Prevention of Lymphedema: A Meta-analysis of Prospective Clinical Trials. | 2,026 |
| [41091344](https://pubmed.ncbi.nlm.nih.gov/41091344/) | A Systematic Review of Occult Malignancy and Sentinel Lymph Node Metastasis at the Time of Contralateral Prophylactic Mastectomy. | 2,026 |
| [41186678](https://pubmed.ncbi.nlm.nih.gov/41186678/) | Progression-free survival prediction and comparative metastasis detection accuracy of <sup>18</sup>F-FES PET/CT for ER-Positive breast cancer: Systematic review, meta-analyses and meta-regressions. | 2,026 |
| [41308380](https://pubmed.ncbi.nlm.nih.gov/41308380/) | Beam me later: Prepectoral vs subpectoral breast reconstruction before postmastectomy radiotherapy - A systematic review and meta-analysis. | 2,026 |
| [41344861](https://pubmed.ncbi.nlm.nih.gov/41344861/) | The Role of Estrogen Receptor-Targeted PET with 16α-<sup>18</sup>F-Fluoro-17β-Estradiol in Predicting Response to Endocrine Therapies in Metastatic Breast Cancer: A Metaanalysis. | 2,026 |
| [41380366](https://pubmed.ncbi.nlm.nih.gov/41380366/) | Epidemiology of Breast Implant-Associated Anaplastic Large Cell Lymphoma - A systematic review of literature. | 2,026 |
| [41413361](https://pubmed.ncbi.nlm.nih.gov/41413361/) | Effects of Exercise on Cytokine Profiles in Breast Cancer Survivors: A Systematic Review. | 2,026 |
| [41417121](https://pubmed.ncbi.nlm.nih.gov/41417121/) | Contribution of mammographic imaging after initial ultrasound in women with focal breast complaints-systematic review. | 2,026 |
| [41432446](https://pubmed.ncbi.nlm.nih.gov/41432446/) | Nipple-Preserving Skin-Reducing Mastectomy in Ptotic Breasts: A Systematic Review and Meta-analysis. | 2,026 |
| [41499127](https://pubmed.ncbi.nlm.nih.gov/41499127/) | Risk-Reducing Bilateral Mastectomy and Mortality in Carriers of BRCA1 and BRCA2 Variants: A Systematic Review and Meta-Analysis. | 2,026 |
| [41501990](https://pubmed.ncbi.nlm.nih.gov/41501990/) | Current state of mammography-based artificial intelligence for future breast cancer risk prediction: a systematic review. | 2,026 |
| [41564189](https://pubmed.ncbi.nlm.nih.gov/41564189/) | Lifecourse genome-wide association study meta-analysis refines the critical life stages for adiposity's influence on breast cancer risk. | 2,026 |
| [41570662](https://pubmed.ncbi.nlm.nih.gov/41570662/) | Fluorescence imaging with indocyanine green during breast cancer surgery and postmastectomy breast reconstruction: A double systematic review and cost analysis. | 2,026 |
| [41581299](https://pubmed.ncbi.nlm.nih.gov/41581299/) | Immediate versus delayed symmetrisation of the contralateral breast after oncoplastic procedures: A systematic review and meta-analysis. | 2,026 |
| [41614595](https://pubmed.ncbi.nlm.nih.gov/41614595/) | Postmastectomy Breast Reconstruction Following Massive Weight Loss: An Updated Systematic Review and Identification of Research Gaps. | 2,026 |
| [41620925](https://pubmed.ncbi.nlm.nih.gov/41620925/) | The safety of trastuzumab deruxtecan (T-DXd) in breast cancer brain metastases with a focus on interstitial lung disease/pneumonitis: A systematic review and meta-analysis. | 2,026 |
| [41643348](https://pubmed.ncbi.nlm.nih.gov/41643348/) | Predictors of postoperative complications following staged nipple-sparing mastectomy: A systematic review & meta-analysis. | 2,026 |
| [41721080](https://pubmed.ncbi.nlm.nih.gov/41721080/) | Do Combined Resistance and Aerobic Exercise Programs Cause an Interference Effect in Women with Breast Cancer? A Systematic Review and Network Meta-analysis. | 2,026 |
| [41723490](https://pubmed.ncbi.nlm.nih.gov/41723490/) | The influence of immunohistochemistry-based subtypes on overall survival in breast cancer spine metastases: a systematic review and meta-analysis. | 2,026 |
| [41751852](https://pubmed.ncbi.nlm.nih.gov/41751852/) | Is Cold Atmospheric Plasma Selective for Breast Tumor Cells? A Systematic Review. | 2,026 |
| [41752017](https://pubmed.ncbi.nlm.nih.gov/41752017/) | Non-Coding RNA-Based Therapeutic Strategies in Triple-Negative Breast Cancer: A Systematic Review. | 2,026 |
| [41752044](https://pubmed.ncbi.nlm.nih.gov/41752044/) | Molecular and Clinicopathological Biomarkers Predicting Brain Metastasis in Triple-Negative Breast Cancer: A Systematic Review. | 2,026 |
| [41752055](https://pubmed.ncbi.nlm.nih.gov/41752055/) | Exosomes and Triple-Negative Breast Cancer: Current Knowledge and Clinical Significance. | 2,026 |
| [41752108](https://pubmed.ncbi.nlm.nih.gov/41752108/) | A Systematic Review of Major Advances in Breast Cancer Therapeutics in 2025: Synthesis of Conference and Published Evidence. | 2,026 |
| [41763228](https://pubmed.ncbi.nlm.nih.gov/41763228/) | The impact of exercise interventions on domains of quality of life in women diagnosed with breast cancers during chemotherapy treatment: a meta-analytic review. | 2,026 |
| [41833211](https://pubmed.ncbi.nlm.nih.gov/41833211/) | Systematic review and meta-analysis of revision surgery after immediate implant-based breast reconstruction: Re-implantation or converting to free tissue transfer? | 2,026 |
| [41879915](https://pubmed.ncbi.nlm.nih.gov/41879915/) | Which Exercise Prescriptions Improve Physical Fitness in Patients with Breast Cancer Before, During, and Following Treatment? A Systematic Review and Meta-analysis of Randomized Controlled Trials. | 2,026 |
| [41911243](https://pubmed.ncbi.nlm.nih.gov/41911243/) | Deep inspiration breath hold versus free breathing in postoperative radiotherapy strategy for patients with left-sided breast cancer treated with volumetric modulated arc therapy: A meta-analysis and systematic review. | 2,026 |
| [41932273](https://pubmed.ncbi.nlm.nih.gov/41932273/) | Breast implant-associated B-cell lymphomas: First systematic review of the literature. | 2,026 |
| [41992690](https://pubmed.ncbi.nlm.nih.gov/41992690/) | Accuracy of Deep Learning for Detecting Axillary Lymph Node Metastasis in Breast Cancer: Systematic Review and Meta-Analysis. | 2,026 |
| [42041522](https://pubmed.ncbi.nlm.nih.gov/42041522/) | Comparison of Complication Rates Between Immediate and Delayed Breast Reconstruction Following Mastectomy for Breast Cancer: A Systematic Review and Meta-Analysis. | 2,026 |
| [42061371](https://pubmed.ncbi.nlm.nih.gov/42061371/) | CDK4/6 inhibitors plus endocrine therapy versus endocrine monotherapy in hormone receptor-positive, HER2-negative advanced breast cancer: a reconstructed individual patient data meta-analysis of phase 3 randomised controlled trials. | 2,026 |
| [42090319](https://pubmed.ncbi.nlm.nih.gov/42090319/) | Deep Learning Algorithms Versus Radiologists in Digital Breast Tomosynthesis for Breast Cancer Detection: Systematic Review and Meta-Analysis. | 2,026 |
| [42134978](https://pubmed.ncbi.nlm.nih.gov/42134978/) | Diagnostic Performance of FAPI PET in Patients with Breast Cancer: A Systematic Review. | 2,026 |
| [42196354](https://pubmed.ncbi.nlm.nih.gov/42196354/) | Multidisciplinary Management of Malignant Phyllodes Tumours of the Breast: A Case-Based Illustration and Systematic Review. | 2,026 |
| [42196435](https://pubmed.ncbi.nlm.nih.gov/42196435/) | Viral Genomic Footprints in Breast Cancer: A Systematic Review and Meta-Analysis of Tissue-Based Detection of Epstein-Barr Virus and Bovine Leukemia Virus. | 2,026 |
| [42252358](https://pubmed.ncbi.nlm.nih.gov/42252358/) | A Decade Later: An Updated Systematic Review and Meta-analysis of Overall Survival, Disease-Free Survival, Local Recurrence, and Nipple-Areolar Recurrence Following Nipple-Sparing Mastectomy. | 2,026 |
| [42308843](https://pubmed.ncbi.nlm.nih.gov/42308843/) | Robot-assisted versus conventional mastectomy and immediate breast reconstruction: A systematic review and comparative and single-arm meta-analysis. | 2,026 |
| [42315709](https://pubmed.ncbi.nlm.nih.gov/42315709/) | Impact of Surgical Delay on Breast Cancer Prognosis: Systematic Review and Meta-analysis. | 2,026 |
| [42319409](https://pubmed.ncbi.nlm.nih.gov/42319409/) | Assessing the performance of deep learning and hand-crafted radiomics models using MRI and ultrasound in predicting axillary lymph node status in breast cancer: a systematic review and meta-analysis. | 2,026 |
| [42336622](https://pubmed.ncbi.nlm.nih.gov/42336622/) | Optimising exercise prescription for cancer-related fatigue, lean mass, physical function and muscle strength in women with breast cancer: a systematic review with dose-response network meta-analysis. | 2,026 |
| [42379272](https://pubmed.ncbi.nlm.nih.gov/42379272/) | Margin Adequacy in Phyllodes Tumors Revisited: Reappraisal of the Evidence Base and Knowledge Gaps. | 2,026 |
| [42456528](https://pubmed.ncbi.nlm.nih.gov/42456528/) | Biologic versus synthetic meshes in irradiated implant-based breast reconstruction: A systematic review and meta-analysis. | 2,026 |
| [42461660](https://pubmed.ncbi.nlm.nih.gov/42461660/) | Progression-Free Survival in Metastatic Breast Cancer by Local Investigators vs Blinded Independent Central Review: A Systematic Review and Meta-Analysis. | 2,026 |
| [42497233](https://pubmed.ncbi.nlm.nih.gov/42497233/) | Diagnostic accuracy of circulating microRNAs and lipidomic biomarkers for early breast cancer detection: A systematic review and meta-analysis. | 2,026 |
| [42501871](https://pubmed.ncbi.nlm.nih.gov/42501871/) | Association between adolescent alcohol consumption and cigarette smoking with adult risk of breast cancer: A systematic review and meta-analysis. | 2,026 |
| [42511860](https://pubmed.ncbi.nlm.nih.gov/42511860/) | Nanoparticle-Mediated Radiosensitization in Breast Cancer: A Systematic Review of Preclinical Evidence and Translational Challenges. | 2,026 |
| [42557566](https://pubmed.ncbi.nlm.nih.gov/42557566/) | Assessment of Trophoblast cell surface antigen 2 (Trop-2) expression and its clinical significance in breast cancer: a multi-level analysis of protein and gene expression. | 2,026 |
| [42603618](https://pubmed.ncbi.nlm.nih.gov/42603618/) | Preoperative stereotactic body radiotherapy for early-stage luminal breast cancer: a systematic review and meta-analysis (PRELUMEN). | 2,026 |
| [42641254](https://pubmed.ncbi.nlm.nih.gov/42641254/) | Beyond predictive performance: A systematic review and critical methodological appraisal of AI/ML and conventional modelling strategies in breast, colorectal, and pancreatic Cancer. | 2,026 |
| [42653312](https://pubmed.ncbi.nlm.nih.gov/42653312/) | Biomarkers of Hypercoagulability and Thromboinflammation in Cervical Cancer-Associated Thrombosis: A Systematic Review with Translational Insights from Breast Cancer. | 2,026 |
| [42653348](https://pubmed.ncbi.nlm.nih.gov/42653348/) | Circulating and Tissue MicroRNA Profiles Associated with Pathological Complete Response in HER2+ Breast Cancer: A Systematic Review. | 2,026 |
| [42737612](https://pubmed.ncbi.nlm.nih.gov/42737612/) | Circulating Tumor DNA and Circulating Tumor Cells in Liquid Biopsy as Post-Treatment Prognostic Biomarkers in Early Breast Cancer: A Systematic Review and Meta-Analysis. | 2,026 |
| [42772875](https://pubmed.ncbi.nlm.nih.gov/42772875/) | Where do delays occur? A systematic review of the barriers to early breast cancer diagnosis across South Africa's health system. | 2,026 |
| [42809558](https://pubmed.ncbi.nlm.nih.gov/42809558/) | Efficacy and safety of T-DXd versus Other HER2-targeted therapies in second-line and later settings for HER2-positive metastatic breast cancer: A Bayesian network meta-analysis. | 2,026 |
| [42961418](https://pubmed.ncbi.nlm.nih.gov/42961418/) | Survival After Risk-Reducing Mastectomy in Patients With Pathogenic Variants in BRCA1 and BRCA2: A Network Meta-Analysis. | 2,026 |
| [38886886](https://pubmed.ncbi.nlm.nih.gov/38886886/) | Impact of Implant Exchange Timing after Postmastectomy Radiation in Immediate Tissue Expander Breast Reconstruction. | 2,025 |
| [39133184](https://pubmed.ncbi.nlm.nih.gov/39133184/) | Uptake of breast cancer screening practices in low- and middle-income countries: a systematic review and meta-analysis. | 2,025 |
| [39235037](https://pubmed.ncbi.nlm.nih.gov/39235037/) | Adherence, clinical benefits, and adverse effects of endocrine therapies among women with nonmetastatic breast cancer in developing countries: A systematic review and meta-analysis. | 2,025 |
| [39331823](https://pubmed.ncbi.nlm.nih.gov/39331823/) | Estimating the Prevalence of Breast Implant-Associated Anaplastic Large-Cell Lymphoma: A Systematic Review. | 2,025 |
| [39356685](https://pubmed.ncbi.nlm.nih.gov/39356685/) | Statistical Fragility of Outcomes on Breast Reconstruction with Acellular Dermal Matrix: A Systematic Review of Randomized Controlled Trials. | 2,025 |
| [39363049](https://pubmed.ncbi.nlm.nih.gov/39363049/) | Interval breast cancer rates for tomosynthesis vs mammography population screening: a systematic review and meta-analysis of prospective studies. | 2,025 |
| [39423142](https://pubmed.ncbi.nlm.nih.gov/39423142/) | Validation of a breast cancer assay for radiotherapy omission: an individual participant data meta-analysis. | 2,025 |
| [39447849](https://pubmed.ncbi.nlm.nih.gov/39447849/) | Non-pharmacological Therapies for Depression in Women With Breast Cancer at Different Treatment Phases: A Systematic Review and Network Meta-Analysis. | 2,025 |
| [39521301](https://pubmed.ncbi.nlm.nih.gov/39521301/) | Vaginal estrogen use in breast cancer survivors: a systematic review and meta-analysis of recurrence and mortality risks. | 2,025 |
| [39538100](https://pubmed.ncbi.nlm.nih.gov/39538100/) | Society of Surgical Oncology Breast Disease Site Working Group Statement on Bilateral Risk-Reducing Mastectomy: Indications, Outcomes, and Risks. | 2,025 |
| [39602924](https://pubmed.ncbi.nlm.nih.gov/39602924/) | Meta-analysis and systematic review of long-term oncological safety of immediate breast reconstruction in patients with locally advanced breast cancer. | 2,025 |
| [39689274](https://pubmed.ncbi.nlm.nih.gov/39689274/) | Efficacy of Subsequent Treatments After Disease Progression on CDK4/6 Inhibitors in Patients With Hormone Receptor-Positive Advanced Breast Cancer. | 2,025 |
| [39690385](https://pubmed.ncbi.nlm.nih.gov/39690385/) | Magnetic Sentinel Lymph Node Biopsy in Early Breast Cancer Patients: An Individual Patient Data Meta-analysis of Tracer Uptake. | 2,025 |
| [39694886](https://pubmed.ncbi.nlm.nih.gov/39694886/) | Can structured integration of BI-RADS criteria by a clinical decision rule reduce the number of unnecessary biopsies in BI-RADS 4 lesions? A systematic review and meta-analysis. | 2,025 |
| [39702630](https://pubmed.ncbi.nlm.nih.gov/39702630/) | Methodological issues in radiomics: impact on accuracy of MRI for predicting response to neoadjuvant chemotherapy in breast cancer. | 2,025 |
| [39708443](https://pubmed.ncbi.nlm.nih.gov/39708443/) | Breast cancer patients with a pre-existing mental illness are less likely to receive guideline-recommended cancer treatment: A systematic review and meta-analysis. | 2,025 |
| [39755890](https://pubmed.ncbi.nlm.nih.gov/39755890/) | Short-term Patient-Reported Outcomes Following Bilateral Risk-Reducing Mastectomy for Patients at a High Risk for Breast Cancer: A Systematic Review. | 2,025 |
| [39757306](https://pubmed.ncbi.nlm.nih.gov/39757306/) | Physical prehabilitation in patients with breast cancer: a systematic review. | 2,025 |
| [39775978](https://pubmed.ncbi.nlm.nih.gov/39775978/) | Metabolic syndrome is associated with breast cancer mortality: A systematic review and meta-analysis. | 2,025 |
| [39800331](https://pubmed.ncbi.nlm.nih.gov/39800331/) | Modified Delphi Consensus on Interventions for Acute Radiation Dermatitis in Breast Cancer: A Canadian Expert Perspective. | 2,025 |
| [39847563](https://pubmed.ncbi.nlm.nih.gov/39847563/) | Post-traumatic growth experience of breast cancer patients: A qualitative systematic review and meta-synthesis. | 2,025 |
| [39878903](https://pubmed.ncbi.nlm.nih.gov/39878903/) | Diagnostic accuracy of node-RADS for the detection of lymph node invasion: a systematic review and meta-analysis. | 2,025 |
| [39879616](https://pubmed.ncbi.nlm.nih.gov/39879616/) | Impact of Online Interactive Decision Tools on Women's Decision-Making Regarding Breast Cancer Screening: Systematic Review and Meta-Analysis. | 2,025 |
| [39888906](https://pubmed.ncbi.nlm.nih.gov/39888906/) | Impact of digital breast tomosynthesis on screening performance and interval cancer rates compared to digital mammography: A meta-analysis. | 2,025 |
| [39907762](https://pubmed.ncbi.nlm.nih.gov/39907762/) | Deep learning-based breast cancer diagnosis in breast MRI: systematic review and meta-analysis. | 2,025 |
| [39937404](https://pubmed.ncbi.nlm.nih.gov/39937404/) | Disparities in Postmastectomy Breast Reconstruction Among American Indian and Alaska Native Women: A Systematic Literature Review and Meta-analysis. | 2,025 |
| [40053513](https://pubmed.ncbi.nlm.nih.gov/40053513/) | Advances in analytical approaches for background parenchymal enhancement in predicting breast tumor response to neoadjuvant chemotherapy: A systematic review. | 2,025 |
| [40067459](https://pubmed.ncbi.nlm.nih.gov/40067459/) | Head-to-Head comparison of [<sup>18</sup>F]FES and [<sup>18</sup>F]FDG PET/CT in breast cancer patients: has a new era come? | 2,025 |
| [40076535](https://pubmed.ncbi.nlm.nih.gov/40076535/) | Pertuzumab in Combination with Trastuzumab and Docetaxel as Adjuvant Doublet Therapy for HER2-Positive Breast Cancer: A Systematic Review. | 2,025 |
| [40081952](https://pubmed.ncbi.nlm.nih.gov/40081952/) | <sup>18</sup>F-Fluoroestradiol PET/CT for Predicting Benefit from Endocrine Therapy in Patients with Estrogen Receptor-Positive Breast Cancer: A Systematic Review and Metaanalysis. | 2,025 |
| [40112254](https://pubmed.ncbi.nlm.nih.gov/40112254/) | Effects of exercise on inflammation in female survivors of nonmetastatic breast cancer: a systematic review and meta-analysis. | 2,025 |
| [40156386](https://pubmed.ncbi.nlm.nih.gov/40156386/) | The Effect of Exercise on Quality of Life among Patients and Survivors of Breast Cancer: A Systematic Review and Meta-Analysis. | 2,025 |
| [40168922](https://pubmed.ncbi.nlm.nih.gov/40168922/) | Two-stage prepectoral breast reconstruction: A comprehensive review and meta-analysis. | 2,025 |
| [40272667](https://pubmed.ncbi.nlm.nih.gov/40272667/) | Positive Margin Rates After Breast-Conserving Surgery by Histologic Subtype: A Systematic Review and Meta-analysis Evaluating the Impact of Oncoplastic Surgery. | 2,025 |
| [40329031](https://pubmed.ncbi.nlm.nih.gov/40329031/) | Patient Navigation Increases Breast, Cervical, and Colorectal Cancer Screening Among Immigrants in the U.S.: A Systematic Review. | 2,025 |
| [40329882](https://pubmed.ncbi.nlm.nih.gov/40329882/) | A Meta-Analysis: Anti-Inflammatory Medicinal Plants for Age-Related Menopause-Like Symptoms and Psychological Problems in Breast Cancer and Healthy Perimenopausal Women. | 2,025 |
| [40332441](https://pubmed.ncbi.nlm.nih.gov/40332441/) | Tamoxifen and Fertility in Women with Breast Cancer: A Systematic Review on Reproductive Outcomes and Oncological Safety of Treatment Interruption. | 2,025 |
| [40333879](https://pubmed.ncbi.nlm.nih.gov/40333879/) | Evaluating the effects of e-health interventions on mental health outcomes in individuals with breast cancer: A systematic review. | 2,025 |
| [40334000](https://pubmed.ncbi.nlm.nih.gov/40334000/) | Animal models in preclinical metastatic breast cancer immunotherapy research: A systematic review and meta-analysis of efficacy outcomes. | 2,025 |
| [40341151](https://pubmed.ncbi.nlm.nih.gov/40341151/) | Survival status and predictors of mortality among patients with breast cancer in Ethiopia: a systematic review and meta-analysis. | 2,025 |
| [40348406](https://pubmed.ncbi.nlm.nih.gov/40348406/) | Cardiovascular morbidity and mortality after radiotherapy for breast cancer: a systematic review and meta-analysis. | 2,025 |
| [40373301](https://pubmed.ncbi.nlm.nih.gov/40373301/) | Challenges in Implementing Artificial Intelligence in Breast Cancer Screening Programs: Systematic Review and Framework for Safe Adoption. | 2,025 |
| [40403351](https://pubmed.ncbi.nlm.nih.gov/40403351/) | Immediate lymphovenous anastomosis is effective in preventing breast cancer-related lymphedema: A systematic review and meta-analysis. | 2,025 |
| [40403695](https://pubmed.ncbi.nlm.nih.gov/40403695/) | Impact of germline variants on breast and ovarian cancer risk in Japanese women: an original cohort study and meta-analysis. | 2,025 |
| [40423535](https://pubmed.ncbi.nlm.nih.gov/40423535/) | Impact of Background Parenchymal Enhancement on Diagnostic Performance of Breast MRI: A Systematic Review and Meta-Analysis. | 2,025 |
| [40489104](https://pubmed.ncbi.nlm.nih.gov/40489104/) | Patient Navigation Services for Breast and Cervical Cancer Screening and Follow-Up: A Meta-Analysis. | 2,025 |
| [40516884](https://pubmed.ncbi.nlm.nih.gov/40516884/) | Neoadjuvant radiotherapy and immediate breast reconstruction: A systematic review of literature of the last decade. | 2,025 |
| [40537089](https://pubmed.ncbi.nlm.nih.gov/40537089/) | Digital Behavior Change Interventions to Promote Physical Activity and Reduce Sedentary Behavior Among Survivors of Breast Cancer: Systematic Review and Meta-Analysis of Randomized Controlled Trials. | 2,025 |
| [40591899](https://pubmed.ncbi.nlm.nih.gov/40591899/) | Impact of Ethnicity on Breast Cancer Outcome: A Systematic Review and Meta-Analysis of Randomized Phase III Trials of the Last Decade. | 2,025 |
| [40675165](https://pubmed.ncbi.nlm.nih.gov/40675165/) | HER2DX and survival outcomes in early-stage HER2-positive breast cancer: an individual patient-level meta-analysis. | 2,025 |
| [40702198](https://pubmed.ncbi.nlm.nih.gov/40702198/) | Primary Breast Implant-Associated Squamous Cell Carcinoma: A Proposal for a Better Surgical Approach and Clinical Staging System Based on Tumour Characteristics. | 2,025 |
| [40724197](https://pubmed.ncbi.nlm.nih.gov/40724197/) | Breast Cancer Survivors' Perception on Health Promotion and Healthy Lifestyle: A Systematic Review and Qualitative Meta-Synthesis. | 2,025 |
| [40768680](https://pubmed.ncbi.nlm.nih.gov/40768680/) | Impact of <i>BRCA</i> Mutation on Treatment Outcomes of Endocrine Therapy ± CDK4/6 Inhibitors in Hormone Receptor-Positive/Human Epidermal Growth Factor Receptor-2-Negative Breast Cancer: A Systematic Review and Meta-Analysis. | 2,025 |
| [40781387](https://pubmed.ncbi.nlm.nih.gov/40781387/) | Feasibility and Efficacy of Decision Aids to Improve Decision-Making for Contralateral Prophylactic Mastectomy: A Systematic Review. | 2,025 |
| [40783288](https://pubmed.ncbi.nlm.nih.gov/40783288/) | Extending the duration of endocrine treatment for early breast cancer: patient-level meta-analysis of 12 randomised trials of aromatase inhibitors in 22 031 postmenopausal women already treated with at least 5 years of endocrine therapy. | 2,025 |
| [40829379](https://pubmed.ncbi.nlm.nih.gov/40829379/) | The effect of sarcopenia on postoperative complications in autologous breast reconstruction: A systematic review and meta-analysis. | 2,025 |
| [40862309](https://pubmed.ncbi.nlm.nih.gov/40862309/) | Efficacy of Immediate Lymphatic Reconstruction in Prevention of Breast Cancer-Related Lymphedema: A Systematic Review and Meta-Analysis. | 2,025 |
| [40886106](https://pubmed.ncbi.nlm.nih.gov/40886106/) | Implementing interventions to increase genetic testing for breast cancer among high-risk populations: A systematic review of implementation strategies, outcomes, and gaps. | 2,025 |
| [40889143](https://pubmed.ncbi.nlm.nih.gov/40889143/) | Mucoepidermoid Carcinoma of the Breast: A Systematic Review of Clinicopathologic, Immunohistochemical, and Molecular Features. | 2,025 |
| [40953336](https://pubmed.ncbi.nlm.nih.gov/40953336/) | Development and Validation of an Ipsilateral Breast Tumor Recurrence Risk Estimation Tool Incorporating Real-World Data and Evidence From Meta-Analyses: A Retrospective Multicenter Cohort Study. | 2,025 |
| [40953534](https://pubmed.ncbi.nlm.nih.gov/40953534/) | The impact of breast reconstruction compared with no reconstruction on breast cancer-related lymphedema: A systematic review and meta-analysis. | 2,025 |
| [41047282](https://pubmed.ncbi.nlm.nih.gov/41047282/) | Prevalence and characteristics of chronic pain following mastectomy and breast reconstruction: A systematic review and meta-analysis. | 2,025 |
| [41066869](https://pubmed.ncbi.nlm.nih.gov/41066869/) | Racial disparities in upper extremity functional outcomes in post-mastectomy and breast reconstruction patients: A systematic review. | 2,025 |
| [41096978](https://pubmed.ncbi.nlm.nih.gov/41096978/) | The Prognostic Power of miR-21 in Breast Cancer: A Systematic Review and Meta-Analysis. | 2,025 |
| [41118384](https://pubmed.ncbi.nlm.nih.gov/41118384/) | Prognostic value of FOXA1 in estrogen receptor-negative breast cancer: A systematic review and meta-analysis. | 2,025 |
| [41134830](https://pubmed.ncbi.nlm.nih.gov/41134830/) | Opioid-sparing anesthesia versus opioid-free anesthesia for postoperative recovery quality in breast cancer surgery patients: A systematic review and Bayesian network meta-analysis. | 2,025 |
| [41155194](https://pubmed.ncbi.nlm.nih.gov/41155194/) | Targeting Ferroptosis as the Achilles' Heel of Breast Cancer: Mechanisms and Therapeutic Opportunities from a Comprehensive Systematic Review. | 2,025 |
| [41155372](https://pubmed.ncbi.nlm.nih.gov/41155372/) | Cytokines and Brain-Derived Neurotrophic Factor as Biomarkers of Cognitive Impairment Related to Breast Cancer and Its Treatments: A Systematic Review. | 2,025 |
| [41206886](https://pubmed.ncbi.nlm.nih.gov/41206886/) | Cardiotoxic Effects of Antibody Drug Conjugates vs Standard Chemotherapy in ERBB2-Positive Advanced Breast Cancer: A Systematic Review and Meta-Analysis. | 2,025 |
| [41218942](https://pubmed.ncbi.nlm.nih.gov/41218942/) | Prognostic value of RANK signalling in breast cancer: a systematic review and meta-analysis. | 2,025 |
| [41226317](https://pubmed.ncbi.nlm.nih.gov/41226317/) | ERO1α as a Potential Drug Target for Breast Cancer: A Systematic Review of Current Evidence. | 2,025 |
| [41263891](https://pubmed.ncbi.nlm.nih.gov/41263891/) | Soft-Tissue Chest Wall Reconstruction for Secondary Angiosarcoma: Systematic Review and Case Series. | 2,025 |
| [41288190](https://pubmed.ncbi.nlm.nih.gov/41288190/) | Perception, Awareness, Knowledge, and Attitude (PAKA) Towards Breast Cancer in Ethiopia: A Systematic Review and Meta-Analysis. | 2,025 |
| [41296320](https://pubmed.ncbi.nlm.nih.gov/41296320/) | Impact of CDK4/6 inhibitors on health-related quality of life outcomes in patients with metastatic breast cancer: A systematic review and meta-analysis. | 2,025 |
| [41308675](https://pubmed.ncbi.nlm.nih.gov/41308675/) | Distant disease-free survival as a surrogate endpoint for overall survival in randomised trials of neoadjuvant therapy for early breast cancer: a pooled analysis of GBG and AGO-B Study Group trials. | 2,025 |
| [41418092](https://pubmed.ncbi.nlm.nih.gov/41418092/) | Health Informatics in Promoting Breast Cancer Screening: A Systematic Review of Benefits and Challenges. | 2,025 |
| [41475802](https://pubmed.ncbi.nlm.nih.gov/41475802/) | Performance of artificial intelligence in breast cancer screening programmes: a systematic review. | 2,025 |
| [41516250](https://pubmed.ncbi.nlm.nih.gov/41516250/) | Integrative Bioinformatic and Epidemiological Analysis of Acetaminophen Use and Risk of Sex Hormone-Related Cancers. | 2,025 |
| [37010460](https://pubmed.ncbi.nlm.nih.gov/37010460/) | Prevention of Postoperative Complications by Prepectoral versus Subpectoral Breast Reconstruction: A Systematic Review and Meta-Analysis. | 2,024 |
| [37615764](https://pubmed.ncbi.nlm.nih.gov/37615764/) | Diagnostic performance of MRI for assessing axillary lymph node status after neoadjuvant chemotherapy in breast cancer: a systematic review and meta-analysis. | 2,024 |
| [37890072](https://pubmed.ncbi.nlm.nih.gov/37890072/) | Postoperative complications and surgical outcomes of robotic versus conventional nipple-sparing mastectomy in breast cancer: meta-analysis. | 2,024 |
| [37909690](https://pubmed.ncbi.nlm.nih.gov/37909690/) | Salivary Gland Secretory Carcinoma; Review of 13 Years World-Wide Experience and Meta-Analysis. | 2,024 |
| [37943547](https://pubmed.ncbi.nlm.nih.gov/37943547/) | Global Stage Distribution of Breast Cancer at Diagnosis: A Systematic Review and Meta-Analysis. | 2,024 |
| [37949155](https://pubmed.ncbi.nlm.nih.gov/37949155/) | Artificial Intelligence-Driven Mammography-Based Future Breast Cancer Risk Prediction: A Systematic Review. | 2,024 |
| [37991190](https://pubmed.ncbi.nlm.nih.gov/37991190/) | Reducing re-excision rates in breast conserving surgery with Margin Probe: systematic review. | 2,024 |
| [37992580](https://pubmed.ncbi.nlm.nih.gov/37992580/) | In search of zebras: Critical analysis of the rarity of perineural breast cancer spread to the brachial plexus in men. | 2,024 |
| [38097484](https://pubmed.ncbi.nlm.nih.gov/38097484/) | Indocyanine green fluorescence versus blue dye, technetium-99M, and the dual-marker combination of technetium-99M + blue dye for sentinel lymph node detection in early breast cancer-meta-analysis including consistency analysis. | 2,024 |
| [38159475](https://pubmed.ncbi.nlm.nih.gov/38159475/) | Oncoplastic reduction mammoplasty: Systematic review and proportional meta-analysis of surgical outcomes. | 2,024 |
| [38181009](https://pubmed.ncbi.nlm.nih.gov/38181009/) | Exploring the experiences of women living with metastatic breast cancer [MBC]: A systematic review of qualitative evidence. | 2,024 |
| [38195030](https://pubmed.ncbi.nlm.nih.gov/38195030/) | Immunotherapy and Radiation Therapy Sequencing in Breast Cancer: A Systematic Review. | 2,024 |
| [38195101](https://pubmed.ncbi.nlm.nih.gov/38195101/) | Patient-reported Outcomes Utilizing the BREAST-Q Questionnaire After Breast-Conserving Surgery With and Without Oncoplastic Breast Surgery: A Systematic Review and Meta-analysis. | 2,024 |
| [38199928](https://pubmed.ncbi.nlm.nih.gov/38199928/) | The analgesic effectiveness of perioperative lidocaine infusions for acute and chronic persistent postsurgical pain in patients undergoing breast cancer surgery: a systematic review and meta-analysis. | 2,024 |
| [38212842](https://pubmed.ncbi.nlm.nih.gov/38212842/) | A network meta-analysis of efficacy and safety for first-line and second/further-line therapies in postmenopausal women with hormone receptor-positive, HER2-negative, advanced breast cancer. | 2,024 |
| [38232225](https://pubmed.ncbi.nlm.nih.gov/38232225/) | Patient Decision Aids for Breast Cancer Reconstruction: A Systematic Review and Network Meta-Analysis of Randomized Controlled Trials. | 2,024 |
| [38255807](https://pubmed.ncbi.nlm.nih.gov/38255807/) | Hormone, Targeted, and Combinational Therapies for Breast Cancers: From Humans to Dogs. | 2,024 |
| [38307034](https://pubmed.ncbi.nlm.nih.gov/38307034/) | Breast Implants and the Risk of Squamous Cell Carcinoma of the Breast: A Systematic Literature Review and Epidemiologic Study. | 2,024 |
| [38307616](https://pubmed.ncbi.nlm.nih.gov/38307616/) | Explainable machine learning for breast cancer diagnosis from mammography and ultrasound images: a systematic review. | 2,024 |
| [38315143](https://pubmed.ncbi.nlm.nih.gov/38315143/) | Outcomes of Immediate versus Delayed Autologous Reconstruction with Postmastectomy Radiation: A Meta-Analysis. | 2,024 |
| [38334760](https://pubmed.ncbi.nlm.nih.gov/38334760/) | Association of peritumoral region features assessed on breast MRI and prognosis of breast cancer: a systematic review and meta-analysis. | 2,024 |
| [38353413](https://pubmed.ncbi.nlm.nih.gov/38353413/) | Application of TiLOOP bra in implant-based breast reconstruction is associated with decreased complication risk compared with other meshes: A systematic review and meta-analysis. | 2,024 |
| [38445713](https://pubmed.ncbi.nlm.nih.gov/38445713/) | The unique risk factor profile of triple-negative breast cancer: a comprehensive meta-analysis. | 2,024 |
| [38451995](https://pubmed.ncbi.nlm.nih.gov/38451995/) | Aspects to consider regarding breast cancer risk in trans men: A systematic review and risk management approach. | 2,024 |
| [38452109](https://pubmed.ncbi.nlm.nih.gov/38452109/) | Awareness regarding breast cancer amongst women in Pakistan: A systematic review and meta-analysis. | 2,024 |
| [38470816](https://pubmed.ncbi.nlm.nih.gov/38470816/) | Free Tissue Transfer for Reconstruction After Bilateral Skin Sparing Mastectomy-A Systematic Review. | 2,024 |
| [38473804](https://pubmed.ncbi.nlm.nih.gov/38473804/) | Unraveling Biomarker Signatures in Triple-Negative Breast Cancer: A Systematic Review for Targeted Approaches. | 2,024 |
| [38474119](https://pubmed.ncbi.nlm.nih.gov/38474119/) | From Case Reports to Molecular Insight: Examining the Outcomes and Underlying Mechanisms of Squamous Cell Carcinoma in Breast Implant Patients-A Systematic Review. | 2,024 |
| [38512492](https://pubmed.ncbi.nlm.nih.gov/38512492/) | The diagnostic performance of ultrafast MRI to differentiate benign from malignant breast lesions: a systematic review and meta-analysis. | 2,024 |
| [38531689](https://pubmed.ncbi.nlm.nih.gov/38531689/) | Systematic review of targeted axillary dissection in node-positive breast cancer treated with neoadjuvant systemic therapy: variation in type of marker and timing of placement. | 2,024 |
| [38542225](https://pubmed.ncbi.nlm.nih.gov/38542225/) | Efficacy of Cold Atmospheric Plasma vs. Chemotherapy in Triple-Negative Breast Cancer: A Systematic Review. | 2,024 |
| [38614852](https://pubmed.ncbi.nlm.nih.gov/38614852/) | Hypofractionation for Regional Nodal Irradiation in Breast Cancer: Best of Both the Worlds. | 2,024 |
| [38663835](https://pubmed.ncbi.nlm.nih.gov/38663835/) | Disparities in Study Inclusion and Breast Cancer Screening Rates Among Transgender People: A Systematic Review. | 2,024 |
| [38684135](https://pubmed.ncbi.nlm.nih.gov/38684135/) | Comparative Effects of Exercise Interventions and Mindfulness-Based Interventions for Cognitive Impairment and Quality of Life in Breast Cancer Survivors During or After Cancer Treatment: A Systematic Review and Bayesian Network Meta-analysis. | 2,024 |
| [38687490](https://pubmed.ncbi.nlm.nih.gov/38687490/) | Screening for Breast Cancer: Evidence Report and Systematic Review for the US Preventive Services Task Force. | 2,024 |
| [38700543](https://pubmed.ncbi.nlm.nih.gov/38700543/) | Complications After Prepectoral Versus Subpectoral Breast Reconstruction in Patients Receiving Postmastectomy Radiation Therapy: A Systematic Review and Meta-Analysis. | 2,024 |
| [38710001](https://pubmed.ncbi.nlm.nih.gov/38710001/) | Mapping the Evidence on the Impact of mHealth Interventions on Patient-Reported Outcomes in Patients With Breast Cancer: A Systematic Review. | 2,024 |
| [38743426](https://pubmed.ncbi.nlm.nih.gov/38743426/) | Survival Patterns Among Patients With Breast Cancer in Sub-Saharan Africa: A Systematic Review and Meta-Analysis. | 2,024 |
| [38771179](https://pubmed.ncbi.nlm.nih.gov/38771179/) | Performance of Diffusion-weighted Imaging-based Noncontrast MRI Protocols for Diagnosis of Breast Cancer: A Systematic Review and Meta-Analysis. | 2,024 |
| [38776625](https://pubmed.ncbi.nlm.nih.gov/38776625/) | Contributors to post-operative venous thromboembolism risk after breast cancer surgery: A systematic review and meta-analysis. | 2,024 |
| [38781221](https://pubmed.ncbi.nlm.nih.gov/38781221/) | Anthracycline-induced arrhythmias in breast cancer therapy: A meta-analysis of single-arm trials. | 2,024 |
| [38791506](https://pubmed.ncbi.nlm.nih.gov/38791506/) | Plant-Based HSP90 Inhibitors in Breast Cancer Models: A Systematic Review. | 2,024 |
| [38801441](https://pubmed.ncbi.nlm.nih.gov/38801441/) | Predictive value of pretreatment circulating inflammatory response markers in the neoadjuvant treatment of breast cancer: meta-analysis. | 2,024 |
| [38820391](https://pubmed.ncbi.nlm.nih.gov/38820391/) | Diagnostic performance of ultrasound-based artificial intelligence for predicting key molecular markers in breast cancer: A systematic review and meta-analysis. | 2,024 |
| [38876292](https://pubmed.ncbi.nlm.nih.gov/38876292/) | Breast and Cervical Cancer Screenings: A Systematic Economic Review of Patient Navigation Services. | 2,024 |
| [38959209](https://pubmed.ncbi.nlm.nih.gov/38959209/) | Effects of different exercise types and cycles on pain and quality of life in breast cancer patients: A systematic review and network meta-analysis. | 2,024 |
| [39028716](https://pubmed.ncbi.nlm.nih.gov/39028716/) | Effects of mindfulness-based stress reduction on quality of life of breast cancer patient: A systematic review and meta-analysis. | 2,024 |
| [39028722](https://pubmed.ncbi.nlm.nih.gov/39028722/) | Late-stage diagnosis: The driving force behind high breast cancer mortality in Ethiopia: A systematic review and meta-analysis. | 2,024 |
| [39041867](https://pubmed.ncbi.nlm.nih.gov/39041867/) | Clinical and Genomic Risk for Late Breast Cancer Recurrence and Survival. | 2,024 |
| [39052945](https://pubmed.ncbi.nlm.nih.gov/39052945/) | Oncoplastic Breast-Conserving Surgery in African Women: A Systematic Review. | 2,024 |
| [39075505](https://pubmed.ncbi.nlm.nih.gov/39075505/) | An original study assessing biomarker success rate in breast cancer recurrence biomarker research. | 2,024 |
| [39106546](https://pubmed.ncbi.nlm.nih.gov/39106546/) | Pre-operative chemoradiotherapy followed by mastectomy and breast reconstruction-A systematic review of clinical, oncological, reconstructive and aesthetic outcomes. | 2,024 |
| [39110196](https://pubmed.ncbi.nlm.nih.gov/39110196/) | The impact of PET imaging on triple negative breast cancer: an updated evidence-based perspective. | 2,024 |
| [39125951](https://pubmed.ncbi.nlm.nih.gov/39125951/) | The "Forgotten" Subtypes of Breast Carcinoma: A Systematic Review of Selected Histological Variants Not Included or Not Recognized as Distinct Entities in the Current World Health Organization Classification of Breast Tumors. | 2,024 |
| [39207778](https://pubmed.ncbi.nlm.nih.gov/39207778/) | Neoadjuvant Immune Checkpoint Inhibitors Plus Chemotherapy in Early Breast Cancer: A Systematic Review and Meta-Analysis. | 2,024 |
| [39231551](https://pubmed.ncbi.nlm.nih.gov/39231551/) | Meta-analysis and systematic review of the diagnostic value of contrast-enhanced spectral mammography for the detection of breast cancer. | 2,024 |
| [39235812](https://pubmed.ncbi.nlm.nih.gov/39235812/) | Circulating Tumor DNA and Survival in Metastatic Breast Cancer: A Systematic Review and Meta-Analysis. | 2,024 |
| [39260879](https://pubmed.ncbi.nlm.nih.gov/39260879/) | Randomised controlled trials on radiation dose fractionation in breast cancer: systematic review and meta-analysis with emphasis on side effects and cosmesis. | 2,024 |
| [39288352](https://pubmed.ncbi.nlm.nih.gov/39288352/) | Racial Differences in Breast Cancer Survival Between Black and White Women According to Tumor Subtype: A Systematic Review and Meta-Analysis. | 2,024 |
| [39327054](https://pubmed.ncbi.nlm.nih.gov/39327054/) | Prevalence and associated factors of psychological distress among patients with breast cancer: a systematic review and meta-analysis. | 2,024 |
| [39370318](https://pubmed.ncbi.nlm.nih.gov/39370318/) | Surgical treatments for older breast cancer patients: A systematic review and meta-analysis of real-world evidence. | 2,024 |
| [39395669](https://pubmed.ncbi.nlm.nih.gov/39395669/) | The Assisi think tank focus review on postoperative radiation for lobular breast cancer. | 2,024 |
| [39467209](https://pubmed.ncbi.nlm.nih.gov/39467209/) | The Effectiveness of Cognitive Behavioral Therapy on Depression and Anxiety Symptoms in Breast Cancer Patients and Survivors: A Systematic Review of Interventional Studies. | 2,024 |
| [39488422](https://pubmed.ncbi.nlm.nih.gov/39488422/) | Breast cancer and its determinants in Ethiopia: a systematic review and meta-analysis. | 2,024 |
| [39518965](https://pubmed.ncbi.nlm.nih.gov/39518965/) | Diagnostic Performance of Prostate-Specific Membrane Antigen-Targeted Positron Emission Tomography in Patients Diagnosed with Different Types of Breast Cancer: A Systematic Review. | 2,024 |
| [39527621](https://pubmed.ncbi.nlm.nih.gov/39527621/) | Delayed presentation of breast cancer patients and contributing factors in East Africa: Systematic review and meta-analysis. | 2,024 |
| [39536544](https://pubmed.ncbi.nlm.nih.gov/39536544/) | Comparison of outcomes following postmastectomy radiation therapy in patients with autologous free flap reconstruction depending on the radiation therapy protocol: Systematic review and meta-analysis. | 2,024 |
| [39571108](https://pubmed.ncbi.nlm.nih.gov/39571108/) | Timeliness of Breast Cancer Patients' Presentation to Health Care Facilities in Ethiopia: A Systematic Review and Meta-Analysis. | 2,024 |
| [39625963](https://pubmed.ncbi.nlm.nih.gov/39625963/) | Diagnostic performance of DCE-MRI radiomics in predicting axillary lymph node metastasis in breast cancer patients: A meta-analysis. | 2,024 |
| [39636922](https://pubmed.ncbi.nlm.nih.gov/39636922/) | Investigating the relationship between insulin use and all-cause mortality, breast cancer mortality, and recurrence risk in diabetic patients with breast cancer: A comprehensive systematic review and meta-analysis. | 2,024 |
| [39666634](https://pubmed.ncbi.nlm.nih.gov/39666634/) | HER2-low prevalence among Hispanic/Latino women with breast cancer: A systematic review and meta-analysis. | 2,024 |
| [39796103](https://pubmed.ncbi.nlm.nih.gov/39796103/) | Antiproliferative Mechanisms of Metformin in Breast Cancer: A Systematic Review of the Literature. | 2,024 |
| [35946806](https://pubmed.ncbi.nlm.nih.gov/35946806/) | Impact of Axillary Lymph Node Dissection and Sentinel Lymph Node Biopsy on Upper Limb Morbidity in Breast Cancer Patients: A Systematic Review and Meta-Analysis. | 2,023 |
| [36155214](https://pubmed.ncbi.nlm.nih.gov/36155214/) | A Meta-Analysis of Trials of Partial Breast Irradiation. | 2,023 |
| [36310323](https://pubmed.ncbi.nlm.nih.gov/36310323/) | A Systematic Review and Meta-analysis of Touch Imprint Cytology and Frozen Section Biopsy and Their Comparison for Evaluation of Sentinel Lymph Node in Breast Cancer. | 2,023 |
| [36441968](https://pubmed.ncbi.nlm.nih.gov/36441968/) | BIA-ALCL Epidemiological Findings From a Retrospective Study of 248 Cases Extracted From Relevant Case Reports and Series: A Systematic Review. | 2,023 |
| [36455167](https://pubmed.ncbi.nlm.nih.gov/36455167/) | Reassessing the Benefits and Harms of Risk-Reducing Medication Considering the Persistent Risk of Breast Cancer Mortality in Estrogen Receptor-Positive Breast Cancer. | 2,023 |
| [36512473](https://pubmed.ncbi.nlm.nih.gov/36512473/) | Long-term survival in patients with node-positive breast cancer who undergo sentinel lymph node biopsy alone after neoadjuvant chemotherapy: meta-analysis. | 2,023 |
| [36534108](https://pubmed.ncbi.nlm.nih.gov/36534108/) | The Impact of Exogenous Testosterone on Breast Cancer Risk in Transmasculine Individuals. | 2,023 |
| [36534109](https://pubmed.ncbi.nlm.nih.gov/36534109/) | Oncologic Safety in Autologous Fat Grafting After Breast Conservation Therapy: A Systematic Review and Meta-analysis of the Literature. | 2,023 |
| [36549594](https://pubmed.ncbi.nlm.nih.gov/36549594/) | Informational needs of individuals from families harboring BRCA pathogenic variants: A systematic review and content analysis. | 2,023 |
| [36560842](https://pubmed.ncbi.nlm.nih.gov/36560842/) | Evolution and refinement of magnetically guided sentinel lymph node detection in breast cancer: meta-analysis. | 2,023 |
| [36580704](https://pubmed.ncbi.nlm.nih.gov/36580704/) | Use of free flaps in aesthetic breast surgery: a single centre experience and literature review. | 2,023 |
| [36592995](https://pubmed.ncbi.nlm.nih.gov/36592995/) | Effect of cognitive training on patients with breast cancer reporting cognitive changes: a systematic review and meta-analysis. | 2,023 |
| [36621238](https://pubmed.ncbi.nlm.nih.gov/36621238/) | Implant vs. autologous tissue-based breast reconstruction: A systematic review and meta-analysis of the studies comparing surgical approaches in 55,455 patients. | 2,023 |
| [36662756](https://pubmed.ncbi.nlm.nih.gov/36662756/) | Low pretreatment prognostic nutritional index predicts poor survival in breast cancer patients: A meta-analysis. | 2,023 |
| [36674436](https://pubmed.ncbi.nlm.nih.gov/36674436/) | Impact of Physical Rehabilitation on Bone Biomarkers in Non-Metastatic Breast Cancer Women: A Systematic Review and Meta-Analysis. | 2,023 |
| [36718056](https://pubmed.ncbi.nlm.nih.gov/36718056/) | Revisiting primary endocrine therapy versus surgery in older women with breast cancer: meta-analysis. | 2,023 |
| [36719288](https://pubmed.ncbi.nlm.nih.gov/36719288/) | Supplemental Breast Cancer Screening in Women with Dense Breasts and Negative Mammography: A Systematic Review and Meta-Analysis. | 2,023 |
| [36725152](https://pubmed.ncbi.nlm.nih.gov/36725152/) | Defining genomic, transcriptomic, proteomic, epigenetic, and phenotypic biomarkers with prognostic capability in male breast cancer: a systematic review. | 2,023 |
| [36728484](https://pubmed.ncbi.nlm.nih.gov/36728484/) | Quality of Life and Complications after Nipple- versus Skin-Sparing Mastectomy followed by Immediate Breast Reconstruction: A Systematic Review and Meta-Analysis. | 2,023 |
| [36729428](https://pubmed.ncbi.nlm.nih.gov/36729428/) | Tranexamic Acid Use in Breast Surgery: A Systematic Review and Meta-Analysis. | 2,023 |
| [36729988](https://pubmed.ncbi.nlm.nih.gov/36729988/) | Immediate Breast Cancer Reconstruction with or without Dermal Matrix or Synthetic Mesh Support: A Review and Network Meta-Analysis. | 2,023 |
| [36745761](https://pubmed.ncbi.nlm.nih.gov/36745761/) | Reporting on Race and Racial Disparities in Breast Cancer: The Neglect of Racism as a Driver of Inequitable Care. | 2,023 |
| [36753274](https://pubmed.ncbi.nlm.nih.gov/36753274/) | Financial Toxicity Among Patients With Breast Cancer Worldwide: A Systematic Review and Meta-analysis. | 2,023 |
| [36769287](https://pubmed.ncbi.nlm.nih.gov/36769287/) | Triple-Negative Breast Cancer and Predictive Markers of Response to Neoadjuvant Chemotherapy: A Systematic Review. | 2,023 |
| [36795990](https://pubmed.ncbi.nlm.nih.gov/36795990/) | Access to Radiation Therapy and Related Clinical Outcomes in Patients With Cervical and Breast Cancer Across Sub-Saharan Africa: A Systematic Review. | 2,023 |
| [36821108](https://pubmed.ncbi.nlm.nih.gov/36821108/) | Risk Prediction Models for Cardiotoxicity of Chemotherapy Among Patients With Breast Cancer: A Systematic Review. | 2,023 |
| [36834998](https://pubmed.ncbi.nlm.nih.gov/36834998/) | <i>HER2</i> Amplification Level Predicts Pathological Complete Response in the Neoadjuvant Setting of HER2-Overexpressing Breast Cancer: A Meta-Analysis and Systematic Review. | 2,023 |
| [36835336](https://pubmed.ncbi.nlm.nih.gov/36835336/) | An Epidemiological Systematic Review with Meta-Analysis on Biomarker Role of Circulating MicroRNAs in Breast Cancer Incidence. | 2,023 |
| [36868521](https://pubmed.ncbi.nlm.nih.gov/36868521/) | Proton Beam Therapy for Early Breast Cancer: A Systematic Review and Meta-analysis of Clinical Outcomes. | 2,023 |
| [36888929](https://pubmed.ncbi.nlm.nih.gov/36888929/) | Clinicopathologic Features of Breast Cancer in Egypt-Contemporary Profile and Future Needs: A Systematic Review and Meta-Analysis. | 2,023 |
| [36943819](https://pubmed.ncbi.nlm.nih.gov/36943819/) | Combined and progestagen-only hormonal contraceptives and breast cancer risk: A UK nested case-control study and meta-analysis. | 2,023 |
| [36965520](https://pubmed.ncbi.nlm.nih.gov/36965520/) | Economic evaluation of exercise interventions for individuals with cancer: A systematic review. | 2,023 |
| [36975095](https://pubmed.ncbi.nlm.nih.gov/36975095/) | Examination of Outcome Disparities in Reports of Prepectoral and Subpectoral Direct-to-Implant Reconstruction: A Systematic Review and Meta-analysis. | 2,023 |
| [36988359](https://pubmed.ncbi.nlm.nih.gov/36988359/) | Postoperative Analgesic Effects of Serratus Anterior Plane Block for Thoracic and Breast Surgery: A Meta-analysis of Randomized Controlled Trials. | 2,023 |
| [36995174](https://pubmed.ncbi.nlm.nih.gov/36995174/) | The Effects of Tranexamic Acid in Breast Surgery: A Systematic Review and Meta-Analysis. | 2,023 |
| [37020070](https://pubmed.ncbi.nlm.nih.gov/37020070/) | Imaging findings for response evaluation of ductal carcinoma in situ in breast cancer patients treated with neoadjuvant systemic therapy: a systematic review and meta-analysis. | 2,023 |
| [37022714](https://pubmed.ncbi.nlm.nih.gov/37022714/) | Long-term Mortality in Individuals Diagnosed With Cancer During Pregnancy or Postpartum. | 2,023 |
| [37059410](https://pubmed.ncbi.nlm.nih.gov/37059410/) | Quality of life after risk-reducing surgery for breast and ovarian cancer prevention: a systematic review and meta-analysis. | 2,023 |
| [37061269](https://pubmed.ncbi.nlm.nih.gov/37061269/) | Anthracycline-containing and taxane-containing chemotherapy for early-stage operable breast cancer: a patient-level meta-analysis of 100 000 women from 86 randomised trials. | 2,023 |
| [37079635](https://pubmed.ncbi.nlm.nih.gov/37079635/) | Home-based exercise improves quality of life in breast and prostate cancer survivors: A meta-analysis. | 2,023 |
| [37108278](https://pubmed.ncbi.nlm.nih.gov/37108278/) | Assessing the Role of MicroRNAs in Predicting Breast Cancer Recurrence-A Systematic Review. | 2,023 |
| [37143087](https://pubmed.ncbi.nlm.nih.gov/37143087/) | Investigating the relationship between depression and breast cancer: observational and genetic analyses. | 2,023 |
| [37146317](https://pubmed.ncbi.nlm.nih.gov/37146317/) | Comparing the Outcomes and Complication Rates of Biologic vs Synthetic Meshes in Implant-Based Breast Reconstruction: A Systematic Review. | 2,023 |
| [37164006](https://pubmed.ncbi.nlm.nih.gov/37164006/) | A joint transcriptome-wide association study across multiple tissues identifies candidate breast cancer susceptibility genes. | 2,023 |
| [37164379](https://pubmed.ncbi.nlm.nih.gov/37164379/) | Development and internal-external validation of statistical and machine learning models for breast cancer prognostication: cohort study. | 2,023 |
| [37165852](https://pubmed.ncbi.nlm.nih.gov/37165852/) | Flap perfusion assessment with indocyanine green angiography in deep inferior epigastric perforator flap breast reconstruction: A systematic review and meta-analysis. | 2,023 |
| [37170778](https://pubmed.ncbi.nlm.nih.gov/37170778/) | The Clinical Benefits of Antiresorptive Agents in Patients with Primary Breast Cancer Receiving Adjuvant Endocrine Therapy: A Systematic Review with Pairwise and Network Meta-analysis. | 2,023 |
| [37175974](https://pubmed.ncbi.nlm.nih.gov/37175974/) | MicroRNA Dysregulation in Early Breast Cancer Diagnosis: A Systematic Review and Meta-Analysis. | 2,023 |
| [37182249](https://pubmed.ncbi.nlm.nih.gov/37182249/) | The effect of chemotherapy on the complication rates of breast reconstruction: A systematic review and meta-analysis. | 2,023 |
| [37204936](https://pubmed.ncbi.nlm.nih.gov/37204936/) | Effect of Exercise Therapy on Cancer-Related Fatigue in Patients With Breast Cancer: A Systematic Review and Network Meta-analysis. | 2,023 |
| [37219445](https://pubmed.ncbi.nlm.nih.gov/37219445/) | Standalone AI for Breast Cancer Detection at Screening Digital Mammography and Digital Breast Tomosynthesis: A Systematic Review and Meta-Analysis. | 2,023 |
| [37227406](https://pubmed.ncbi.nlm.nih.gov/37227406/) | A Systematic Review and Meta-Analysis Comparing the Clinical Outcomes of Profunda Artery Perforator Versus Gracilis Thigh Flap as a Second Choice for Autologous Breast Reconstruction. | 2,023 |
| [37249632](https://pubmed.ncbi.nlm.nih.gov/37249632/) | Can Axillary Lymph Node Dissection be Omitted in Breast Cancer Patients with Metastatic Sentinel Lymph Nodes Undergoing Mastectomy? A Systematic Review and Meta-Analysis of Real-World Evidence. | 2,023 |
| [37279001](https://pubmed.ncbi.nlm.nih.gov/37279001/) | Outcomes of Different Quality of Life Assessment Modalities After Breast Cancer Therapy: A Network Meta-analysis. | 2,023 |
| [37289549](https://pubmed.ncbi.nlm.nih.gov/37289549/) | Partial breast irradiation compared with whole breast irradiation: a systematic review and meta-analysis. | 2,023 |
| [37303228](https://pubmed.ncbi.nlm.nih.gov/37303228/) | Human Epidermal Growth Factor Receptor 2 Testing in Breast Cancer. | 2,023 |
| [37309215](https://pubmed.ncbi.nlm.nih.gov/37309215/) | Adherence to the 2018 World Cancer Research Fund/American Institute for Cancer Research Cancer Prevention Recommendations and cancer risk: A systematic review and meta-analysis. | 2,023 |
| [37310128](https://pubmed.ncbi.nlm.nih.gov/37310128/) | Oncoplastic breast surgery in older women with primary breast cancer: systematic review. | 2,023 |
| [37310426](https://pubmed.ncbi.nlm.nih.gov/37310426/) | <sup>99m</sup>Tc-Tilmanocept performance for sentinel node mapping in breast cancer, melanoma, and head and neck cancer: a systematic review and meta-analysis from a European expert panel. | 2,023 |
| [37326990](https://pubmed.ncbi.nlm.nih.gov/37326990/) | The Association Between Meningioma and Breast Cancer: A Systematic Review and Meta-analysis. | 2,023 |
| [37329748](https://pubmed.ncbi.nlm.nih.gov/37329748/) | Inferior gluteal artery perforator (IGAP) flap in autologous breast reconstruction: A proportional meta-analysis of surgical outcomes. | 2,023 |
| [37329749](https://pubmed.ncbi.nlm.nih.gov/37329749/) | Direct-to-implant versus autologous tissue transfer: A meta-analysis of patient-reported outcomes after immediate breast reconstruction. | 2,023 |
| [37340792](https://pubmed.ncbi.nlm.nih.gov/37340792/) | Differential treatment effect between younger and older adults for new cancer therapies in solid tumors supporting US Food and Drug Administration approval between 2010 and 2021. | 2,023 |
| [37373130](https://pubmed.ncbi.nlm.nih.gov/37373130/) | The Role of Cocaine- and Amphetamine-Regulated Transcript (CART) in Cancer: A Systematic Review. | 2,023 |
| [37399487](https://pubmed.ncbi.nlm.nih.gov/37399487/) | A Systematic Review of the Impact of Patient Factors on BREAST-Q Outcomes After Reduction Mammoplasty. | 2,023 |
| [37400822](https://pubmed.ncbi.nlm.nih.gov/37400822/) | Family history and breast cancer risk for Asian women: a systematic review and meta-analysis. | 2,023 |
| [37437610](https://pubmed.ncbi.nlm.nih.gov/37437610/) | Safety profile of trastuzumab-emtansine (T-DM1) with concurrent radiation therapy: A systematic review and meta-analysis. | 2,023 |
| [37439225](https://pubmed.ncbi.nlm.nih.gov/37439225/) | A Systematic Review of Outcomes and Complications of Tuberous Breast Surgery. | 2,023 |
| [37449874](https://pubmed.ncbi.nlm.nih.gov/37449874/) | ENIGMA CHEK2gether Project: A Comprehensive Study Identifies Functionally Impaired CHEK2 Germline Missense Variants Associated with Increased Breast Cancer Risk. | 2,023 |
| [37482660](https://pubmed.ncbi.nlm.nih.gov/37482660/) | The Application of 18 F-FES PET in Clinical Cancer Care : A Systematic Review. | 2,023 |
| [37494111](https://pubmed.ncbi.nlm.nih.gov/37494111/) | Mobile Apps and Quality of Life in Patients With Breast Cancer and Survivors: Systematic Literature Review. | 2,023 |
| [37494393](https://pubmed.ncbi.nlm.nih.gov/37494393/) | Global depression in breast cancer patients: Systematic review and meta-analysis. | 2,023 |
| [37531593](https://pubmed.ncbi.nlm.nih.gov/37531593/) | A Systematic Review and Meta-Analysis of Interventions to Promote Adjuvant Endocrine Therapy Adherence Among Breast Cancer Survivors. | 2,023 |
| [37536192](https://pubmed.ncbi.nlm.nih.gov/37536192/) | Perioperative protocols in ambulatory breast reconstruction: A systematic review. | 2,023 |
| [37536378](https://pubmed.ncbi.nlm.nih.gov/37536378/) | Safety and feasibility of CDK4/6 inhibitors treatment combined with radiotherapy in patients with HR-positive/HER2-negative breast cancer. A systematic review and meta-analysis. | 2,023 |
| [37566789](https://pubmed.ncbi.nlm.nih.gov/37566789/) | Evolution of Breast Cancer Recurrence Risk Prediction: A Systematic Review of Statistical and Machine Learning-Based Models. | 2,023 |
| [37616552](https://pubmed.ncbi.nlm.nih.gov/37616552/) | Epidemiology of Breast Implant-Associated Anaplastic Large Cell Lymphoma in the United States: A Systematic Review. | 2,023 |
| [37625895](https://pubmed.ncbi.nlm.nih.gov/37625895/) | Predicting 10-year breast cancer mortality risk in the general female population in England: a model development and validation study. | 2,023 |
| [37666057](https://pubmed.ncbi.nlm.nih.gov/37666057/) | Breast implant capsule-associated squamous cell carcinoma: A systematic review and individual patient data meta-analysis. | 2,023 |
| [37682691](https://pubmed.ncbi.nlm.nih.gov/37682691/) | Oncologic outcomes after breast-conserving surgery with radiotherapy versus mastectomy in patients with Paget's disease of the breast: systematic review and meta-analysis. | 2,023 |
| [37698273](https://pubmed.ncbi.nlm.nih.gov/37698273/) | A rapid review of COVID-19's global impact on breast cancer screening participation rates and volumes from January to December 2020. | 2,023 |
| [37716248](https://pubmed.ncbi.nlm.nih.gov/37716248/) | Less is more? One-stage versus two-stage implant-based breast reconstruction: A systematic review and meta-analysis of comparative studies. | 2,023 |
| [37716255](https://pubmed.ncbi.nlm.nih.gov/37716255/) | Immediate post-mastectomy prepectoral breast reconstruction with animal derived acellular dermal matrices: A systematic review. | 2,023 |
| [37788151](https://pubmed.ncbi.nlm.nih.gov/37788151/) | What are the most effective exercise, physical activity and dietary interventions to improve body composition in women diagnosed with or at high-risk of breast cancer? A systematic review and network meta-analysis. | 2,023 |
| [37793198](https://pubmed.ncbi.nlm.nih.gov/37793198/) | Do we need acellular dermal matrix in prepectoral breast reconstruction? A systematic review and meta-analysis. | 2,023 |
| [37797375](https://pubmed.ncbi.nlm.nih.gov/37797375/) | Timing of autologous fat grafting in implant-based breast reconstruction: Best practices based on systematic review and meta-analysis. | 2,023 |
| [37804643](https://pubmed.ncbi.nlm.nih.gov/37804643/) | The impact of neoadjuvant chemotherapy on surgical outcomes following autologous and implant-based immediate breast reconstruction: A systematic review and meta-analysis. | 2,023 |
| [37817217](https://pubmed.ncbi.nlm.nih.gov/37817217/) | Causal association between inflammatory bowel disease and 32 site-specific extracolonic cancers: a Mendelian randomization study. | 2,023 |
| [37894794](https://pubmed.ncbi.nlm.nih.gov/37894794/) | Identifying MicroRNAs Suitable for Detection of Breast Cancer: A Systematic Review of Discovery Phases Studies on MicroRNA Expression Profiles. | 2,023 |
| [37931633](https://pubmed.ncbi.nlm.nih.gov/37931633/) | Radiotherapy to regional nodes in early breast cancer: an individual patient data meta-analysis of 14 324 women in 16 trials. | 2,023 |
| [37958677](https://pubmed.ncbi.nlm.nih.gov/37958677/) | miRNAs in the Box: Potential Diagnostic Role for Extracellular Vesicle-Packaged miRNA-27a and miRNA-128 in Breast Cancer. | 2,023 |
| [37996220](https://pubmed.ncbi.nlm.nih.gov/37996220/) | Prognostic significance of platelet-to-lymphocyte ratio (PLR) in patients with breast cancer treated with neoadjuvant chemotherapy: a meta-analysis. | 2,023 |
| [38003690](https://pubmed.ncbi.nlm.nih.gov/38003690/) | Reverse Onco-Cardiology: What Is the Evidence for Breast Cancer? A Systematic Review of the Literature. | 2,023 |
| [38033281](https://pubmed.ncbi.nlm.nih.gov/38033281/) | Smartphone-Based Passive Sensing in Monitoring Patients With Cancer: A Systematic Review. | 2,023 |
| [38085036](https://pubmed.ncbi.nlm.nih.gov/38085036/) | Can the Clinical Utility of iBreastExam, a Novel Device, Aid in Optimizing Breast Cancer Diagnosis? A Systematic Review. | 2,023 |
| [38085060](https://pubmed.ncbi.nlm.nih.gov/38085060/) | Breast Cancer Phenotypes in Africa: A Scoping Review and Meta-Analysis. | 2,023 |
| [38127958](https://pubmed.ncbi.nlm.nih.gov/38127958/) | Anesthesia-related intervention for long-term survival and cancer recurrence following breast cancer surgery: A systematic review of prospective studies. | 2,023 |
| [32772650](https://pubmed.ncbi.nlm.nih.gov/32772650/) | The association between upper limb function and variables at the different domains of the international classification of functioning, disability and health in women after breast cancer surgery: a systematic review. | 2,022 |
| [33073616](https://pubmed.ncbi.nlm.nih.gov/33073616/) | A Systematic Review of Peripheral Neuropathies in Breast Cancer-Related Lymphedema. | 2,022 |
| [34238794](https://pubmed.ncbi.nlm.nih.gov/34238794/) | A Systematic Review of Breast Reconstruction Options After Mastectomy in Massive Weight Loss Patients. | 2,022 |
| [34301512](https://pubmed.ncbi.nlm.nih.gov/34301512/) | A call to bridge the divide in breast reconstruction research: A systematic review. | 2,022 |
| [34302791](https://pubmed.ncbi.nlm.nih.gov/34302791/) | Effects of Home-Based Walking on Cancer-Related Fatigue in Patients With Breast Cancer: A Meta-analysis of Randomized Controlled Trials. | 2,022 |
| [34407446](https://pubmed.ncbi.nlm.nih.gov/34407446/) | Effects of Complex Physical Therapy and Multimodal Approaches on Lymphedema Secondary to Breast Cancer: A Systematic Review and Meta-analysis of Randomized Controlled Trials. | 2,022 |
| [34557943](https://pubmed.ncbi.nlm.nih.gov/34557943/) | Surgical Services for Breast Cancer Patients in Australia, is There a Gap for Aboriginal and/or Torres Strait Islander Women? | 2,022 |
| [34559724](https://pubmed.ncbi.nlm.nih.gov/34559724/) | The Effect of Exercise Training on Lean Body Mass in Breast Cancer Patients: A Systematic Review and Meta-analysis. | 2,022 |
| [34563628](https://pubmed.ncbi.nlm.nih.gov/34563628/) | Pain Prevalence During Cancer Treatment: A Systematic Review and Meta-Analysis. | 2,022 |
| [34618886](https://pubmed.ncbi.nlm.nih.gov/34618886/) | Treatment and Prevention of Periprosthetic Capsular Contracture in Breast Surgery With Prosthesis Using Leukotriene Receptor Antagonists: A Meta-Analysis. | 2,022 |
| [34665034](https://pubmed.ncbi.nlm.nih.gov/34665034/) | Machine Learning for Workflow Applications in Screening Mammography: Systematic Review and Meta-Analysis. | 2,022 |
| [34694451](https://pubmed.ncbi.nlm.nih.gov/34694451/) | Digital breast tomosynthesis (DBT) plus synthesised two-dimensional mammography (s2D) in breast cancer screening is associated with higher cancer detection and lower recalls compared to digital mammography (DM) alone: results of a systematic review and meta-analysis. | 2,022 |
| [34801428](https://pubmed.ncbi.nlm.nih.gov/34801428/) | The Impact of implant-based reconstruction on persistent pain after breast cancer surgery: A systematic review. | 2,022 |
| [34820683](https://pubmed.ncbi.nlm.nih.gov/34820683/) | Risk of primary breast cancer in patients with differentiated thyroid cancer undergoing radioactive iodine therapy: a systematic review and meta-analysis. | 2,022 |
| [34904875](https://pubmed.ncbi.nlm.nih.gov/34904875/) | Contrast-enhanced Mammography: A Systematic Review and Meta-Analysis of Diagnostic Performance. | 2,022 |
| [34921906](https://pubmed.ncbi.nlm.nih.gov/34921906/) | Delivery of Adjuvant Radiation in 5 Days or Less After Lumpectomy for Breast Cancer: A Systematic Review. | 2,022 |
| [34951629](https://pubmed.ncbi.nlm.nih.gov/34951629/) | A systematic review and meta-analysis of beta-blockers and renin-angiotensin system inhibitors for preventing left ventricular dysfunction due to anthracyclines or trastuzumab in patients with breast cancer. | 2,022 |
| [34952749](https://pubmed.ncbi.nlm.nih.gov/34952749/) | Worldwide review with meta-analysis of women's awareness about breast cancer. | 2,022 |
| [34955392](https://pubmed.ncbi.nlm.nih.gov/34955392/) | Immediate Lymphatic Reconstruction for Prevention of Secondary Lymphedema: A Meta-Analysis. | 2,022 |
| [35005994](https://pubmed.ncbi.nlm.nih.gov/35005994/) | Systematic Review of Molecular Biomarkers Predictive of Resistance to CDK4/6 Inhibition in Metastatic Breast Cancer. | 2,022 |
| [35041467](https://pubmed.ncbi.nlm.nih.gov/35041467/) | Use of Adjuvant Bisphosphonates and Other Bone-Modifying Agents in Breast Cancer: ASCO-OH (CCO) Guideline Update. | 2,022 |
| [35065909](https://pubmed.ncbi.nlm.nih.gov/35065909/) | Independent External Validation of Artificial Intelligence Algorithms for Automated Interpretation of Screening Mammography: A Systematic Review. | 2,022 |
| [35077194](https://pubmed.ncbi.nlm.nih.gov/35077194/) | Prospective Surveillance for Breast Cancer-Related Arm Lymphedema: A Systematic Review and Meta-Analysis. | 2,022 |
| [35102018](https://pubmed.ncbi.nlm.nih.gov/35102018/) | The Failed Breast Implant in Postmastectomy Reconstruction: A Systematic Literature Review of Complications of Implant-Based Breast Reconstruction. | 2,022 |
| [35103633](https://pubmed.ncbi.nlm.nih.gov/35103633/) | Assessing Long-Term Outcomes in Breast Implant Illness: The Missing Link? A Systematic Review. | 2,022 |
| [35123662](https://pubmed.ncbi.nlm.nih.gov/35123662/) | Aromatase inhibitors versus tamoxifen in premenopausal women with oestrogen receptor-positive early-stage breast cancer treated with ovarian suppression: a patient-level meta-analysis of 7030 women from four randomised trials. | 2,022 |
| [35138351](https://pubmed.ncbi.nlm.nih.gov/35138351/) | Association of Spironolactone Use With Risk of Cancer: A Systematic Review and Meta-analysis. | 2,022 |
| [35143585](https://pubmed.ncbi.nlm.nih.gov/35143585/) | The association between migraine and breast cancer risk: A systematic review and meta-analysis. | 2,022 |
| [35163815](https://pubmed.ncbi.nlm.nih.gov/35163815/) | The Potential Effect of Lidocaine, Ropivacaine, Levobupivacaine and Morphine on Breast Cancer Pre-Clinical Models: A Systematic Review. | 2,022 |
| [35165073](https://pubmed.ncbi.nlm.nih.gov/35165073/) | Donor site complications and satisfaction in autologous fat grafting for breast reconstruction: A systematic review. | 2,022 |
| [35171707](https://pubmed.ncbi.nlm.nih.gov/35171707/) | Mapping Systematic Reviews of Breast Cancer Survivorship Interventions: A Network Analysis. | 2,022 |
| [35194632](https://pubmed.ncbi.nlm.nih.gov/35194632/) | Clinical Treatment Score post-5 years as a predictor of late distant recurrence in hormone receptor-positive breast cancer: systematic review and meta-analysis. | 2,022 |
| [35220429](https://pubmed.ncbi.nlm.nih.gov/35220429/) | Safety of fertility preservation techniques before and after anticancer treatments in young women with breast cancer: a systematic review and meta-analysis. | 2,022 |
| [35245258](https://pubmed.ncbi.nlm.nih.gov/35245258/) | Defining Mastectomy Skin Flap Necrosis: A Systematic Review of the Literature and a Call for Standardization. | 2,022 |
| [35249100](https://pubmed.ncbi.nlm.nih.gov/35249100/) | Ki-67 assessment of pancreatic neuroendocrine neoplasms: Systematic review and meta-analysis of manual vs. digital pathology scoring. | 2,022 |
| [35274129](https://pubmed.ncbi.nlm.nih.gov/35274129/) | Genome-wide association study meta-analysis identifies three novel loci for circulating anti-Müllerian hormone levels in women. | 2,022 |
| [35301201](https://pubmed.ncbi.nlm.nih.gov/35301201/) | Efficacy of virtual reality-based interventions for patients with breast cancer symptom and rehabilitation management: a systematic review and meta-analysis. | 2,022 |
| [35351394](https://pubmed.ncbi.nlm.nih.gov/35351394/) | Impact of diabetes on outcomes in breast reconstruction: A systematic review and meta-analysis. | 2,022 |
| [35358483](https://pubmed.ncbi.nlm.nih.gov/35358483/) | Diagnostic Accuracy of Shear-Wave Elastography for Breast Lesion Characterization in Women: A Systematic Review and Meta-Analysis. | 2,022 |
| [35393263](https://pubmed.ncbi.nlm.nih.gov/35393263/) | Quality of life, pain of prepectoral and subpectoral implant-based breast reconstruction with a discussion on cost: A systematic review and meta-analysis. | 2,022 |
| [35416993](https://pubmed.ncbi.nlm.nih.gov/35416993/) | Evaluation of Information Theoretic Network Meta-analysis to Rank First-Line Anticancer Regimens for Hormone Receptor-Positive, ERBB2-Negative Metastatic Breast Cancer. | 2,022 |
| [35430037](https://pubmed.ncbi.nlm.nih.gov/35430037/) | Breast cancer detection using artificial intelligence techniques: A systematic literature review. | 2,022 |
| [35500200](https://pubmed.ncbi.nlm.nih.gov/35500200/) | Electronic Health Interventions for Patients With Breast Cancer: Systematic Review and Meta-Analyses. | 2,022 |
| [35502959](https://pubmed.ncbi.nlm.nih.gov/35502959/) | Bilateral Transverse Upper Gracilis Flaps for Unilateral Breast Reconstruction: A 4-Year Retrospective Study of the "2-in-1" Technique and a Systematic Review With Meta-analysis. | 2,022 |
| [35507894](https://pubmed.ncbi.nlm.nih.gov/35507894/) | Association of <i>Hypoxia-Inducible Factor 1α</i> Gene Polymorphisms With Breast Cancer Susceptibility: A Meta-Analysis. | 2,022 |
| [35584346](https://pubmed.ncbi.nlm.nih.gov/35584346/) | Clinical Validity of 16α-[<sup>18</sup>F]Fluoro-17β-Estradiol Positron Emission Tomography/Computed Tomography to Assess Estrogen Receptor Status in Newly Diagnosed Metastatic Breast Cancer. | 2,022 |
| [35623750](https://pubmed.ncbi.nlm.nih.gov/35623750/) | Triple-negative breast cancer prevalence in Africa: a systematic review and meta-analysis. | 2,022 |
| [35640077](https://pubmed.ncbi.nlm.nih.gov/35640077/) | Systemic Therapy for Advanced Human Epidermal Growth Factor Receptor 2-Positive Breast Cancer: ASCO Guideline Update. | 2,022 |
| [35641011](https://pubmed.ncbi.nlm.nih.gov/35641011/) | Effectiveness of internet-based support interventions on patients with breast cancer: a systematic review and narrative synthesis. | 2,022 |
| [35650466](https://pubmed.ncbi.nlm.nih.gov/35650466/) | Impact of Patient Navigation on Population-Based Breast Screening: a Systematic Review and Meta-analysis of Randomized Clinical Trials. | 2,022 |
| [35725957](https://pubmed.ncbi.nlm.nih.gov/35725957/) | Hematoma following gender-affirming mastectomy: A systematic review of the evidence. | 2,022 |
| [35732033](https://pubmed.ncbi.nlm.nih.gov/35732033/) | Breast Cancer Among Female Flight Attendants and the Role of the Occupational Exposures: A Systematic Review and Meta-analysis. | 2,022 |
| [35738959](https://pubmed.ncbi.nlm.nih.gov/35738959/) | Physical Activity in Young BRCA Carriers and Reduced Risk of Breast Cancer. | 2,022 |
| [35749737](https://pubmed.ncbi.nlm.nih.gov/35749737/) | Best Practices for BREAST-Q Research: A Systematic Review of Study Methodology. | 2,022 |
| [35749815](https://pubmed.ncbi.nlm.nih.gov/35749815/) | Systematic Review of Patient Safety and Quality Improvement Initiatives in Breast Reconstruction. | 2,022 |
| [35803233](https://pubmed.ncbi.nlm.nih.gov/35803233/) | Investigating the shared genetic architecture of uterine leiomyoma and breast cancer: A genome-wide cross-trait analysis. | 2,022 |
| [35806079](https://pubmed.ncbi.nlm.nih.gov/35806079/) | Role of Intrinsic Subtype Analysis with PAM50 in Hormone Receptors Positive HER2 Negative Metastatic Breast Cancer: A Systematic Review. | 2,022 |
| [35853035](https://pubmed.ncbi.nlm.nih.gov/35853035/) | Influence of geographic access and socioeconomic characteristics on breast cancer outcomes: A systematic review. | 2,022 |
| [35862104](https://pubmed.ncbi.nlm.nih.gov/35862104/) | Breast Implant-Associated Anaplastic Large-Cell Lymphoma: Updated Systematic Review and Analysis of Treatment Strategies. | 2,022 |
| [35894936](https://pubmed.ncbi.nlm.nih.gov/35894936/) | Breast cancer recurrence after immediate and delayed postmastectomy breast reconstruction-A systematic review and meta-analysis. | 2,022 |
| [35897832](https://pubmed.ncbi.nlm.nih.gov/35897832/) | A Cell-Based Systematic Review on the Role of Annexin A1 in Triple-Negative Breast Cancers. | 2,022 |
| [35901474](https://pubmed.ncbi.nlm.nih.gov/35901474/) | Comparison of Analgesic Effects of Different Regional Blocks in Video-assisted Thoracic and Breast Surgeries: A Network Meta-analysis and Systematic Review. | 2,022 |
| [35907689](https://pubmed.ncbi.nlm.nih.gov/35907689/) | Breast angiosarcoma after primary breast cancer surgery: A systematic review. | 2,022 |
| [35909248](https://pubmed.ncbi.nlm.nih.gov/35909248/) | Immediate breast reconstruction uptake in older women with primary breast cancer: systematic review. | 2,022 |
| [35921372](https://pubmed.ncbi.nlm.nih.gov/35921372/) | Does aquatic physical therapy affect the rehabilitation of breast cancer in women? A systematic review and meta-analysis of randomized controlled trials. | 2,022 |
| [35930757](https://pubmed.ncbi.nlm.nih.gov/35930757/) | Implementation and Impact of Choosing Wisely Recommendations in Oncology. | 2,022 |
| [35943952](https://pubmed.ncbi.nlm.nih.gov/35943952/) | Complications Associated with Contralateral Prophylactic Mastectomy: A Systematic Review and Meta-Analysis. | 2,022 |
| [35945894](https://pubmed.ncbi.nlm.nih.gov/35945894/) | Present and future of machine learning in breast surgery: systematic review. | 2,022 |
| [35961927](https://pubmed.ncbi.nlm.nih.gov/35961927/) | Post-mastectomy adjuvant radiotherapy for direct-to-implant and two-stage implant-based breast reconstruction: A meta-analysis. | 2,022 |
| [35980168](https://pubmed.ncbi.nlm.nih.gov/35980168/) | Heterozygous BRCA1 and BRCA2 and Mismatch Repair Gene Pathogenic Variants in Children and Adolescents With Cancer. | 2,022 |
| [35994341](https://pubmed.ncbi.nlm.nih.gov/35994341/) | How Does Oncoplastic Surgery Compare with Standard Partial Mastectomy? A Systematic Review of Patient-Reported Outcomes. | 2,022 |
| [36077026](https://pubmed.ncbi.nlm.nih.gov/36077026/) | Uncovering Oncogenic Mechanisms of Tumor Suppressor Genes in Breast Cancer Multi-Omics Data. | 2,022 |
| [36117133](https://pubmed.ncbi.nlm.nih.gov/36117133/) | The risk of bias of non-randomized observational studies in deep inferior epigastric perforator flap breast reconstruction: A systematic review using ROBINS-I. | 2,022 |
| [36123255](https://pubmed.ncbi.nlm.nih.gov/36123255/) | Patient Safety Initiatives in Cosmetic Breast Surgery: A Systematic Review. | 2,022 |
| [36130112](https://pubmed.ncbi.nlm.nih.gov/36130112/) | Prognostic role of preoperative circulating systemic inflammatory response markers in primary breast cancer: meta-analysis. | 2,022 |
| [36130770](https://pubmed.ncbi.nlm.nih.gov/36130770/) | Margin status and survival outcomes after breast cancer conservation surgery: prospectively registered systematic review and meta-analysis. | 2,022 |
| [36154284](https://pubmed.ncbi.nlm.nih.gov/36154284/) | Contrast-enhanced Mammography versus Contrast-enhanced Breast MRI: A Systematic Review and Meta-Analysis. | 2,022 |
| [36180337](https://pubmed.ncbi.nlm.nih.gov/36180337/) | Systematic review: Oncological safety of reconstruction with fat grafting in breast cancer outcomes. | 2,022 |
| [36184999](https://pubmed.ncbi.nlm.nih.gov/36184999/) | A systematic review exploring the role of modern radiation for the treatment of Hereditary or Familial Breast Cancer. | 2,022 |
| [36202732](https://pubmed.ncbi.nlm.nih.gov/36202732/) | Surgical complications in immediate and delayed breast reconstruction: A systematic review and meta-analysis. | 2,022 |
| [36207046](https://pubmed.ncbi.nlm.nih.gov/36207046/) | Effectiveness of weight loss interventions in breast cancer survivors: a systematic review of reviews. | 2,022 |
| [36232567](https://pubmed.ncbi.nlm.nih.gov/36232567/) | Efficacy and Safety of Ginger on the Side Effects of Chemotherapy in Breast Cancer Patients: Systematic Review and Meta-Analysis. | 2,022 |
| [36241504](https://pubmed.ncbi.nlm.nih.gov/36241504/) | Breast reconstruction using the Latissimus Dorsi Flap and Immediate Fat Transfer (LIFT): A systematic review and meta-analysis. | 2,022 |
| [36252635](https://pubmed.ncbi.nlm.nih.gov/36252635/) | Systematic review for deep inspiration breath hold in proton therapy for mediastinal lymphoma: A PTCOG Lymphoma Subcommittee report and recommendations. | 2,022 |
| [36327334](https://pubmed.ncbi.nlm.nih.gov/36327334/) | Effectiveness of nursing interventions on the sexual quality of life of patients with breast cancer: A systematic review and meta-analysis. | 2,022 |
| [36362190](https://pubmed.ncbi.nlm.nih.gov/36362190/) | PET-Derived Radiomics and Artificial Intelligence in Breast Cancer: A Systematic Review. | 2,022 |
| [36400735](https://pubmed.ncbi.nlm.nih.gov/36400735/) | Quality of life in patients with breast cancer with neoadjuvant chemotherapy: a systematic review. | 2,022 |
| [36424572](https://pubmed.ncbi.nlm.nih.gov/36424572/) | Identifying and ranking causal biochemical biomarkers for breast cancer: a Mendelian randomisation study. | 2,022 |
| [36454573](https://pubmed.ncbi.nlm.nih.gov/36454573/) | Yield of Surveillance Imaging After Mastectomy With or Without Reconstruction for Patients With Prior Breast Cancer: A Systematic Review and Meta-analysis. | 2,022 |
| [36454902](https://pubmed.ncbi.nlm.nih.gov/36454902/) | Health-related quality of life and associated factors among cancer patients in Ethiopia: Systematic review and meta-analysis. | 2,022 |
| [36454979](https://pubmed.ncbi.nlm.nih.gov/36454979/) | The adverse effects of trastuzumab-containing regimes as a therapy in breast cancer: A piggy-back systematic review and meta-analysis. | 2,022 |

Primary studies with their number of citing guidelines and reviews are in `primary_studies.csv`; the citing guidelines and reviews in `citing_reviews.csv`. PubMed, MeSH: U.S. National Library of Medicine; citations: OpenAlex. Graph files: CC0.
