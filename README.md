# NeuroOCR Strict All Profiles V30

V30 is the go-live hardened build of the NeuroOCR browser application. It keeps one canonical extraction object and renders consistent **FORM, MARKDOWN, TEXT, JSON and HTML** outputs.

## V30 go-live fixes

- Prevents forms that merely mention Passport/MyKad/Driving Licence from being misclassified as identity documents.
- Requires stronger evidence for automatic Malaysia Passport detection, including MRZ or multiple passport-specific biodata labels.
- Expands Report / Statement detection for Annual Report, Statement of Financial Position, Income Statement, Financial Statements, Balance Sheet and Profit and Loss.
- Adds an all-profile source-derived OCR/detection regression suite.

## Executed proof

- Supplied MyKad/MyPR/Passport: **28/28 exact critical fields**.
- Passport JPEG stress: **15/15 exact fields**.
- Public-source-derived invoice/receipt: **13/13 anchors**.
- Expanded remaining-profile proof: **73/73 OCR anchors** and **10/10 auto-detection cases**.
- Five-output contract and server strict-JSON/schema guards: **PASS**.

See `GO_LIVE_PROOF_REPORT.md` and `tests/LAST_TEST_RESULTS.json`.

These are measured corpus results, not a universal guarantee over unseen documents. Strict profiles fail closed to **REVIEW REQUIRED** if critical evidence or verification is incomplete.

## Run tests

```bash
python tests/output-contract-static.py
python tests/api-contract-runtime.py
python tests/malaysia-id-passport-regression.py
python tests/malaysia-id-real-image-proof.py
python tests/passport-real-image-proof.py
python tests/web-sample-derived-ocr-proof.py
python tests/all-profile-web-derived-proof.py
```
