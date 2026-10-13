
from pathlib import Path
import pandas as pd, re, json, math
ROOT=Path(__file__).resolve().parents[1]; IN=ROOT/"input"; OUT=ROOT/"outputs"
df=pd.read_csv(IN/"M2_SETR_Core_Balanced_400_v1.1.csv")

num_re=re.compile(r'(?<!\w)\d+(?:[.,]\d+)?%?')
acr_re=re.compile(r'\b[A-Z][A-Z0-9-]{1,}\b')
en_neg=re.compile(r'\b(?:no|not|never|without|neither|nor|none|non[- ]?)\b',re.I)
th_neg=re.compile(r'(?:ไม่|ไม่มี|มิได้|ปราศจาก|ไร้)')
en_hedge=re.compile(r'\b(?:may|might|could|possibly|possible|potentially|likely|suggest(?:s|ed)?|indicat(?:e|es|ed)|appears?|seems?)\b',re.I)
th_hedge=re.compile(r'(?:อาจ|น่าจะ|เป็นไปได้|มีแนวโน้ม|ชี้ให้เห็น|บ่งชี้)')
en_cert=re.compile(r'\b(?:prove(?:s|d)?|confirm(?:s|ed)?|demonstrat(?:e|es|ed)|establish(?:es|ed)?|clearly|definitively)\b',re.I)
th_cert=re.compile(r'(?:พิสูจน์|ยืนยัน|อย่างชัดเจน|แน่นอน|แสดงให้เห็นอย่างชัดเจน)')

method_pairs=[
 ("rct", re.compile(r'\b(?:randomi[sz]ed controlled trial|randomi[sz]ed trial|rct)\b',re.I), re.compile(r'(?:การทดลองแบบสุ่มมีกลุ่มควบคุม|การทดลองแบบสุ่ม|อาร์ซีที)')),
 ("cross_sectional",re.compile(r'\bcross[- ]sectional\b',re.I),re.compile(r'(?:ภาคตัดขวาง|ตัดขวาง)')),
 ("longitudinal",re.compile(r'\blongitudinal\b',re.I),re.compile(r'(?:ตามยาว|ระยะยาว|ติดตามผลหลายช่วงเวลา)')),
 ("survey",re.compile(r'\bsurvey\b',re.I),re.compile(r'(?:การสำรวจ|แบบสำรวจ)')),
 ("qualitative",re.compile(r'\bqualitative\b',re.I),re.compile(r'(?:เชิงคุณภาพ|การวิจัยคุณภาพ)')),
 ("systematic_review",re.compile(r'\bsystematic review\b',re.I),re.compile(r'(?:การทบทวนอย่างเป็นระบบ|ทบทวนวรรณกรรมอย่างเป็นระบบ)')),
 ("meta_analysis",re.compile(r'\bmeta[- ]analysis\b',re.I),re.compile(r'(?:การวิเคราะห์อภิมาน|เมตาอะนาลิซิส)')),
 ("experiment",re.compile(r'\bexperiment(?:al)?\b',re.I),re.compile(r'(?:การทดลอง|เชิงทดลอง)')),
]

def norm_nums(t):
    return [x.replace(",","").replace("%","") for x in num_re.findall(str(t))]
def recall(src,cand):
    s=norm_nums(src); c=norm_nums(cand)
    if not s:return 1.0
    cc=list(c); hit=0
    for x in s:
        if x in cc: hit+=1;cc.remove(x)
    return hit/len(s)
def acr_recall(src,cand):
    s=acr_re.findall(str(src)); c=set(acr_re.findall(str(cand)))
    return 1.0 if not s else sum(x in c for x in s)/len(s)
def method_mismatch(src,cand):
    vals=[]
    for _,er,tr in method_pairs:
        e=bool(er.search(str(src))); t=bool(tr.search(str(cand)))
        vals.append(int(e!=t))
    return sum(vals),sum(int(bool(er.search(str(src)))) for _,er,tr in method_pairs)

rows=[]
for _,r in df.iterrows():
    src=str(r.source_en); th=str(r.candidate_th)
    nrec=recall(src,th); arec=acr_recall(src,th)
    mm,ms=method_mismatch(src,th)
    enneg=len(en_neg.findall(src));thneg=len(th_neg.findall(th))
    enh=len(en_hedge.findall(src));thh=len(th_hedge.findall(th))
    enc=len(en_cert.findall(src));thc=len(th_cert.findall(th))
    rows.append({
      "instance_id":r.instance_id,"document_id":r.document_id,"panel":r.panel,
      "true_label":int(r.label),"true_family":r.family,"severity":r.severity,
      "det_number_recall":nrec,"det_number_mismatch":1-nrec,
      "det_acronym_recall":arec,"det_acronym_mismatch":1-arec,
      "det_neg_presence_mismatch":int((enneg>0)!=(thneg>0)),
      "det_neg_count_absdiff":abs(enneg-thneg),
      "det_hedge_presence_mismatch":int((enh>0)!=(thh>0)),
      "det_hedge_count_absdiff":abs(enh-thh),
      "det_certainty_presence_mismatch":int((enc>0)!=(thc>0)),
      "det_certainty_count_absdiff":abs(enc-thc),
      "det_method_concept_mismatch_count":mm,
      "det_source_method_concepts":ms,
      "det_char_ratio_th_en":len(th)/max(len(src),1),
      "det_log_char_ratio_abs":abs(math.log(max(len(th),1)/max(len(src),1)))
    })
out=pd.DataFrame(rows)
out.to_csv(OUT/"M2_D1_Deterministic_Signals.csv",index=False,encoding="utf-8-sig")
print("D1 rows:",len(out),"unique IDs:",out.instance_id.nunique())
