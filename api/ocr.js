const OPENAI_URL = "https://api.openai.com/v1/responses";

const schema = {
  type: "object",
  additionalProperties: false,
  required: ["document","full_transcription","sections","tables","lists","checkboxes","visual_elements","entities","uncertain_regions"],
  properties: {
    document: {type:"object",additionalProperties:false,required:["title","type","language","summary"],properties:{title:{type:"string"},type:{type:"string"},language:{type:"string"},summary:{type:"string"}}},
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
    entities: {type:"object",additionalProperties:false,required:["emails","phones","dates","amounts","ids"],properties:{emails:{type:"array",items:{type:"string"}},phones:{type:"array",items:{type:"string"}},dates:{type:"array",items:{type:"string"}},amounts:{type:"array",items:{type:"string"}},ids:{type:"array",items:{type:"string"}}}},
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
    const content = [{type:"input_text",text:`You are a precision document-understanding engine. Extract ALL visible information from the supplied page image(s). Preserve spelling, punctuation, reading order, field labels, table cells, list items and checkbox state. Detect handwriting, stamps/seals, signatures, diagrams, photos and QR content when visibly present. Never invent unreadable content. Use confidence 0 to 1. Local OCR is supporting evidence only and may contain errors.\n\nLocal OCR evidence:\n${local}`}];
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
