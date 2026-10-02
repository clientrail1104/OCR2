from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageOps
import subprocess,json,re,statistics,difflib,html as htmlmod

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'tests'/'fresh_stress'
IMG=OUT/'images'; OCR=OUT/'ocr'; EVID=ROOT/'evidence'/'fresh_stress'
for d in (OUT,IMG,OCR,EVID): d.mkdir(parents=True,exist_ok=True)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'; BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

def sample(name,profile,expected_type,lines,anchors,fields=None,kind='doc'):
    return dict(name=name,profile=profile,expected_type=expected_type,lines=lines,anchors=anchors,fields=fields or {},kind=kind)

samples=[
sample('mykad_fresh','Malaysia ID / Passport — MyKad','Malaysia MyKad',[
'KAD PENGENALAN MALAYSIA','MyKad','860712-08-2468','NUR AISYAH BINTI RAHMAN','NO 18 JALAN BUNGA RAYA 3','TAMAN DESA INDAH','43000 KAJANG','SELANGOR','WARGANEGARA','ISLAM','PEREMPUAN'],
['860712-08-2468','NUR AISYAH BINTI RAHMAN','43000 KAJANG','SELANGOR','WARGANEGARA','ISLAM','PEREMPUAN'],
{'Identity Number':'860712-08-2468','Name':'NUR AISYAH BINTI RAHMAN','Address':'NO 18 JALAN BUNGA RAYA 3 TAMAN DESA INDAH 43000 KAJANG SELANGOR','Religion':'ISLAM','Citizenship':'WARGANEGARA','Gender':'PEREMPUAN'},'card'),
sample('mypr_fresh','Malaysia ID / Passport — MyPR','Malaysia MyPR',[
'KAD PENGENALAN MALAYSIA','PEMASTAUTIN TETAP','MyPR','901105-10-1357','LEE WEI JIAN','NO 9 JALAN MERPATI 2','TAMAN MELAWATI','53100 KUALA LUMPUR','PNL','BUDDHA','LELAKI'],
['901105-10-1357','LEE WEI JIAN','53100 KUALA LUMPUR','PNL','BUDDHA','LELAKI'],
{'Identity Number':'901105-10-1357','Name':'LEE WEI JIAN','Address':'NO 9 JALAN MERPATI 2 TAMAN MELAWATI 53100 KUALA LUMPUR','Country of Origin':'PNL','Religion':'BUDDHA','Citizenship':'PEMASTAUTIN TETAP / PR','Gender':'LELAKI'},'card'),
sample('passport_fresh','Malaysia ID / Passport — Passport','Malaysia Passport',[
'MALAYSIA','PASPORT / PASSPORT','Jenis / Type: P','Kod Negara / Country Code: MYS','Passport Number: B12345678','Nama / Name: NURUL HUDA BINTI AMIR','Warganegara / Nationality: MALAYSIA','No. Pengenalan / Identity No.: 920614-10-2468','Tarikh Lahir / Date of Birth: 14 JUN 1992','Tempat Lahir / Place of Birth: SELANGOR','Jantina / Sex: P-F','Tinggi / Height: 162 cm','Tarikh Dikeluarkan / Date of Issue: 15 MAY 2024','Tarikh Tamat / Date of Expiry: 15 MAY 2029','Pejabat Pengeluar / Issuing Office: PUTRAJAYA','P<MYSNURUL<HUDA<BINTI<AMIR<<<<<<<<<<<<<<<<<<','B123456781MYS9206148F2905154920614102468<<16'],
['B12345678','NURUL HUDA BINTI AMIR','920614-10-2468','14 JUN 1992','SELANGOR','P-F','162 cm','15 MAY 2024','15 MAY 2029','PUTRAJAYA'],
{'Jenis / Type':'P','Kod Negara / Country Code':'MYS','Passport Number':'B12345678','Nama / Name':'NURUL HUDA BINTI AMIR','Warganegara / Nationality':'MALAYSIA','No. Pengenalan / Identity No.':'920614102468','Tarikh lahir / Date of Birth':'14 JUN 1992','Tempat Lahir / Place of Birth':'SELANGOR','Jantina / Sex':'P-F','Tinggi / Height':'162 cm','Tarikh Dikeluarkan / Date of Issue':'15 MAY 2024','Tarikh Tamat / Date of Expiry':'15 MAY 2029','Pejabat Pengeluar / Issuing Office':'PUTRAJAYA'},'card'),
sample('driving_fresh','Malaysia Driving Licence','Malaysia Driving Licence',[
'LESEN MEMANDU MALAYSIA','MALAYSIA DRIVING LICENCE','Licence Type: Full','Nama / Name: AHMAD FIRDAUS BIN SALLEH','Warganegara / Nationality: MALAYSIA','No. Pengenalan / Identity No.: 880203-06-3579','Kelas / Class: B2 D','Tempoh / Validity','12/09/2024 - 12/09/2029','Alamat / Address: NO 22 JALAN IMPIAN 4','TAMAN IMPIAN EMAS','81300 SKUDAI JOHOR'],
['AHMAD FIRDAUS BIN SALLEH','880203-06-3579','B2 D','12/09/2024','12/09/2029','81300 SKUDAI JOHOR'],
{'Licence Type':'Full','Name':'AHMAD FIRDAUS BIN SALLEH','Nationality':'MALAYSIA','Identity Number':'880203063579','Class':'B2 D','Valid From':'12/09/2024','Valid Until':'12/09/2029','Address':'NO 22 JALAN IMPIAN 4 TAMAN IMPIAN EMAS 81300 SKUDAI JOHOR'},'card'),
sample('cidb_ppk_fresh','CIDB Certificate — PPK','CIDB PPK / Perakuan Pendaftaran',[
'CIDB MALAYSIA','PERAKUAN PENDAFTARAN','No. Pendaftaran: 1234567-PK045678','Nama Kontraktor: BINA MAJU RESOURCES SDN. BHD.','Alamat Berdaftar: NO 7 JALAN INDUSTRI 2','TAMAN INDUSTRI JAYA','81700 PASIR GUDANG JOHOR','Daerah: JOHOR BAHRU','Tarikh Mula Berdaftar: 03/02/2015','GRED KATEGORI PENGKHUSUSAN','G5 B B04 B18','G5 CE CE21 CE36','Tarikh Mula Berkuatkuasa: 01/01/2026','Tarikh Habis Tempoh Perakuan: 31/12/2026','Status: AKTIF'],
['1234567-PK045678','BINA MAJU RESOURCES SDN. BHD.','81700 PASIR GUDANG JOHOR','03/02/2015','B04 B18','CE21 CE36','31/12/2026','AKTIF'],
{'No. Pendaftaran / Registration Number':'1234567-PK045678','Nama Kontraktor / Contractor Name':'BINA MAJU RESOURCES SDN. BHD.','Daerah / District':'JOHOR BAHRU','Tarikh Mula Berdaftar':'03/02/2015','Tarikh Mula Berkuatkuasa / Effective Date':'01/01/2026','Tarikh Habis Tempoh Perakuan / Expiry Date':'31/12/2026','Status':'AKTIF'}),
sample('cidb_spkk_fresh','CIDB Certificate — SPKK','CIDB SPKK',[
'CIDB MALAYSIA','SIJIL PEROLEHAN KERJA KERAJAAN','No. Pendaftaran: 7654321-SP012345','Nama Kontraktor: MEGA CEKAP SDN. BHD.','Alamat Berdaftar: 18 JALAN UTAMA 5','BANDAR BARU NILAI','71800 NILAI NEGERI SEMBILAN','Daerah: SEREMBAN','Tarikh Mula Berdaftar: 14/06/2018','GRED KATEGORI','G6 B','G6 CE','PEGAWAI SYARIKAT YANG DITAULIAHKAN','MOHD AZLAN BIN YUSOF 780101-05-4321','Tarikh Mula Berkuatkuasa: 01/06/2026','Tarikh Habis Tempoh Perakuan: 31/05/2027'],
['7654321-SP012345','MEGA CEKAP SDN. BHD.','71800 NILAI','14/06/2018','MOHD AZLAN BIN YUSOF','31/05/2027'],
{'No. Pendaftaran / Registration Number':'7654321-SP012345','Nama Kontraktor / Contractor Name':'MEGA CEKAP SDN. BHD.','Daerah / District':'SEREMBAN','Initial Registration Date / Tarikh Mula Berdaftar':'14/06/2018','Tarikh Mula Berkuatkuasa / Effective Date':'01/06/2026','Tarikh Habis Tempoh Perakuan / Expiry Date':'31/05/2027'}),
sample('cidb_stb_fresh','CIDB Certificate — STB','CIDB STB',[
'CIDB MALAYSIA','SIJIL KONTRAKTOR KERJA TARAF BUMIPUTERA','No. Sijil Pendaftaran: 0120180507-WP012216','Gred Pendaftaran: G4 (Bumiputera)','Kategori / Category: B CE','Tempoh Sah Laku','DARI: 01/04/2026','HINGGA: 31/03/2027','Nama dan Alamat Berdaftar','TEGUH BUMI ENTERPRISE','NO 15 JALAN SENTOSA 1 40000 SHAH ALAM SELANGOR','Pegawai Syarikat Yang Ditauliahkan','MUHAMMAD HAFIZ BIN KARIM','No. K/P: 850505-10-6789'],
['SIJIL KONTRAKTOR KERJA TARAF BUMIPUTERA','0120180507-WP012216','G4 (Bumiputera)','01/04/2026','31/03/2027','MUHAMMAD HAFIZ BIN KARIM','850505-10-6789'],
{'Effective Date':'01/04/2026','Expiry Date':'31/03/2027','No. Sijil Pendaftaran':'0120180507-WP012216','Gred Pendaftaran':'G4 (Bumiputera)','Pegawai Syarikat Yang DiTauliahkan':'MUHAMMAD HAFIZ BIN KARIM','No. K/P':'850505-10-6789'}),
sample('ssm_company_fresh','SSM Document — Company Profile','SSM Company Profile',[
'SURUHANJAYA SYARIKAT MALAYSIA','COMPANIES COMMISSION OF MALAYSIA','MAKLUMAT SYARIKAT','Nama : INOVASI DIGITAL MALAYSIA SDN. BHD.','Nama Lama : TEKNOLOGI AWAN SDN. BHD.','Tarikh Pertukaran : 12-08-2020','No. Pendaftaran : 201801012345(934370-X)','Tarikh Penubuhan : 05-04-2018','Tarikh Pendaftaran : 05-04-2018','Jenis : BERHAD MENURUT SYER','SYARIKAT PERSENDIRIAN','Status : EXISTING','Alamat Daftar : 12 JALAN TEKNOLOGI 3','CYBERJAYA','SELANGOR','Poskod 63000','Tempat Penubuhan : MALAYSIA','Alamat Perniagaan : UNIT 8-2 TOWER A','PERSIARAN MULTIMEDIA','CYBERJAYA SELANGOR','Poskod 63000','Jenis Perniagaan : SOFTWARE DEVELOPMENT AND DATA PROCESSING'],
['INOVASI DIGITAL MALAYSIA SDN. BHD.','201801012345(934370-X)','05-04-2018','EXISTING','63000','SOFTWARE DEVELOPMENT AND DATA PROCESSING'],
{'Nama Syarikat / Company Name':'INOVASI DIGITAL MALAYSIA SDN. BHD.','Nama Syarikat Lama / Old Company Name':'TEKNOLOGI AWAN SDN. BHD.','Tarikh Pertukaran / Date of Change':'12-08-2020','No Syarikat / Company Registration No.':'201801012345(934370-X)','Tarikh Pemerbadanan / Date of Incorporation':'05-04-2018','Tarikh Pendaftaran / Registration Date':'05-04-2018','Status':'EXISTING','Poskod / Postcode (Registered Address)':'63000','Tempat Penubuhan / Place of Incorporation':'MALAYSIA','Poskod / Postcode (Business Address)':'63000'}),
sample('ssm_business_profile_fresh','SSM Document — Business Profile','SSM Business Profile / Maklumat Perniagaan',[
'SURUHANJAYA SYARIKAT MALAYSIA','MAKLUMAT PERNIAGAAN / BUSINESS PROFILE','Nama Perniagaan: KEDAI SERI MAJU','No Pendaftaran Perniagaan: 202603001234','Alamat Utama Perniagaan: NO 5 JALAN MELATI 2','TAMAN MELATI','53100 KUALA LUMPUR','Bentuk Perniagaan: MILIKAN TUNGGAL','Tarikh Mula Berniaga: 02-01-2026','Tarikh Pendaftaran: 02-01-2026','Tarikh Luput Pendaftaran: 01-01-2027','Tarikh Perubahan Terakhir: 15-06-2026','Status: ACTIVE','Jenis Perniagaan: RETAIL SALE OF GROCERIES','Maklumat Cawangan: TIADA'],
['KEDAI SERI MAJU','202603001234','53100 KUALA LUMPUR','MILIKAN TUNGGAL','01-01-2027','RETAIL SALE OF GROCERIES'],
{'Nama Perniagaan / Company Name':'KEDAI SERI MAJU','No Pendaftaran Perniagaan / Registration Number':'202603001234','Bentuk Perniagaan / Business Type':'MILIKAN TUNGGAL','Tarikh Mula Berniaga / Business Start Date':'02-01-2026','Tarikh Pendaftaran / Registration Date':'02-01-2026','Tarikh Luput Pendaftaran / Registration Expiry':'01-01-2027','Tarikh Perubahan Terakhir / Last Change Date':'15-06-2026','Status':'ACTIVE','Maklumat Cawangan / Branch Information':'TIADA'}),
sample('ssm_registration_cert_fresh','SSM Business Registration — Certificate','SSM Business Registration Certificate',[
'SURUHANJAYA SYARIKAT MALAYSIA','CERTIFICATE OF REGISTRATION','THE REGISTRATION OF BUSINESSES ACT 1956 (ACT 197)','FORM D (RULE 13)','This is to certify that the Business carried on under the name SERI MAJU TRADING','Registration No.: 202603001234','has been registered until 31 DECEMBER 2027 in accordance with the Registration of Businesses Act 1956','with its principal place of business at NO 20 JALAN MAWAR 6, TAMAN MAWAR, 43000 KAJANG SELANGOR','Number of branches: N/A (0)','Dated at SISTEM EZBIZ this 02 JANUARY 2026','REGISTRAR OF BUSINESSES PENINSULAR OF MALAYSIA'],
['SERI MAJU TRADING','202603001234','31 DECEMBER 2027','43000 KAJANG SELANGOR','N/A (0)','02 JANUARY 2026','SISTEM EZBIZ'],
{'Form':'FORM D (RULE 13)','Nama Perniagaan / Business Name':'SERI MAJU TRADING','No. Pendaftaran / Registration Number':'202603001234','Valid Until / Sah Hingga':'31 DECEMBER 2027','Registered Address':'NO 20 JALAN MAWAR 6, TAMAN MAWAR, 43000 KAJANG SELANGOR','Bil. Cawangan / Number of Branches':'N/A (0)','Certificate Date':'02 JANUARY 2026','Issuing System':'SISTEM EZBIZ'}),
sample('ssm_registration_renewal_fresh','SSM Business Registration — Renewal','SSM Business Registration Renewal',[
'SURUHANJAYA SYARIKAT MALAYSIA','PERAKUAN PEMBAHARUAN PENDAFTARAN','AKTA PENDAFTARAN PERNIAGAAN 1956 (AKTA 197)','BORANG E (KAEDAH 13)','Nama Perniagaan: CAHAYA MAJU ENTERPRISE','No. Pendaftaran: 202501009876','Perniagaan ini diperbaharui sehingga 30 NOVEMBER 2027','beralamat di NO 8 JALAN CEMPAKA 4, BANDAR BARU, 40150 SHAH ALAM SELANGOR','Bil. Cawangan: TIADA (0)','Bertarikh di SISTEM EZBIZ pada 01 DECEMBER 2026','PENDAFTAR PERNIAGAAN SEMENANJUNG MALAYSIA'],
['CAHAYA MAJU ENTERPRISE','202501009876','30 NOVEMBER 2027','40150 SHAH ALAM SELANGOR','TIADA (0)','01 DECEMBER 2026','SISTEM EZBIZ'],
{'Form':'BORANG E (KAEDAH 13)','Nama Perniagaan / Business Name':'CAHAYA MAJU ENTERPRISE','No. Pendaftaran / Registration Number':'202501009876','Valid Until / Sah Hingga':'30 NOVEMBER 2027','Registered Address':'NO 8 JALAN CEMPAKA 4, BANDAR BARU, 40150 SHAH ALAM SELANGOR','Bil. Cawangan / Number of Branches':'TIADA (0)','Certificate Date':'01 DECEMBER 2026','Issuing System':'SISTEM EZBIZ'}),
sample('invoice_fresh','Invoice / Receipt','Invoice / Receipt',[
'INVOICE','Invoice No: INV-MY-2026-1098','Date: 30/09/2026','Vendor: Alpha Office Supplies Sdn. Bhd.','Customer: Beta Services Sdn. Bhd.','Description Qty Unit Price Amount','A4 Paper 10 18.50 185.00','Printer Toner 2 245.00 490.00','Subtotal: RM 675.00','SST 8%: RM 54.00','Grand Total: RM 729.00','Amount Due: RM 729.00'],
['INV-MY-2026-1098','30/09/2026','Alpha Office Supplies Sdn. Bhd.','Beta Services Sdn. Bhd.','RM 675.00','RM 54.00','RM 729.00']),
sample('form_fresh','Form / Application','Form / Application',[
'APPLICATION FORM','Applicant Details','Name: SITI FARHANA BINTI OMAR','NRIC: 900909-14-2468','Email: siti.farhana@example.com','Mobile: 012-3456789','Please tick one','[X] New Application','[ ] Renewal','Declaration','I confirm the information above is correct.'],
['APPLICATION FORM','SITI FARHANA BINTI OMAR','900909-14-2468','siti.farhana@example.com','012-3456789','New Application']),
sample('certificate_fresh','Certificate / Licence','Certificate / Licence',[
'CIVIL AVIATION AUTHORITY OF MALAYSIA','REMOTE PILOT LICENCE','Licence Number: RPL-2026-004321','Name: DANIEL TAN WEI MING','Identity No: 910101-10-2468','Category: SMALL UNMANNED AIRCRAFT','Date of Issue: 01 SEP 2026','Valid Until: 31 AUG 2028','This is to certify that the holder is authorised under the applicable regulations.'],
['REMOTE PILOT LICENCE','RPL-2026-004321','DANIEL TAN WEI MING','01 SEP 2026','31 AUG 2028']),
sample('letter_fresh','Letter / Memo','Letter / Memo',[
'ABC SERVICES SDN. BHD.','Reference No: ABC/OPS/2026/091','30 September 2026','Dear Sir,','RE: AUTHORISATION FOR DOCUMENT COLLECTION','We hereby authorise Ms. Nur Iman Binti Salleh to collect the documents on behalf of the company.','Please contact 03-7788 1122 if further verification is required.','Yours sincerely,','OPERATIONS MANAGER'],
['ABC/OPS/2026/091','30 September 2026','AUTHORISATION FOR DOCUMENT COLLECTION','Nur Iman Binti Salleh','03-7788 1122']),
sample('report_fresh','Report / Statement','Report / Statement',[
'MONTHLY OPERATIONS REPORT','Report Date: 30 September 2026','Prepared By: Service Excellence Team','EXECUTIVE SUMMARY','A total of 12,450 customer interactions were handled during September 2026.','FINDINGS','First contact resolution: 88.4%','Average handling time: 326 seconds','Customer satisfaction: 91.2%','CONCLUSION','Performance remained within the agreed service thresholds.'],
['MONTHLY OPERATIONS REPORT','30 September 2026','12,450','88.4%','326 seconds','91.2%','CONCLUSION']),
sample('general_fresh','General Document','General Document',[
'CUSTOMER SERVICE QUICK GUIDE','This document explains how users can submit supporting documents through the portal.','Step 1: Sign in using the registered email address.','Step 2: Select Upload Documents.','Step 3: Attach files in PDF, JPG or PNG format.','Maximum file size: 10 MB per file.','For assistance call 03-9000 1234.'],
['CUSTOMER SERVICE QUICK GUIDE','Upload Documents','PDF, JPG or PNG','10 MB','03-9000 1234'])
]

