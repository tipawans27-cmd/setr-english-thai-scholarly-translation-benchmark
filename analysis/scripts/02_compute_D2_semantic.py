
from pathlib import Path
import pandas as pd, numpy as np, json, os
from sentence_transformers import SentenceTransformer
ROOT=Path(__file__).resolve().parents[1]; IN=ROOT/"input"; OUT=ROOT/"outputs"
df=pd.read_csv(IN/"M2_SETR_Core_Balanced_400_v1.1.csv")
repo="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
rev="e8f8c211226b894fcb81acc59f3b34ba3efd5f42"
model=SentenceTransformer(repo,revision=rev,device="cpu")
es=model.encode(df.source_en.fillna("").tolist(),normalize_embeddings=True,batch_size=16,show_progress_bar=True)
et=model.encode(df.candidate_th.fillna("").tolist(),normalize_embeddings=True,batch_size=16,show_progress_bar=True)
cos=np.sum(es*et,axis=1)
out=df[["instance_id","document_id","panel","label","family","severity"]].copy()
out.columns=["instance_id","document_id","panel","true_label","true_family","severity"]
out["semantic_cosine_en_th"]=cos
out["D2_semantic_risk"]=1-cos
out.to_csv(OUT/"M2_D2_Semantic_Signals.csv",index=False,encoding="utf-8-sig")
meta={"model":repo,"revision":rev,"n":len(out)}
(OUT/"M2_D2_Model_Metadata.json").write_text(json.dumps(meta,indent=2),encoding="utf-8")
print("D2 rows:",len(out))
