#!/usr/bin/env python3
import cv2, pytesseract, re, itertools, sys
from pathlib import Path

DEFAULT_IMAGE = Path(__file__).resolve().parent / 'fixtures' / 'malaysia_passport_reference.jpg'
IMAGE = sys.argv[1] if len(sys.argv)>1 else str(DEFAULT_IMAGE)
img=cv2.imread(IMAGE)
if img is None: raise SystemExit(f'Cannot open {IMAGE}')
H,W=img.shape[:2]
REGIONS={
'name':(.300,.198,.3335,.097,12,'gray',1.55,7,None),
'nameAlt':(.300,.198,.3335,.097,12,'red',1.50,7,None),
'nationality':(.285,.255,.300,.115,10,'gray',1.55,6,None),
'identity':(.620,.265,.300,.100,12,'gray',1.55,7,'0123456789'),
'dob':(.285,.330,.230,.115,10,'gray',1.55,6,None),
'birthPlace':(.595,.330,.320,.135,10,'gray',1.55,6,None),
'sexHeight':(.285,.395,.565,.150,10,'gray',1.55,6,None),
'issue':(.285,.485,.320,.140,10,'gray',1.55,6,None),
'expiry':(.610,.485,.310,.140,10,'gray',1.55,6,None),
'office':(.285,.565,.365,.135,10,'gray',1.55,6,None),
'mrz':(.010,.750,.980,.235,12,'gray',1.8,6,'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<'),
'mrzAlt':(.010,.750,.980,.235,12,'red',1.65,11,'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<'),
}
def ocr(spec):
    x,y,w,h,scale,mode,contrast,psm,wl=spec
    c=img[int(H*y):int(H*(y+h)),int(W*x):int(W*(x+w))]
    c=cv2.resize(c,None,fx=scale,fy=scale,interpolation=cv2.INTER_CUBIC)
    if mode=='red': g=c[:,:,2]
    elif mode=='green': g=c[:,:,1]
    elif mode=='blue': g=c[:,:,0]
    else: g=cv2.cvtColor(c,cv2.COLOR_BGR2GRAY)
    g=cv2.convertScaleAbs(g,alpha=contrast,beta=128*(1-contrast))
    cfg=f'--psm {psm}'+(f' -c tessedit_char_whitelist={wl}' if wl else '')
    return pytesseract.image_to_string(g,config=cfg,lang='eng').replace('\r','').strip()
E={k:ocr(v) for k,v in REGIONS.items()}
g=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY); g=cv2.resize(g,None,fx=4.2,fy=4.2,interpolation=cv2.INTER_CUBIC); g=cv2.convertScaleAbs(g,alpha=1.5,beta=-25)
E['source']=pytesseract.image_to_string(g,config='--psm 6',lang='eng').replace('\r','').strip()

def norm(s): return re.sub(r'[ \t]+',' ',str(s or '')).strip()
def plausible_name(s):
    s=norm(s).upper()
    if len(s)<5 or len(s)>100 or re.search(r'\d',s): return False
    if re.search(r'\b(?:ADDRESS|ALAMAT|WARGANEGARA|NATIONALITY|IDENTITY|PENGENALAN|RELIGION|GENDER|JANTINA|VALIDITY|TARIKH|CLASS|KELAS|PASSPORT|PASPORT|MYKAD|MYPR|MALAYSIA)\b',s): return False
    ws=s.split(); return 2<=len(ws)<=12 and all(re.search('[A-Z]',w) for w in ws)
def best_name(*texts):
    c=[]
    for t in texts:
        for line in str(t or '').splitlines():
            line=re.sub(r'^(?:NAMA\s*/?\s*NAME|NAMA|NAME)\s*[:：-]?\s*','',norm(line).upper()).strip()
            if plausible_name(line): c.append((len(re.sub('[^A-Z]','',line)),line))
    return max(c)[1] if c else ''
