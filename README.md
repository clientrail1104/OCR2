# NeuroOCR Strict All Profiles V32

V32 is the production-hardened go-live build of the NeuroOCR browser application. It keeps one canonical extraction object and renders consistent **FORM, MARKDOWN, TEXT, JSON and HTML** outputs.


## V32 passport critical-field hardening

- Hardens **Tempat Lahir / Place of Birth** using multi-crop consensus including an Otsu-binary recovery pass.
- Hardens **MRZ Line 1** using three dedicated line reads plus the full MRZ block.
- Requires MRZ Line 1 to be exactly 44 characters beginning `P<MYS` and cross-checks its name letters against the independently captured printed passport name.
- Added wider passport-name recovery so MRZ reconciliation remains reliable under JPEG compression, blur and darker scans.
- Stress test on the real passport fixture: **8/8 critical checks exact = 100.00%** across original, JPEG quality 55, 70% downscale + blur and darkened/JPEG variants.

See `V32_PASSPORT_CRITICAL_PROOF.md`, `evidence/V32_PASSPORT_CRITICAL_PROOF.png` and `tests/V32_PASSPORT_CRITICAL_RESULTS.json`.

## V31 fixes discovered during fresh profile testing

- Corrects official **SSM Company Profile** auto-detection for short Malay labels such as `Nama`, `No. Pendaftaran` and `Tarikh Penubuhan`.
- Preserves modern + legacy SSM company numbers such as `201101006232(934369-T)` and separates registered/business addresses and postcodes.
- Expands English **SSM Business Registration Certificate** parsing and bounds the certificate date so registrar text cannot be appended.
- Accepts Malaysian passport identity numbers printed with NRIC punctuation then canonicalises them to 12 digits.
- Preserves passport issuing-office values containing punctuation such as `KDN - PUTRAJAYA`.
- Detects generic **Certificate / Licence** samples using `Licence Number` and `Pilot Licence` without confusing them with Malaysian driving licences.
- Retains V30 safeguards against false Passport/MyKad detection inside forms and expanded Report / Statement detection.

## Executed proof

- User-supplied MyKad/MyPR/Passport critical fields: **28/28 = 100.00%**.
- Fresh public-source-based profile auto-detection: **13/13 = 100.00%**.
- Fresh degraded-fixture OCR anchors: **102/102 = 100.00%**.
- Fresh structured parser fields with explicit ground truth: **48/48 = 100.00%**.
- Mean raw Tesseract token confidence on the fresh external fixtures: **93.72%**.
- FORM / MARKDOWN / TEXT / JSON / HTML contract and browser/API JavaScript syntax: **PASS**.
- Strict API JSON/schema/error guards: **PASS**.

See `V32_PASSPORT_CRITICAL_PROOF.md`, `V31_EXTERNAL_VALIDATION_REPORT.md`, `evidence/PROOF_GALLERY.html`, `evidence/V31_ALL_PROFILES_CONTACT_SHEET.png` and `tests/V31_LAST_TEST_RESULTS.json`.

The 100.00% values above are measured results for the executed corpus. They are **not** a universal 99.99% guarantee for every unseen document. Strict profiles fail closed to **REVIEW REQUIRED** if required evidence is missing, redacted or cannot be independently verified.

## Run tests

```bash
python tests/output-contract-static.py
python tests/api-contract-runtime.py
python tests/malaysia-id-passport-regression.py
python tests/malaysia-id-real-image-proof.py
python tests/passport-real-image-proof.py
python tests/v31_external_profile_proof.py
python tests/v32_passport_critical_proof.py
python tests/render_v31_proof_screenshots.py
```
