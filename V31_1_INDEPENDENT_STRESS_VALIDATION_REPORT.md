# NeuroOCR V31.1 — Independent Stress Validation, Debug Fixes and Proof

**Validation date:** 30 September 2026  
**Build basis:** uploaded `neuroocr-github-go-live-v31.zip`  
**Patched package label:** V31.1 QA hardening

## Executive result

- Fresh independent image stress corpus: **17/17 type detection**, **111/111 OCR anchors**, **88/88 checked structured fields**, **17/17 five-format contracts** — all passed after fixes.
- Fresh stress mean raw Tesseract token confidence: **93.62%**.
- Original public-source corpus rerun after fixes: **13/13 type detection**, **102/102 OCR anchors**, **48/48 checked structured fields**.
- Existing user-supplied identity regressions rerun: **MyKad + MyPR 13/13** critical fields and **Malaysia Passport 15/15** canonical fields including both MRZ lines.
- FORM, MARKDOWN, TEXT, JSON and HTML output contract: **PASS** on all 17 fresh profiles.
- API strict JSON/schema/error guard suite: **PASS**.

> Accuracy statement: the executed corpora achieved 100% exact matching on the checks above. This is measured corpus performance, not statistical proof that every unseen production document will achieve 99.99%. Raw OCR confidence is also not the same as field correctness. The application intentionally fails closed to REVIEW REQUIRED for strict profiles when independent AI verification is unavailable or evidence is incomplete.

## Defects found and fixed

1. **Validation-suite portability:** two V31 proof scripts hard-coded `/mnt/data/neuroocr_v31` and failed after normal ZIP extraction. They now derive the project root from the script location.
2. **Malaysia Driving Licence name loss:** a leading OCR border character such as `| Nama / Name:` caused the name parser to miss the full name. The label matcher now tolerates harmless leading OCR punctuation.
3. **CIDB STB NRIC fidelity:** `No. K/P` was normalized to unformatted digits. It now preserves canonical Malaysian NRIC formatting while still validating the digit count.
4. **SSM Business Registration Renewal name loss:** the parser only handled sentence-form certificates and could miss an explicit `Nama Perniagaan:` label. A direct-label fallback was added.
5. **SSM Business Profile modern registration number:** the strict validator rejected valid 12-digit modern SSM registration numbers. It now accepts modern 12-digit and legacy registration formats.

## Fresh profile-by-profile proof