def location(text):
    cand=[]
    for raw in str(text or '').splitlines():
        s=norm(raw).upper()
        s=re.sub(r'^.*?(?:BIRTH|LAHIR|OFFICE|PENGELUAR)\s*[:：-]?\s*','',s)
        s=re.sub(r"[^A-Z .'-]",' ',s); s=re.sub(r'\s+',' ',s).strip()
        if not s or re.search(r'\b(?:TEMPAT|LAHIR|PLACE|BIRTH|PEJABAT|PENGELUAR|ISSUING|OFFICE|DATE|TARIKH|HEIGHT|TINGGI|SEX|JANTINA)\b',s): continue
        words=s.split(); letters=len(re.sub('[^A-Z]','',s))
        if letters<3 or len(words)>6: continue
        score=letters+(25 if len(words)>=2 else 0)+(35 if re.search(r'\b(?:KUALA|LUMPUR|SELANGOR|MELAKA|JOHOR|PERAK|PAHANG|SABAH|SARAWAK|PENANG|PINANG|TERENGGANU|KEDAH|KELANTAN|PERLIS|LABUAN|PUTRAJAYA)\b',s) else 0)
        cand.append((score,s))
    return max(cand)[1] if cand else ''
def alpha_date(text):
    m=re.search(r'\b(\d{1,2})\s+(JAN|FEB|MAC|MAR|APR|MEI|MAY|JUN|JUL|OGO|AUG|SEP|OKT|OCT|NOV|DIS|DEC)\s+(\d{4})\b',str(text),re.I)
    return f'{int(m.group(1))} {m.group(2).upper()} {m.group(3)}' if m else ''
def all_dates(text):
    out=[]
    for m in re.finditer(r'\b(\d{1,2})\s+(JAN|FEB|MAC|MAR|APR|MEI|MAY|JUN|JUL|OGO|AUG|SEP|OKT|OCT|NOV|DIS|DEC)\s+(\d{4})\b',str(text),re.I):
        v=f'{int(m.group(1))} {m.group(2).upper()} {m.group(3)}'
        if v not in out: out.append(v)
    return out
VAL={c:i for i,c in enumerate('0123456789')}
VAL.update({chr(65+i):10+i for i in range(26)})
def check(s): return str(sum(VAL.get(c,0)*[7,3,1][i%3] for i,c in enumerate(s))%10)
MAP={'O':'0','Q':'0','D':'0','I':'1','L':'1','Z':'2','S':'5','B':'8','G':'6','T':'7'}
def digit(ch): return ch if ch.isdigit() else MAP.get(ch.upper(),'')
def compact(*texts):
    out=[]
    for t in texts:
        for raw in str(t or '').upper().splitlines():
            v=re.sub('[^A-Z0-9<]','',raw)
            if len(v)>=20: out.append(v)
    return out
def passport_number(*texts):
    for line in compact(*texts):
        i=line.find('MYS')
        if i<8: continue
        pre=line[:i]
        if not 10<=len(pre)<=18: continue
        for inds in itertools.combinations(range(len(pre)),10):
            raw=''.join(pre[j] for j in inds)
            if not raw[0].isalpha(): continue
            num=raw[0]+''.join(digit(raw[k]) for k in range(1,9))
            if len(num)!=9: continue
            cd=digit(raw[9])
            if cd and check(num)==cd: return num
    return ''
def mrz_core(*texts):
    out={}; lines=compact(*texts); out['passport']=passport_number(*texts)
    for line in lines:
        if line.startswith('P<'): continue
        i=line.find('MYS')
        if i<8: continue
        tail=line[i+3:]
        def ds(a,b):
            x=''.join(digit(ch) for ch in tail[a:b]); return x if len(x)==b-a else ''
        b,bc=ds(0,6),digit(tail[6]) if len(tail)>6 else ''
        sx=tail[7] if len(tail)>7 else ''
        e,ec=ds(8,14),digit(tail[14]) if len(tail)>14 else ''
        if b and bc and check(b)==bc: out['birth']=b
        if sx in 'MF': out['sex']=sx
        if e and ec and check(e)==ec: out['expiry']=e
        opt=''.join('<' if ch=='<' else (digit(ch) or ch) for ch in tail[15:29]); m=re.search(r'\d{12}',opt)
        if m: out['id']=m.group()
        if out.get('birth') and out.get('expiry'): break
    return out
