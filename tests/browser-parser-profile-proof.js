const fs=require('fs'),vm=require('vm');
const input=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const html=fs.readFileSync('index.html','utf8');
const script=html.split('<script>')[1].split('</script>')[0];
function el(id){return {id,style:{},checked:true,value:id==='documentProfile'?'auto':'',textContent:'',innerHTML:'',files:[],dataset:{},classList:{add(){},remove(){},toggle(){}},addEventListener(){},appendChild(){},append(){},querySelectorAll(){return[]},setAttribute(){},click(){},remove(){},focus(){},select(){}}}
const elements=new Map();const document={getElementById(id){if(!elements.has(id))elements.set(id,el(id));return elements.get(id)},querySelectorAll(){return[]},createElement(){return el('created')},body:el('body')};
const sandbox={console:{log(){},error(){}},document,window:{},pdfjsLib:{GlobalWorkerOptions:{}},Tesseract:{},mammoth:{},JSZip:{},XLSX:{},jsQR(){},DOMParser:class{},FileReader:class{},Image:class{},URL:{createObjectURL(){return''},revokeObjectURL(){}},Blob:class{},structuredClone:global.structuredClone,fetch:async()=>({ok:false}),setTimeout(){},clearTimeout(){},Date,Math,JSON,Set,Map,RegExp,String,Number,Array,Object,Promise,Intl};sandbox.window=sandbox;vm.createContext(sandbox);vm.runInContext(script,sandbox,{timeout:5000});
const results=[];
for(const s of input.samples){const lines=s.text.split(/\r?\n/).map(x=>x.trim()).filter(Boolean);const detected=vm.runInContext(`detectDocumentType(${JSON.stringify(lines)})`,sandbox);results.push({name:s.name,expected_type:s.expected_type,detected_type:detected,pass:detected===s.expected_type});}
process.stdout.write(JSON.stringify({results}));
