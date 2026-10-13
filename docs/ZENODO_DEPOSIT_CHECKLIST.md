# Zenodo deposit checklist

## Recommended record
**Title:** SETR M2: Reproducibility materials for stress-testing epistemically consequential English–Thai scholarly translation corruptions

**Resource type:** Dataset (with software/code components described in the record).

**Version:** 1.0.0

**Publication date:** use the actual date the Zenodo record is published.

**Creators:** insert all manuscript authors in final agreed order with ORCID identifiers.

**Description:**
This versioned research compendium contains public reproducibility materials for a controlled English–Thai scholarly machine-translation stress test. It includes compatibility-patched analysis scripts, frozen aggregate statistical outputs, publication figures, model/version and random-seed registries, and documentation. The balanced benchmark comprised 400 instances from 80 documents: 80 clean translations and 320 controlled perturbations spanning polarity, epistemic force, methodological design, and evidence omission. Verbatim scholarly source abstracts and full derived translations are excluded from the public release where redistribution rights are not established.

**Keywords:** machine translation; English–Thai; translation quality estimation; scholarly communication; controlled perturbation; epistemic integrity; multilingual NLP; reproducibility

**License:** CC BY 4.0 for the deposited research compendium; note in Description that code files are additionally available under MIT and third-party materials are excluded.

**Related identifiers:**
- GitHub release URL (Is supplement to / Is identical to, as appropriate)
- Article DOI after publication (Is supplement to)
- Preprint DOI, if any

## Before publishing
1. Reserve DOI in Zenodo.
2. Replace `[RESERVED_DOI_SUFFIX]`, `[OWNER]`, author placeholders and ORCID in `CITATION.cff`.
3. Add the reserved DOI to manuscript Data Availability.
4. Confirm no verbatim Scopus abstracts/source texts are present in the public ZIP.
5. Confirm `results/tables/M2_Stage3_3_Freeze_Report.json` reports freeze pass.
6. Create Git tag/release `v1.0.0`.
7. Upload this ZIP to Zenodo, or connect the GitHub repository to Zenodo and archive the GitHub release.
8. Publish Zenodo record only after author list, license, description, and related identifiers are verified.