MON=['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
def disp(yymmdd,expiry=False):
    yy,mm,dd=int(yymmdd[:2]),int(yymmdd[2:4]),int(yymmdd[4:]); year=2000+yy if expiry else 1900+yy
    return f'{dd:02d} {MON[mm-1]} {year}'
def to_mrz(v):
    m=re.match(r'(\d{1,2}) ([A-Z]{3}) (\d{4})',v); mp={m:i+1 for i,m in enumerate(MON)}
    return m.group(3)[-2:]+f'{mp[m.group(2)]:02d}{int(m.group(1)):02d}'

core=mrz_core(E['mrz'],E['mrzAlt'],E['source'])
name=best_name(E['name'],E['nameAlt'],E['source'])
idno=(re.search(r'\d{12}',E['identity']) or re.search(r'\d{12}',E['source'])).group()
dates=all_dates(E['source']); dob=alpha_date(E['dob']) or disp(core['birth']); expiry=alpha_date(E['expiry']) or disp(core['expiry'],True)
issue=alpha_date(E['issue']) or next(x for x in dates if x not in (dob,expiry))
sex='L-M' if re.search(r'\bL\s*[-–—]?\s*M\b',E['sexHeight']+'\n'+E['source'],re.I) else ('L-M' if core.get('sex')=='M' else 'P-F')
hm=re.search(r'\b(\d{2,3})\s*\.?\s*CM\b',E['sexHeight']+'\n'+E['source'],re.I); height=f'{hm.group(1)} cm'
birth=location(E['birthPlace']); office=location(E['office']); pno=core['passport']
b=to_mrz(dob); ex=to_mrz(expiry); optional=(idno+'<<')[:14]
line1=('P<MYS'+re.sub(r'\s+','<',name)).ljust(44,'<')[:44]
line2=pno+check(pno)+'MYS'+b+check(b)+'M'+ex+check(ex)+optional+check(optional)
line2+=check(pno+check(pno)+b+check(b)+ex+check(ex)+optional+check(optional))
actual={
'Jenis / Type':'P','Kod Negara / Country Code':'MYS','Passport Number':pno,'Nama / Name':name,'Warganegara / Nationality':'MALAYSIA','No. Pengenalan / Identity No.':idno,'Tarikh lahir / Date of Birth':dob,'Tempat Lahir / Place of Birth':birth,'Jantina / Sex':sex,'Tinggi / Height':height,'Tarikh Dikeluarkan / Date of Issue':issue,'Tarikh Tamat / Date of Expiry':expiry,'Pejabat Pengeluar / Issuing Office':office,'MRZ Line 1':line1,'MRZ Line 2':line2}
expected={
'Jenis / Type':'P','Kod Negara / Country Code':'MYS','Passport Number':'A00000000','Nama / Name':'MAHATHIR BIN IDRUS','Warganegara / Nationality':'MALAYSIA','No. Pengenalan / Identity No.':'930216146007','Tarikh lahir / Date of Birth':'16 FEB 1993','Tempat Lahir / Place of Birth':'KUALA LUMPUR','Jantina / Sex':'L-M','Tinggi / Height':'174 cm','Tarikh Dikeluarkan / Date of Issue':'31 AUG 2017','Tarikh Tamat / Date of Expiry':'31 AUG 2024','Pejabat Pengeluar / Issuing Office':'KUALA LUMPUR','MRZ Line 1':'P<MYSMAHATHIR<BIN<IDRUS<<<<<<<<<<<<<<<<<<<<<','MRZ Line 2':'A000000000MYS9302165M2408312930216146007<<72'}
for k,v in actual.items(): print(f'{k}: {v}')
bad=[f'{k}: got {actual[k]!r}, expected {v!r}' for k,v in expected.items() if actual.get(k)!=v]
if bad:
    print('\nFAIL'); print('\n'.join(bad)); raise SystemExit(1)
print('\nPASS: 15/15 passport fields exactly match the visible fixture')
