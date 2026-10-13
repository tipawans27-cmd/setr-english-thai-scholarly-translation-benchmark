
from pathlib import Path
import pandas as pd,numpy as np,json,hashlib,math,warnings
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold,cross_val_predict
from sklearn.metrics import (roc_auc_score,average_precision_score,roc_curve,confusion_matrix,
                             f1_score,matthews_corrcoef,brier_score_loss,roc_curve,precision_recall_curve)
from scipy import stats
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1];IN=ROOT/"input";OUT=ROOT/"outputs";FIG=ROOT/"figures"
FIG.mkdir(exist_ok=True)
B=10000;BOOT_SEED=2026101206
rng=np.random.default_rng(BOOT_SEED)

base=pd.read_csv(IN/"M2_SETR_Core_Balanced_400_v1.1.csv")
ot=pd.read_csv(IN/"M2_OpenThai_SETR_400_v1.2.csv")
d1=pd.read_csv(OUT/"M2_D1_Deterministic_Signals.csv")
d2=pd.read_csv(OUT/"M2_D2_Semantic_Signals.csv")
d3=pd.read_csv(OUT/"M2_D3_Backtranslation_Signals.csv")

if len(ot)!=400 or not (ot.status=="COMPLETE").all():raise SystemExit("OpenThai must be 400 COMPLETE")
keep_ot=ot[["instance_id","risk_probability"]].rename(columns={"risk_probability":"D4_OpenThai_risk"})
df=(base[["instance_id","document_id","panel","label","family","severity"]]
    .merge(d1,on=["instance_id","document_id","panel"],validate="one_to_one",suffixes=("","_d1"))
    .merge(d2[["instance_id","D2_semantic_risk"]],on="instance_id",validate="one_to_one")
    .merge(d3[["instance_id","bt_semantic_risk","bt_token_jaccard_risk","bt_number_mismatch","bt_neg_presence_mismatch"]],on="instance_id",validate="one_to_one")
    .merge(keep_ot,on="instance_id",validate="one_to_one"))
df["y"]=df["label"].astype(int)

docs=sorted(df.document_id.astype(str).unique(),
    key=lambda d:hashlib.sha256(f"2026101203|{d}".encode()).hexdigest())
devdocs=set(docs[:40]);testdocs=set(docs[40:])
df["split"]=np.where(df.document_id.astype(str).isin(devdocs),"development","test")
dev=df[df.split=="development"].copy();test=df[df.split=="test"].copy()

d1feat=[c for c in df.columns if c.startswith("det_")]
d3feat=["bt_semantic_risk","bt_token_jaccard_risk","bt_number_mismatch","bt_neg_presence_mismatch"]

def pipe():
    return Pipeline([("scale",StandardScaler()),("lr",LogisticRegression(max_iter=3000,class_weight="balanced",random_state=2026101207))])

# OOF base predictions on dev, full fits for test
gkf=GroupKFold(n_splits=5)
def oof_and_test(feat):
    m=pipe()
    oof=cross_val_predict(m,dev[feat],dev.y,groups=dev.document_id,cv=gkf,method="predict_proba")[:,1]
    m.fit(dev[feat],dev.y)
    tst=m.predict_proba(test[feat])[:,1]
    return oof,tst,m

d1dev,d1test,d1model=oof_and_test(d1feat)
d3dev,d3test,d3model=oof_and_test(d3feat)
dev["D1_score"]=d1dev;test["D1_score"]=d1test
dev["D2_score"]=dev["D2_semantic_risk"];test["D2_score"]=test["D2_semantic_risk"]
dev["D3_score"]=d3dev;test["D3_score"]=d3test
dev["D4_score"]=pd.to_numeric(dev["D4_OpenThai_risk"]);test["D4_score"]=pd.to_numeric(test["D4_OpenThai_risk"])

# Stacked ensemble: meta OOF within dev, final model trained on all dev base OOF signals.
basecols=["D1_score","D2_score","D3_score","D4_score"]
meta=pipe()
meta_oof=cross_val_predict(meta,dev[basecols],dev.y,groups=dev.document_id,cv=gkf,method="predict_proba")[:,1]
meta.fit(dev[basecols],dev.y)
test["D5_score"]=meta.predict_proba(test[basecols])[:,1]
dev["D5_score"]=meta_oof

