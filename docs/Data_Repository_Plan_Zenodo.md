# Data repository plan for Manuscript 2 (Language Resources and Evaluation)

## Recommended repository of record: Zenodo

**Decision:** Use **Zenodo** as the repository of record and **GitHub** as the companion code-development repository.

### Why Zenodo is the best fit
- Springer Nature explicitly lists Zenodo among its recommended generalist repositories.
- The research object is mixed: benchmark metadata, detector outputs, statistical tables, figures, software, environment registries, and provenance files.
- Zenodo assigns persistent DOIs and supports version-specific DOI citation.
- Zenodo supports versioning and GitHub release archiving.
- Zenodo supports open and restricted-access workflows, which is useful because verbatim Scopus-indexed abstracts and derived translations may have third-party rights constraints.
- A single DOI-bearing archival record is easier for LRE reviewers and readers to cite than a GitHub URL alone.

## Why not use CLARIN/LINDAT as the primary repository now?
CLARIN/LINDAT is more discipline-specific for language resources and is an excellent option when the depositor can resolve IPR and licensing for the deposited language data. For this study, however, the text-bearing benchmark derives from abstracts accessed through Scopus and machine translations of those texts. Depositing verbatim text requires a clear right to redistribute or deposit those materials. Until that position is confirmed, Zenodo is the more practical repository of record because it can archive the public reproducibility layer while clearly documenting restricted inputs. A CLARIN/LINDAT mirror may be considered later if redistribution rights are confirmed.

## Recommended record structure

### Public Zenodo record — required
Publish this record before manuscript submission and cite its **version-specific DOI**.

Recommended contents:
1. `README.md`
2. `CITATION.cff`
3. `LICENSE-CODE` — MIT
4. `LICENSE-DATA-DOCS` — CC BY 4.0 for author-created material only
5. `data_dictionary.csv`
6. `benchmark_manifest_public.csv`
   - document ID / DOI or other identifier where lawful
   - panel
   - split
   - corruption family
   - severity
   - label
   - hashes and provenance identifiers
   - **no verbatim source or translated text unless rights are confirmed**
7. detector features and scores that contain no restricted text
8. frozen statistical tables
9. publication figures
10. `M2_Final_Statistical_Summary.json`
11. `M2_RQ_to_Results_Map.csv`
12. `M2_Stage3_3_Freeze_Report.json`
13. `model_registry.json`
14. `seeds_and_versions.json`
15. `requirements.txt`
16. analysis scripts
17. `SHA256_MANIFEST_PUBLIC.json`
18. `restricted_inputs/README.md`
19. `restricted_inputs/input_schema.csv`
20. `reproduction_instructions.md`

### Restricted text-bearing component
Do **not** publicly upload verbatim Scopus abstracts, `source_en`, full `candidate_th`, or candidate backtranslations unless redistribution rights are confirmed.

If legal or contractual review confirms that a restricted deposit is permissible:
- create a **separate linked restricted-access Zenodo record** for text-bearing inputs and outputs;
- state access conditions;
- link it to the public DOI using Related Identifiers.

If deposit is not permissible:
- retain the text-bearing files in secure institutional storage;
- provide exact reconstruction instructions for researchers with lawful Scopus access;
- state this limitation explicitly in the manuscript Data Availability Statement.

## DOI strategy
- Cite the **version-specific DOI** for the exact frozen release used in the article.
- The Zenodo concept DOI may be listed in the repository README for the evolving project.
- Publish the Zenodo record before manuscript submission so that the DOI resolves during peer review.

## Suggested Zenodo metadata

**Title**  
English–Thai scholarly translation stress-test benchmark and reproducibility materials for epistemically consequential errors

**Version**  
1.0

**Resource type**  
Dataset, with a related Software/GitHub release

**Keywords**  
English–Thai; machine translation; translation quality estimation; challenge set; scholarly communication; epistemic integrity; reproducibility

**Description**  
A reproducibility compendium for a controlled English–Thai scholarly translation stress-test benchmark. The public record contains benchmark metadata, controlled corruption labels, detector features and scores that do not reproduce third-party source text, frozen statistical outputs, figures, model and seed registries, analysis code, and provenance manifests. Text-bearing inputs derived from licensed scholarly abstracts are excluded from the public record unless redistribution rights are confirmed.

## Data citation template after publication
[Author(s)]. (2026). *English–Thai scholarly translation stress-test benchmark and reproducibility materials for epistemically consequential errors* (Version 1.0) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.xxxxxxx

Insert this citation in the manuscript reference list and cite the dataset in the Data Availability section before submission.
