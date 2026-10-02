from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import subprocess, json, re, statistics, difflib, shutil, math

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'tests'/'v31_external'
IMGDIR=OUT/'images'; TXTDIR=OUT/'ocr'; EVDIR=ROOT/'evidence'/'screenshots'
for d in (OUT,IMGDIR,TXTDIR,EVDIR): d.mkdir(parents=True,exist_ok=True)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'; BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

samples=[
{
'name':'mykad_public_sarawak','label':'Malaysia ID / Passport — MyKad','expected_type':'Malaysia MyKad','kind':'card','tint':(226,243,246),
'source':'Kapit District Office, Sarawak — Contoh Dokumen (public sample)','source_url':'https://kapit.sarawak.gov.my/web/attachment/show/?docid=emttS1o5cHBocml4ekZYK082NWZjZz09Ojp2blZd9AI2V-ugyPHHW99U',
'lines':['KAD PENGENALAN MALAYSIA','MyKad','460619-12-5087','ABD RAUF BIN HAMSAH','KAMPUNG MASJID','P O BOX 42','89007 KENINGAU','SABAH','WARGANEGARA','ISLAM','LELAKI'],
'anchors':['460619-12-5087','ABD RAUF BIN HAMSAH','KAMPUNG MASJID','89007 KENINGAU','SABAH','WARGANEGARA','ISLAM','LELAKI'],
'fields':{'Identity Number':'460619-12-5087','Name':'ABD RAUF BIN HAMSAH','Address':'KAMPUNG MASJID P O BOX 42 89007 KENINGAU SABAH','Religion':'ISLAM','Citizenship':'WARGANEGARA','Gender':'LELAKI'}},
{
'name':'mypr_public_structure','label':'Malaysia ID / Passport — MyPR','expected_type':'Malaysia MyPR','kind':'card','tint':(249,214,220),
'source':'Jabatan Pendaftaran Negara — MyPR features (public reference)','source_url':'https://www.jpn.gov.my/en/information/mypr/',
'lines':['KAD PENGENALAN MALAYSIA','PEMASTAUTIN TETAP','MyPR','IDENTITY NUMBER: [REDACTED]','NAME: [REDACTED]','ADDRESS: [REDACTED]','PNL','ISLAM','LELAKI'],
'anchors':['KAD PENGENALAN MALAYSIA','PEMASTAUTIN TETAP','MyPR','PNL','ISLAM','LELAKI'],
'fields':{},'expected_review':True},
{
'name':'passport_public_firefly','label':'Malaysia ID / Passport — Passport','expected_type':'Malaysia Passport','kind':'card','tint':(222,240,249),
'source':'Firefly Airlines — Malaysian passport booking guide sample','source_url':'https://www.fireflyz.com.my/my/en/booking-guide.html',
'lines':['MALAYSIA','Pasport / Passport','Jenis / Type: P','Kod Negara / Country Code: MYS','Nama / Name: ALIA BINTI MOHD ZULKIFLI','Warganegara / Nationality: MALAYSIA','No. Pengenalan / Identity No.: 950425-14-5678','Tarikh lahir / Date of Birth: 25 APR 1995','Tempat Lahir / Place of Birth: KUALA LUMPUR','Jantina / Sex: P-F','Tinggi / Height: 164 cm','Tarikh Dikeluarkan / Date of Issue: 10 MAR 2022','Tarikh Tamat / Date of Expiry: 10 MAR 2027','Pejabat Pengeluar / Issuing Office: KDN - PUTRAJAYA'],
'anchors':['ALIA BINTI MOHD ZULKIFLI','950425-14-5678','25 APR 1995','KUALA LUMPUR','P-F','164 cm','10 MAR 2022','10 MAR 2027','KDN - PUTRAJAYA'],
'fields':{'Jenis / Type':'P','Kod Negara / Country Code':'MYS','Nama / Name':'ALIA BINTI MOHD ZULKIFLI','Warganegara / Nationality':'MALAYSIA','No. Pengenalan / Identity No.':'950425145678','Tarikh lahir / Date of Birth':'25 APR 1995','Tempat Lahir / Place of Birth':'KUALA LUMPUR','Jantina / Sex':'P-F','Tinggi / Height':'164 cm','Tarikh Dikeluarkan / Date of Issue':'10 MAR 2022','Tarikh Tamat / Date of Expiry':'10 MAR 2027','Pejabat Pengeluar / Issuing Office':'KDN - PUTRAJAYA'},'expected_review':True},
{
'name':'driving_public_wikimedia','label':'Malaysia Driving Licence','expected_type':'Malaysia Driving Licence','kind':'card','tint':(246,238,218),
'source':'Wikimedia Commons — Malaysia driving licence specimen','source_url':'https://commons.wikimedia.org/wiki/File:Malaysia_driving_licence.jpg',
'lines':['LESEN MEMANDU MALAYSIA','MALAYSIA DRIVING LICENCE','Nama / Name: [SPECIMEN REDACTED]','Warganegara / Nationality: MALAYSIA','No. Pengenalan / Identity No.: [REDACTED]','Kelas / Class: B2, D, E','Tempoh / Validity','11/05/2021 - 24/11/2025','Alamat / Address: [SPECIMEN REDACTED]'],
'anchors':['LESEN MEMANDU MALAYSIA','MALAYSIA DRIVING LICENCE','MALAYSIA','B2, D, E','11/05/2021','24/11/2025'],
'fields':{'Nationality':'MALAYSIA','Class':'B2 D E','Valid From':'11/05/2021','Valid Until':'24/11/2025'},'expected_review':True},
{
'name':'cidb_ppk_public','label':'CIDB Certificate — PPK','expected_type':'CIDB PPK / Perakuan Pendaftaran','kind':'doc','tint':(255,255,255),
'source':'CIDB CIMS — public PPK certificate','source_url':'https://cims.cidb.gov.my/SMIS/regcontractor/GenerateFileAdv.vbhtml?DocId=PPKUpgradeCertificate_12052023100756.pdf&s=155a1dd9-c235-4b6d-9e91-a3d42dfdd75f',
'lines':['CIDB MALAYSIA','PERAKUAN PENDAFTARAN','No. Pendaftaran: 1970522-PK032492','Nama Kontraktor: LOYAL ENGINEERING SDN. BHD.','Alamat Berdaftar: NO. 43 (FIRST FLOOR), JALAN SARIKEI, OFF JALAN PAHANG,','53000 KUALA LUMPUR','WILAYAH PERSEKUTUAN KUALA LUMPUR','Daerah: KUALA LUMPUR','Tarikh Mula Berdaftar: 22/05/1998','GRED KATEGORI PENGKHUSUSAN','G7 B B01 B04 B29','G7 CE CE01 CE02 CE06 CE08 CE10 CE19 CE20 CE21 CE24 CE33 CE36 CE40 CE41 CE42','G7 ME M15 M19','Tarikh Mula Berkuatkuasa: 12/05/2023','Tarikh Habis Tempoh Perakuan: 09/03/2025','STATUS: AKTIF'],
'anchors':['1970522-PK032492','LOYAL ENGINEERING SDN. BHD.','53000 KUALA LUMPUR','22/05/1998','G7','12/05/2023','09/03/2025','AKTIF'],
'fields':{'No. Pendaftaran / Registration Number':'1970522-PK032492','Nama Kontraktor / Contractor Name':'LOYAL ENGINEERING SDN. BHD.','Daerah / District':'KUALA LUMPUR','Tarikh Mula Berdaftar':'22/05/1998','Tarikh Mula Berkuatkuasa / Effective Date':'12/05/2023','Tarikh Habis Tempoh Perakuan / Expiry Date':'09/03/2025','Status':'AKTIF'}},
{
'name':'ssm_registration_public','label':'SSM Business Registration','expected_type':'SSM Business Registration Certificate','kind':'doc','tint':(255,255,255),
'source':'SSM — official Business Certificate sample','source_url':'https://www.ssm.com.my/Pages/Product/PDF/ROB/BUSINESS%20CERTIFICATE.pdf',
'lines':['SURUHANJAYA SYARIKAT MALAYSIA','COMPANIES COMMISSION OF MALAYSIA','CERTIFICATE OF REGISTRATION','THE REGISTRATION OF BUSINESSES ACT 1956 (ACT 197)','FORM D (RULE 13)','This is to certify that the Business carried on under the name [REDACTED]','has been registered until 22 JANUARY in accordance with the Registration of Business Act 1956','with its principal place of business at B-7-13, Z RESIDENCE BUKIT JALIL,','JALAN JALIL PERWIRA 2, BUKIT JALIL, 58200 KUALA LUMPUR WILAYAH PERSEKUTUAN','Number of branches: N/A (0)','Dated at SISTEM EZBIZ this 23 JANUARY','DATUK NOR AZIMAH ABDUL AZIZ','REGISTRAR OF BUSINESSES PENINSULAR OF MALAYSIA'],
'anchors':['CERTIFICATE OF REGISTRATION','FORM D','22 JANUARY','B-7-13, Z RESIDENCE BUKIT JALIL','58200 KUALA LUMPUR','N/A (0)','23 JANUARY','SISTEM EZBIZ'],
'fields':{'Form':'FORM D (RULE 13)','Valid Until / Sah Hingga':'22 JANUARY','Registered Address':'B-7-13, Z RESIDENCE BUKIT JALIL, JALAN JALIL PERWIRA 2, BUKIT JALIL, 58200 KUALA LUMPUR WILAYAH PERSEKUTUAN','Bil. Cawangan / Number of Branches':'N/A (0)','Certificate Date':'23 JANUARY','Issuing System':'SISTEM EZBIZ'},'expected_review':True},
{
'name':'ssm_company_public','label':'SSM Document — Company Profile','expected_type':'SSM Company Profile','kind':'doc','tint':(255,255,255),
'source':'SSM — official Company Profile sample','source_url':'https://www.ssm.com.my/Pages/Product/PDF/ROC/COMPANY%20PROFILE.pdf',
'lines':['SURUHANJAYA SYARIKAT MALAYSIA','COMPANIES COMMISSION OF MALAYSIA','MAKLUMAT SYARIKAT','Nama : BIG DATAWORKS SDN. BHD.','Nama Lama : BIG DATAWORKS MANAGEMENT SDN. BHD.','Tarikh Pertukaran : 22-09-2016','No. Pendaftaran : 201101006232(934369-T)','Tarikh Penubuhan : 01-03-2011','Jenis : BERHAD MENURUT SYER','SYARIKAT PERSENDIRIAN','Status : EXISTING','Alamat Daftar : 10 JALAN RAJA','ALANG BANGSAR','KUALA LUMPUR','WILAYAH PERSEKUTUAN','Poskod 59000','Tempat Penubuhan : MALAYSIA','Alamat Perniagaan : A-7-10 WISMA MUTIARA','15 JALAN TANDANG','PETALING JAYA','SELANGOR','Poskod 46050','Jenis Perniagaan : 1. DATA ANALYTICS AND SOFTWARE DEVELOPMENT','2. DOCUMENTS STORAGE, MANAGEMENT SERVICES AND MOVERS'],
'anchors':['BIG DATAWORKS SDN. BHD.','BIG DATAWORKS MANAGEMENT SDN. BHD.','201101006232(934369-T)','01-03-2011','EXISTING','59000','46050','DATA ANALYTICS AND SOFTWARE DEVELOPMENT'],
'fields':{'Nama Syarikat / Company Name':'BIG DATAWORKS SDN. BHD.','Nama Syarikat Lama / Old Company Name':'BIG DATAWORKS MANAGEMENT SDN. BHD.','Tarikh Pertukaran / Date of Change':'22-09-2016','No Syarikat / Company Registration No.':'201101006232(934369-T)','Tarikh Pemerbadanan / Date of Incorporation':'01-03-2011','Jenis / Type':'BERHAD MENURUT SYER SYARIKAT PERSENDIRIAN','Status':'EXISTING','Alamat Daftar / Registered Address':'10 JALAN RAJA ALANG BANGSAR KUALA LUMPUR WILAYAH PERSEKUTUAN','Poskod / Postcode (Registered Address)':'59000','Tempat Penubuhan / Place of Incorporation':'MALAYSIA','Alamat Perniagaan / Business Address':'A-7-10 WISMA MUTIARA 15 JALAN TANDANG PETALING JAYA SELANGOR','Poskod / Postcode (Business Address)':'46050','Jenis Perniagaan / Business Activity':'1. DATA ANALYTICS AND SOFTWARE DEVELOPMENT 2. DOCUMENTS STORAGE, MANAGEMENT SERVICES AND MOVERS'}},
{
'name':'invoice_receipt_public','label':'Invoice / Receipt','expected_type':'Invoice / Receipt','kind':'receipt','tint':(250,249,243),
'source':'Asprise/receipt-ocr — public McDonald’s receipt OCR sample','source_url':'https://github.com/Asprise/receipt-ocr',
'lines':["McDonald's Toa Payoh Central",'600 @ Toa Payoh #01-02,','Singapore 319515','Tel: 62596362',"McDonald's Restaurants Pte Ltd",'GST REGN NO: M2-0023981-4','TAX INVOICE','INV. 002201330026','ORD # 57 -REG #1- 13/01/2016 15:49:52','QTY ITEM TOTAL','1 Med Ice Lemon Tea 2.95','1 Coffee with Milk 2.40','Eat-In Total (incl GST) 5.35','Cash Tendered 10.00','Change 4.65','TOTAL INCLUDES GST OF 0.35','Thank You and Have A Nice Day'],
'anchors':["McDonald's Toa Payoh Central",'M2-0023981-4','TAX INVOICE','002201330026','13/01/2016','Med Ice Lemon Tea','2.95','Coffee with Milk','2.40','5.35','10.00','4.65','0.35'],'fields':{}},
{
'name':'form_application_public','label':'Form / Application','expected_type':'Form / Application','kind':'doc','tint':(255,255,255),
'source':'Bank Negara Malaysia — CCRIS/eCCRIS Application Form','source_url':'https://www.bnm.gov.my/download-forms',
'lines':['BANK NEGARA MALAYSIA','BORANG PERMOHONAN / APPLICATION FORM','Nama Pemohon / Name of Applicant: ____________________','Nombor MyKad/Pasport / MyKad/Passport Number: ____________________','Alamat / Address: ______________________________________________','Nombor Telefon / Telephone Number: ____________________','Tujuan Permohonan / Purpose of Application','[ ] Permohonan Laporan CCRIS','PENGISYTIHARAN PINJAMAN / LOAN DECLARATION','Tandatangan Pemohon / Applicant Signature: ____________________'],
'anchors':['BORANG PERMOHONAN','APPLICATION FORM','Nama Pemohon','Nombor MyKad/Pasport','Purpose of Application','LOAN DECLARATION'],'fields':{}},
{
'name':'letter_memo_public','label':'Letter / Memo','expected_type':'Letter / Memo','kind':'doc','tint':(255,255,255),
'source':'Bank Negara Malaysia — Sample Authorisation Letter (Company)','source_url':'https://www.bnm.gov.my/download-forms',
'lines':['Syarikat XXX Sdn Bhd','46000 Petaling Jaya','Selangor','Bank Negara Malaysia','Jalan Dato Onn','50480 Kuala Lumpur','Dear Sir / Madam','Request for CCRIS Report for XXX Sdn. Bhd','We hereby authorise our representative to submit the application and collect the CCRIS report on behalf of the company.','Enclosed are the required documents for the above purposes.','Yours faithfully','Authorised Signatory'],
'anchors':['Syarikat XXX Sdn Bhd','46000 Petaling Jaya','Bank Negara Malaysia','Request for CCRIS Report','Enclosed are the required documents','Yours faithfully'],'fields':{}},
{
'name':'certificate_licence_public','label':'Certificate / Licence','expected_type':'Certificate / Licence','kind':'doc','tint':(255,255,255),
'source':'Civil Aviation Authority of Malaysia — Attachment 1 Sample Licence','source_url':'https://www.caam.gov.my/wp-content/uploads/2022/03/AI-22_2021-REV-1-Revised-Flight-Crew-Licence.pdf',
'lines':['CAAM 1','CIVIL AVIATION AUTHORITY OF MALAYSIA','MALAYSIA','AIRLINE TRANSPORT PILOT LICENCE (AEROPLANE)','Nombor Lesen / Licence Number: 8888','Nama Penuh / Name in Full: DARYL AJAY SEE','Tarikh Lahir / Date of Birth: 10.01.2001','Alamat / Address: LOT AD-13 TAMAN DATUK REZA, CYBER RAYA, 81250 JOHOR BAHRU','Kerakyatan / Nationality: MALAYSIAN','Nombor MyKad atau Pasport / MyKad or Passport Number: 010110-11-5335','Tarikh / Date: 03.01.2022','Perkelasan / Rating: REFER TO RATINGS PAGE','Catatan / Remarks: ELP LEVEL 6 RTOL','Lain-lain / Others: FI 2'],
'anchors':['AIRLINE TRANSPORT PILOT LICENCE','8888','DARYL AJAY SEE','10.01.2001','81250 JOHOR BAHRU','MALAYSIAN','010110-11-5335','03.01.2022','ELP LEVEL 6','RTOL'],'fields':{}},
{
'name':'report_statement_public','label':'Report / Statement','expected_type':'Report / Statement','kind':'report','tint':(255,255,255),
'source':'Bank Negara Malaysia — Annual Report 2025, Statement of Financial Position','source_url':'https://www.bnm.gov.my/documents/20124/21185005/ar2025_en_ch4.pdf',
'lines':['BANK NEGARA MALAYSIA','ANNUAL REPORT 2025','STATEMENT OF FINANCIAL POSITION AS AT 31 DECEMBER 2025','2025 2024','RM million RM million','ASSETS Note','Gold and Foreign Financial Assets 3 480,292 489,309','International Monetary Fund Reserve Position 4 29,494 30,821','Total Assets 602,219 621,540','LIABILITIES AND CAPITAL','Total Liabilities 405,474 431,474','Capital 13 100 100','Risk Reserve 15 155,310 147,896','Total Capital and Reserves 196,745 190,066','Total Liabilities and Capital 602,219 621,540'],
'anchors':['STATEMENT OF FINANCIAL POSITION AS AT 31 DECEMBER 2025','480,292','489,309','602,219','621,540','405,474','431,474','196,745','190,066'],'fields':{}},
{
'name':'general_document_public','label':'General Document','expected_type':'General Document','kind':'doc','tint':(255,255,255),
'source':'CIDB iProject — FAQ Maklumat Kos Projek Pembinaan','source_url':'https://iprojek.cidb.gov.my/Files/FAQ.pdf',
'lines':['FAQ','Maklumat Kos Projek Pembinaan','1. Apakah tujuan program ini dilaksanakan?','CIDB Malaysia sedang menjalankan kajian pengumpulan maklumat data kos pembinaan untuk kerja-kerja bangunan dan kejuruteraan awam.','2. Bagaimanakah pihak kontraktor menghantar segala maklumat yang diperlukan?','Pihak kontraktor perlu mengemukakan maklumat seperti yang dinyatakan di dalam pautan yang diterima melalui emel syarikat.','3. Apakah format dokumen yang diperlukan untuk dimuatnaik ke dalam sistem tersebut?','Pihak kontraktor perlu memastikan segala dokumen yang diperlukan dimuat naik dalam format PDF sahaja.','7. Bagaimana jika pihak kontraktor menghadapi masalah semasa mengisi borang?','Pihak kontraktor boleh menghubungi kami di talian 03-4040 0399 untuk sebarang bantuan.'],
'anchors':['FAQ','Maklumat Kos Projek Pembinaan','CIDB Malaysia','format PDF sahaja','03-4040 0399'],'fields':{}}
]

