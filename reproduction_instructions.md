# Reproduction instructions

## Scope
This release reproduces the M2 SETR detector/statistical pipeline after the frozen controlled benchmark and OpenThai inference outputs have been placed locally in `input/`. It does not regenerate the upstream Scopus corpus or redistribute verbatim scholarly abstracts.

## Tested workflow
Windows PowerShell, Python virtual environment, CPU-compatible execution. GPU is optional.

## 1. Create environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r .\analysis\environment\requirements.txt
```

## 2. Supply restricted/local inputs
Copy the following files into `analysis/input/`:
- `M2_SETR_Core_Balanced_400_v1.1.csv`
- `M2_OpenThai_SETR_400_v1.2.csv`

Expected benchmark: 400 instances from 80 documents, five instances per document. OpenThai rows must be 400 with `status == COMPLETE`.

## 3. Run pipeline
From the `analysis/` directory:
```powershell
cd .\analysis
python .\scripts\00_preflight.py
python .\analysis\scripts\01_compute_D1_deterministic.py
python .\analysis\scripts\02_compute_D2_semantic.py
python .\analysis\scripts\03_backtranslate_400.py
python .\analysis\scripts\04_compute_D3_backtranslation.py
python .\analysis\scripts\05_assemble_and_analyze_final.py
python .\analysis\scripts\06_freeze_M2_stage3_3.py
```

The public scripts incorporate three technical compatibility patches applied after the original frozen run: safe conversion of regex matches in D1, `numpy.trapezoid` for NumPy 2.x, and `tick_labels` for Matplotlib 3.9+, plus correct recombination of development/test scores before final matrix export. These patches do not change the prespecified benchmark, split, detector definitions, thresholds, or statistical design.

## 4. Frozen design
- Split seed: `2026101203`; SHA-256 ordering by `document_id`; 40 development + 40 held-out test documents.
- Bootstrap: 10,000 document-level resamples; seed `2026101206`.
- D1: deterministic features → leakage-controlled logistic classifier.
- D2: `1 - cosine(source_en, candidate_th)`.
- D3: backtranslation features → leakage-controlled logistic classifier.
- D4: OpenThai-SystemOne risk probability.
- D5: stacked logistic ensemble D1–D4.

## 5. Verification
A successful finalization should create Tables 1–7b, Figures 2–8, `M2_Final_Statistical_Summary.json`, and a freeze report with `freeze_pass = true`. Compare generated aggregate outputs with `results/tables/` and figures with `results/figures/`. Small binary/image checksum differences can occur across plotting backends; reported numeric table values should match.

## Claim boundary
This is a controlled perturbation stress test. It does not estimate naturally occurring translation-error prevalence, establish human-equivalent translation quality, or certify safety.