def youden(y,s):
    fpr,tpr,thr=roc_curve(y,s)
    ix=int(np.nanargmax(tpr-fpr))
    return float(thr[ix])

def point_metrics(y,s,thr):
    y=np.asarray(y,int);s=np.asarray(s,float);p=(s>=thr).astype(int)
    tn,fp,fn,tp=confusion_matrix(y,p,labels=[0,1]).ravel()
    return {
      "AUROC":roc_auc_score(y,s),"AUPRC":average_precision_score(y,s),
      "sensitivity":tp/(tp+fn),"specificity":tn/(tn+fp),
      "F1":f1_score(y,p),"MCC":matthews_corrcoef(y,p),
      "Brier":brier_score_loss(y,s),"threshold":thr
    }

# document-cluster bootstrap test CIs
def cluster_boot(yframe,scorecol,thr):
    docs0=list(yframe.document_id.unique()); vals={k:[] for k in ["AUROC","AUPRC","sensitivity","specificity","F1","MCC","Brier"]}
    for _ in range(B):
        sampled=rng.choice(docs0,size=len(docs0),replace=True)
        parts=[]
        for j,d in enumerate(sampled):
            g=yframe[yframe.document_id==d].copy()
            # repeated sampled docs remain separate clusters but metrics need rows only
            parts.append(g)
        z=pd.concat(parts,ignore_index=True)
        m=point_metrics(z.y,z[scorecol],thr)
        for k in vals:vals[k].append(m[k])
    return {k:(float(np.quantile(v,.025)),float(np.quantile(v,.975))) for k,v in vals.items()}

detcols={"D1":"D1_score","D2":"D2_score","D3":"D3_score","D4":"D4_score","D5":"D5_score"}
perf=[]
thresholds={}
for det,col in detcols.items():
    thr=youden(dev.y,dev[col]);thresholds[det]=thr
    pm=point_metrics(test.y,test[col],thr);ci=cluster_boot(test,col,thr)
    row={"detector":det,"development_threshold":thr,"test_n":len(test),"test_docs":test.document_id.nunique(),**pm}
    for k,(lo,hi) in ci.items():
        row[k+"_CI95_low"]=lo;row[k+"_CI95_high"]=hi
    perf.append(row)
pd.DataFrame(perf).to_csv(OUT/"Table2_Primary_Detector_Performance.csv",index=False,encoding="utf-8-sig")

# Table 1 benchmark characteristics
t1=[]
for split,g in df.groupby("split"):
    for fam,h in g.groupby("family"):
        t1.append({"split":split,"family":fam,"instances":len(h),"documents":h.document_id.nunique(),
                   "positive":int(h.y.sum()),"negative":int((1-h.y).sum())})
pd.DataFrame(t1).to_csv(OUT/"Table1_Benchmark_Characteristics.csv",index=False,encoding="utf-8-sig")

# Family-specific test performance for every detector: each family vs clean
famrows=[]
for fam in sorted(x for x in test.family.unique() if x!="CLEAN"):
    z=test[test.family.isin(["CLEAN",fam])].copy()
    for det,col in detcols.items():
        m=point_metrics(z.y,z[col],thresholds[det])
        famrows.append({"family":fam,"detector":det,"n":len(z),"documents":z.document_id.nunique(),**m})
pd.DataFrame(famrows).to_csv(OUT/"Table3_By_Error_Family.csv",index=False,encoding="utf-8-sig")

# Severity + ordinal trend, D5 primary
sevmap={"subtle":1,"moderate":2,"severe":3}
pos=test[test.y==1].copy();pos["sev_code"]=pos.severity.map(sevmap)
rho,pv=stats.spearmanr(pos.sev_code,pos.D5_score,nan_policy="omit")
try:
    groups=[g.D5_score.values for _,g in pos.groupby("severity")]
    H,kp=stats.kruskal(*groups)
except Exception:
    H=kp=np.nan
sevrows=[]
for s,g in pos.groupby("severity"):
    sevrows.append({"severity":s,"n":len(g),"documents":g.document_id.nunique(),
      "mean_D5_risk":g.D5_score.mean(),"median_D5_risk":g.D5_score.median(),
      "detection_rate_D5":(g.D5_score>=thresholds["D5"]).mean(),
      "spearman_severity_rho_all":rho,"spearman_p_all":pv,"Kruskal_H_all":H,"Kruskal_p_all":kp})
