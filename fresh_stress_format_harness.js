const fs=require('fs'),vm=require('vm');
const input=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const html=fs.readFileSync(process.argv[3]||'index.html','utf8');
const script=html.split('<script>')[1].split('</script>')[0];
function el(id){
  let value='';
  if(id==='documentProfile') value='auto';
  if(id==='accuracyMode') value='high';
  if(id==='outputMode') value='ultra';
  if(id==='ocrLanguage') value='eng';
  if(id==='visionEndpoint') value='';
  return {id,style:{},checked:true,value,textContent:'',innerHTML:'',files:[],dataset:{},classList:{add(){},remove(){},toggle(){}},addEventListener(){},appendChild(){},append(){},querySelectorAll(){return[]},setAttribute(){},click(){},remove(){},focus(){},select(){}};
}
const elements=new Map();
const document={getElementById(id){if(!elements.has(id))elements.set(id,el(id));return elements.get(id)},querySelectorAll(){return[]},createElement(){return el('created')},body:el('body')};
const sandbox={console:{log(){},error(){}},document,window:{},pdfjsLib:{GlobalWorkerOptions:{}},Tesseract:{},mammoth:{},JSZip:{},XLSX:{},jsQR(){},DOMParser:class{},FileReader:class{},Image:class{},URL:{createObjectURL(){return''},revokeObjectURL(){}},Blob:class{},structuredClone:global.structuredClone,fetch:async()=>({ok:false}),setTimeout(){},clearTimeout(){},Date,Math,JSON,Set,Map,RegExp,String,Number,Array,Object,Promise,Intl};
sandbox.window=sandbox;vm.createContext(sandbox);vm.runInContext(script,sandbox,{timeout:10000});
const results=[];
for(const s of input.samples){
  sandbox.document.getElementById('documentProfile').value='auto';
  const lines=String(s.text||'').split(/\r?\n/).map(x=>x.trim()).filter(Boolean);
  const page={fileName:s.name+'.jpg',pageNumber:1,totalPages:1,bodyLines:lines,lineDetails:lines.map(text=>({text,confidence:Number(s.confidence||90)})),confidence:Number(s.confidence||90)};
  const doc=sandbox.buildStructuredDocument([page]);
  doc.validation=sandbox.buildStrictValidation(doc);
  doc.universal=sandbox.buildUniversalPayload([page],doc);
  if(sandbox.isStrictTextDocumentType(doc.documentType)) doc.strict_text_document=sandbox.buildStrictTextDocumentJson(doc,null);
  const canonical=sandbox.canonicalOutputData(doc);
  const outputs={
    form:sandbox.buildCanonicalHtml(doc,{form:true}),
    markdown:sandbox.buildCanonicalMarkdown(doc),
    text:sandbox.buildCanonicalText(doc),
    json:JSON.stringify(canonical,null,2),
    html:sandbox.buildCanonicalHtml(doc)
  };
  const contract=sandbox.validateOutputContract(doc,outputs);
  const fields=sandbox.canonicalFields(canonical).map(f=>({label:f.label,value:f.value}));
  results.push({name:s.name,detected_type:doc.documentType,fields,validation:doc.validation,output_contract:contract,output_lengths:Object.fromEntries(Object.entries(outputs).map(([k,v])=>[k,String(v||'').length]))});
}
process.stdout.write(JSON.stringify({results}));