def font(sz,bold=False): return ImageFont.truetype(BOLD if bold else FONT,sz)

def wrap(draw,text,f,maxw):
    words=text.split(); out=[]; cur=''
    for w in words:
        cand=(cur+' '+w).strip()
        if draw.textbbox((0,0),cand,font=f)[2] <= maxw: cur=cand
        else:
            if cur: out.append(cur)
            cur=w
    if cur: out.append(cur)
    return out or ['']

def render_sample(s):
    kind=s['kind']
    if kind=='card': W,H=1700,1050; margin=90; body_size=39
    elif kind=='receipt': W,H=1300,2100; margin=110; body_size=34
    else: W,H=1800,2450; margin=140; body_size=34
    im=Image.new('RGB',(W,H),s['tint']); d=ImageDraw.Draw(im)
    # subtle border and header for layout realism
    d.rounded_rectangle((25,25,W-25,H-25),radius=30,outline=(160,170,180),width=3)
    y=margin
    for i,line in enumerate(s['lines']):
        is_head=i<2 or bool(re.match(r'^(?:CERTIFICATE|PERAKUAN|BORANG|FORM|STATEMENT|AIRLINE|FAQ|MAKLUMAT SYARIKAT|TAX INVOICE)',line,re.I))
        f=font(body_size+7 if is_head else body_size,bold=is_head)
        for part in wrap(d,line,f,W-2*margin):
            d.text((margin,y),part,font=f,fill=(20,30,40))
            y += (body_size+20 if is_head else body_size+16)
        y += 6
        if y>H-margin-60: break
    # add light diagonal test watermark on public/source-derived fixtures
    wm=Image.new('RGBA',im.size,(0,0,0,0)); wd=ImageDraw.Draw(wm); wf=font(52,True)
    wd.text((W*0.28,H*0.50),'SOURCE-DERIVED QA FIXTURE',font=wf,fill=(80,90,100,28))
    im=Image.alpha_composite(im.convert('RGBA'),wm).convert('RGB')
    # slight real-world degradation
    im=im.rotate(0.22,resample=Image.Resampling.BICUBIC,expand=False,fillcolor=s['tint']).filter(ImageFilter.GaussianBlur(0.18))
    path=IMGDIR/(s['name']+'.jpg'); im.save(path,'JPEG',quality=80,optimize=True,dpi=(220,220)); return path

