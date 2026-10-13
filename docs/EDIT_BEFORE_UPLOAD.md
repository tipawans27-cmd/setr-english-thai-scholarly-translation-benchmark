# Required edits before public upload

Replace these placeholders:
- `[GIVEN NAME]`, `[FAMILY NAME]`, `[ORCID]` in `CITATION.cff`
- `[OWNER]` in GitHub URL
- `[RESERVED_DOI_SUFFIX]` after Zenodo DOI reservation

Also verify:
- final author order and contributions;
- funder/grant metadata;
- whether your institution permits public redistribution of any additional derived texts;
- repository name and GitHub owner;
- final journal manuscript DOI relationship after publication.

## Mandatory before public Zenodo release
- Replace creator placeholders in `CITATION.cff` and `zenodo_metadata_template.json`.
- Confirm final author order and ORCID(s).
- Confirm every public file is either author-created or legally redistributable.
- Remove all `__pycache__`, API keys, credentials, local paths, and temporary logs.
- Populate `benchmark_manifest_public.csv` without verbatim restricted text.
- Publish Zenodo Version 1.0 and record the **version-specific DOI**.
- Insert the DOI into the manuscript Data Availability statement and add the dataset citation to References.
- Create/tag the matching GitHub release and insert its URL in the manuscript.