| Profile | Detected type | OCR conf. | Anchors | Fields | 5 formats | Strict local status | Concern / proof focus |
| --- | --- | ---: | ---: | ---: | --- | --- | --- |
| Malaysia ID / Passport — MyKad | Malaysia MyKad | 92.75% | 7/7 | 6/6 | PASS | REVIEW REQUIRED* | Exact NRIC, full printed name and full multi-line address including postcode/state. Strict profile intentionally requires independent AI confirmation before production PASS. |
| Malaysia ID / Passport — MyPR | Malaysia MyPR | 93.48% | 6/6 | 7/7 | PASS | REVIEW REQUIRED* | PNL must remain Country of Origin and must never leak into Address. Full name/address/religion/residency/gender checked. |
| Malaysia ID / Passport — Passport | Malaysia Passport | 89.12% | 10/10 | 13/13 | PASS | REVIEW REQUIRED* | Printed biodata fields captured exactly. Fresh local stress OCR did not reliably preserve the MRZ under degradation, so strict gate correctly remained REVIEW REQUIRED; the separate real passport regression still passes 15/15 including both MRZ lines. |
| Malaysia Driving Licence | Malaysia Driving Licence | 90.13% | 6/6 | 8/8 | PASS | REVIEW REQUIRED* | OCR inserted a leading | before the Nama/Name line. Parser previously lost the full name; patched to tolerate leading OCR border artefacts while preserving the name. |
| CIDB Certificate — PPK | CIDB PPK / Perakuan Pendaftaran | 92.72% | 8/8 | 7/7 | PASS | REVIEW REQUIRED* | Registration number, contractor identity, dates, status and multiple classification/specialisation codes must stay separate and exact. |
| CIDB Certificate — SPKK | CIDB SPKK | 91.96% | 6/6 | 6/6 | PASS | PASS | Contractor, district, registration dates and authorised-officer section checked. No regression after fixes. |
| CIDB Certificate — STB | CIDB STB | 93.19% | 7/7 | 6/6 | PASS | REVIEW REQUIRED* | Officer NRIC formatting was being stripped to digits. Patched to preserve canonical Malaysian hyphenated NRIC while validating digit count. |
| SSM Document — Company Profile | SSM Company Profile | 92.89% | 6/6 | 10/10 | PASS | REVIEW REQUIRED* | Modern 12-digit + legacy company number, company names, dates, postcodes and business activity must remain distinct. Realistic legacy-number format verified. |
| SSM Document — Business Profile | SSM Business Profile / Maklumat Perniagaan | 93.06% | 6/6 | 9/9 | PASS | REVIEW REQUIRED* | Strict validator previously rejected a correct modern 12-digit SSM business registration number. Patched to accept modern 12-digit and legacy formats. |
| SSM Business Registration — Certificate | SSM Business Registration Certificate | 95.05% | 7/7 | 8/8 | PASS | REVIEW REQUIRED* | Business name, registration number, valid-until date and registered-address boundary verified; registrar/footer text must not leak into address. |
| SSM Business Registration — Renewal | SSM Business Registration Renewal | 93.57% | 7/7 | 8/8 | PASS | REVIEW REQUIRED* | Explicit Nama Perniagaan label was not handled by the renewal parser. Patched fallback now captures it without affecting certificate sentence-based extraction. |
| Invoice / Receipt | Invoice / Receipt | 96.09% | 7/7 | n/a | PASS | PASS | Repeated monetary values can cross-map. Invoice number, subtotal, tax and grand total anchors remained exact. |
| Form / Application | Form / Application | 92.85% | 6/6 | n/a | PASS | PASS | Contains NRIC-like content but must remain Form / Application rather than being promoted to an identity profile. |
| Certificate / Licence | Certificate / Licence | 96.05% | 5/5 | n/a | PASS | PASS | Contains identity wording and a licence number but must remain generic Certificate / Licence rather than Driving Licence. |
| Letter / Memo | Letter / Memo | 96.14% | 5/5 | n/a | PASS | PASS | Reference number, date, body wording and contact details must remain plain-text content without unwanted translation/correction. |
| Report / Statement | Report / Statement | 96.33% | 7/7 | n/a | PASS | PASS | Repeated percentages and metrics must remain exact while preserving Report / Statement detection. |
| General Document | General Document | 96.23% | 5/5 | n/a | PASS | PASS | General guidance includes document-upload terms but must not be misclassified as a certificate/form profile. |

*`REVIEW REQUIRED` is expected for profiles configured to require independent AI verification. This validation environment has no `OPENAI_API_KEY`, so I did not weaken that gate or fabricate a successful second-opinion pass.

## Five-format proof

For every fresh test profile the canonical extracted values were rendered into **FORM, MARKDOWN, TEXT, JSON and HTML**. The contract validator verified that JSON is parseable, no required canonical value disappears and all five rendered outputs are non-empty. Result: **17/17 PASS**.

## Files in this proof package

- `tests/fresh_stress/fresh_stress_results.json` — machine-readable fresh results including OCR text, field comparisons, strict problems and output lengths.
- `evidence/FRESH_STRESS_CONTACT_SHEET.png` — visual overview of all 17 fresh fixtures and test outcomes.
- `evidence/FRESH_STRESS_PROOF_GALLERY.html` — per-profile image, OCR text, expected/captured fields and concern notes.
- `tests/v31_external/v31_external_results.json` — rerun public-source corpus results.
- `tests/fresh_stress_validation.py` and `tests/fresh_stress_format_harness.js` — reproducible independent stress test.

## Remaining production concern

The local OCR/parser and format layers are reproducibly passing the executed corpora. A **live server-side AI Vision call was not executed here because no OpenAI API key is present in the runtime**. The API handler and strict schema/error paths were runtime-tested with the existing harness, and strict profiles correctly stay in REVIEW REQUIRED without independent AI confirmation. For a production 99.99%-style SLA claim, you still need a much larger representative real-document corpus and statistically justified confidence bounds rather than a small perfect regression set.