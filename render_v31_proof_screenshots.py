from pathlib import Path
import json, base64, html
from PIL import Image, ImageOps, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
RES=ROOT/'tests/v31_external/v31_external_results.json'
OUT=ROOT/'evidence/screenshots'; OUT.mkdir(parents=True,exist_ok=True)
GALLERY=ROOT/'evidence/PROOF_GALLERY.html'
CONTACT=ROOT/'evidence/V31_ALL_PROFILES_CONTACT_SHEET.png'
data=json.loads(RES.read_text())
concerns={
'mykad_public_sarawak':'Security-pattern background, small card text, NRIC and multi-line address must remain exact.',
'mypr_public_structure':'Official public reference is structural/redacted. Personal identity fields cannot be independently proven from this sample, so strict production review remains required.',
'passport_public_firefly':'Visible biographic fields can be checked, but the public sample does not expose a safely readable full passport number and full MRZ. Strict production review remains required.',
'driving_public_wikimedia':'Specimen masks personal name, identity number and address. Class and validity dates must still parse without inventing masked values.',
'cidb_ppk_public':'Dense grade/category/specialisation codes, multi-line address and multiple registration/effective/expiry dates can be confused.',
'ssm_registration_public':'Official public sample redacts business name/registration number and parts of validity year. Parser must preserve visible fields and fail closed for redacted mandatory fields.',
'ssm_company_public':'Modern plus legacy company number, optional old-name fields, two addresses/postcodes and long business-activity text must remain distinct.',
'invoice_receipt_public':'Thermal-style receipt layout has many similar decimal amounts. Totals, change, tax and invoice number must not cross-map.',
'form_application_public':'The form contains MyKad/Passport wording but is not an identity document. False passport/MyKad classification is a key regression risk.',
'letter_memo_public':'Letter wording and addresses must remain body text while document type detection must not depend on one phrase only.',
'certificate_licence_public':'Contains “Licence Number” and MyKad/Passport wording but is not a driving licence or identity document. Generic licence detection must win.',
'report_statement_public':'Financial statements contain repeated year columns and similar large numbers. Numeric anchors and report type must remain stable.',
'general_document_public':'Contains CIDB references but is a general FAQ. It must not be incorrectly promoted to a CIDB certificate profile.'
}

def pct(passn,total): return 'N/A' if total==0 else f'{passn/total*100:.2f}%'
def img_data(path):
    b=Path(path).read_bytes(); ext=Path(path).suffix.lower(); mime='image/jpeg' if ext in ('.jpg','.jpeg') else 'image/png'
    return f'data:{mime};base64,'+base64.b64encode(b).decode()

def table_html(r):
    rows=[]
    if r['fields']:
        for f in r['fields']:
            status='PASS' if f['pass'] else 'FAIL'
            rows.append(f"<tr><td>{html.escape(f['label'])}</td><td>{html.escape(str(f['expected']))}</td><td>{html.escape(str(f['actual']))}</td><td class='{status.lower()}'>{status}</td></tr>")
        head='<th>Field</th><th>Expected</th><th>Captured</th><th>Check</th>'
    else:
        for a in r['anchors']:
            status='PASS' if a['pass'] else 'FAIL'
            rows.append(f"<tr><td colspan='2'>{html.escape(str(a['expected']))}</td><td colspan='1'>OCR anchor</td><td class='{status.lower()}'>{status}</td></tr>")
        head='<th colspan="2">Expected visible anchor</th><th>Method</th><th>Check</th>'
    return f'<table><thead><tr>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table>'

