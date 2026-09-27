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
