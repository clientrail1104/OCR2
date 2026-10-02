#!/usr/bin/env python3
from PIL import Image, ImageEnhance, ImageFilter
from pathlib import Path
import pytesseract, io, json, re, time

ROOT=Path(__file__).resolve().parents[1]
SAMPLES=[
  {"name":"MyKad reference","path":ROOT/'tests/fixtures/mykad_reference.png',"expected":"950830-05-5465","passes":[
    (.035,.190,.330,.105,13,'gray',1.60,7),
    (.035,.185,.345,.115,13,'green',1.50,7),
    (.035,.185,.345,.115,13,'blue',1.40,7),
    (.010,.140,.470,.180,10,'green',1.50,6),
  ]},
  {"name":"MyPR reference","path":ROOT/'tests/fixtures/mypr_reference.png',"expected":"901231-10-6789","passes":[
    (.090,.300,.345,.085,10,'gray',1.55,7),
    (.090,.300,.345,.085,10,'green',1.45,7),
    (.090,.300,.345,.085,10,'red',1.40,7),
    (.050,.250,.440,.140,9,'gray',1.40,6),
  ]},
]

def variants(im):
    out=[('original',im)]
    for f in (.78,.90,1.10,1.22): out.append((f'brightness_{f}',ImageEnhance.Brightness(im).enhance(f)))
    for f in (.78,1.22): out.append((f'contrast_{f}',ImageEnhance.Contrast(im).enhance(f)))
    for r in (.45,.75): out.append((f'blur_{r}',im.filter(ImageFilter.GaussianBlur(r))))
    for deg in (-1.5,1.5): out.append((f'rotate_{deg}',im.rotate(deg,resample=Image.Resampling.BICUBIC,expand=False,fillcolor=(255,255,255))))
    b=io.BytesIO(); im.save(b,format='JPEG',quality=58,optimize=True); b.seek(0); out.append(('jpeg_q58',Image.open(b).convert('RGB')))
    return out

def focus(im,spec):
    x,y,w,h,scale,mode,contrast,psm=spec; W,H=im.size
    box=(round(W*x),round(H*y),round(W*(x+w)),round(H*(y+h)))
    c=im.crop(box).resize((max(1,round((box[2]-box[0])*scale)),max(1,round((box[3]-box[1])*scale))),Image.Resampling.LANCZOS)
    if mode=='gray': c=c.convert('L')
    else: c=c.convert('RGB').getchannel({'red':0,'green':1,'blue':2}[mode])
    return ImageEnhance.Contrast(c).enhance(contrast),psm

def valid_date(d):
    yy,mm,dd=int(d[:2]),int(d[2:4]),int(d[4:6])
    if not 1<=mm<=12 or dd<1:return False
    md=[31,29 if yy%4==0 else 28,31,30,31,30,31,31,30,31,30,31]
    return dd<=md[mm-1]

def candidates(text):
    cmap={'O':'0','Q':'0','D':'0','I':'1','L':'1','|':'1','!':'1','Z':'2','S':'5','G':'6','T':'7','B':'8'}
    patt=re.compile(r'(?<![A-Z0-9])([0-9OQDILZSBGT|!]{6})\s*[-–—]?\s*([0-9OQDILZSBGT|!]{2})\s*[-–—]?\s*([0-9OQDILZSBGT|!]{4})(?![A-Z0-9])',re.I)
    out=[]
    for m in patt.finditer(text):
        raw=''.join(m.groups()).upper(); d=''.join(ch if ch.isdigit() else cmap.get(ch,'') for ch in raw)
        if len(d)==12 and valid_date(d): out.append(f'{d[:6]}-{d[6:8]}-{d[8:]}')
    return out

def ocr_pass(im,spec):
    c,psm=focus(im,spec)
    return pytesseract.image_to_string(c,config=f'--psm {psm} -c tessedit_char_whitelist=0123456789-').strip()

rows=[]; start=time.time()
for sample in SAMPLES:
    base=Image.open(sample['path']).convert('RGB')
    for vname,im in variants(base):
        reads=[]; chosen=''
        # Browser normal path: primary + alternate. Only add strong/wide when unresolved.
        for spec in sample['passes'][:2]: reads.append(ocr_pass(im,spec))
        vals=[]
        for r in reads: vals.extend(candidates(r))
        uniq=list(dict.fromkeys(vals))
        if len(uniq)==1: chosen=uniq[0]
        elif len(uniq)>1:
            for extra in sample['passes'][2:]:
                reads.append(ocr_pass(im,extra)); vals=[]
                for r in reads: vals.extend(candidates(r))
                counts={x:vals.count(x) for x in set(vals)}
                ranked=sorted(counts,key=lambda x:(counts[x],x),reverse=True)
                if ranked and counts[ranked[0]]>=2: chosen=ranked[0]; break
        if not chosen:
            for extra in sample['passes'][2:]:
                if len(reads)>=4:break
                reads.append(ocr_pass(im,extra)); vals=[]
                for r in reads: vals.extend(candidates(r))
                uniq=list(dict.fromkeys(vals))
                if len(uniq)==1: chosen=uniq[0]; break
        rows.append({"sample":sample['name'],"variant":vname,"expected":sample['expected'],"detected":chosen,"pass":chosen==sample['expected'],"reads":reads})

summary={}
for s in SAMPLES:
    subset=[r for r in rows if r['sample']==s['name']]; summary[s['name']]={"passed":sum(r['pass'] for r in subset),"total":len(subset),"accuracy":sum(r['pass'] for r in subset)/len(subset)}
out={"summary":summary,"overall":{"passed":sum(r['pass'] for r in rows),"total":len(rows),"accuracy":sum(r['pass'] for r in rows)/len(rows),"elapsed_seconds":round(time.time()-start,2)},"failures":[r for r in rows if not r['pass']]}
(ROOT/'tests/NRIC_IMAGE_ROBUSTNESS_RESULTS.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))
raise SystemExit(0 if out['overall']['passed']==out['overall']['total'] else 1)