pd.DataFrame(sevrows).to_csv(OUT/"Table4_By_Severity.csv",index=False,encoding="utf-8-sig")

# Discipline effects, D5 primary
disc=[]
for panel,g in test.groupby("panel"):
    m=point_metrics(g.y,g.D5_score,thresholds["D5"])
    disc.append({"panel":panel,"n":len(g),"documents":g.document_id.nunique(),**m})
pd.DataFrame(disc).to_csv(OUT/"Table5_By_Discipline.csv",index=False,encoding="utf-8-sig")

# Ablation: meta models removing one detector family, OOF threshold + final test
abl=[]
full_auc=roc_auc_score(test.y,test.D5_score);full_ap=average_precision_score(test.y,test.D5_score)
abl.append({"configuration":"Full D1+D2+D3+D4","removed":"none","AUROC":full_auc,"AUPRC":full_ap,
            "delta_AUROC_vs_full":0.0,"delta_AUPRC_vs_full":0.0,"threshold":thresholds["D5"]})
for removed in basecols:
    cols=[c for c in basecols if c!=removed]
    mm=pipe()
    oof=cross_val_predict(mm,dev[cols],dev.y,groups=dev.document_id,cv=gkf,method="predict_proba")[:,1]
    thr=youden(dev.y,oof)
    mm.fit(dev[cols],dev.y)
    pred=mm.predict_proba(test[cols])[:,1]
    auc=roc_auc_score(test.y,pred);ap=average_precision_score(test.y,pred)
    abl.append({"configuration":"+ ".join(cols),"removed":removed.replace("_score",""),"AUROC":auc,"AUPRC":ap,
                "delta_AUROC_vs_full":auc-full_auc,"delta_AUPRC_vs_full":ap-full_ap,"threshold":thr})
pd.DataFrame(abl).to_csv(OUT/"Table6_Ablation.csv",index=False,encoding="utf-8-sig")

# Calibration and selective risk/coverage D5
# Calibration bins: fixed quintiles of predicted risk on test
tmp=test[["instance_id","document_id","y","D5_score"]].copy()
tmp["bin"]=pd.qcut(tmp.D5_score,q=5,duplicates="drop")
cal=tmp.groupby("bin",observed=True).agg(n=("y","size"),mean_predicted_risk=("D5_score","mean"),observed_event_rate=("y","mean")).reset_index()
cal["bin"]=cal["bin"].astype(str)
cal.to_csv(OUT/"Table7a_Calibration.csv",index=False,encoding="utf-8-sig")

# selective classification: retain most confident around frozen threshold
thr=thresholds["D5"]
tmp["confidence"]=np.abs(tmp.D5_score-thr)
riskrows=[]
for cov in [0.50,0.60,0.70,0.80,0.90,1.00]:
    n=max(1,int(round(len(tmp)*cov)))
    z=tmp.sort_values("confidence",ascending=False).head(n).copy()
    pred=(z.D5_score>=thr).astype(int)
    err=float(np.mean(pred!=z.y))
    riskrows.append({"coverage":cov,"retained_n":n,"selective_error_rate":err,
                     "selective_accuracy":1-err,"mean_confidence":z.confidence.mean()})
riskdf=pd.DataFrame(riskrows)
riskdf.to_csv(OUT/"Table7b_Risk_Coverage.csv",index=False,encoding="utf-8-sig")
aurc=float(np.trapezoid(riskdf.selective_error_rate,riskdf.coverage))

# Save analysis matrix (no clean_th)
analysis_df=pd.concat([dev,test],ignore_index=True)
analysis_df=analysis_df.sort_values(["split","document_id","instance_id"]).reset_index(drop=True)
safe_cols=["instance_id","document_id","panel","family","severity","y","split"]+basecols+["D5_score"]
missing_cols=[c for c in safe_cols if c not in analysis_df.columns]
if missing_cols:
    raise SystemExit("Missing final analysis columns: "+", ".join(missing_cols))
analysis_df[safe_cols].to_csv(OUT/"M2_Final_Analysis_Matrix.csv",index=False,encoding="utf-8-sig")