def tesseract_variant(path, variant):
    """Run one Tesseract TSV pass and reconstruct line-preserving OCR text from it."""
    im=Image.open(path).convert('RGB')
    if variant=='gray':
        im=ImageOps.autocontrast(ImageOps.grayscale(im)).convert('RGB')
    elif variant=='binary':
        g=ImageOps.autocontrast(ImageOps.grayscale(im))
        im=g.point(lambda x: 255 if x>178 else 0).convert('RGB')
    tmp=OUT/f'_tmp_{path.stem}_{variant}.png'; im.save(tmp, optimize=True)
    base=OUT/f'_tess_{path.stem}_{variant}'
    cmd=['tesseract',str(tmp),str(base),'-l','eng','--psm','6','tsv']
    subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    rows=Path(str(base)+'.tsv').read_text(errors='ignore').splitlines()
    line_words={}; line_order=[]; confs=[]
    for row in rows[1:]:
        cols=row.split('\t')
        if len(cols)<12: continue
        txt=cols[11].strip()
        if not txt: continue
        try: c=float(cols[10])
        except: c=-1
        if c>=0: confs.append(c)
        key=tuple(cols[i] for i in (1,2,3,4))  # page, block, paragraph, line
        if key not in line_words:
            line_words[key]=[]; line_order.append(key)
        line_words[key].append(txt)
    txt='\n'.join(' '.join(line_words[k]) for k in line_order).strip()
    mean=statistics.mean(confs) if confs else 0
    tmp.unlink(missing_ok=True); Path(str(base)+'.tsv').unlink(missing_ok=True)
    return txt,mean

