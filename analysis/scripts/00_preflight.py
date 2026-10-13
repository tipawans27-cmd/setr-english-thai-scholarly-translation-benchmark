
from pathlib import Path
import pandas as pd, json, hashlib
ROOT=Path(__file__).resolve().parents[1]
IN=ROOT/"input"; OUT=ROOT/"outputs"
OUT.mkdir(exist_ok=True)

req=["M2_SETR_Core_Balanced_400_v1.1.csv","M2_OpenThai_SETR_400_v1.2.csv"]
missing=[x for x in req if not (IN/x).exists()]
if missing: raise SystemExit("Missing required input(s): "+", ".join(missing))

b=pd.read_csv(IN/req[0])
o=pd.read_csv(IN/req[1])

checks={}
checks["benchmark_rows"]=len(b)
checks["benchmark_unique_instances"]=b.instance_id.nunique()
checks["benchmark_unique_docs"]=b.document_id.nunique()
checks["instances_per_doc_min"]=int(b.groupby("document_id").size().min())
checks["instances_per_doc_max"]=int(b.groupby("document_id").size().max())
checks["family_counts"]=b.family.value_counts().to_dict()

checks["openthai_rows"]=len(o)
checks["openthai_unique_instances"]=o.instance_id.nunique()
checks["openthai_complete"]=int((o.status=="COMPLETE").sum())
checks["openthai_unique_docs"]=o.document_id.nunique()

bids=set(b.instance_id.astype(str)); oids=set(o.instance_id.astype(str))
checks["id_alignment"]=bids==oids

docs=sorted(b.document_id.astype(str).unique(),
            key=lambda d:hashlib.sha256(f"2026101203|{d}".encode()).hexdigest())
dev=set(docs[:40]); test=set(docs[40:])
checks["dev_docs"]=len(dev);checks["test_docs"]=len(test);checks["split_overlap"]=len(dev&test)
checks["dev_rows"]=int(b.document_id.astype(str).isin(dev).sum())
checks["test_rows"]=int(b.document_id.astype(str).isin(test).sum())

checks["pass"]=(
    len(b)==400 and b.instance_id.nunique()==400 and b.document_id.nunique()==80 and
    checks["instances_per_doc_min"]==5 and checks["instances_per_doc_max"]==5 and
    len(o)==400 and checks["openthai_complete"]==400 and o.instance_id.nunique()==400 and
    checks["id_alignment"] and len(dev)==40 and len(test)==40 and len(dev&test)==0
)
(OUT/"M2_Stage3_3_Preflight.json").write_text(json.dumps(checks,indent=2),encoding="utf-8")
print(json.dumps(checks,indent=2))
if not checks["pass"]: raise SystemExit("M2 Stage 3.3 PRE-FLIGHT FAILED")
print("M2 STAGE 3.3 PRE-FLIGHT PASS")