# RQ map
rq=pd.DataFrame([
 ["RQ1","Detection accuracy of automated safeguards","Table2","D1-D5 AUROC/AUPRC/Sensitivity/Specificity/F1/MCC with document-bootstrap CIs"],
 ["RQ2","Which signal families contribute most","Table2, Table6","individual detectors + ablation deltas"],
 ["RQ3","Ensemble risk-score discrimination","Table2, Table7a, Table7b","D5 discrimination, Brier calibration, risk-coverage"],
 ["RQ4","Hardest controlled error families","Table3","family-specific D1-D5 performance"],
 ["RQ5","Variation by severity and discipline","Table4, Table5","D5 severity trend and discipline-specific performance"]
],columns=["RQ","question","outputs","primary_evidence"])
rq.to_csv(OUT/"M2_RQ_to_Results_Map.csv",index=False,encoding="utf-8-sig")

# Figures (matplotlib defaults only)
plt.figure(figsize=(7,5))
for det,col in detcols.items():
    fpr,tpr,_=roc_curve(test.y,test[col]);plt.plot(fpr,tpr,label=det)
plt.plot([0,1],[0,1],"--")
plt.xlabel("False positive rate");plt.ylabel("True positive rate");plt.legend();plt.tight_layout()
plt.savefig(FIG/"Figure2_ROC_Detectors.png",dpi=300);plt.close()

plt.figure(figsize=(7,5))
for det,col in detcols.items():
    pr,rc,_=precision_recall_curve(test.y,test[col]);plt.plot(rc,pr,label=det)
plt.xlabel("Recall");plt.ylabel("Precision");plt.legend();plt.tight_layout()
plt.savefig(FIG/"Figure3_PR_Detectors.png",dpi=300);plt.close()

order=["CLEAN","E1_POLARITY","E2_EPISTEMIC_FORCE","E3_METHOD_DESIGN","E4_EVIDENCE_OMISSION"]
plt.figure(figsize=(9,5))
data=[test.loc[test.family==x,"D5_score"].values for x in order]
plt.boxplot(data,tick_labels=order);plt.xticks(rotation=25,ha="right");plt.ylabel("D5 ensemble risk");plt.tight_layout()
plt.savefig(FIG/"Figure4_Risk_by_ErrorFamily.png",dpi=300);plt.close()

plt.figure(figsize=(7,5))
sorder=["subtle","moderate","severe"]
data=[pos.loc[pos.severity==x,"D5_score"].values for x in sorder]
plt.boxplot(data,tick_labels=sorder);plt.ylabel("D5 ensemble risk");plt.tight_layout()
plt.savefig(FIG/"Figure5_Risk_by_Severity.png",dpi=300);plt.close()

ab=pd.DataFrame(abl)
plt.figure(figsize=(7,5));plt.bar(ab.removed.astype(str),ab.delta_AUPRC_vs_full);plt.xlabel("Detector family removed");plt.ylabel("ΔAUPRC vs full ensemble");plt.tight_layout()
plt.savefig(FIG/"Figure6_Ablation_DeltaAUPRC.png",dpi=300);plt.close()

plt.figure(figsize=(6,5));plt.plot(cal.mean_predicted_risk,cal.observed_event_rate,marker="o");plt.plot([0,1],[0,1],"--");plt.xlabel("Mean predicted risk");plt.ylabel("Observed event rate");plt.tight_layout()
plt.savefig(FIG/"Figure7_Calibration.png",dpi=300);plt.close()

plt.figure(figsize=(6,5));plt.plot(riskdf.coverage,riskdf.selective_error_rate,marker="o");plt.xlabel("Coverage");plt.ylabel("Selective error rate");plt.tight_layout()
plt.savefig(FIG/"Figure8_Risk_Coverage.png",dpi=300);plt.close()

summary={
 "n_total":len(analysis_df),"n_documents":analysis_df.document_id.nunique(),"development_docs":len(devdocs),"test_docs":len(testdocs),
 "thresholds":thresholds,"D5_test_AUROC":full_auc,"D5_test_AUPRC":full_ap,
 "D5_test_Brier":brier_score_loss(test.y,test.D5_score),"risk_coverage_AURC":aurc,
 "bootstrap_B":B,"bootstrap_seed":BOOT_SEED,
 "claim_boundary":"Controlled perturbation benchmark; not natural-error prevalence or human safety certification."
}
(OUT/"M2_Final_Statistical_Summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
print(json.dumps(summary,indent=2))
print("M2 Stage 3.3 FINAL ANALYSIS COMPLETE")
