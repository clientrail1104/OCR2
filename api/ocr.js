const OPENAI_URL = "https://api.openai.com/v1/responses";

const schema = {
  type: "object",
  additionalProperties: false,
  required: ["document","profile","full_transcription","sections","tables","lists","checkboxes","visual_elements","entities","uncertain_regions"],
  properties: {
    document: {type:"object",additionalProperties:false,required:["title","type","language","summary"],properties:{title:{type:"string"},type:{type:"string"},language:{type:"string"},summary:{type:"string"}}},
    profile: {type:"object",additionalProperties:false,required:["document_type","fields"],properties:{document_type:{type:"string"},fields:{type:"array",items:{type:"object",additionalProperties:false,required:["label","value","confidence","source_text"],properties:{label:{type:"string"},value:{type:"string"},confidence:{type:"number"},source_text:{type:"string"}}}}}},
    full_transcription: {type:"string"},
    sections: {type:"array",items:{type:"object",additionalProperties:false,required:["name","fields"],properties:{name:{type:"string"},fields:{type:"array",items:{type:"object",additionalProperties:false,required:["label","value","confidence","source_text"],properties:{label:{type:"string"},value:{type:"string"},confidence:{type:"number"},source_text:{type:"string"}}}}}}},
    tables: {type:"array",items:{type:"object",additionalProperties:false,required:["title","headers","rows"],properties:{title:{type:"string"},headers:{type:"array",items:{type:"string"}},rows:{type:"array",items:{type:"array",items:{type:"string"}}}}}},
    lists: {type:"array",items:{type:"object",additionalProperties:false,required:["title","items"],properties:{title:{type:"string"},items:{type:"array",items:{type:"string"}}}}},
    checkboxes: {type:"array",items:{type:"object",additionalProperties:false,required:["label","checked","confidence"],properties:{label:{type:"string"},checked:{anyOf:[{type:"boolean"},{type:"null"}]},confidence:{type:"number"}}}},
    visual_elements: {type:"object",additionalProperties:false,required:["handwriting","stamps_seals","signatures","diagrams","photos","qr_codes"],properties:{
      handwriting:{type:"array",items:{type:"object",additionalProperties:false,required:["text","confidence"],properties:{text:{type:"string"},confidence:{type:"number"}}}},
      stamps_seals:{type:"array",items:{type:"object",additionalProperties:false,required:["text","description"],properties:{text:{type:"string"},description:{type:"string"}}}},
      signatures:{type:"array",items:{type:"object",additionalProperties:false,required:["name_or_label","description"],properties:{name_or_label:{type:"string"},description:{type:"string"}}}},
      diagrams:{type:"array",items:{type:"object",additionalProperties:false,required:["description","labels"],properties:{description:{type:"string"},labels:{type:"array",items:{type:"string"}}}}},
      photos:{type:"array",items:{type:"object",additionalProperties:false,required:["description"],properties:{description:{type:"string"}}}},
      qr_codes:{type:"array",items:{type:"object",additionalProperties:false,required:["decoded_text"],properties:{decoded_text:{type:"string"}}}}
    }},
    entities: {type:"object",additionalProperties:false,required:["names","emails","phones","dates","amounts","ids"],properties:{names:{type:"array",items:{type:"string"}},emails:{type:"array",items:{type:"string"}},phones:{type:"array",items:{type:"string"}},dates:{type:"array",items:{type:"string"}},amounts:{type:"array",items:{type:"string"}},ids:{type:"array",items:{type:"string"}}}},
    uncertain_regions: {type:"array",items:{type:"object",additionalProperties:false,required:["description","visible_text","confidence"],properties:{description:{type:"string"},visible_text:{type:"string"},confidence:{type:"number"}}}}
  }
};

function outputText(data){
  if (typeof data.output_text === "string") return data.output_text;
  for (const item of data.output || []) for (const part of item.content || []) if (typeof part.text === "string") return part.text;
  return "";
}

