
from pathlib import Path
import os,csv,json,re
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
ROOT=Path(__file__).resolve().parents[1]; IN=ROOT/"input"; OUT=ROOT/"outputs"
df=pd.read_csv(IN/"M2_SETR_Core_Balanced_400_v1.1.csv")
outpath=OUT/"M2_Candidate_Backtranslations_400.csv"
repo="Helsinki-NLP/opus-mt-th-en"; rev="0fff80b"

stage2=os.getenv("TMEI_STAGE2_DIR","").strip()
local=None
if stage2:
    p=Path(stage2)/"models"/"MOD_BT_PRIMARY_CPU"
    if p.exists(): local=str(p)
source=local or repo
print("Backtranslation model source:",source)

tok=AutoTokenizer.from_pretrained(source,revision=None if local else rev)
model=AutoModelForSeq2SeqLM.from_pretrained(source,revision=None if local else rev)
model.to("cpu");model.eval()

# Conservative sentence/chunk handling for CPU.
def split_chunks(text,max_tokens=400):
    text=str(text).strip()
    if not text:return []
    sents=[x.strip() for x in re.split(r'(?<=[.!?。])\s+|[\r\n]+',text) if x.strip()]
    if not sents:sents=[text]
    chunks=[];cur=[]
    for s in sents:
        candidate=(" ".join(cur+[s])).strip()
        n=len(tok(candidate,add_special_tokens=True,truncation=False)["input_ids"])
        if n<=max_tokens:
            cur.append(s)
        else:
            if cur: chunks.append(" ".join(cur));cur=[]
            ids=tok(s,add_special_tokens=False,truncation=False)["input_ids"]
            for i in range(0,len(ids),max_tokens-8):
                chunks.append(tok.decode(ids[i:i+max_tokens-8],skip_special_tokens=True))
    if cur:chunks.append(" ".join(cur))
    return chunks

existing={}
if outpath.exists():
    old=pd.read_csv(outpath)
    existing={str(r.instance_id):r for _,r in old.iterrows() if str(r.status)=="COMPLETE"}

rows=[]
for i,r in df.iterrows():
    iid=str(r.instance_id)
    if iid in existing:
        z=existing[iid].to_dict();rows.append(z);print(i+1,400,"SKIP");continue
    z={"instance_id":iid,"document_id":r.document_id,"panel":r.panel,"candidate_bt_en":"","bt_chunks":0,
       "model_repo":repo,"model_revision":rev,"status":"","error":""}
    try:
        outs=[]
        chunks=split_chunks(r.candidate_th)
        with torch.inference_mode():
            for ch in chunks:
                batch=tok(ch,return_tensors="pt",truncation=True,max_length=512)
                gen=model.generate(**batch,num_beams=1,do_sample=False,max_new_tokens=512,renormalize_logits=True)
                outs.append(tok.decode(gen[0],skip_special_tokens=True))
        z["candidate_bt_en"]=" ".join(outs).strip();z["bt_chunks"]=len(chunks);z["status"]="COMPLETE"
    except Exception as e:
        z["status"]="ERROR";z["error"]=repr(e)
    rows.append(z)
    pd.DataFrame(rows).to_csv(outpath,index=False,encoding="utf-8-sig")
    print(i+1,400,z["status"])
print("COMPLETE",sum(str(x["status"])=="COMPLETE" for x in rows),"/",len(rows))
