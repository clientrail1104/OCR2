# NeuroOCR Strict All Profiles V31

V31 is the externally revalidated go-live build of the NeuroOCR browser application. It keeps one canonical extraction object and renders consistent **FORM, MARKDOWN, TEXT, JSON and HTML** outputs.

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

See `V31_EXTERNAL_VALIDATION_REPORT.md`, `evidence/PROOF_GALLERY.html`, `evidence/V31_ALL_PROFILES_CONTACT_SHEET.png` and `tests/V31_LAST_TEST_RESULTS.json`.

The 100.00% values above are measured results for the executed corpus. They are **not** a universal 99.99% guarantee for every unseen document. Strict profiles fail closed to **REVIEW REQUIRED** if required evidence is missing, redacted or cannot be independently verified.

## Run tests

```bash
python tests/output-contract-static.py
python tests/api-contract-runtime.py
python tests/malaysia-id-passport-regression.py
python tests/malaysia-id-real-image-proof.py
python tests/passport-real-image-proof.py
python tests/v31_external_profile_proof.py
python tests/render_v31_proof_screenshots.py
```

## V31.1 independent QA hardening (30 Sep 2026)

A second independent 17-profile image stress corpus was added after unpacking this build. It exposed and fixed parser/validator issues not caught by the original suite. Post-fix results: **17/17 type detection**, **111/111 OCR anchors**, **88/88 checked structured fields** and **17/17 FORM/MARKDOWN/TEXT/JSON/HTML output contracts**. The original 13-profile public-source suite still passes unchanged. See `V31_1_INDEPENDENT_STRESS_VALIDATION_REPORT.md`.

These are measured corpus results, not a universal 99.99% guarantee. Strict profiles still fail closed to REVIEW REQUIRED when independent AI verification is unavailable.

## V32 — Global Passport ICAO TD3
The passport engine now supports country-independent ICAO TD3 machine-readable passports through the `International Passport / ICAO TD3` profile. It validates MRZ check digits, preserves issuing-country and nationality codes separately, supports arbitrary TD3 passport/document-number patterns and uses adaptive MRZ rereads before marking a field high confidence. See `GLOBAL_PASSPORT_V32_VALIDATION_REPORT.md` for the measured acceptance results.

## V32.2 — Malaysia NRIC hardening (1 Oct 2026)

Malaysia NRIC extraction is now hardened across MyKad, MyPR, Malaysia Driving Licence and Malaysia Passport identity-number fields. The parser validates the embedded `YYMMDD` birth-date segment, supports hyphenated and compact 12-digit forms, recovers tightly constrained OCR confusions only in NRIC-shaped numeric tokens and rejects conflicting focused OCR reads instead of guessing. MyKad/MyPR now use two fast NRIC crops plus conditional strong/wide fallbacks only when the normal reads are unresolved.

Executed NRIC proof: **1,150,000/1,150,000 deterministic parser cases = 100.00%**, **200,003/200,003 API helper cases = 100.00%** and **24/24 degraded MyKad/MyPR reference-image variants = 100.00%**. The existing production-readiness suite also remains PASS. These are measured results for the executed corpus and do not establish a universal 99.99% guarantee on every unseen camera image, damaged card or unsupported layout. Ambiguous NRIC evidence fails closed for review rather than returning a guessed number.

See `PATCH_NOTES_V32_2_MALAYSIA_NRIC.md`, `MALAYSIA_NRIC_VALIDATION_REPORT.md`, `tests/NRIC_STRESS_RESULTS.json` and `tests/NRIC_IMAGE_ROBUSTNESS_RESULTS.json`.
