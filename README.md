# NeuroOCR deployment

## Recommended setup

This repository has two extraction layers:

1. `index.html` — local PDF/text extraction, 1-pass or 3-pass Tesseract OCR, Malaysian profile parsing and universal structured fallback processing.
2. `api/ocr.js` — secure multimodal AI vision verification for difficult layouts, low-quality scans, handwriting, stamps, signatures and field recovery.

The normal flow is **upload → automatic extraction → FORM view**. The user does not need to press Extract for the first run.

## Deploy with GitHub + Vercel

1. Put `index.html` at the repository root.
2. Put `api/ocr.js` inside an `api` folder.
3. Import the GitHub repository into Vercel.
4. In Vercel Project Settings → Environment Variables, add `OPENAI_API_KEY`.
5. Optional: add `OPENAI_MODEL` to choose the model used by the server endpoint.
6. Deploy. The front end already points to `/api/ocr`.

Never place a secret API key in `index.html` or any JavaScript committed to a public repository.

## GitHub Pages only

The local OCR layer still works on GitHub Pages. The AI vision pass requires a server-side endpoint. When the front end is hosted on GitHub Pages, deploy `api/ocr.js` separately and enter that HTTPS endpoint in **AI VISION ENDPOINT**.

## Malaysian structured profiles

The parser recognises these profiles and places the extracted values directly into the predefined FORM fields:

- Malaysia Passport
- Malaysia MyKad
- Malaysia MyPR
- Malaysia Driving Licence
- CIDB SPKK
- CIDB STB
- CIDB PPK / Perakuan Pendaftaran
- SSM Business Profile / Maklumat Perniagaan
- SSM Company Profile — **Butir-Butir Setiausaha Syarikat / Maklumat Syarikat**
- SSM Business Registration Certificate / Borang D
- SSM Business Registration Renewal / Borang E

Strict detected-document labels used in FORM output:

- `Perakuan Pembaharuan Pendaftaran — Akta Pendaftaran Perniagaan 1956`
- `Perakuan Pendaftaran — Akta Pendaftaran Perniagaan 1956`
- `Butir-Butir Setiausaha Syarikat / Maklumat Syarikat`
- `CIDB STB / Sijil Taraf Bumiputera Kontraktor Kerja`

### Person-name handling

Visible names are treated as first-class document fields. The system is instructed to:

- capture the complete printed or handwritten person name exactly as visible
- retain `BIN`, `BINTI`, `A/L`, `A/P`, honorifics and multi-part names when present
- recover Passport names from the printed field and use MRZ as a fallback/cross-check
- recover MyKad/MyPR names from the card text around the identity-number region
- recover Driving Licence names from the licence text region
- preserve CIDB authorised-officer names with their corresponding identity numbers
- keep SSM Borang D/E registrar text out of the default profile FORM while retaining it only in the full transcription when visible
- never infer a person's identity from the portrait or photograph itself
- never silently redact a visible name in the OCR/AI extraction pipeline

The universal JSON output also contains `entities.names` for person names recovered from recognised profile fields.

## Important profile behaviour

Passport MRZ rows remain exact, including `<` characters, and are used as a fallback for passport number, name, nationality, DOB, sex and expiry.

MyKad/MyPR identity numbers preserve the printed Malaysian format where possible. Multiline addresses are joined into the Address field rather than being emitted as loose text.

### Malaysian NRIC handling

The parser recognises both `YYMMDD-PB-###G` and compact `YYMMDDPB###G` forms and normalises a detected 12-digit NRIC to `YYMMDD-PB-###G` for the structured form. The final digit is **not** interpreted as gender globally. NRIC-derived gender is gated by an explicit profile rule. For the current `Malaysia MyKad` and `Malaysia MyPR` profiles only, if the document does not visibly provide gender, odd final digit maps to `LELAKI` and even final digit maps to `PEREMPUAN`. Visible printed gender always takes precedence.

CIDB PPK classifications retain each `Gred / Kategori / Pengkhususan` record and preserve multiple specialization codes on the same classification row. SPKK officer lists retain officer-to-ID relationships. STB keeps certificate number, grade, every category, validity dates, registered name/address and authorised officer fields separate.

SSM Borang D/E certificates capture the business name, registration number, validity date, registered address, branch count, EZBIZ certificate date and issuing system. The registrar is intentionally excluded from the default profile FORM, per the strict profile requirement.

For **SSM Company Information**, the detected-document label is `Butir-Butir Setiausaha Syarikat / Maklumat Syarikat`. The parser uses an ordered company-information layout so that `Nama Syarikat`, `Nama Syarikat Lama`, incorporation/registration dates, type, status, registered address, the first `Poskod`, place of incorporation, business address, the second `Poskod` and multi-line `Jenis Perniagaan` are routed into their correct FORM fields. The two postcodes are kept separate based on their address context.

The FORM view intentionally does **not** show an `Unclassified Text` section. Unmatched OCR evidence remains in the internal/universal extraction record for verification.

## Extraction design

The JSON output preserves:

- document type and language
- complete page transcription
- page-level blocks and reading order
- predefined profile fields
- person names in `entities.names`
- generic key/value fields
- tables
- lists
- checkbox states
- emails, URLs, phone numbers, dates, amounts, percentages and identity-number patterns
- handwriting, stamps/seals, signatures, diagrams, photos and QR content when AI vision is enabled
- low-confidence and uncertain regions
- local OCR vs AI vision audit information

## Accuracy

No OCR pipeline can guarantee zero errors on every source image. NeuroOCR uses complementary local OCR passes, profile-specific parsers and an optional multimodal verification pass. Unreadable values should remain empty/Not detected rather than being invented.

## Parser regression test

A dependency-free regression test is included for Malaysian profile routing and person-name capture:

```bash
node tests/profile-regression.mjs
```

The fixtures are synthetic and verify the strict target set: two MyKad layouts with full wrapped names, MyPR with full address, Passport with full name and MRZ, Driving Licence with wrapped full name and full address, SSM Borang D/E with the registrar excluded from profile fields, the full SSM Company Information layout, CIDB PPK with multiple specialization codes and CIDB STB with grade/category/date/address/officer routing. NRIC and exact detected-document display labels are also regression-tested.