export default async function handler(req, res) {
  if (req.method !== "POST") return res.status(405).json({error:"POST only"});
  if (!process.env.OPENAI_API_KEY) return res.status(500).json({error:"OPENAI_API_KEY is not configured on the server"});
  try {
    const body = typeof req.body === "string" ? JSON.parse(req.body) : (req.body || {});
    const pages = Array.isArray(body.page_images) ? body.page_images.slice(0, 2) : [];
    if (!pages.length) return res.status(400).json({error:"No page_images supplied"});
    const local = JSON.stringify(body.local_ocr || {}).slice(0, 60000);
    const content = [{type:"input_text",text:`You are a precision document-understanding engine. Extract ALL visible information from the supplied page image(s). Preserve spelling, punctuation, reading order, field labels, table cells, list items and checkbox state. Detect handwriting, stamps/seals, signatures, diagrams, photos and QR content when visibly present. Never invent unreadable content. Use confidence 0 to 1. Local OCR is supporting evidence only and may contain errors.

When the document is one of these Malaysian profiles, set profile.document_type to the EXACT matching name and return profile.fields using the canonical labels below, in document order. Only return values visibly supported by the image; use an empty string when not visible.

IMPORTANT NAME RULE: printed or handwritten person names are ordinary document text and MUST be extracted exactly as visibly written. Never redact, mask, shorten, replace or omit a visible person's name merely because the document also contains a portrait/photo. Do not identify the person from facial appearance. Use only visible text on the document.

Malaysia Passport: Jenis / Type; Kod Negara / Country Code; Passport Number; Nama / Name; Warganegara / Nationality; No. Pengenalan / Identity No.; Tarikh lahir / Date of Birth; Tempat Lahir / Place of Birth; Jantina / Sex; Tinggi / Height; Tarikh Dikeluarkan / Date of Issue; Tarikh Tamat / Date of Expiry; Pejabat Pengeluar / Issuing Office; MRZ Line 1; MRZ Line 2.
Malaysia MyKad: Identity Number; Name; Address; Religion; Citizenship; Gender.
Malaysia MyPR: Identity Number; Name; Address; Religion; Citizenship; Gender.
Malaysia Driving Licence: Licence Type; Name; Nationality; Identity Number; Class; Valid From; Valid Until; Address.
CIDB SPKK: No. Pendaftaran / Registration Number; Nama Kontraktor / Contractor Name; Alamat Berdaftar / Registered Address; Daerah / District; Initial Registration Date / Tarikh Mula Berdaftar; Gred / Grade / Kategori / Category; Pegawai Syarikat Yang Ditauliahkan / Authorised Company Officer(s); Tarikh Mula Berkuatkuasa / Effective Date; Tarikh Habis Tempoh Perakuan / Expiry Date.
SSM Business Profile / Maklumat Perniagaan: Nama Perniagaan / Company Name; No Pendaftaran Perniagaan / Registration Number; Registered / Main Address; Bentuk Perniagaan / Business Type; Tarikh Mula Berniaga / Business Start Date; Tarikh Pendaftaran / Registration Date; Tarikh Luput Pendaftaran / Registration Expiry; Tarikh Perubahan Terakhir / Last Change Date; Status; Jenis Perniagaan / Business Activity; Maklumat Cawangan / Branch Information.
SSM Business Registration Renewal: Form; Nama Perniagaan / Business Name; No. Pendaftaran / Registration Number; Valid Until / Sah Hingga; Registered Address; Bil. Cawangan / Number of Branches; Certificate Date; Issuing System. Set document.title exactly to "Perakuan Pembaharuan Pendaftaran — Akta Pendaftaran Perniagaan 1956". Do NOT add the registrar as a profile field.
SSM Business Registration Certificate: Form; Nama Perniagaan / Business Name; No. Pendaftaran / Registration Number; Valid Until / Sah Hingga; Registered Address; Bil. Cawangan / Number of Branches; Certificate Date; Issuing System. Set document.title exactly to "Perakuan Pendaftaran — Akta Pendaftaran Perniagaan 1956". Do NOT add the registrar as a profile field.
SSM Company Profile: Nama Syarikat / Company Name; Nama Syarikat Lama / Old Company Name; Tarikh Pertukaran / Date of Change; No Syarikat / Company Registration No.; Tarikh Pemerbadanan / Date of Incorporation; Tarikh Pendaftaran / Registration Date; Jenis / Type; Status; Alamat Daftar / Registered Address; Poskod / Postcode (Registered Address); Tempat Penubuhan / Place of Incorporation; Alamat Perniagaan / Business Address; Poskod / Postcode (Business Address); Jenis Perniagaan / Business Activity. For this profile, document.title MUST be exactly "Butir-Butir Setiausaha Syarikat / Maklumat Syarikat". Detect it from headings such as "BUTIR-BUTIR SETIAUSAHA SYARIKAT" and "MAKLUMAT SYARIKAT". Do not classify it as an SSM Business Profile, Borang D or Borang E. Treat the first Poskod after Alamat Daftar as the registered-address postcode and the second Poskod after Alamat Perniagaan as the business-address postcode. Preserve multi-line addresses as one field. Preserve all numbered Jenis Perniagaan / Business Activity entries in their original order.
CIDB STB: Effective Date; Expiry Date; No. Sijil Pendaftaran; Gred Pendaftaran; Kategori / Category; Tempoh Sah Laku; Nama dan Alamat Berdaftar; Pegawai Syarikat Yang DiTauliahkan; No. K/P. Set document.title exactly to "CIDB STB / Sijil Taraf Bumiputera Kontraktor Kerja". Preserve every visible grade/category row and combine repeated grade/category values without dropping categories.
CIDB PPK / Perakuan Pendaftaran: No. Pendaftaran / Registration Number; Nama Kontraktor / Contractor Name; Alamat Berdaftar / Registered Address; Daerah / District; Tarikh Mula Berdaftar; Gred / Grade / Kategori / Category / Specialization / Pengkhususan; Tarikh Mula Berkuatkuasa / Effective Date; Tarikh Habis Tempoh Perakuan / Expiry Date; Status.

For Malaysian passport MRZ, preserve each MRZ line exactly including < characters. For MyKad/MyPR and Malaysian Driving Licence, preserve the FULL printed name even when it wraps across two or more lines. For MyKad/MyPR, preserve the FULL front-side address as one field and do not mix in back-side reference numbers, scanner watermarks, citizenship, religion or gender text. Preserve names and identity numbers exactly as printed. Recognize Malaysian NRIC in both YYMMDD-PB-###G and YYMMDDPB###G forms. Do NOT treat the final NRIC digit as gender generically. Only when the active document/profile rule explicitly applies Malaysian NRIC gender validation (currently Malaysia MyKad and Malaysia MyPR) and no visible gender value is available, use: odd final digit = Male / Lelaki, even final digit = Female / Perempuan. A visible printed gender value always takes precedence over an NRIC-derived value. For CIDB officer lists preserve each officer name with the matching ID. For PPK grade/category/specialisation preserve every classification row and every specialization code on that row, including multiple codes such as B18 and B04. For SSM registration certificates keep the business name and registered address intact. The registrar may appear in full_transcription but must NOT be included in profile.fields.

If the document is not one of those profiles, set profile.document_type to an empty string and profile.fields to an empty array.

Local OCR evidence:
${local}`}];
    for (const p of pages) content.push({type:"input_image",image_url:p.image_data_url,detail:"original"});
    const api = await fetch(OPENAI_URL, {
      method: "POST",
      headers: {"Authorization":`Bearer ${process.env.OPENAI_API_KEY}`,"Content-Type":"application/json"},
      body: JSON.stringify({
        model: process.env.OPENAI_MODEL || "gpt-6-astra",
        input: [{role:"user",content}],
        text: {format:{type:"json_schema",name:"document_extraction",strict:true,schema}}
      })
    });
    const data = await api.json();
    if (!api.ok) return res.status(api.status).json({error:data?.error?.message || "OpenAI request failed"});
    const text = outputText(data);
    if (!text) return res.status(502).json({error:"Model returned no structured text"});
    let result;
    try { result = JSON.parse(text); } catch { return res.status(502).json({error:"Model output was not valid JSON"}); }
    return res.status(200).json({result});
  } catch (err) {
    return res.status(500).json({error:err?.message || String(err)});
  }
}
