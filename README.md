# NeuroOCR deployment

## Recommended setup

This project now has two layers:

1. `index.html` — local PDF/text extraction, 1-pass or 3-pass Tesseract OCR, universal document structuring and fallback processing.
2. `api/ocr.js` — secure multimodal AI vision endpoint for complex layouts, handwriting, stamps, signatures, diagrams and cross-checking.

## Deploy with GitHub + Vercel

1. Put `index.html` at the repository root.
2. Put `api/ocr.js` inside an `api` folder.
3. Import the GitHub repository into Vercel.
4. In Vercel Project Settings → Environment Variables, add `OPENAI_API_KEY`.
5. Optional: add `OPENAI_MODEL` to choose a different vision-capable model.
6. Deploy. The web page already points to `/api/ocr`.

Never put an API key directly inside `index.html`, JavaScript committed to GitHub or a public GitHub Pages repository.

## GitHub Pages only

The local OCR layer will still work on GitHub Pages, but the AI vision pass needs a server-side endpoint. If hosting the front end on GitHub Pages, deploy `api/ocr.js` separately on a serverless platform and paste that HTTPS endpoint into **AI VISION ENDPOINT**.

## Auto extraction and Malaysian profile Markdown

Uploading a supported document now starts extraction automatically and opens the **MARKDOWN** result when processing finishes. The manual button remains available as **RE-EXTRACT DOCUMENT** after changing OCR settings.

Dedicated Important Information templates are included for:

- Malaysia Passport
- Malaysia MyKad
- Malaysia MyPR
- CIDB SPKK
- CIDB STB
- CIDB PPK / Perakuan Pendaftaran
- SSM Business Profile / Maklumat Perniagaan
- SSM Company Profile / Particulars of Company Secretary

Passport MRZ values are used as a fallback for passport number, nationality, date of birth, sex and expiry date. CIDB officer lists preserve matching identity numbers and PPK grade/category/specialisation records are emitted individually in Markdown.

When AI Vision is enabled, the server endpoint requests the same canonical Malaysian profile labels and high-confidence AI fields can fill or verify the profile output while local OCR remains available for auditing.

## Extraction design

The JSON output preserves:

- document type and language
- complete page transcription
- page-level blocks and reading order
- sections and key/value fields
- tables
- lists
- checkbox states
- emails, URLs, phone numbers, dates, amounts, percentages and identity-number patterns
- handwriting, stamps/seals, signatures, diagrams, photos and QR content when AI vision is enabled
- low-confidence and uncertain regions
- local OCR vs AI vision audit information

No OCR system can guarantee zero errors. The app is designed to expose uncertainty instead of silently inventing content.
