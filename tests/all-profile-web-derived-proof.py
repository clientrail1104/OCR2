#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import pytesseract, re, json, subprocess, textwrap, shutil

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'tests'/'generated_profiles'
OUT.mkdir(exist_ok=True)
FONT_PATH=next((p for p in ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf'] if Path(p).exists()),None)
if not FONT_PATH: raise SystemExit('No font available')
font=ImageFont.truetype(FONT_PATH,26)
font_b=ImageFont.truetype(FONT_PATH,31)

SAMPLES=[
{
'name':'driving_licence','expected_type':'Malaysia Driving Licence','profile':'Malaysia Driving Licence','source':'Wikimedia Commons Malaysia driving licence specimen',
'url':'https://commons.wikimedia.org/wiki/File:Malaysia_driving_licence.jpg',
'text':'''LESEN MEMANDU\nDRIVING LICENCE\nMALAYSIA\nNama / Name\nNUR AISYAH BINTI RAHMAN\nWarganegara / Nationality\nMALAYSIA\nNo. Pengenalan / Identity No.\n900101105678\nKelas / Class\nB2, D, E\nTempoh / Validity\n11/05/2021 - 24/11/2025\nAlamat / Address\nNO 12 JALAN MAWAR 3\nTAMAN MAWAR\n43000 KAJANG\nSELANGOR''',
'anchors':['DRIVING LICENCE','NUR AISYAH BINTI RAHMAN','MALAYSIA','900101105678','B2, D, E','11/05/2021','24/11/2025','NO 12 JALAN MAWAR 3','43000 KAJANG','SELANGOR']},
{
'name':'cidb_spkk','expected_type':'CIDB SPKK','profile':'CIDB Certificate','source':'CIDB official SPKK guidance/sample certificate',
'url':'https://www.cidb.gov.my/wp-content/uploads/2022/10/1.0-Syarat-Pendaftaran-Sijil-Perolehan-.pdf',
'text':'''CIDB MALAYSIA\nSIJIL PEROLEHAN KERJA KERAJAAN\nSPKK\nNo. Pendaftaran / Registration Number: 0123456-AB1234\nNama Kontraktor / Contractor Name: CONTOH BINA SDN BHD\nAlamat Berdaftar / Registered Address: NO 10 JALAN INDUSTRI 2, 40150 SHAH ALAM, SELANGOR\nDaerah / District: PETALING\nTarikh Mula Berdaftar / Initial Registration Date: 01/01/2020\nGred / Grade / Kategori / Category: G7 B CE ME\nPegawai Syarikat Yang Ditauliahkan / Authorised Company Officer(s): AHMAD BIN ALI\nTarikh Mula Berkuatkuasa / Effective Date: 01/01/2026\nTarikh Habis Tempoh Perakuan / Expiry Date: 31/12/2026''',
'anchors':['SIJIL PEROLEHAN KERJA KERAJAAN','0123456-AB1234','CONTOH BINA SDN BHD','40150 SHAH ALAM','G7 B CE ME','AHMAD BIN ALI','01/01/2026','31/12/2026']},
{
'name':'ssm_registration','expected_type':'SSM Business Registration Certificate','profile':'SSM Business Registration','source':'SSM official Business Certificate sample',
'url':'https://www.ssm.com.my/Pages/Product/PDF/ROB/BUSINESS%20CERTIFICATE.pdf',
'text':'''SURUHANJAYA SYARIKAT MALAYSIA\nCOMPANIES COMMISSION OF MALAYSIA\nBORANG D (KAEDAH 13)\nPERAKUAN PENDAFTARAN\nAKTA PENDAFTARAN PERNIAGAAN 1956\nCERTIFICATE OF REGISTRATION\nTHE REGISTRATION OF BUSINESSES ACT 1956\nJIN XIAO LONG TRADING\nREGISTRATION NO. : 201903350205 (003058656-T)\nhas this day been registered until 22 JANUARY\nprincipal place of business at B-7-13, Z RESIDENCE BUKIT JALIL, JALAN JALIL PERWIRA 2, BUKIT JALIL, 58200 KUALA LUMPUR WILAYAH PERSEKUTUAN\nNumber of branches: N/A (0)\nDated at SISTEM EZBIZ this 23 JANUARY\nDATUK NOR AZIMAH ABDUL AZIZ\nREGISTRAR OF BUSINESSES''',
'anchors':['CERTIFICATE OF REGISTRATION','JIN XIAO LONG TRADING','201903350205','003058656-T','22 JANUARY','58200 KUALA LUMPUR','N/A (0)','SISTEM EZBIZ','DATUK NOR AZIMAH ABDUL AZIZ']},
{
'name':'ssm_company','expected_type':'SSM Company Profile','profile':'SSM Document','source':'SSM Company Information product/sample structure',
'url':'https://www.ssm.com.my/Pages/Product/Company-Information.aspx',
'text':'''SURUHANJAYA SYARIKAT MALAYSIA\nCOMPANIES COMMISSION OF MALAYSIA\nMAKLUMAT SYARIKAT\nNama Syarikat / Company Name : CONTOH DIGITAL SDN. BHD.\nNama Syarikat Lama / Old Company Name : CONTOH TEKNOLOGI SDN. BHD.\nTarikh Pertukaran / Date of Change : 22-09-2016\nNo Syarikat / Company Registration No. : 123231-T\nTarikh Pemerbadanan / Date of Incorporation : 01-03-2011\nJenis / Type : LIMITED BY SHARES PRIVATE LIMITED\nStatus : EXISTING\nAlamat Daftar / Registered Address : 15 JALAN TANDANG TAMAN TASIK PERDANA KUALA LUMPUR\nPoskod / Postcode : 50480\nTempat Penubuhan / Place of Incorporation : MALAYSIA\nAlamat Perniagaan / Business Address : WISMA CONTOH 15 JALAN TANDANG KUALA LUMPUR\nPoskod / Postcode : 50480\nJenis Perniagaan / Business Activity : INFORMATION TECHNOLOGY SERVICES''',
'anchors':['MAKLUMAT SYARIKAT','CONTOH DIGITAL SDN. BHD.','22-09-2016','123231-T','01-03-2011','EXISTING','50480','INFORMATION TECHNOLOGY SERVICES']},
{
'name':'invoice_receipt','expected_type':'Invoice / Receipt','profile':'Invoice / Receipt','source':'Public OCR receipt/invoice datasets on GitHub',
'url':'https://github.com/themurtez/receipt-dataset-standardized',
'text':'''TAX INVOICE\nInvoice No: INV-001\nDate: 26/08/2026\nCustomer: Jane Doe\nVendor: Tech Store Inc.\nKeyboard 2 RM 500.00\nMouse 3 RM 150.00\nSubtotal RM 1450.00\nTax RM 87.00\nGrand Total RM 1537.00\nAmount Due RM 1537.00''',
'anchors':['TAX INVOICE','INV-001','26/08/2026','Jane Doe','Tech Store Inc.','Keyboard','Grand Total RM 1537.00','Amount Due RM 1537.00']},
{
'name':'form_application','expected_type':'Form / Application','profile':'Form / Application','source':'Bank Negara Malaysia CCRIS/eCCRIS Application Form',
'url':'https://www.bnm.gov.my/documents/20124/6190098/CCRIS_eCCRIS_Form.pdf',
'text':'''BANK NEGARA MALAYSIA\nCENTRAL BANK OF MALAYSIA\nBORANG CCRIS/eCCRIS 01 / CCRIS/eCCRIS 01 FORM\nBORANG PERMOHONAN / APPLICATION FORM\nPlease fill up completely and tick in the box\neCCRIS Registration\nName of Applicant: NUR AISYAH BINTI RAHMAN\nPurpose of Application: Check credit status\nMyKad Number/Passport Number: 900101105678\nDate of Birth: 01/01/1990\nE-mail Address: sample@example.com\nBusiness Registration Number: 202601234567\nSignature:\nDate:''',
'anchors':['BORANG PERMOHONAN','APPLICATION FORM','Name of Applicant','Purpose of Application','900101105678','sample@example.com','Business Registration Number']},
{
'name':'letter_memo','expected_type':'Letter / Memo','profile':'Letter / Memo','source':'Bank Negara Malaysia Sample Authorisation Letter for Company',
'url':'https://www.bnm.gov.my/documents/20124/6190098/Sample_Authorisation_Letter_CCRIS_Company_en.pdf',
'text':'''Company's Official Letterhead\nSyarikat XXX Sdn Bhd\nJalan 18B\n46000 Petaling Jaya\nSelangor\nDate: 30 September 2026\nBank Negara Malaysia\nJalan Dato' Onn\n50480 Kuala Lumpur\nDear Sir / Madam,\nRequest for CCRIS Report for XXX Sdn. Bhd\nWith reference to the above, Syarikat XXX Sdn Bhd has appointed Mr. Ahmad Bin Ali as the authorised person to request the CCRIS report for the company.\nEnclosed are the required documents for the above purposes.\nYours sincerely,\nCompany Director''',
'anchors':['Syarikat XXX Sdn Bhd','46000 Petaling Jaya','Bank Negara Malaysia','Request for CCRIS Report','authorised person','Yours sincerely']},
{
'name':'certificate_licence','expected_type':'Certificate / Licence','profile':'Certificate / Licence','source':'SSM official business certificate used as generic certificate regression',
'url':'https://www.ssm.com.my/Pages/Product/PDF/ROB/BUSINESS%20CERTIFICATE.pdf',
'text':'''CERTIFICATE OF REGISTRATION\nCertificate No: CERT-2026-001\nThis is to certify that\nCONTOH ENTERPRISE\nhas satisfied the applicable registration requirements.\nLicence No: LIC-778899\nValid From: 01 JANUARY 2026\nValid Until: 31 DECEMBER 2026\nIssued by: DEPARTMENT OF LICENSING''',
'anchors':['CERTIFICATE OF REGISTRATION','CERT-2026-001','This is to certify that','CONTOH ENTERPRISE','LIC-778899','31 DECEMBER 2026']},
{
'name':'report_statement','expected_type':'Report / Statement','profile':'Report / Statement','source':'Bank Negara Malaysia Annual Report 2025 - Our Finances',
'url':'https://www.bnm.gov.my/documents/20124/21185005/ar2025_en_ch4.pdf',
'text':'''BANK NEGARA MALAYSIA\nANNUAL REPORT 2025\nOUR FINANCES\nSTATEMENT OF FINANCIAL POSITION AS AT 31 DECEMBER 2025\n2025 2024\nRM million RM million\nASSETS\nGold and Foreign Financial Assets 480,292 489,309\nTotal Assets 602,219 621,540\nLIABILITIES AND CAPITAL\nTotal Liabilities 405,474 431,474\nTotal Capital and Reserves 196,745 190,066\nINCOME STATEMENT FOR THE YEAR ENDED 31 DECEMBER 2025\nTotal Income 14,345 14,978\nNet Profit After Tax 12,447 13,162''',
'anchors':['ANNUAL REPORT 2025','OUR FINANCES','STATEMENT OF FINANCIAL POSITION','Total Assets 602,219 621,540','INCOME STATEMENT','Net Profit After Tax 12,447 13,162']},
{
'name':'general_document','expected_type':'General Document','profile':'General document','source':'Generic regression document',
'url':'local-regression-fixture',
'text':'''PROJECT IMPLEMENTATION NOTE\nReference: OCR-GOLIVE-2026\nDate: 30 September 2026\nThe document processing service shall preserve all visible wording exactly as printed.\nIt shall not invent unreadable values.\nQuality checks must be completed before production acceptance.\nOwner: Document Automation Team\nStatus: Ready for controlled release''',
'anchors':['PROJECT IMPLEMENTATION NOTE','OCR-GOLIVE-2026','30 September 2026','preserve all visible wording exactly as printed','Document Automation Team']},
]

def fold(s):
    return re.sub(r'[^a-z0-9]+',' ',str(s).lower()).strip()

def render(sample,path):
    width=1700; margin=80; y=70
    wrapped=[]
    for i,line in enumerate(sample['text'].splitlines()):
        if len(line)>95:
            wrapped.extend(textwrap.wrap(line,95,break_long_words=False,replace_whitespace=False))
        else: wrapped.append(line)
    height=max(850,140+len(wrapped)*48)
    im=Image.new('RGB',(width,height),'white'); d=ImageDraw.Draw(im)
    for idx,line in enumerate(wrapped):
        use=font_b if idx<3 or re.search(r'CERTIFICATE|INVOICE|APPLICATION FORM|ANNUAL REPORT|DRIVING LICENCE|SIJIL',line,re.I) else font
        d.text((margin,y),line,fill='black',font=use); y+=48
    # light production-style degradation: JPEG recompression after tiny blur
    im=im.filter(ImageFilter.GaussianBlur(radius=.18))
    im.save(path,'JPEG',quality=88,subsampling=1)

results=[]; total=passed=0
ocr_texts={}
for s in SAMPLES:
    p=OUT/f"{s['name']}.jpg"; render(s,p)
    img=Image.open(p)
    txt=pytesseract.image_to_string(img,lang='eng',config='--psm 6')
    data=pytesseract.image_to_data(img,lang='eng',config='--psm 6',output_type=pytesseract.Output.DICT)
    confs=[float(c) for c,t in zip(data.get('conf',[]),data.get('text',[])) if str(t).strip() and float(c)>=0]
    raw_confidence=round(sum(confs)/len(confs),2) if confs else 0.0
    (OUT/f"{s['name']}.txt").write_text(txt,encoding='utf-8')
    ocr_texts[s['name']]=txt
    f=fold(txt); misses=[]
    for a in s['anchors']:
        total+=1
        ok=fold(a) in f
        passed+=int(ok)
        if not ok: misses.append(a)
    results.append({'name':s['name'],'profile':s['profile'],'expected_type':s['expected_type'],'source':s['source'],'url':s['url'],'anchor_pass':len(s['anchors'])-len(misses),'anchor_total':len(s['anchors']),'misses':misses,'raw_ocr':txt,'raw_ocr_confidence':raw_confidence})

# Browser parser/detector regression: execute the actual index.html parser in Node with DOM stubs.
node_script=ROOT/'tests'/'browser-parser-profile-proof.js'
parser_in={'samples':[{'name':s['name'],'expected_type':s['expected_type'],'text':ocr_texts[s['name']]} for s in SAMPLES]}
(OUT/'parser_input.json').write_text(json.dumps(parser_in,ensure_ascii=False),encoding='utf-8')
cp=subprocess.run(['node',str(node_script),str(OUT/'parser_input.json')],cwd=ROOT,text=True,capture_output=True)
if cp.returncode!=0:
    print(cp.stdout); print(cp.stderr); raise SystemExit('Browser parser proof failed')
parser=json.loads(cp.stdout)
by={x['name']:x for x in parser['results']}
for r in results:
    pr=by[r['name']]; r['detected_type']=pr['detected_type']; r['detection_pass']=pr['pass'];
    if not pr['pass']:
        print(json.dumps(r,indent=2)); raise SystemExit(f"Detection failed for {r['name']}: {pr['detected_type']} != {r['expected_type']}")
if passed!=total:
    for r in results:
        if r['misses']: print(r['name'],r['misses'])
    raise SystemExit(f'OCR anchors failed {passed}/{total}')
summary={'status':'PASS','web_source_derived_profiles':len(results),'ocr_anchor_exact_normalized':{'passed':passed,'total':total,'percent':round(passed/total*100,2)},'browser_detection':{'passed':sum(r['detection_pass'] for r in results),'total':len(results),'percent':100.0},'results':[{k:v for k,v in r.items() if k!='raw_ocr'} for r in results]}
(OUT/'all_profile_results.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
