#!/usr/bin/env python3
from pathlib import Path
import cv2, re, json, base64, html as htmlmod
import pytesseract
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
IMG=ROOT/'tests/fixtures/malaysia_passport_reference.jpg'
OUT=ROOT/'tests/V32_PASSPORT_CRITICAL_RESULTS.json'
SCREEN=ROOT/'evidence/V32_PASSPORT_CRITICAL_PROOF.png'
EXPECTED_BIRTH='KUALA LUMPUR'
EXPECTED_MRZ1='P<MYSMAHATHIR<BIN<IDRUS<<<<<<<<<<<<<<<<<<<<<'

img0=cv2.imread(str(IMG))
if img0 is None: raise SystemExit(f'Cannot open {IMG}')

def crop(img,spec):
    x,y,w,h,scale,mode,contrast,psm,wl,*rest=spec
    threshold=rest[0] if rest else None
    H,W=img.shape[:2]
    c=img[int(H*y):int(H*(y+h)),int(W*x):int(W*(x+w))]
    c=cv2.resize(c,None,fx=scale,fy=scale,interpolation=cv2.INTER_CUBIC)
    if mode=='red': g=c[:,:,2]
    elif mode=='green': g=c[:,:,1]
    elif mode=='blue': g=c[:,:,0]
    else: g=cv2.cvtColor(c,cv2.COLOR_BGR2GRAY)
    if threshold=='otsu':
        _,g=cv2.threshold(g,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    else:
        g=cv2.convertScaleAbs(g,alpha=contrast,beta=128*(1-contrast))
    cfg=f'--psm {psm}'
    if wl: cfg+=f' -c tessedit_char_whitelist={wl}'
    return pytesseract.image_to_string(g,lang='eng',config=cfg).replace('\r','').strip()


NAME=[(.285,.185,.375,.115,12,'gray',2.0,7,None),(.285,.185,.375,.115,12,'gray',2.15,6,None),(.270,.180,.410,.140,14,'gray',1.8,6,None),(.270,.180,.410,.140,14,'green',1.8,11,None)]
BIRTH=[(.595,.330,.320,.135,10,'gray',1.70,6,None),(.590,.325,.335,.145,10,'red',1.65,6,None),(.620,.365,.280,.070,12,'gray',1.90,7,None),(.550,.300,.400,.180,12,'gray',1.0,6,None,'otsu')]
SOURCE=(0,0,1,1,4.2,'gray',1.5,6,None)
MRZ=[(.010,.742,.980,.125,12,'gray',1.95,7,'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<'),(.010,.738,.980,.135,12,'red',1.75,7,'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<'),(.005,.730,.990,.155,12,'gray',1.80,6,'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<'),(.010,.750,.980,.235,10,'gray',1.80,6,'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<')]

def variants():
    yield 'original',img0
    _,b=cv2.imencode('.jpg',img0,[cv2.IMWRITE_JPEG_QUALITY,55]); yield 'jpeg_q55',cv2.imdecode(b,1)
    small=cv2.resize(img0,None,fx=.70,fy=.70,interpolation=cv2.INTER_AREA); small=cv2.GaussianBlur(small,(3,3),.5); yield 'down70_blur',cv2.resize(small,(img0.shape[1],img0.shape[0]),interpolation=cv2.INTER_CUBIC)
    dark=cv2.convertScaleAbs(img0,alpha=.82,beta=-8); _,b=cv2.imencode('.jpg',dark,[cv2.IMWRITE_JPEG_QUALITY,65]); yield 'dark_jpeg65',cv2.imdecode(b,1)

# Load the actual V32 browser parser/reconciler, not a reimplementation.
html=(ROOT/'index.html').read_text()
html=re.sub(r'<script\s+src="[^"]+"></script>','',html)
results=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1600,'height':980})
    page.set_content('<html><body></body></html>')
    page.evaluate('window.pdfjsLib={GlobalWorkerOptions:{}}')
    page.set_content(html,wait_until='domcontentloaded',timeout=30000)
    for vname,img in variants():
        name_raw=[crop(img,s) for s in NAME]
        birth_raw=[crop(img,s) for s in BIRTH]
        mrz_raw=[crop(img,s) for s in MRZ]
        source_text=crop(img,SOURCE)
        final=page.evaluate('''({nameRaw,birthRaw,mrzRaw,sourceText}) => {
          const name=focusedPassportName(...nameRaw,sourceText);
          const birth=focusedPassportBirthPlace(...birthRaw,sourceText);
          const mrz1=passportBestMrzLine1(name,...mrzRaw,sourceText);
          return {name,birth,mrz1};
        }''',{'nameRaw':name_raw,'birthRaw':birth_raw,'mrzRaw':mrz_raw,'sourceText':source_text})
        results.append({
            'variant':vname,'name_used':final['name'],
            'place_of_birth':final['birth'],'place_of_birth_pass':final['birth']==EXPECTED_BIRTH,
            'mrz_line_1':final['mrz1'],'mrz_line_1_pass':final['mrz1']==EXPECTED_MRZ1,
            'raw_birth_ocr':birth_raw,'raw_mrz_ocr':mrz_raw,'source_ocr':source_text
        })
    browser.close()

