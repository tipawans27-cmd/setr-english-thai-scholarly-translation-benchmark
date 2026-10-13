## Scope

This repository accompanies the article: “A Reproducible English–Thai Benchmark for Stress-Testing Epistemically Consequential Errors in Scholarly Translation.”

The public release contains the frozen benchmark metadata,derived detector outputs, statistical results, analysis code, figures, model/version registries, and provenance manifests.

Verbatim Scopus-indexed abstracts and full derived translations are not redistributed because lawful access to bibliographic content does not necessarily imply redistribution rights.

## What is frozen
- 80 source documents in M2; 400 balanced core instances.
- Five instances per document: CLEAN plus four corruption families.
- E1 polarity; E2 epistemic force; E3 methodological design; E4 evidence omission.
- Document-level split: 40 development / 40 held-out test documents, no overlap.
- D1 deterministic safeguards; D2 cross-lingual semantic displacement; D3 backtranslation consistency; D4 OpenThai-SystemOne risk; D5 stacked ensemble.
- 10,000 document-cluster bootstrap replicates.

## Public contents
```text
analysis/
  scripts/                 reproducibility scripts (compatibility-patched)
  environment/             requirements, model registry, seeds/versions
  input/                   local-only restricted inputs (not tracked)
  outputs/                 outputs generated on rerun
  figures/                 figures generated on rerun
results/
  tables/                  frozen aggregate tables, RQ map, summary, freeze report
  figures/                 publication figures
docs/                      frozen reporting map and deposit guidance
restricted_inputs/         schemas and access notes; no verbatim scholarly source text
data_dictionary.csv
reproduction_instructions.md
CITATION.cff
LICENSE*
```

## Why source abstracts are not in the public release
The upstream corpus was identified via Scopus-indexed scholarly records. Verbatim title/abstract text and full derived translations are not redistributed in this public package unless redistribution rights are independently confirmed. This repository therefore separates **public reproducibility artifacts** from **restricted/local inputs**. See `restricted_inputs/README.md`.

## Reproduce
See [`reproduction_instructions.md`](reproduction_instructions.md). Exact end-to-end reruns require local copies of the two restricted input files.

## Frozen headline results
On the held-out test set, D1 achieved AUROC 0.671 and AUPRC 0.892; D5 achieved AUROC 0.668 and AUPRC 0.891. Removing D1 reduced D5 AUPRC by 0.084. Methodological-design corruption was most detectable (D5 AUROC 0.894), whereas polarity corruption was near chance (D5 AUROC 0.508). These values must be interpreted against the controlled benchmark design and 0.80 positive prevalence.

## Citation
After reserving a Zenodo DOI, replace placeholders in `CITATION.cff` and `docs/ZENODO_DEPOSIT_CHECKLIST.md`. Cite the versioned Zenodo DOI for this release; use the concept DOI when referring to the evolving repository across versions.

## License
- Code: MIT (`LICENSE-CODE`).
- Repository-authored documentation, aggregate result tables, and figures: CC BY 4.0 (`LICENSE-DATA-DOCS`).
- Third-party source texts/model weights: not covered; original terms apply.

## Claim boundary
The repository supports controlled-error sensitivity and reproducibility claims. It does not establish natural translation-error prevalence, human-equivalent translation correctness, or safety certification.

## Repository of record

The archival repository of record for the manuscript is **Zenodo**. The companion GitHub repository is used for version control and code distribution; each frozen release should be archived in Zenodo and cited with the **version-specific DOI**.

### Public versus restricted materials

The public release contains author-created code, non-text benchmark metadata, detector features/scores that do not reproduce third-party source text, frozen statistical outputs, figures, registries, and provenance manifests. Verbatim Scopus-indexed abstracts, full English source text, Thai translations, and candidate backtranslations are not included in the public release unless redistribution rights are confirmed. See `restricted_inputs/README.md` and `docs/Data_Repository_Plan_Zenodo.md`.
