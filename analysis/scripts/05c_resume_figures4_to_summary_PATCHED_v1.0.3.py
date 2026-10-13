
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"outputs"
FIG=ROOT/"figures"
FIG.mkdir(exist_ok=True)

required=[
    OUT/"M2_Final_Analysis_Matrix.csv",
    OUT/"Table2_Primary_Detector_Performance.csv",
    OUT/"Table6_Ablation.csv",
    OUT/"Table7a_Calibration.csv",
    OUT/"Table7b_Risk_Coverage.csv",
    OUT/"M2_RQ_to_Results_Map.csv",
]
missing=[str(x.name) for x in required if not x.exists()]
if missing:
    raise SystemExit("Missing required completed output(s): "+", ".join(missing))

print("RESUME FROM FIGURE 4 START")

df=pd.read_csv(OUT/"M2_Final_Analysis_Matrix.csv")
if len(df)!=400 or df.document_id.nunique()!=80:
    raise SystemExit(f"Unexpected final matrix shape: rows={len(df)}, docs={df.document_id.nunique()}")

test=df[df["split"]=="test"].copy()
if len(test)!=200 or test.document_id.nunique()!=40:
    raise SystemExit(f"Unexpected test split: rows={len(test)}, docs={test.document_id.nunique()}")

# Figure 4
order=["CLEAN","E1_POLARITY","E2_EPISTEMIC_FORCE","E3_METHOD_DESIGN","E4_EVIDENCE_OMISSION"]
plt.figure(figsize=(9,5))
data=[test.loc[test.family==x,"D5_score"].dropna().values for x in order]
plt.boxplot(data,tick_labels=order)
plt.xticks(rotation=25,ha="right")
plt.ylabel("D5 ensemble risk")
plt.tight_layout()
plt.savefig(FIG/"Figure4_Risk_by_ErrorFamily.png",dpi=300)
plt.close()
print("WROTE Figure4_Risk_by_ErrorFamily.png")

# Figure 5
pos=test[test["y"]==1].copy()
sorder=["subtle","moderate","severe"]
plt.figure(figsize=(7,5))
data=[pos.loc[pos.severity==x,"D5_score"].dropna().values for x in sorder]
plt.boxplot(data,tick_labels=sorder)
plt.ylabel("D5 ensemble risk")
plt.tight_layout()
plt.savefig(FIG/"Figure5_Risk_by_Severity.png",dpi=300)
plt.close()
print("WROTE Figure5_Risk_by_Severity.png")

# Figure 6
ab=pd.read_csv(OUT/"Table6_Ablation.csv")
plt.figure(figsize=(7,5))
plt.bar(ab["removed"].astype(str),ab["delta_AUPRC_vs_full"])
plt.xlabel("Detector family removed")
plt.ylabel("Delta AUPRC vs full ensemble")
plt.tight_layout()
plt.savefig(FIG/"Figure6_Ablation_DeltaAUPRC.png",dpi=300)
plt.close()
print("WROTE Figure6_Ablation_DeltaAUPRC.png")

# Figure 7
cal=pd.read_csv(OUT/"Table7a_Calibration.csv")
plt.figure(figsize=(6,5))
plt.plot(cal["mean_predicted_risk"],cal["observed_event_rate"],marker="o")
plt.plot([0,1],[0,1],"--")
plt.xlabel("Mean predicted risk")
plt.ylabel("Observed event rate")
plt.tight_layout()
plt.savefig(FIG/"Figure7_Calibration.png",dpi=300)
plt.close()
print("WROTE Figure7_Calibration.png")

# Figure 8
riskdf=pd.read_csv(OUT/"Table7b_Risk_Coverage.csv")
plt.figure(figsize=(6,5))
plt.plot(riskdf["coverage"],riskdf["selective_error_rate"],marker="o")
plt.xlabel("Coverage")
plt.ylabel("Selective error rate")
plt.tight_layout()
plt.savefig(FIG/"Figure8_Risk_Coverage.png",dpi=300)
plt.close()
print("WROTE Figure8_Risk_Coverage.png")

# Summary from already-computed Table 2 / Table 7b
t2=pd.read_csv(OUT/"Table2_Primary_Detector_Performance.csv")
d5=t2[t2["detector"]=="D5"]
if len(d5)!=1:
    raise SystemExit("Table2 must contain exactly one D5 row")
d5=d5.iloc[0]

thresholds={}
for _,r in t2.iterrows():
    thresholds[str(r["detector"])]=float(r["development_threshold"])

aurc=float(np.trapezoid(
    riskdf["selective_error_rate"].to_numpy(float),
    riskdf["coverage"].to_numpy(float)
))

summary={
    "n_total": int(len(df)),
    "n_documents": int(df.document_id.nunique()),
    "development_docs": int(df.loc[df["split"]=="development","document_id"].nunique()),
    "test_docs": int(test.document_id.nunique()),
    "thresholds": thresholds,
    "D5_test_AUROC": float(d5["AUROC"]),
    "D5_test_AUPRC": float(d5["AUPRC"]),
    "D5_test_Brier": float(d5["Brier"]),
    "risk_coverage_AURC": aurc,
    "bootstrap_B": 10000,
    "bootstrap_seed": 2026101206,
    "finalization_patch": "05c_resume_figures4_to_summary_PATCHED_v1.0.3.py",
    "claim_boundary": "Controlled perturbation benchmark; not natural-error prevalence or human safety certification."
}

(OUT/"M2_Final_Statistical_Summary.json").write_text(
    json.dumps(summary,indent=2),
    encoding="utf-8"
)

print(json.dumps(summary,indent=2))
print("M2 Stage 3.3 FINALIZATION COMPLETE")