def norm(s): return re.sub(r'[^A-Z0-9]+',' ',str(s).upper()).strip()
def anchor_hit(anchor,text):
    a=norm(anchor); t=norm(text)
    if not a: return True
    if a in t: return True
    # conservative fuzzy only for punctuation/OCR noise; threshold very high
    return difflib.SequenceMatcher(None,a,t).quick_ratio()>0.995 if len(a)>8 else False

def value_equal(exp,act): return norm(exp)==norm(act)

rendered=[]
for s in samples:
    path=render_sample(s)
    variants=[]
    for v in ('original','gray'):
        txt,conf=tesseract_variant(path,v); variants.append((conf,txt,v))
    conf,txt,var=max(variants,key=lambda x:x[0])
    (TXTDIR/(s['name']+'.txt')).write_text(txt)
    rendered.append({**s,'image':str(path),'ocr_text':txt,'raw_confidence':round(conf,2),'selected_variant':var})

# Call actual browser-app parser functions from V31 using the OCR output.
parser_input={'samples':[{'name':x['name'],'text':x['ocr_text']} for x in rendered]}
(OUT/'parser_input.json').write_text(json.dumps(parser_input,indent=2))
proc=subprocess.run(['node',str(ROOT/'tests'/'v31_parser_extract.js'),str(OUT/'parser_input.json'),str(ROOT/'index.html')],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,check=True)
parser=json.loads(proc.stdout)['results']; pm={x['name']:x for x in parser}
results=[]
for s in rendered:
    p=pm[s['name']]; fmap={f['label']:f['value'] for f in p['fields']}
    anchors=[{'expected':a,'pass':anchor_hit(a,s['ocr_text'])} for a in s['anchors']]
    fields=[]
    for label,expected in s.get('fields',{}).items():
        actual=str(fmap.get(label,'') or '')
        fields.append({'label':label,'expected':expected,'actual':actual,'pass':value_equal(expected,actual)})
    results.append({
        'name':s['name'],'profile':s['label'],'source':s['source'],'source_url':s['source_url'],'image':s['image'],
        'expected_type':s['expected_type'],'detected_type':p['detected_type'],'type_pass':p['detected_type']==s['expected_type'],
        'raw_ocr_confidence':s['raw_confidence'],'selected_variant':s['selected_variant'],
        'anchors':anchors,'anchor_pass':sum(a['pass'] for a in anchors),'anchor_total':len(anchors),
        'fields':fields,'field_pass':sum(f['pass'] for f in fields),'field_total':len(fields),
        'expected_review':bool(s.get('expected_review',False)),
        'parser_fields':p['fields'],'ocr_text':s['ocr_text']
    })

summary={
  'profiles_tested':len(results),
  'type_pass':sum(r['type_pass'] for r in results),'type_total':len(results),
  'anchor_pass':sum(r['anchor_pass'] for r in results),'anchor_total':sum(r['anchor_total'] for r in results),
  'field_pass':sum(r['field_pass'] for r in results),'field_total':sum(r['field_total'] for r in results),
  'mean_raw_ocr_confidence':round(statistics.mean(r['raw_ocr_confidence'] for r in results),2)
}
(OUT/'v31_external_results.json').write_text(json.dumps({'summary':summary,'results':results},indent=2))
print(json.dumps(summary,indent=2))
for r in results:
    print(f"{r['name']}: type={r['detected_type']} {'PASS' if r['type_pass'] else 'FAIL'} anchors={r['anchor_pass']}/{r['anchor_total']} fields={r['field_pass']}/{r['field_total']} conf={r['raw_ocr_confidence']}")
