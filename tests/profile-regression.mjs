import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const html = fs.readFileSync(path.join(here, '..', 'index.html'), 'utf8');
const start = html.indexOf('<script>') + '<script>'.length;
const end = html.lastIndexOf('</script>');
if (start < '<script>'.length || end < start) throw new Error('index.html script block not found');
const app = html.slice(start, end);

const prelude = String.raw`
const _els=new Map();
function makeEl(id){return {id,value:id==='documentProfile'?'auto':id==='accuracyMode'?'high':id==='ocrLanguage'?'eng+msa':id==='visionEndpoint'?'/api/ocr':'',checked:['suppressHeaderFooter','preserveLiteral','excludeQR','preferPdfText','detectTables','groupFields','universalExtraction','aiVision'].includes(id),style:{},classList:{add(){},remove(){}},addEventListener(){},querySelectorAll(){return[]},appendChild(){},remove(){},setAttribute(){},click(){},innerHTML:'',textContent:'',disabled:false,files:[],dataset:{},scrollTop:0,scrollHeight:0};}
globalThis.document={getElementById(id){if(!_els.has(id))_els.set(id,makeEl(id));return _els.get(id)},querySelectorAll(){return[]},createElement(tag){return makeEl(tag)},body:{appendChild(){}}};
globalThis.pdfjsLib={GlobalWorkerOptions:{}};
globalThis.Tesseract={};
globalThis.navigator={clipboard:{writeText:async()=>{}}};
globalThis.URL={createObjectURL(){return''},revokeObjectURL(){}};
globalThis.Blob=function(){};
`;