def fnt(sz,bold=False): return ImageFont.truetype(BOLD if bold else FONT,sz)
def wrap(draw,text,font,maxw):
    words=text.split(); out=[]; cur=''
    for w in words:
        cand=(cur+' '+w).strip()
        if draw.textbbox((0,0),cand,font=font)[2] <= maxw: cur=cand
        else:
            if cur: out.append(cur)
            cur=w
    if cur: out.append(cur)
    return out or ['']
def render(s):
    kind=s['kind']; W,H=(1800,1120) if kind=='card' else (1800,2450); margin=115; size=38 if kind=='card' else 34
    im=Image.new('RGB',(W,H),(250,250,248)); d=ImageDraw.Draw(im); d.rounded_rectangle((28,28,W-28,H-28),radius=26,outline=(155,160,170),width=3)
    y=margin
    for i,line in enumerate(s['lines']):
        head=i<2 or bool(re.match(r'^(?:APPLICATION FORM|INVOICE|MONTHLY OPERATIONS REPORT|CUSTOMER SERVICE QUICK GUIDE|CERTIFICATE|PERAKUAN|SIJIL|MAKLUMAT|CIVIL AVIATION)',line,re.I))
        font=fnt(size+6 if head else size,head)
        for part in wrap(d,line,font,W-2*margin):
            d.text((margin,y),part,font=font,fill=(20,28,35)); y += (size+22 if head else size+17)
        y+=5
    wm=Image.new('RGBA',im.size,(0,0,0,0)); wd=ImageDraw.Draw(wm); wd.text((W*.37,H*.48),'FRESH QA FIXTURE',font=fnt(50,True),fill=(80,90,100,24)); im=Image.alpha_composite(im.convert('RGBA'),wm).convert('RGB')
    im=im.rotate(0.28,resample=Image.Resampling.BICUBIC,expand=False,fillcolor=(250,250,248)).filter(ImageFilter.GaussianBlur(0.16))
    p=IMG/(s['name']+'.jpg'); im.save(p,'JPEG',quality=78,optimize=True,dpi=(220,220)); return p