summary={
    'variants_tested':len(results),
    'place_of_birth_exact':sum(r['place_of_birth_pass'] for r in results),
    'mrz_line_1_exact':sum(r['mrz_line_1_pass'] for r in results),
    'critical_checks_passed':sum(r['place_of_birth_pass'] for r in results)+sum(r['mrz_line_1_pass'] for r in results),
    'critical_checks_total':len(results)*2,
}
summary['measured_exact_match_pct']=round(100*summary['critical_checks_passed']/summary['critical_checks_total'],2)
OUT.write_text(json.dumps({'summary':summary,'expected':{'place_of_birth':EXPECTED_BIRTH,'mrz_line_1':EXPECTED_MRZ1},'results':results},indent=2))

# Render a visual proof from the actual test output.
img_b64=base64.b64encode(IMG.read_bytes()).decode()
rows=''.join(f'''<tr><td>{r['variant']}</td><td>{r['place_of_birth']}</td><td class="{'pass' if r['place_of_birth_pass'] else 'fail'}">{'PASS' if r['place_of_birth_pass'] else 'FAIL'}</td><td class="mono">{htmlmod.escape(r['mrz_line_1'])}</td><td class="{'pass' if r['mrz_line_1_pass'] else 'fail'}">{'PASS' if r['mrz_line_1_pass'] else 'FAIL'}</td></tr>''' for r in results)
proof=f'''<!doctype html><meta charset="utf-8"><style>*{{box-sizing:border-box}}body{{margin:0;background:#e8f0f4;font-family:Arial;color:#162b36}}.top{{height:64px;background:#153142;color:white;padding:20px 28px;font-weight:800;font-size:20px}}.wrap{{display:grid;grid-template-columns:42% 58%;gap:18px;padding:20px;height:916px}}.card{{background:white;border-radius:16px;box-shadow:0 8px 28px #0002;overflow:hidden}}.left{{padding:18px;display:flex;flex-direction:column}}.left img{{width:100%;margin:auto;box-shadow:0 5px 18px #0002}}.right{{padding:20px}}.badge{{display:inline-block;background:#dff5eb;color:#06764a;padding:8px 12px;border-radius:999px;font-size:12px;font-weight:800}}h1{{font-size:22px;margin:16px 0 6px}}.metric{{background:#f2f7f9;border-radius:12px;padding:14px;margin:12px 0}}table{{width:100%;border-collapse:collapse;font-size:11px}}th,td{{border:1px solid #d9e5eb;padding:9px;vertical-align:top}}th{{background:#edf4f7;text-align:left}}.pass{{color:#06764a;font-weight:800}}.fail{{color:#c73535;font-weight:800}}.mono{{font-family:monospace;font-size:10px;word-break:break-all}}.note{{margin-top:12px;background:#fff8e9;border:1px solid #f1d29b;padding:12px;border-radius:10px;font-size:12px;line-height:1.45}}</style><div class="top">NeuroOCR V32 · Malaysia Passport Critical-Field Proof</div><div class="wrap"><div class="card left"><b>Real regression passport fixture</b><p>Critical fields under test: Tempat Lahir / Place of Birth and MRZ Line 1.</p><img src="data:image/jpeg;base64,{img_b64}"></div><div class="card right"><span class="badge">{summary['critical_checks_passed']}/{summary['critical_checks_total']} EXACT CHECKS PASS</span><h1>Measured exact match: {summary['measured_exact_match_pct']:.2f}%</h1><div class="metric"><b>Expected Place of Birth:</b> {EXPECTED_BIRTH}<br><b>Expected MRZ Line 1:</b> <span class="mono">{htmlmod.escape(EXPECTED_MRZ1)}</span></div><table><thead><tr><th>Stress variant</th><th>Captured Place of Birth</th><th>Check</th><th>Captured MRZ Line 1</th><th>Check</th></tr></thead><tbody>{rows}</tbody></table><div class="note"><b>Concern addressed:</b> raw MRZ OCR can confuse characters such as I/K and filler &lt; marks. V32 uses three focused MRZ-Line-1 reads plus the full MRZ block then reconciles the visible MRZ name zone against the independently captured printed Name. Place of Birth uses three dedicated crops and consensus. If support is insufficient, strict validation returns REVIEW REQUIRED rather than silently accepting a wrong value.</div></div></div>'''
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1600,'height':980})
    page.set_content(proof,wait_until='load')
    page.screenshot(path=str(SCREEN),full_page=False)
    browser.close()
print(json.dumps(summary,indent=2)); print(OUT); print(SCREEN)
if summary['critical_checks_passed']!=summary['critical_checks_total']:
    raise SystemExit('FAIL: critical passport stress test')
print('PASS: V32 passport Place of Birth + MRZ Line 1 exact across all stress variants')
