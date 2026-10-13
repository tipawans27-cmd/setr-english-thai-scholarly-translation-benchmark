
from pathlib import Path
import pandas as pd,numpy as np,re,json
from sentence_transformers import SentenceTransformer
ROOT=Path(__file__).resolve().parents[1];IN=ROOT/"input";OUT=ROOT/"outputs"
b=pd.read_csv(IN/"M2_SETR_Core_Balanced_400_v1.1.csv")
bt=pd.read_csv(OUT/"M2_Candidate_Backtranslations_400.csv")
if len(bt)!=400 or not (bt.status=="COMPLETE").all(): raise SystemExit("Need 400 COMPLETE candidate backtranslations")
df=b.merge(bt[["instance_id","candidate_bt_en"]],on="instance_id",validate="one_to_one")

repo="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
rev="e8f8c211226b894fcb81acc59f3b34ba3efd5f42"
model=SentenceTransformer(repo,revision=rev,device="cpu")
a=model.encode(df.source_en.fillna("").tolist(),normalize_embeddings=True,batch_size=16,show_progress_bar=True)
c=model.encode(df.candidate_bt_en.fillna("").tolist(),normalize_embeddings=True,batch_size=16,show_progress_bar=True)
cos=np.sum(a*c,axis=1)

tok_re=re.compile(r"[A-Za-z][A-Za-z'-]*")
num_re=re.compile(r'(?<!\w)\d+(?:[.,]\d+)?%?')
neg_re=re.compile(r'\b(?:no|not|never|without|neither|nor|none)\b',re.I)
def toks(t):return set(tok_re.findall(str(t).lower()))
def jacc(a,b):
    a=toks(a);b=toks(b)
    return len(a&b)/max(len(a|b),1)
def nums(t):return [x.replace(",","").replace("%","") for x in num_re.findall(str(t))]
def num_mismatch(a,b):return int(sorted(nums(a))!=sorted(nums(b)))

out=df[["instance_id","document_id","panel","label","family","severity"]].copy()
out.columns=["instance_id","document_id","panel","true_label","true_family","severity"]
out["bt_cosine_en_en"]=cos
out["bt_semantic_risk"]=1-cos
out["bt_token_jaccard"]=[jacc(x,y) for x,y in zip(df.source_en,df.candidate_bt_en)]
out["bt_token_jaccard_risk"]=1-out["bt_token_jaccard"]
out["bt_number_mismatch"]=[num_mismatch(x,y) for x,y in zip(df.source_en,df.candidate_bt_en)]
out["bt_neg_presence_mismatch"]=[int(bool(neg_re.search(str(x)))!=bool(neg_re.search(str(y)))) for x,y in zip(df.source_en,df.candidate_bt_en)]
out.to_csv(OUT/"M2_D3_Backtranslation_Signals.csv",index=False,encoding="utf-8-sig")
print("D3 rows:",len(out))