def ocr(path):
    variants=[]
    for mode in ('original','gray'):
        im=Image.open(path).convert('RGB')
        if mode=='gray': im=ImageOps.autocontrast(ImageOps.grayscale(im)).convert('RGB')
        tmp=OUT/f'_tmp_{path.stem}_{mode}.png'; im.save(tmp)
        base=OUT/f'_tess_{path.stem}_{mode}'
        subprocess.run(['tesseract',str(tmp),str(base),'-l','eng','--psm','6','tsv'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
        rows=Path(str(base)+'.tsv').read_text(errors='ignore').splitlines(); line_words={}; order=[]; confs=[]
        for row in rows[1:]:
            c=row.split('\t')
            if len(c)<12 or not c[11].strip(): continue
            try: cf=float(c[10])
            except: cf=-1
            if cf>=0: confs.append(cf)
            key=tuple(c[i] for i in (1,2,3,4))
            if key not in line_words: line_words[key]=[]; order.append(key)
            line_words[key].append(c[11].strip())
        txt='\n'.join(' '.join(line_words[k]) for k in order).strip(); mean=statistics.mean(confs) if confs else 0
        tmp.unlink(missing_ok=True); Path(str(base)+'.tsv').unlink(missing_ok=True); variants.append((mean,txt,mode))
    return max(variants,key=lambda x:x[0])

def norm(v): return re.sub(r'[^A-Z0-9]+',' ',str(v).upper()).strip()
def eq(a,b): return norm(a)==norm(b)
def anchor_hit(a,text): return norm(a) in norm(text)

runs=[]
for s in samples:
    path=render(s); conf,txt,mode=ocr(path); (OCR/(s['name']+'.txt')).write_text(txt)
    runs.append({**s,'image':str(path),'ocr_text':txt,'raw_confidence':round(conf,2),'variant':mode})
parser_input={'samples':[{'name':r['name'],'text':r['ocr_text'],'confidence':r['raw_confidence']} for r in runs]}
(OUT/'parser_input.json').write_text(json.dumps(parser_input,indent=2))
proc=subprocess.run(['node',str(ROOT/'tests'/'fresh_stress_format_harness.js'),str(OUT/'parser_input.json'),str(ROOT/'index.html')],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,check=True)
parsed=json.loads(proc.stdout)['results']; pm={x['name']:x for x in parsed}
results=[]
for r in runs:
    p=pm[r['name']]; fmap={f['label']:str(f.get('value') or '') for f in p['fields']}
    ach=[{'expected':a,'pass':anchor_hit(a,r['ocr_text'])} for a in r['anchors']]
    fld=[]
    for label,exp in r['fields'].items():
        act=fmap.get(label,''); fld.append({'label':label,'expected':exp,'actual':act,'pass':eq(exp,act)})
    results.append({'name':r['name'],'profile':r['profile'],'expected_type':r['expected_type'],'detected_type':p['detected_type'],'type_pass':p['detected_type']==r['expected_type'],'raw_ocr_confidence':r['raw_confidence'],'variant':r['variant'],'anchors':ach,'anchor_pass':sum(x['pass'] for x in ach),'anchor_total':len(ach),'fields':fld,'field_pass':sum(x['pass'] for x in fld),'field_total':len(fld),'strict_complete':bool(p.get('validation',{}).get('complete')),'strict_problems':p.get('validation',{}).get('problems',[]),'output_contract_pass':bool(p.get('output_contract',{}).get('valid')),'output_contract_issues':p.get('output_contract',{}).get('issues',[]),'output_lengths':p.get('output_lengths',{}),'image':str(Path(r['image']).relative_to(ROOT)),'ocr_text':r['ocr_text']})
summary={'profiles_tested':len(results),'type_pass':sum(x['type_pass'] for x in results),'type_total':len(results),'anchor_pass':sum(x['anchor_pass'] for x in results),'anchor_total':sum(x['anchor_total'] for x in results),'field_pass':sum(x['field_pass'] for x in results),'field_total':sum(x['field_total'] for x in results),'output_contract_pass':sum(x['output_contract_pass'] for x in results),'output_contract_total':len(results),'mean_raw_ocr_confidence':round(statistics.mean(x['raw_ocr_confidence'] for x in results),2)}
(OUT/'fresh_stress_results.json').write_text(json.dumps({'summary':summary,'results':results},indent=2))
print(json.dumps(summary,indent=2))
for r in results:
    print(f"{r['name']}: type={'PASS' if r['type_pass'] else 'FAIL'} {r['detected_type']} anchors={r['anchor_pass']}/{r['anchor_total']} fields={r['field_pass']}/{r['field_total']} formats={'PASS' if r['output_contract_pass'] else 'FAIL'} strict={'PASS' if r['strict_complete'] else 'REVIEW'} conf={r['raw_ocr_confidence']}")
    for f in r['fields']:
        if not f['pass']: print('  FIELD FAIL',f['label'],'expected=',f['expected'],'actual=',f['actual'])
    if not r['type_pass']: print('  TYPE EXPECTED',r['expected_type'])
    if not r['output_contract_pass']: print('  OUTPUT ISSUES',r['output_contract_issues'])
