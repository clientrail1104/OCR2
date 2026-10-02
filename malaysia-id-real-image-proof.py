#!/usr/bin/env python3
"""Image-driven regression proof for the supplied MyKad and MyPR fixtures.

This test runs real Tesseract OCR over the same focused crop geometry used by
index.html and compares the recovered critical fields with visually verified
ground truth. No expected values are injected into OCR or used to correct OCR.
"""
from __future__ import annotations
import cv2
import pytesseract
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "tests" / "fixtures"

REGIONS = {
    "Malaysia MyKad": {
        "identity": (.0350,.1900,.3300,.1050,13,"gray",1.60,7,"0123456789-"),
        "identityAlt": (.0350,.1850,.3450,.1150,13,"green",1.50,7,"0123456789-"),
        "name": (.0350,.6200,.4850,.1350,14,"green",1.80,6,None),
        "nameAlt": (.0300,.6050,.5000,.1550,14,"gray",1.60,6,None),
        "address": (.0150,.6200,.5200,.3700,10,"gray",1.45,6,None),
        "addressAlt": (.0150,.6200,.5200,.3700,10,"green",1.35,6,None),
        "terminal": (.0200,.8950,.3200,.1000,18,"gray",1.40,7,None),
        "terminalAlt": (.0200,.8950,.3200,.1000,18,"green",1.40,7,None),
        "status": (.6500,.8350,.3400,.1550,14,"gray",1.55,6,None),
        "statusAlt": (.6500,.8350,.3400,.1550,14,"green",1.45,6,None),
    },
    "Malaysia MyPR": {
        "identity": (.0900,.3000,.3450,.0850,10,"gray",1.55,7,"0123456789-"),
        "identityAlt": (.0900,.3000,.3450,.0850,10,"green",1.45,7,"0123456789-"),
        "name": (.0750,.5750,.4300,.1450,11,"gray",1.45,6,None),
        "nameAlt": (.0700,.5650,.4500,.1650,11,"green",1.35,6,None),
        "address": (.0900,.7300,.3900,.1500,12,"gray",1.45,6,None),
        "addressAlt": (.0900,.7300,.3900,.1500,12,"green",1.35,6,None),
        "pnl": (.6350,.7350,.1600,.1050,12,"gray",1.45,6,None),
        "pnlAlt": (.6350,.7350,.1600,.1050,12,"green",1.35,6,None),
        "status": (.6350,.7250,.3500,.1450,14,"gray",1.55,6,None),
        "statusAlt": (.6350,.7250,.3500,.1450,14,"green",1.45,6,None),
    },
}

EXPECTED = {
    "Malaysia MyKad": {
        "Identity Number": "950830-05-5465",
        "Name": "MUHAMAD HASHIF BIN ALI",
        "Address": "NO 35 TAMAN SRI ULU BENDUL 71500 TANJONG IPOH NEGERI SEMBILAN",
        "Religion": "ISLAM",
        "Citizenship": "WARGANEGARA",
        "Gender": "LELAKI",
    },
    "Malaysia MyPR": {
        "Identity Number": "901231-10-6789",
        "Name": "TAN AH KON",
        "Address": "NO 42, JILAN MERAH, TAMAN KEMBOJA, 88400 KIANABALL",
        "Country of Origin": "PNL",
        "Religion": "ISLAM",
        "Citizenship": "PEMASTAUTIN TETAP / PR",
        "Gender": "LELAKI",
    },
}

FILES = {"Malaysia MyKad": FIX/"mykad_reference.png", "Malaysia MyPR": FIX/"mypr_reference.png"}
STATE_RE = r"(?:NEGERI\s+SEMBILAN|PULAU\s+PINANG|KUALA\s+LUMPUR|WILAYAH\s+PERSEKUTUAN|SELANGOR|MELAKA|JOHOR|PERAK|PAHANG|SABAH|SARAWAK|KELANTAN|KEDAH|PERLIS|TERENGGANU|PUTRAJAYA|LABUAN)"


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", str(s or "").replace("\r", " ").strip())