const tests = String.raw`
function valueOf(fields,label){return (fields.find(x=>x.label===label)||{}).value||''}
function assertNoField(fields,label,name){if(fields.some(x=>x.label===label)){console.error('UNWANTED FIELD:',name,label);return 1}return 0}
const samples=[
  {
    name:'MyKad image 1 full wrapped name and full front address',
    type:'Malaysia MyKad',
    lines:['KAD PENGENALAN MALAYSIA','IDENTITY CARD','860815-38-6718','NOOR TEST BINTI','EXAMPLE','NO 17','JALAN PERISAI 3','BANDAR SEBERANG PERAK','36000 KAMPUNG GAJAH','PERAK','WARGANEGARA','ISLAM','PEREMPUAN'],
    checks:[['Name','NOOR TEST BINTI EXAMPLE'],['Identity Number','860815-38-6718'],['Address','NO 17 JALAN PERISAI 3 BANDAR SEBERANG PERAK 36000 KAMPUNG GAJAH PERAK'],['Religion','ISLAM'],['Citizenship','WARGANEGARA'],['Gender','PEREMPUAN']]
  },
  {
    name:'MyKad front plus back excludes back reference and scanner text',
    type:'Malaysia MyKad',
    lines:['KAD PENGENALAN MALAYSIA','IDENTITY CARD','940202-10-6330','TESTSWARY A/P VASU','NO 32 BATU 34','JALAN RAWANG','KAMPUNG SUNGAI DARAH','45600 BATANG BERJUNTAI','SELANGOR','WARGANEGARA','PEREMPUAN','Scanned with CamScanner','KETUA PENGARAH PENDAFTARAN NEGARA','940202-10-6330-02-01'],
    checks:[['Name','TESTSWARY A/P VASU'],['Identity Number','940202-10-6330'],['Address','NO 32 BATU 34 JALAN RAWANG KAMPUNG SUNGAI DARAH 45600 BATANG BERJUNTAI SELANGOR'],['Citizenship','WARGANEGARA'],['Gender','PEREMPUAN']]
  },
  {
    name:'MyPR full name and full address',
    type:'Malaysia MyPR',
    lines:['KAD PENGENALAN','MyPR','901231-10-6789','TAN TEST BIN SAMPLE','NO 42, JALAN MERAH','TAMAN KEMBOJA','88400 KOTA TEST','SABAH','PEMASTAUTIN TETAP','LELAKI'],
    checks:[['Name','TAN TEST BIN SAMPLE'],['Identity Number','901231-10-6789'],['Address','NO 42, JALAN MERAH TAMAN KEMBOJA 88400 KOTA TEST SABAH'],['Citizenship','PEMASTAUTIN TETAP / PR'],['Gender','LELAKI']]
  },
  {
    name:'Passport full printed name and MRZ',
    type:'Malaysia Passport',
    lines:['MALAYSIA','Passport / Pasport','Jenis / Type P','Kod Negara / Country Code MYS','No. Pasport / Passport No A00000000','Nama / Name TEST BIN PERSON','Warganegara / Nationality MALAYSIA','No. Pengenalan / Identity No. 930216146007','Tarikh Lahir / Date of Birth 16 FEB 1993','Tempat Lahir / Place of Birth KUALA LUMPUR','Jantina / Sex L-M','Tinggi / Height 174 cm','Tarikh Dikeluarkan / Date of Issue 31 AUG 2017','Tarikh Tamat / Date of Expiry 31 AUG 2024','Pejabat Pengeluar / Issuing Office KUALA LUMPUR','P<MYSTEST<BIN<PERSON<<<<<<<<<<<<<<<<<<<<<<','A00000000<MYS9302165M2408312930216146007<<72'],
    checks:[['Nama / Name','TEST BIN PERSON'],['Passport Number','A00000000'],['Warganegara / Nationality','MALAYSIA'],['No. Pengenalan / Identity No.','930216146007'],['MRZ Line 1','P<MYSTEST<BIN<PERSON<<<<<<<<<<<<<<<<<<<<<<'],['MRZ Line 2','A00000000<MYS9302165M2408312930216146007<<72']]
  },
  {
    name:'Driving licence wrapped full name and full address',
    type:'Malaysia Driving Licence',
    lines:['LESEN MEMANDU','DRIVING LICENCE','TENGKU TEST BIN','TENGKU SAMPLE','Warganegara / Nationality','MALAYSIA','No Pengenalan / Identity No.','801231114554','Kelas / Class','A B C D E F G H I','Tarikh / Validity','31 DIS 2014 - 31 DIS 2015','Alamat / Address','NO. 727, BLOK B PANGSAPURI PENYU,','JALAN KASAWARI EMAS 2,','TAMAN TEST,','52340 KUALA TERENGGANU,','TERENGGANU DARUL IMAN'],
    checks:[['Name','TENGKU TEST BIN TENGKU SAMPLE'],['Identity Number','801231114554'],['Class','A B C D E F G H I'],['Valid From','31 DIS 2014'],['Valid Until','31 DIS 2015'],['Address','NO. 727, BLOK B PANGSAPURI PENYU, JALAN KASAWARI EMAS 2, TAMAN TEST, 52340 KUALA TERENGGANU, TERENGGANU DARUL IMAN']]
  },
  {
    name:'SSM Business Registration Renewal excludes registrar',
    type:'SSM Business Registration Renewal',
    lines:['SURUHANJAYA SYARIKAT MALAYSIA','BORANG E (KAEDAH 13)','PERAKUAN PEMBAHARUAN PENDAFTARAN','AKTA PENDAFTARAN PERNIAGAAN 1956','Dengan ini diperakui bahawa perniagaan yang dijalankan dengan nama','TEST ENERGY ENTERPRISE','NO. PENDAFTARAN: 001772726-T','telah didaftarkan dari hari ini sehingga 24 JUN 2021 di bawah Akta Pendaftaran Perniagaan 1956, beralamat di PT12958A, FIRST FLOOR JALAN BBN 1/7D BANDAR PUTRA NILAI, 71800 NILAI, NEGERI SEMBILAN.','Bil. Cawangan: TIADA','Bertarikh di SISTEM EZBIZ pada 25 JUN 2019.','DATO TEST REGISTRAR','Pendaftar Perniagaan','Semenanjung Malaysia'],
    checks:[['Form','BORANG E (KAEDAH 13)'],['Nama Perniagaan / Business Name','TEST ENERGY ENTERPRISE'],['No. Pendaftaran / Registration Number','001772726-T'],['Valid Until / Sah Hingga','24 JUN 2021'],['Registered Address','PT12958A, FIRST FLOOR JALAN BBN 1/7D BANDAR PUTRA NILAI, 71800 NILAI, NEGERI SEMBILAN.'],['Bil. Cawangan / Number of Branches','TIADA'],['Certificate Date','25 JUN 2019'],['Issuing System','SISTEM EZBIZ']],
    absent:['Registrar']
  },
  {
    name:'SSM Business Registration Certificate excludes registrar',
    type:'SSM Business Registration Certificate',
    lines:['SURUHANJAYA SYARIKAT MALAYSIA','BORANG D (KAEDAH 13)','PERAKUAN PENDAFTARAN','AKTA PENDAFTARAN PERNIAGAAN 1956','Dengan ini diperakui bahawa perniagaan yang dijalankan dengan nama','TEST PERSON TRADING','NO. PENDAFTARAN: 202503028024 (003693443-X)','telah didaftarkan dari hari ini sehingga 26 JANUARI 2026 di bawah Akta Pendaftaran Perniagaan 1956, beralamat di 433 A, KAMPUNG BALIK BUKIT, 14120 SIMPANG AMPAT, PULAU PINANG','Bil. Cawangan: TIADA','Bertarikh di SISTEM EZBIZ pada 27 JANUARI 2025.','DATUK TEST REGISTRAR','Pendaftar Perniagaan','Semenanjung Malaysia'],
    checks:[['Form','BORANG D (KAEDAH 13)'],['Nama Perniagaan / Business Name','TEST PERSON TRADING'],['No. Pendaftaran / Registration Number','202503028024 (003693443-X)'],['Valid Until / Sah Hingga','26 JANUARI 2026'],['Registered Address','433 A, KAMPUNG BALIK BUKIT, 14120 SIMPANG AMPAT, PULAU PINANG'],['Bil. Cawangan / Number of Branches','TIADA'],['Certificate Date','27 JANUARI 2025'],['Issuing System','SISTEM EZBIZ']],
    absent:['Registrar']
  },
  {
    name:'SSM company information exact routing',
    type:'SSM Company Profile',
    lines:['SURUHANJAYA SYARIKAT MALAYSIA','BUTIR-BUTIR SETIAUSAHA SYARIKAT','MAKLUMAT SYARIKAT','Nama Syarikat :BIG DATAWORKS SDN. BHD.','Nama Syarikat Lama :BIG DATAWORKS MANAGEMENT SDN. BHD.','Tarikh Pertukaran :22-09-2016','No Syarikat :934369-U','Tarikh Pemerbadanan :01-03-2011','Tarikh Pendaftaran :TIADA','Jenis :BERHAD MENURUT SYER','SYARIKAT PERSENDIRIAN','Status :EXISTING','Alamat Daftar :110 JALAN MAAROF','BANGSAR BARU','KUALA LUMPUR','WILAYAH PERSEKUTUAN','Poskod :59000','Tempat Penubuhan :MALAYSIA','Alamat Perniagaan :1ST TIER WAREHOUSE','WISMA COMMERCEDOTCOM','NO. 15 JALAN TANDANG','PETALING JAYA','SELANGOR','Poskod :46050','Jenis Perniagaan :1. INFORMATION SERVICE SUPPLY, DATA ANALYTICS','AND SOFTWARE DEVELOPMENT','2. DOCUMENTS STORAGE, MANAGEMENT SERVICES AND','MOVERS','User Id: myq'],
    checks:[['Nama Syarikat / Company Name','BIG DATAWORKS SDN. BHD.'],['Nama Syarikat Lama / Old Company Name','BIG DATAWORKS MANAGEMENT SDN. BHD.'],['Tarikh Pertukaran / Date of Change','22-09-2016'],['No Syarikat / Company Registration No.','934369-U'],['Tarikh Pemerbadanan / Date of Incorporation','01-03-2011'],['Tarikh Pendaftaran / Registration Date','TIADA'],['Jenis / Type','BERHAD MENURUT SYER SYARIKAT PERSENDIRIAN'],['Status','EXISTING'],['Alamat Daftar / Registered Address','110 JALAN MAAROF BANGSAR BARU KUALA LUMPUR WILAYAH PERSEKUTUAN'],['Poskod / Postcode (Registered Address)','59000'],['Tempat Penubuhan / Place of Incorporation','MALAYSIA'],['Alamat Perniagaan / Business Address','1ST TIER WAREHOUSE WISMA COMMERCEDOTCOM NO. 15 JALAN TANDANG PETALING JAYA SELANGOR'],['Poskod / Postcode (Business Address)','46050'],['Jenis Perniagaan / Business Activity','1. INFORMATION SERVICE SUPPLY, DATA ANALYTICS AND SOFTWARE DEVELOPMENT 2. DOCUMENTS STORAGE, MANAGEMENT SERVICES AND MOVERS']]
  },
  {
    name:'CIDB PPK multiple specialisation codes are preserved',
    type:'CIDB PPK / Perakuan Pendaftaran',
    lines:['CIDB MALAYSIA','PERAKUAN PENDAFTARAN','No Pendaftaran: 1970616-SL035482','Nama Kontraktor: EXPERT METAL WORKS SDN. BHD.','Alamat Berdaftar: ROOM 102,229-1','JALAN PERKASA SATU','TAMAN MALURI, CHERAS,KUALA LUMPUR','55100 KUALA LUMPUR','WILAYAH PERSEKUTUAN','Gred, kategori dan pengkhususan pendaftaran','G7 B B18 B04','G7 CE CE21','G7 ME M15','Tarikh Mula Berkuatkuasa: 12 JAN 2016','Tarikh Habis Tempoh Perakuan: 18 MAR 2019','STATUS : AKTIF'],
    checks:[['No. Pendaftaran / Registration Number','1970616-SL035482'],['Nama Kontraktor / Contractor Name','EXPERT METAL WORKS SDN. BHD.'],['Alamat Berdaftar / Registered Address','ROOM 102,229-1 JALAN PERKASA SATU TAMAN MALURI, CHERAS,KUALA LUMPUR 55100 KUALA LUMPUR WILAYAH PERSEKUTUAN'],['Gred / Grade / Kategori / Category / Specialization / Pengkhususan','G7 B B18, B04\nG7 CE CE21\nG7 ME M15'],['Tarikh Mula Berkuatkuasa / Effective Date','12 JAN 2016'],['Tarikh Habis Tempoh Perakuan / Expiry Date','18 MAR 2019'],['Status','AKTIF']]
  },
  {
    name:'CIDB STB certificate number grade categories dates address and officer',
    type:'CIDB STB',
    lines:['PUSAT KHIDMAT KONTRAKTOR','SIJIL TARAF BUMIPUTERA','KONTRAKTOR KERJA','NO. SIJIL PENDAFTARAN GRED PENDAFTARAN KATEGORI TEMPOH SAH LAKU','0120221027-SL108244 G7 B DARI : 17/02/2023','G7 CE HINGGA : 10/11/2024','G7 ME','NAMA DAN ALAMAT BERDAFTAR','SHAH MAJU GLOBAL SDN. BHD.','SA37-2-A LORONG PANDAN UTAMA 3 PANDAN UTAMA','68000 AMPANG','SELANGOR','Hulu Langat','PEGAWAI SYARIKAT YANG DITAULIAHKAN NO. K/P','SYARIFAH TEST BINTI SAMPLE'],
    checks:[['No. Sijil Pendaftaran','0120221027-SL108244'],['Gred Pendaftaran','G7'],['Kategori / Category','B\nCE\nME'],['Effective Date','17/02/2023'],['Expiry Date','10/11/2024'],['Tempoh Sah Laku','Dari: 17/02/2023 Hingga: 10/11/2024'],['Nama dan Alamat Berdaftar','SHAH MAJU GLOBAL SDN. BHD. SA37-2-A LORONG PANDAN UTAMA 3 PANDAN UTAMA 68000 AMPANG SELANGOR Hulu Langat'],['Pegawai Syarikat Yang DiTauliahkan','SYARIFAH TEST BINTI SAMPLE']]
  }
];
let failed=0;
for(const sample of samples){
  const type=detectDocumentType(sample.lines);
  const fields=extractImportantFields(sample.lines,type);
  if(type!==sample.type){console.error('TYPE FAIL:',sample.name,type,'!=',sample.type);failed++}
  for(const [label,want] of sample.checks){const got=valueOf(fields,label);if(got!==want){console.error('FIELD FAIL:',sample.name,label,JSON.stringify(got),'!=',JSON.stringify(want));failed++}}
  for(const label of sample.absent||[]) failed+=assertNoField(fields,label,sample.name);
}
if(genderFromMalaysianNric('050905102913',{enabled:false})!==''){console.error('RULE FAIL: NRIC gender must stay disabled without an explicit profile rule');failed++}
if(genderFromMalaysianNric('050905-10-2913',{enabled:true})!=='LELAKI'){console.error('RULE FAIL: odd final digit should map to LELAKI when enabled');failed++}
if(genderFromMalaysianNric('901231106788',{enabled:true})!=='PEREMPUAN'){console.error('RULE FAIL: even final digit should map to PEREMPUAN when enabled');failed++}
const displayChecks=[
 ['SSM Business Registration Renewal','Perakuan Pembaharuan Pendaftaran — Akta Pendaftaran Perniagaan 1956'],
 ['SSM Business Registration Certificate','Perakuan Pendaftaran — Akta Pendaftaran Perniagaan 1956'],
 ['SSM Company Profile','Butir-Butir Setiausaha Syarikat / Maklumat Syarikat'],
 ['CIDB STB','CIDB STB / Sijil Taraf Bumiputera Kontraktor Kerja']
];
for(const [type,want] of displayChecks){const got=displayDocumentName(type);if(got!==want){console.error('DISPLAY FAIL:',type,got,'!=',want);failed++}}
if(failed) throw new Error(failed+' profile regression check(s) failed');
console.log('NeuroOCR strict profile regression tests passed:',samples.length,'document fixtures + NRIC + display rules');
`;

new Function(prelude + app + tests)();
