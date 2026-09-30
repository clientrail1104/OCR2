#!/usr/bin/env python3
"""Runtime smoke-test the Vercel OCR handler with a mocked Responses API."""
from pathlib import Path
import shutil, subprocess, tempfile, textwrap

ROOT=Path(__file__).resolve().parents[1]
node=shutil.which('node')
if not node:
    raise SystemExit('SKIP: node not installed')
api=(ROOT/'api'/'ocr.js').read_text(encoding='utf-8')
with tempfile.TemporaryDirectory() as td:
    td=Path(td)
    mod=td/'ocr.mjs'; mod.write_text(api,encoding='utf-8')
    harness=td/'test.mjs'
    harness.write_text(textwrap.dedent(f'''
      import handler from {mod.as_uri()!r};
      function resObj(){{return {{code:200,body:null,status(n){{this.code=n;return this}},json(x){{this.body=x;return this}}}}}}
      async function call(req){{const r=resObj();await handler(req,r);return r}}
      const oldKey=process.env.OPENAI_API_KEY;
      delete process.env.OPENAI_API_KEY;
      let r=await call({{method:'GET'}}); if(r.code!==405) throw new Error('GET guard failed');
      r=await call({{method:'POST',body:{{page_images:[{{image_data_url:'data:image/png;base64,AA=='}}]}}}}); if(r.code!==500) throw new Error('key guard failed');
      process.env.OPENAI_API_KEY='test-key';
      r=await call({{method:'POST',body:{{page_images:[]}}}}); if(r.code!==400) throw new Error('page guard failed');

      const valid={{
        document:{{title:'TEST',type:'General Document',language:'en',summary:'test'}},
        profile:{{document_type:'',fields:[]}},full_transcription:'HELLO',sections:[],tables:[],lists:[],checkboxes:[],
        visual_elements:{{handwriting:[],stamps_seals:[],signatures:[],diagrams:[],photos:[],qr_codes:[]}},
        entities:{{names:[],emails:[],phones:[],dates:[],amounts:[],ids:[]}},uncertain_regions:[]
      }};
      let sent=null;
      globalThis.fetch=async (url,opts)=>{{sent=JSON.parse(opts.body);return {{ok:true,status:200,json:async()=>({{output_text:JSON.stringify(valid)}})}}}};
      r=await call({{method:'POST',body:{{document_profile:'General Document',page_images:[{{image_data_url:'data:image/png;base64,AA=='}}],local_ocr:{{}}}}}});
      if(r.code!==200) throw new Error('valid contract rejected: '+JSON.stringify(r.body));
      if(!r.body?.validation?.json_syntax||!r.body?.validation?.strict_schema_contract||!r.body?.validation?.canonicalized) throw new Error('validation flags missing');
      if(sent?.text?.format?.type!=='json_schema'||sent?.text?.format?.strict!==true) throw new Error('strict json schema not sent');

      globalThis.fetch=async()=>({{ok:true,status:200,json:async()=>({{output_text:'{{bad json'}})}});
      r=await call({{method:'POST',body:{{page_images:[{{image_data_url:'data:image/png;base64,AA=='}}]}}}}); if(r.code!==502) throw new Error('invalid JSON not rejected');

      const invalid=structuredClone(valid);invalid.profile.fields=[{{label:'X',value:'Y',confidence:1.5,source_text:'Y'}}];
      globalThis.fetch=async()=>({{ok:true,status:200,json:async()=>({{output_text:JSON.stringify(invalid)}})}});
      r=await call({{method:'POST',body:{{page_images:[{{image_data_url:'data:image/png;base64,AA=='}}]}}}}); if(r.code!==502) throw new Error('invalid confidence not rejected');
      if(oldKey===undefined) delete process.env.OPENAI_API_KEY; else process.env.OPENAI_API_KEY=oldKey;
      console.log('PASS: API runtime guards, strict JSON schema request, JSON parse rejection and confidence validation');
    '''),encoding='utf-8')
    subprocess.run([node,str(harness)],check=True)
