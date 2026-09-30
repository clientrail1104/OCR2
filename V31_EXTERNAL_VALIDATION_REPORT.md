# NeuroOCR V31 — External Profile Validation and Go-Live Evidence

**Validation date:** 30 September 2026  
**Build:** V31  
**Status on the executed corpus:** PASS

## Executive result

Fresh source-based regression coverage was executed for every configured document profile. Each public-source example was converted into a **source-derived QA fixture**, deliberately degraded with JPEG compression, slight rotation and blur, then processed by Tesseract OCR. The OCR output was passed into the **actual V31 browser document detector and field parser functions** from `index.html`. These public QA fixtures are not represented as downloaded originals.

- Fresh profile auto-detection: **13/13 = 100.00%**
- Fresh visible OCR anchors: **102/102 = 100.00%**
- Fresh structured fields with explicit ground truth: **48/48 = 100.00%**
- Mean raw OCR token confidence across fresh fixtures: **93.72%**
- Supplied real MyKad/MyPR/Passport critical fields: **28/28 = 100.00%**
- FORM / MARKDOWN / TEXT / JSON / HTML output contract and browser/API JavaScript syntax: **PASS**
- Strict API JSON/schema/error guards: **PASS**

**Important:** the fresh corpus measured 100.00% exact matching on the checks above. It does **not** statistically prove universal 99.99% accuracy or 99.99% raw OCR confidence on every unseen production document. Raw OCR confidence is an engine token-confidence measure, not field correctness. The production gate deliberately returns **REVIEW REQUIRED** when required evidence is missing, redacted or cannot be cross-validated.

## Profile-by-profile proof and concern

| Tested profile | Detected type | Raw OCR confidence | Exact-match proof | Strict status | Main concern tested | Evidence |
|---|---|---:|---:|---|---|---|
| Malaysia ID / Passport — MyKad | Malaysia MyKad | 92.27% | 6/6 fields — 100.00% | PASS | Security-pattern background, small card text, NRIC and multi-line address must remain exact. | [screenshot](evidence/screenshots/mykad_public_sarawak.png) |
| Malaysia ID / Passport — MyPR | Malaysia MyPR | 91.69% | 6/6 anchors — 100.00% | REVIEW REQUIRED (expected for incomplete/redacted public sample) | Official public reference is structural/redacted. Personal identity fields cannot be independently proven from this sample, so strict production review remains required. | [screenshot](evidence/screenshots/mypr_public_structure.png) |
| Malaysia ID / Passport — Passport | Malaysia Passport | 93.20% | 12/12 fields — 100.00% | REVIEW REQUIRED (expected for incomplete/redacted public sample) | Visible biographic fields can be checked, but the public sample does not expose a safely readable full passport number and full MRZ. Strict production review remains required. | [screenshot](evidence/screenshots/passport_public_firefly.png) |
| Malaysia Driving Licence | Malaysia Driving Licence | 93.45% | 4/4 fields — 100.00% | REVIEW REQUIRED (expected for incomplete/redacted public sample) | Specimen masks personal name, identity number and address. Class and validity dates must parse without inventing masked values. | [screenshot](evidence/screenshots/driving_public_wikimedia.png) |
| CIDB Certificate — PPK | CIDB PPK / Perakuan Pendaftaran | 92.01% | 7/7 fields — 100.00% | PASS | Dense grade/category/specialisation codes, multi-line address and multiple registration/effective/expiry dates can be confused. | [screenshot](evidence/screenshots/cidb_ppk_public.png) |
| SSM Business Registration | SSM Business Registration Certificate | 95.56% | 6/6 fields — 100.00% | REVIEW REQUIRED (expected for incomplete/redacted public sample) | Official public sample redacts some mandatory values in the chosen fixture. Parser must preserve visible fields and fail closed for redacted values. | [screenshot](evidence/screenshots/ssm_registration_public.png) |
| SSM Document — Company Profile | SSM Company Profile | 93.29% | 13/13 fields — 100.00% | PASS | Modern plus legacy company number, optional old-name fields, two addresses/postcodes and long business-activity text must remain distinct. | [screenshot](evidence/screenshots/ssm_company_public.png) |
| Invoice / Receipt | Invoice / Receipt | 95.18% | 13/13 anchors — 100.00% | PASS | Thermal-style receipt layout has many similar decimal amounts. Totals, change, tax and invoice number must not cross-map. | [screenshot](evidence/screenshots/invoice_receipt_public.png) |
| Form / Application | Form / Application | 93.24% | 6/6 anchors — 100.00% | PASS | The form contains MyKad/Passport wording but is not an identity document. False passport/MyKad classification is a key regression risk. | [screenshot](evidence/screenshots/form_application_public.png) |
| Letter / Memo | Letter / Memo | 96.03% | 6/6 anchors — 100.00% | PASS | Letter wording and addresses must remain body text while document type detection must not depend on one phrase only. | [screenshot](evidence/screenshots/letter_memo_public.png) |
| Certificate / Licence | Certificate / Licence | 93.77% | 10/10 anchors — 100.00% | PASS | Contains “Licence Number” and MyKad/Passport wording but is not a driving licence or identity document. Generic licence detection must win. | [screenshot](evidence/screenshots/certificate_licence_public.png) |
| Report / Statement | Report / Statement | 96.03% | 9/9 anchors — 100.00% | PASS | Financial statements contain repeated year columns and similar large numbers. Numeric anchors and report type must remain stable. | [screenshot](evidence/screenshots/report_statement_public.png) |
| General Document | General Document | 92.65% | 5/5 anchors — 100.00% | PASS | Contains CIDB references but is a general FAQ. It must not be incorrectly promoted to a CIDB certificate profile. | [screenshot](evidence/screenshots/general_document_public.png) |

