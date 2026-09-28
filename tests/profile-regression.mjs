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
const samples=[
  {name:'MyKad person name',type:'Malaysia MyKad',lines:['KAD PENGENALAN MALAYSIA','IDENTITY CARD','860815-38-6718','NUR TEST BINTI EXAMPLE','NO 17','JALAN PERISAI 3','36000 KAMPUNG TEST','PERAK','WARGANEGARA','ISLAM','PEREMPUAN'],checks:[['Name','NUR TEST BINTI EXAMPLE'],['Identity Number','860815-38-6718'],['Gender','PEREMPUAN']]},
  {name:'MyPR person name',type:'Malaysia MyPR',lines:['KAD PENGENALAN','MyPR','901231-10-6789','TAN TEST BIN SAMPLE','NO 42','JALAN MERAH','88400 TEST CITY','PEMASTAUTIN TETAP','LELAKI'],checks:[['Name','TAN TEST BIN SAMPLE'],['Identity Number','901231-10-6789'],['Citizenship','PEMASTAUTIN TETAP / PR']]},
  {name:'MyKad compact NRIC infers male only under profile rule',type:'Malaysia MyKad',lines:['KAD PENGENALAN MALAYSIA','IDENTITY CARD','050905102913','TEST PERSON BIN SAMPLE','NO 8 JALAN TEST','WARGANEGARA','ISLAM'],checks:[['Identity Number','050905-10-2913'],['Gender','LELAKI']]},
  {name:'MyPR compact NRIC infers female only under profile rule',type:'Malaysia MyPR',lines:['KAD PENGENALAN','MyPR','901231106788','TEST PERSON BINTI SAMPLE','NO 42 JALAN TEST','PEMASTAUTIN TETAP'],checks:[['Identity Number','901231-10-6788'],['Gender','PEREMPUAN']]},
  {name:'Passport person name and MRZ',type:'Malaysia Passport',lines:['MALAYSIA','Passport / Pasport','Jenis / Type P','Kod Negara / Country Code MYS','No. Pasport / Passport No A00000000','Nama / Name TEST BIN PERSON','Warganegara / Nationality MALAYSIA','No. Pengenalan / Identity No. 930216146007','Tarikh Lahir / Date of Birth 16 FEB 1993','Tempat Lahir / Place of Birth KUALA LUMPUR','Jantina / Sex L-M','Tinggi / Height 174 cm','Tarikh Dikeluarkan / Date of Issue 31 AUG 2017','Tarikh Tamat / Date of Expiry 31 AUG 2024','Pejabat Pengeluar / Issuing Office KUALA LUMPUR','P<MYSTEST<<BIN<PERSON<<<<<<<<<<<<<<<<<<<<<<','A00000000<MYS9302165M2408312930216146007<<72'],checks:[['Nama / Name','TEST BIN PERSON'],['Passport Number','A00000000'],['No. Pengenalan / Identity No.','930216146007']]},
  {name:'Driving Licence person name',type:'Malaysia Driving Licence',lines:['LESEN MEMANDU','DRIVING LICENCE','TENGKU TEST BIN SAMPLE','Warganegara / Nationality','MALAYSIA','No Pengenalan / Identity No.','801231114554','Kelas / Class','A B C D E F G H I','Tarikh / Validity','31 DIS 2014 - 31 DIS 2015','Alamat / Address','NO. 727, BLOK B PANGSAPURI TEST','52340 KUALA TERENGGANU','TERENGGANU DARUL IMAN'],checks:[['Name','TENGKU TEST BIN SAMPLE'],['Identity Number','801231114554'],['Valid From','31 DIS 2014'],['Valid Until','31 DIS 2015']]},
  {name:'SSM renewal fields and registrar',type:'SSM Business Registration Renewal',lines:['SURUHANJAYA SYARIKAT MALAYSIA','BORANG E (KAEDAH 13)','PERAKUAN PEMBAHARUAN PENDAFTARAN','AKTA PENDAFTARAN PERNIAGAAN 1956','Dengan ini diperakui bahawa perniagaan yang dijalankan dengan nama','TEST ENERGY ENTERPRISE','NO. PENDAFTARAN: 001772726-T','telah didaftarkan dari hari ini sehingga 24 JUN 2021 di bawah Akta Pendaftaran Perniagaan 1956, beralamat di PT12958A, FIRST FLOOR JALAN BBN 1/7D BANDAR PUTRA NILAI, 71800 NILAI, NEGERI SEMBILAN.','Bil. Cawangan: TIADA','Bertarikh di SISTEM EZBIZ pada 25 JUN 2019.','DATO TEST REGISTRAR','Pendaftar Perniagaan','Semenanjung Malaysia'],checks:[['Nama Perniagaan / Business Name','TEST ENERGY ENTERPRISE'],['No. Pendaftaran / Registration Number','001772726-T'],['Registrar','DATO TEST REGISTRAR']]},
  {name:'SSM company information exact field routing',type:'SSM Company Profile',lines:['SURUHANJAYA SYARIKAT MALAYSIA','BUTIR-BUTIR SETIAUSAHA SYARIKAT','MAKLUMAT SYARIKAT','Nama Syarikat :BIG DATAWORKS SDN. BHD.','Nama Syarikat Lama :BIG DATAWORKS MANAGEMENT SDN. BHD.','Tarikh Pertukaran :22-09-2016','No Syarikat :934369-U','Tarikh Pemerbadanan :01-03-2011','Tarikh Pendaftaran :TIADA','Jenis :BERHAD MENURUT SYER','SYARIKAT PERSENDIRIAN','Status :EXISTING','Alamat Daftar :110 JALAN MAAROF','BANGSAR BARU','KUALA LUMPUR','WILAYAH PERSEKUTUAN','Poskod :59000','Tempat Penubuhan :MALAYSIA','Alamat Perniagaan :1ST TIER WAREHOUSE','WISMA COMMERCEDOTCOM','NO. 15 JALAN TANDANG','PETALING JAYA','SELANGOR','Poskod :46050','Jenis Perniagaan :1. INFORMATION SERVICE SUPPLY, DATA ANALYTICS','AND SOFTWARE DEVELOPMENT','2. DOCUMENTS STORAGE, MANAGEMENT SERVICES AND','MOVERS','User Id: myq'],checks:[['Nama Syarikat / Company Name','BIG DATAWORKS SDN. BHD.'],['Nama Syarikat Lama / Old Company Name','BIG DATAWORKS MANAGEMENT SDN. BHD.'],['Tarikh Pertukaran / Date of Change','22-09-2016'],['No Syarikat / Company Registration No.','934369-U'],['Tarikh Pemerbadanan / Date of Incorporation','01-03-2011'],['Tarikh Pendaftaran / Registration Date','TIADA'],['Jenis / Type','BERHAD MENURUT SYER SYARIKAT PERSENDIRIAN'],['Status','EXISTING'],['Alamat Daftar / Registered Address','110 JALAN MAAROF BANGSAR BARU KUALA LUMPUR WILAYAH PERSEKUTUAN'],['Poskod / Postcode (Registered Address)','59000'],['Tempat Penubuhan / Place of Incorporation','MALAYSIA'],['Alamat Perniagaan / Business Address','1ST TIER WAREHOUSE WISMA COMMERCEDOTCOM NO. 15 JALAN TANDANG PETALING JAYA SELANGOR'],['Poskod / Postcode (Business Address)','46050'],['Jenis Perniagaan / Business Activity','1. INFORMATION SERVICE SUPPLY, DATA ANALYTICS AND SOFTWARE DEVELOPMENT 2. DOCUMENTS STORAGE, MANAGEMENT SERVICES AND MOVERS']]},
  {name:'CIDB SPKK officer and ID',type:'CIDB SPKK',lines:['CIDB','SIJIL PEROLEHAN KERJA KERAJAAN','No. Pendaftaran: 0120040322-SL093643','Nama Kontraktor: TEST CONTRACTOR SDN. BHD.','Alamat Berdaftar: LOT 1 TEST ROAD','Daerah: PETALING','Tarikh Mula Berdaftar: 22/03/2004','G7 B Pembinaan Bangunan','Pegawai Syarikat Yang Ditauliahkan','ALI TEST BIN SAMPLE 980105016268','Tarikh Mula Berkuatkuasa: 10/03/2026','Tarikh Habis Tempoh Perakuan: 08/04/2028'],checks:[['Pegawai Syarikat Yang Ditauliahkan / Authorised Company Officer(s)','ALI TEST BIN SAMPLE — 980105016268']]}
];
let failed=0;
for(const sample of samples){
  const type=detectDocumentType(sample.lines);
  const fields=extractImportantFields(sample.lines,type);
  if(type!==sample.type){console.error('TYPE FAIL:',sample.name,type,'!=',sample.type);failed++}
  for(const [label,want] of sample.checks){const got=valueOf(fields,label);if(got!==want){console.error('FIELD FAIL:',sample.name,label,JSON.stringify(got),'!=',JSON.stringify(want));failed++}}
}
if(genderFromMalaysianNric('050905102913',{enabled:false})!==''){console.error('RULE FAIL: NRIC gender must stay disabled without an explicit profile rule');failed++}
if(genderFromMalaysianNric('050905-10-2913',{enabled:true})!=='LELAKI'){console.error('RULE FAIL: odd final digit should map to LELAKI when enabled');failed++}
if(genderFromMalaysianNric('901231106788',{enabled:true})!=='PEREMPUAN'){console.error('RULE FAIL: even final digit should map to PEREMPUAN when enabled');failed++}
if(displayDocumentName('SSM Company Profile')!=='Butir-Butir Setiausaha Syarikat / Maklumat Syarikat'){console.error('DISPLAY FAIL: SSM company detected document name is incorrect');failed++}
if(failed) throw new Error(failed+' profile regression check(s) failed');
console.log('NeuroOCR profile regression tests passed:',samples.length,'fixtures + NRIC rule checks');
`;

new Function(prelude + app + tests)();
