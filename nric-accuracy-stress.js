const fs=require('fs'),vm=require('vm');
const html=fs.readFileSync('index.html','utf8');
const script=html.split('<script>')[1].split('</script>')[0];
function el(id){return {id,style:{},checked:true,value:id==='documentProfile'?'auto':'',textContent:'',innerHTML:'',files:[],dataset:{},classList:{add(){},remove(){},toggle(){}},addEventListener(){},appendChild(){},append(){},querySelectorAll(){return[]},setAttribute(){},click(){},remove(){},focus(){},select(){}}}
const elements=new Map();const document={getElementById(id){if(!elements.has(id))elements.set(id,el(id));return elements.get(id)},querySelectorAll(){return[]},createElement(){return el('created')},body:el('body')};
const sandbox={console:{log(){},error(){}},document,window:{},pdfjsLib:{GlobalWorkerOptions:{}},Tesseract:{},mammoth:{},JSZip:{},XLSX:{},jsQR(){},DOMParser:class{},FileReader:class{},Image:class{},URL:{createObjectURL(){return''},revokeObjectURL(){}},Blob:class{},structuredClone:global.structuredClone,fetch:async()=>({ok:false}),setTimeout(){},clearTimeout(){},Date,Math,JSON,Set,Map,RegExp,String,Number,Array,Object,Promise,Intl};sandbox.window=sandbox;vm.createContext(sandbox);vm.runInContext(script,sandbox,{timeout:10000});
const result=vm.runInContext(`(()=>{
  const N=250000, invalidN=100000, contextN=50000;
  const conf={0:['O','Q','D'],1:['I','L','!'],2:['Z'],5:['S'],6:['G'],7:['T'],8:['B']};
  function maxDay(yy,mm){return [31,yy%4===0?29:28,31,30,31,30,31,31,30,31,30,31][mm-1]}
  function digits(i){const yy=i%100,mm=(Math.floor(i/7)%12)+1,dd=(Math.floor(i/13)%maxDay(yy,mm))+1,pb=(Math.floor(i/17)%99)+1,last=(i*7919+1234)%10000;return String(yy).padStart(2,'0')+String(mm).padStart(2,'0')+String(dd).padStart(2,'0')+String(pb).padStart(2,'0')+String(last).padStart(4,'0')}
  function canon(d){return d.slice(0,6)+'-'+d.slice(6,8)+'-'+d.slice(8)}
  function noisy(d,count,seed){let a=[...d],used=0;for(let k=0;k<12&&used<count;k++){const pos=(seed+k*7)%12,ch=a[pos],opts=conf[ch];if(opts){a[pos]=opts[(seed+k)%opts.length];used++}}for(let pos=0;pos<12&&used<count;pos++){const ch=a[pos],opts=conf[ch];if(opts){a[pos]=opts[(seed+pos)%opts.length];used++}}return {text:a.slice(0,6).join('')+'-'+a.slice(6,8).join('')+'-'+a.slice(8).join(''),used}}
  const metrics={formatted:{pass:0,total:N},compact:{pass:0,total:N},ocr1:{pass:0,total:N},ocr2:{pass:0,total:N},invalid_rejection:{pass:0,total:invalidN},context_selection:{pass:0,total:contextN}};
  const failures=[];const t0=Date.now();
  for(let i=0;i<N;i++){
    const d=digits(i),c=canon(d);
    if(normalizeIdentityNumber(c)===c&&isValidMalaysianNric(c))metrics.formatted.pass++;else if(failures.length<10)failures.push({kind:'formatted',d,c,out:normalizeIdentityNumber(c)});
    if(normalizeIdentityNumber(d)===c&&isValidMalaysianNric(normalizeIdentityNumber(d)))metrics.compact.pass++;else if(failures.length<10)failures.push({kind:'compact',d,out:normalizeIdentityNumber(d)});
    const n1=noisy(d,1,i+11);if(n1.used>=1&&normalizeIdentityNumber(n1.text)===c)metrics.ocr1.pass++;else if(failures.length<10)failures.push({kind:'ocr1',d,noisy:n1,out:normalizeIdentityNumber(n1.text)});
    const n2=noisy(d,2,i+29);if(n2.used>=2&&normalizeIdentityNumber(n2.text)===c)metrics.ocr2.pass++;else if(failures.length<10)failures.push({kind:'ocr2',d,noisy:n2,out:normalizeIdentityNumber(n2.text)});
  }
  for(let i=0;i<invalidN;i++){
    const yy=String(i%100).padStart(2,'0'),bad=i%2===0?yy+'13'+String((i%28)+1).padStart(2,'0'):(yy+'02'+'30'),rest=String((i%99)+1).padStart(2,'0')+String((i*31)%10000).padStart(4,'0'),token=bad+'-'+rest.slice(0,2)+'-'+rest.slice(2);
    if(findMalaysianNric(token)===''&&!isValidMalaysianNric(token))metrics.invalid_rejection.pass++;else if(failures.length<10)failures.push({kind:'invalid',token,out:findMalaysianNric(token)});
  }
  for(let i=0;i<contextN;i++){
    const target=digits(i+700000),other=digits(i+900000),text='Company Registration: '+other+'\\nNRIC: '+target;
    const raw=findMalaysianNric(text),out=normalizeIdentityNumber(raw);
    if(out===canon(target))metrics.context_selection.pass++;else if(failures.length<10)failures.push({kind:'context',target,other,raw,out});
  }
  const elapsed_ms=Date.now()-t0;let total=0,passed=0;for(const m of Object.values(metrics)){total+=m.total;passed+=m.pass;m.accuracy=m.pass/m.total}
  return {metrics,total,passed,accuracy:passed/total,elapsed_ms,cases_per_second:Math.round(total/(elapsed_ms/1000)),failures};
})()`,sandbox,{timeout:120000});
console.log(JSON.stringify(result,null,2));
if(result.passed!==result.total)process.exitCode=1;