## Defects found and fixed in V31

1. **SSM Company Profile:** the official SSM sample used short Malay labels such as `Nama`, `No. Pendaftaran` and `Tarikh Penubuhan`. V30 could fall back to generic `SSM Document` and could truncate a modern registration number such as `201101006232(934369-T)`. V31 expands the official label patterns, preserves modern+legacy registration numbers and separates registered/business addresses. Fresh result: **13/13 structured fields exact**.
2. **SSM Business Registration:** English certificate labels and the phrase `principal place of business` needed dedicated support. The prior certificate-date regex could consume following registrar text when no period was present. V31 bounds the date to a date expression. Fresh result: **6/6 structured fields exact**.
3. **Malaysia Passport:** a visible identity number in Malaysian hyphenated NRIC form could be blanked by strict sanitisation and an issuing office like `KDN - PUTRAJAYA` could be rejected because the punctuation token was treated as a one-character word. Both are corrected. Fresh visible-field result: **12/12 exact**. The sample still correctly remains **REVIEW REQUIRED** because a full passport number and full MRZ are not safely available in that public example.
4. **Generic Certificate / Licence:** the CAAM pilot licence uses `Licence Number`, which was not covered by the older `licence no` detector. V31 adds `licence number` and `pilot licence` recognition. The same public sample now detects **Certificate / Licence** with **10/10 visible anchors exact**.

## Sources used for the fresh corpus

- MyKad — Kapit District Office, Sarawak, public document example
- MyPR — Jabatan Pendaftaran Negara MyPR feature reference
- Malaysia Passport — Firefly Airlines Malaysian passport booking-guide sample
- Malaysia Driving Licence — Wikimedia Commons specimen
- CIDB Certificate — CIDB/CIMS public PPK certificate reference
- SSM Business Registration — SSM official Business Certificate sample
- SSM Company Profile — SSM official Company Profile sample
- Invoice / Receipt — Asprise public receipt OCR example
- Form / Application and Letter / Memo — Bank Negara Malaysia CCRIS/eCCRIS forms
- Certificate / Licence — Civil Aviation Authority of Malaysia sample pilot licence
- Report / Statement — Bank Negara Malaysia Annual Report 2025 financial statement
- General Document — CIDB iProject FAQ

Exact source URLs are recorded in `tests/v31_external/v31_external_results.json`.

## Production interpretation

V31 should not force a value merely to display a high score. A 99.99% label would be unsafe if a document is blurred, cropped, masked, redacted or missing mandatory evidence. The safer production contract is: **extract → validate → cross-check → render five formats → PASS or REVIEW REQUIRED**. This build now passes the executed corpus and keeps review behavior for incomplete strict-profile evidence.

## Evidence files

- `evidence/PROOF_GALLERY.html` — all 13 browser-rendered OCR/parser screenshots
- `evidence/V31_ALL_PROFILES_CONTACT_SHEET.png` — one-page visual overview
- `tests/v31_external/v31_external_results.json` — per-profile OCR output, raw confidence, fields and anchor checks
- `tests/V31_LAST_TEST_RESULTS.json` — combined go-live result