def page_html(r):
    exact_pass=r['field_pass'] if r['field_total'] else r['anchor_pass']; exact_total=r['field_total'] if r['field_total'] else r['anchor_total']
    review='REVIEW REQUIRED' if r.get('expected_review') else ('PASS' if r['type_pass'] and exact_pass==exact_total else 'REVIEW REQUIRED')
    reviewcls='review' if review!='PASS' else 'ok'
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
    *{{box-sizing:border-box}} body{{margin:0;background:#e9f0f4;font-family:Arial,Helvetica,sans-serif;color:#13232d}}
    .top{{height:62px;background:#132d3d;color:white;display:flex;align-items:center;padding:0 30px;justify-content:space-between}}
    .brand{{font-weight:800;letter-spacing:1.5px;font-size:22px}} .badge{{background:#f0f8fa;color:#0d6071;padding:9px 15px;border-radius:999px;font-size:11px;font-weight:800;letter-spacing:1px}}
    .wrap{{padding:22px;display:grid;grid-template-columns:42% 58%;gap:20px;height:calc(100vh - 62px)}}
    .card{{background:white;border-radius:18px;box-shadow:0 8px 28px rgba(36,64,78,.12);overflow:hidden}}
    .left{{display:flex;flex-direction:column}} .source{{padding:14px 18px;border-bottom:1px solid #dce7ed;font-size:12px;line-height:1.45}}
    .source strong{{font-size:13px}} .imgbox{{flex:1;display:flex;align-items:center;justify-content:center;padding:20px;background:#f4f7f9}}
    .imgbox img{{max-width:100%;max-height:650px;object-fit:contain;box-shadow:0 5px 18px rgba(0,0,0,.12)}}
    .right{{padding:18px;overflow:hidden}} .metrics{{display:grid;grid-template-columns:1.2fr .8fr .8fr .9fr;gap:10px;margin-bottom:12px}}
    .metric{{background:#f1f6f8;border-radius:13px;padding:12px;min-height:72px}} .metric small{{display:block;color:#667b86;font-size:9px;letter-spacing:1px;font-weight:bold;margin-bottom:8px}}
    .metric b{{font-size:14px}} .ok{{color:#06764a}} .review{{color:#c53a35}} .concern{{border:1px solid #f1c98d;background:#fff8ec;padding:11px 13px;border-radius:12px;margin:10px 0 12px;font-size:12px;line-height:1.4}}
    .title{{font-size:13px;font-weight:800;margin:4px 0 7px}} table{{width:100%;border-collapse:collapse;font-size:10px;table-layout:fixed}} th{{background:#edf4f7;text-align:left;padding:7px;border:1px solid #dbe6ec}} td{{padding:6px;border:1px solid #dbe6ec;vertical-align:top;word-wrap:break-word}} td.pass{{color:#06764a;font-weight:800}} td.fail{{color:#c53a35;font-weight:800}}
    .foot{{position:absolute;bottom:8px;right:26px;font-size:9px;color:#647784}} .qa{{font-size:10px;color:#607782;margin-top:8px}}
    </style></head><body>
    <div class="top"><div class="brand">NeuroOCR <span style="opacity:.65">V31 QA</span></div><div class="badge">AUTOMATED REGRESSION · ACTUAL OCR + V31 PARSER</div></div>
    <div class="wrap">
      <div class="card left"><div class="source"><strong>{html.escape(r['profile'])}</strong><br>Public source basis: {html.escape(r['source'])}<br><span style="color:#6a7b84">Fixture is source-derived and intentionally degraded for OCR QA.</span></div><div class="imgbox"><img src="{img_data(r['image'])}"></div></div>
      <div class="card right">
        <div class="metrics">
          <div class="metric"><small>DETECTED DOCUMENT</small><b>{html.escape(r['detected_type'])}</b></div>
          <div class="metric"><small>TYPE CHECK</small><b class="{'ok' if r['type_pass'] else 'review'}">{'PASS' if r['type_pass'] else 'FAIL'}</b></div>
          <div class="metric"><small>RAW OCR CONFIDENCE</small><b>{r['raw_ocr_confidence']:.2f}%</b></div>
          <div class="metric"><small>STRICT TEST STATUS</small><b class="{reviewcls}">{review}</b></div>
        </div>
        <div class="metric" style="min-height:55px;margin-bottom:10px"><small>MEASURED EXACT MATCH</small><b>{pct(exact_pass,exact_total)} ({exact_pass}/{exact_total})</b></div>
        <div class="concern"><b>PROOF OF CONCERN:</b> {html.escape(concerns[r['name']])}</div>
        <div class="title">Captured output verification</div>{table_html(r)}
        <div class="qa">Selected OCR preprocessing: <b>{html.escape(r['selected_variant'])}</b>. Raw confidence is engine token confidence and is not a universal field-accuracy guarantee.</div>
      </div>
    </div><div class="foot">NeuroOCR V31 test evidence · 30 Sep 2026</div></body></html>'''

screens=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1600,'height':1000}, device_scale_factor=1)
    for r in data['results']:
        h=page_html(r); page.set_content(h, wait_until='load')
        out=OUT/(r['name']+'.png'); page.screenshot(path=str(out), full_page=False)
        screens.append((r,out))
    browser.close()

# Create gallery (portable with relative screenshot paths)
cards=[]
for r,p in screens:
    exact_pass=r['field_pass'] if r['field_total'] else r['anchor_pass']; exact_total=r['field_total'] if r['field_total'] else r['anchor_total']
    cards.append(f'''<article><h2>{html.escape(r['profile'])}</h2><p>Detected: <b>{html.escape(r['detected_type'])}</b> · Exact match: <b>{pct(exact_pass,exact_total)}</b> · Raw OCR confidence: <b>{r['raw_ocr_confidence']:.2f}%</b></p><img src="screenshots/{p.name}"><p><b>Concern:</b> {html.escape(concerns[r['name']])}</p></article>''')
GALLERY.write_text(f'''<!doctype html><meta charset="utf-8"><title>NeuroOCR V31 Proof Gallery</title><style>body{{font-family:Arial;background:#edf3f6;margin:30px;color:#142833}}article{{background:#fff;padding:18px;border-radius:16px;margin:0 0 24px;box-shadow:0 5px 18px #0001}}img{{width:100%;max-width:1200px;border:1px solid #ccd9df}}p{{line-height:1.5}}</style><h1>NeuroOCR V31 — Profile Validation Proof Gallery</h1><p>Browser-rendered evidence from actual Tesseract OCR output and the V31 parser. Public-source fixtures are source-derived and degraded for QA; they are not claimed to be downloaded originals.</p>{''.join(cards)}''')

# Contact sheet thumbnails
thumb_w,thumb_h=600,375
cols=2; rows=(len(screens)+cols-1)//cols
sheet=Image.new('RGB',(cols*thumb_w,rows*thumb_h),(232,239,243))
for i,(r,p) in enumerate(screens):
    im=Image.open(p).convert('RGB'); im.thumbnail((thumb_w,thumb_h),Image.Resampling.LANCZOS)
    canvas=Image.new('RGB',(thumb_w,thumb_h),'white'); canvas.paste(im,((thumb_w-im.width)//2,(thumb_h-im.height)//2))
    sheet.paste(canvas,((i%cols)*thumb_w,(i//cols)*thumb_h))
sheet.save(CONTACT,optimize=True)
print(f'Created {len(screens)} screenshots')
print(GALLERY); print(CONTACT)