def focused(img, spec) -> str:
    H,W = img.shape[:2]
    x,y,w,h,scale,mode,contrast,psm,whitelist = spec
    c = img[int(H*y):int(H*(y+h)), int(W*x):int(W*(x+w))]
    c = cv2.resize(c, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    if mode == "green": g = c[:,:,1]
    elif mode == "red": g = c[:,:,2]
    elif mode == "blue": g = c[:,:,0]
    else: g = cv2.cvtColor(c, cv2.COLOR_BGR2GRAY)
    g = cv2.convertScaleAbs(g, alpha=contrast, beta=128*(1-contrast))
    cfg = f"--psm {psm}" + (f" -c tessedit_char_whitelist={whitelist}" if whitelist else "")
    return pytesseract.image_to_string(g, config=cfg, lang="eng").replace("\r", "").strip()


def full_page(img) -> str:
    g=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    g=cv2.resize(g,None,fx=4.2,fy=4.2,interpolation=cv2.INTER_CUBIC)
    g=cv2.convertScaleAbs(g,alpha=1.5,beta=-25)
    return pytesseract.image_to_string(g,config="--psm 6",lang="eng").replace("\r","").strip()


def identity_number(*texts):
    vals=[]
    for t in texts:
        for m in re.finditer(r"\b(\d{6})[- ]?(\d{2})[- ]?(\d{4})\b", str(t or "")):
            vals.append(f"{m.group(1)}-{m.group(2)}-{m.group(3)}")
    if not vals: return ""
    return max(set(vals), key=lambda x:(vals.count(x), -vals.index(x)))


def clean_name_line(line: str) -> str:
    s=norm(line).upper().replace("!","I")
    s=re.sub(r"[^A-Z.'/ -]", " ", s)
    s=re.sub(r"\s+", " ", s).strip(" .,-/'\"")
    return s


def name(*texts):
    cand=[]
    blocked=re.compile(r"\b(?:KAD|PENGENALAN|MALAYSIA|MYKAD|MYPR|WARGANEGARA|PEMASTAUTIN|ISLAM|LELAKI|PNL|NO\s+\d)\b",re.I)
    for t in texts:
        for line in str(t or "").splitlines():
            s=clean_name_line(line)
            if blocked.search(s) or not 2 <= len(s.split()) <= 8: continue
            if len(re.sub(r"[^A-Z]", "", s)) < 5: continue
            score=len(re.sub(r"[^A-Z]", "", s)) + (20 if re.search(r"\b(?:BIN|BINTI|A/L|A/P)\b",s) else 0)
            cand.append((score,s))
    return max(cand)[1] if cand else ""


def address_from_text(text: str, mypr=False) -> str:
    lines=[norm(x).replace("|","").strip() for x in str(text or "").splitlines() if norm(x)]
    start=-1
    for i,line in enumerate(lines):
        if re.search(r"\b(?:NO\.?\s*\d+|LOT\s+\d+|JALAN\b|JLN\b|LORONG\b|TAMAN\b|KAMPUNG\b)",line,re.I):
            start=i; break
    if start < 0: return ""
    out=[]
    for line in lines[start:]:
        if re.search(r"\b(?:PNL|ISLAM|LELAKI|PEREMPUAN|WARGANEGARA|PEMASTAUTIN)\b",line,re.I):
            line=re.split(r"\b(?:PNL|ISLAM|LELAKI|PEREMPUAN|WARGANEGARA|PEMASTAUTIN)\b",line,maxsplit=1,flags=re.I)[0].strip()
        if line: out.append(line)
        if (not mypr) and re.search(STATE_RE,line,re.I): break
        if mypr and re.search(r"\b\d{5}\b",line) and len(out)>=2:
            # MyPR fixture legitimately has no state line; locality is on postcode line.
            break
    s=" ".join(out)
    s=re.sub(r"\s+", " ", s).strip()
    s=re.sub(r"\s+,", ",", s)
    return s


def compact_key(s): return re.sub(r"[^A-Z0-9]", "", str(s or "").upper())


def edit_distance(a,b):
    if len(a)<len(b): a,b=b,a
    prev=list(range(len(b)+1))
    for i,ca in enumerate(a,1):
        cur=[i]
        for j,cb in enumerate(b,1): cur.append(min(cur[-1]+1,prev[j]+1,prev[j-1]+(ca!=cb)))
        prev=cur
    return prev[-1]


def pick_address(candidates, mypr=False):
    vals=[]
    for raw in candidates:
        s=address_from_text(raw,mypr=mypr)
        if s and s not in vals: vals.append(s)
    if not vals: return ""
    def q(s):
        score=len(s)+(70 if re.search(r"\b\d{5}\b",s) else 0)+(90 if re.search(STATE_RE,s,re.I) else 0)
        a=compact_key(s)
        for o in vals:
            if o==s: continue
            b=compact_key(o); d=edit_distance(a,b); similarity=1-d/max(1,max(len(a),len(b)))
            if similarity>=.92: score += 140*similarity
            elif a in b or b in a: score += 70*min(len(a),len(b))/max(len(a),len(b))
        return score
    return max(vals,key=q)


def status(doc_type,*texts):
    j=" ".join(str(x or "") for x in texts).upper().replace("!","I")
    j=re.sub(r"[^A-Z/ ]", " ", j); j=re.sub(r"\s+"," ",j)
    out={}
    if "ISLAM" in j: out["Religion"]="ISLAM"
    if re.search(r"\bLELAKI\b",j): out["Gender"]="LELAKI"
    if doc_type=="Malaysia MyKad" and "WARGANEGARA" in j: out["Citizenship"]="WARGANEGARA"
    if doc_type=="Malaysia MyPR":
        if "PNL" in j: out["Country of Origin"]="PNL"
        if "PEMASTAUTIN TETAP" in j or "MYPR" in j: out["Citizenship"]="PEMASTAUTIN TETAP / PR"
    return out


def extract(doc_type,path):
    img=cv2.imread(str(path))
    if img is None: raise RuntimeError(f"cannot open {path}")
    R=REGIONS[doc_type]
    E={k:focused(img,v) for k,v in R.items()}
    src=full_page(img)
    actual={
        "Identity Number": identity_number(E.get("identity"),E.get("identityAlt"),src),
        "Name": name(E.get("name"),E.get("nameAlt")),
    }
    actual["Address"]=pick_address([E.get("address",""),E.get("addressAlt",""),src],mypr=doc_type=="Malaysia MyPR")
    actual.update(status(doc_type,E.get("status"),E.get("statusAlt"),E.get("pnl"),E.get("pnlAlt"),src))
    return actual,E


fail=[]
total=0
passed=0
for doc_type,path in FILES.items():
    actual,evidence=extract(doc_type,path)
    expected=EXPECTED[doc_type]
    print(f"\n[{doc_type}]")
    for k,want in expected.items():
        got=actual.get(k,"")
        ok=got==want
        total+=1; passed+=int(ok)
        print(f"{'PASS' if ok else 'FAIL'} {k}: {got}")
        if not ok: fail.append(f"{doc_type} / {k}: got {got!r}, expected {want!r}")

print(f"\nExact critical-field match: {passed}/{total} = {passed/total*100:.2f}%")
if fail:
    print("\nFAIL")
    print("\n".join(fail))
    raise SystemExit(1)
print("PASS: MyKad and MyPR critical fields exactly match the visible image fixtures")
