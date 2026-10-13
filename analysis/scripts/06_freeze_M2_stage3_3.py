
from pathlib import Path
import pandas as pd,json,hashlib
ROOT=Path(__file__).resolve().parents[1];IN=ROOT/"input";OUT=ROOT/"outputs";FIG=ROOT/"figures"
required=[
 OUT/"M2_D1_Deterministic_Signals.csv",
 OUT/"M2_D2_Semantic_Signals.csv",
 OUT/"M2_Candidate_Backtranslations_400.csv",
 OUT/"M2_D3_Backtranslation_Signals.csv",
 OUT/"M2_Final_Analysis_Matrix.csv",
 OUT/"Table1_Benchmark_Characteristics.csv",
 OUT/"Table2_Primary_Detector_Performance.csv",
 OUT/"Table3_By_Error_Family.csv",
 OUT/"Table4_By_Severity.csv",
 OUT/"Table5_By_Discipline.csv",
 OUT/"Table6_Ablation.csv",
 OUT/"Table7a_Calibration.csv",
 OUT/"Table7b_Risk_Coverage.csv",
 OUT/"M2_RQ_to_Results_Map.csv",
 OUT/"M2_Final_Statistical_Summary.json",
]
missing=[str(p.relative_to(ROOT)) for p in required if not p.exists()]
report={"missing":missing}
if not missing:
    b=pd.read_csv(IN/"M2_SETR_Core_Balanced_400_v1.1.csv")
    o=pd.read_csv(IN/"M2_OpenThai_SETR_400_v1.2.csv")
    d1=pd.read_csv(OUT/"M2_D1_Deterministic_Signals.csv")
    d2=pd.read_csv(OUT/"M2_D2_Semantic_Signals.csv")
    bt=pd.read_csv(OUT/"M2_Candidate_Backtranslations_400.csv")
    d3=pd.read_csv(OUT/"M2_D3_Backtranslation_Signals.csv")
    mat=pd.read_csv(OUT/"M2_Final_Analysis_Matrix.csv")
    ids=set(b.instance_id.astype(str))
    report.update({
      "benchmark_rows":len(b),"benchmark_docs":b.document_id.nunique(),
      "openthai_rows":len(o),"openthai_complete":int((o.status=="COMPLETE").sum()),
      "D1_rows":len(d1),"D2_rows":len(d2),"BT_rows":len(bt),"BT_complete":int((bt.status=="COMPLETE").sum()),
      "D3_rows":len(d3),"analysis_rows":len(mat),
      "all_ids_align":all(set(x.instance_id.astype(str))==ids for x in [o,d1,d2,bt,d3,mat]),
      "development_docs":mat.loc[mat.split=="development","document_id"].nunique(),
      "test_docs":mat.loc[mat.split=="test","document_id"].nunique()
    })
    report["freeze_pass"]=(
      len(b)==400 and b.document_id.nunique()==80 and len(o)==400 and report["openthai_complete"]==400 and
      len(d1)==len(d2)==len(bt)==len(d3)==len(mat)==400 and report["BT_complete"]==400 and
      report["all_ids_align"] and report["development_docs"]==40 and report["test_docs"]==40
    )
else: report["freeze_pass"]=False

# Output integrity manifest
manifest=[]
for p in sorted(list(OUT.glob("*"))+list(FIG.glob("*"))):
    if p.is_file():
        manifest.append({"file":str(p.relative_to(ROOT)),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size})
(ROOT/"M2_STAGE3_3_SHA256_MANIFEST.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
(ROOT/"M2_Stage3_3_Freeze_Report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps(report,indent=2))
if not report["freeze_pass"]: raise SystemExit("M2 STAGE 3.3 FREEZE FAILED")
print("M2_STAGE3_3_FREEZE_PASS=true")
print("M2 SETR EXPERIMENTAL FREEZE = PASS")
