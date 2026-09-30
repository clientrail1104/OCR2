# NeuroOCR V30 — Go-Live Proof & Concern Report

**Execution date:** 30 September 2026  
**Release status:** Go-live hardened build; executed regression corpus PASS.

## What was actually proven

- Supplied internal/user sample corpus: Malaysia MyKad, MyPR and Passport — **28/28 critical fields exact = 100.00%**.
- Passport recompression stress case — **15/15 exact = 100.00%**.
- Public-source-derived Invoice/Receipt smoke anchors — **13/13 exact/normalised = 100.00%**.
- Expanded source-derived coverage across the remaining UI document profiles — **73/73 OCR anchors = 100.00%** and **10/10 auto-detection cases = 100.00%**.
- FORM, MARKDOWN, TEXT, JSON and HTML output contract — **PASS**.
- Server strict JSON/schema/runtime guards — **PASS**.

**Important:** the percentages above are measurements on the executed corpus. They do not statistically prove 99.99% accuracy on every unseen production document. Raw OCR confidence is not a calibrated probability of field correctness. For strict profiles, production acceptance remains fail-closed: structurally incomplete or unverified documents must show **REVIEW REQUIRED**.

## Go-live defects found and fixed in this run

1. **Form / Application false identity detection** — the BNM CCRIS form contains words such as “Passport” and “MyKad”. V29 could classify it as a Malaysia Passport. V30 now requires strong passport evidence such as MRZ or multiple passport-specific biodata labels before identity classification.
2. **Report / Statement under-detection** — a BNM annual financial report was detected as General Document. V30 now recognises Annual Report, Statement of Financial Position, Income Statement, Financial Statements, Balance Sheet and Profit and Loss indicators.

## Proof and concern by document profile

| Document profile | Proof sample | OCR proof | Raw OCR confidence* | Detection | Main production concern | V30 action/status |
| --- | --- | ---: | ---: | --- | --- | --- |
| Malaysia Driving Licence | Wikimedia Commons Malaysia driving licence specimen | 10/10 (100%) | 91.28% | Malaysia Driving Licence | Public specimen redacts personal values; exact end-to-end field validation therefore uses a source-grounded complete regression fixture plus label/layout validation. | PASS: no new parser defect found in this proof run. |
| CIDB Certificate | CIDB official SPKK guidance/sample certificate | 8/8 (100%) | 92.72% | CIDB SPKK | Official CIDB web reference exposes certificate examples/guidance but not a machine-readable ground-truth dataset. Keep strict required-field gate and AI verification enabled. | PASS: no new parser defect found in this proof run. |
| SSM Business Registration | SSM official Business Certificate sample | 9/9 (100%) | 94.48% | SSM Business Registration Certificate | Official sample contains footer/portal metadata and certification furniture that can leak into fields. Footer and address sanitation must stay enabled. | PASS: no new parser defect found in this proof run. |
| SSM Document | SSM Company Information product/sample structure | 8/8 (100%) | 93.03% | SSM Company Profile | SSM company/business profiles vary by product and print generation. Keep profile detection and footer/noise suppression enabled. | PASS: no new parser defect found in this proof run. |
| Invoice / Receipt | Public OCR receipt/invoice datasets on GitHub | 8/8 (100%) | 95.17% | Invoice / Receipt | Real receipts can be crumpled, thermal-faded, skewed or handwritten. Low-quality cases must fail to review rather than be auto-accepted. | PASS: no new parser defect found in this proof run. |
| Form / Application | Bank Negara Malaysia CCRIS/eCCRIS Application Form | 7/7 (100%) | 93.12% | Form / Application | Forms frequently mention MyKad, Passport and Driving Licence as supporting documents. V30 fixes the false-positive identity classification discovered in go-live testing. | FIXED: passport/MyKad mentions inside a form no longer trigger identity classification without strong passport/card evidence. |
| Letter / Memo | Bank Negara Malaysia Sample Authorisation Letter for Company | 6/6 (100%) | 95.12% | Letter / Memo | Free-form body text has no fixed schema. Preserve literal transcription and do not auto-correct names, dates or reference numbers. | PASS: no new parser defect found in this proof run. |
| Certificate / Licence | SSM official business certificate used as generic certificate regression | 6/6 (100%) | 95.38% | Certificate / Licence | Certificate layouts are highly variable. Generic profile should not override stronger known SSM/CIDB document detection unless manually selected. | PASS: no new parser defect found in this proof run. |
| Report / Statement | Bank Negara Malaysia Annual Report 2025 - Our Finances | 6/6 (100%) | 95.57% | Report / Statement | Annual reports and financial statements were previously under-detected. V30 adds Annual Report, Statement of Financial Position, Income Statement and related indicators. | FIXED: expanded report/statement auto-detection for annual reports and financial statements. |
| General document | Generic regression document | 5/5 (100%) | 95.64% | General Document | No fixed field schema. Acceptance should be based on complete literal transcription and anomaly reporting rather than a fixed-field score. | PASS: no new parser defect found in this proof run. |

\* Raw OCR confidence shown here is the mean positive Tesseract word confidence on the regression fixture. It is **not** the same as field accuracy or production verification.

## Internal identity-document proof

| Profile | Exact critical fields | Raw OCR confidence* | Production proof |
| --- | ---: | ---: | --- |
| Malaysia MyKad | 6/6 = 100.00% | 47.35% | Exact NRIC, name, complete address, religion, citizenship and gender |
| Malaysia MyPR | 7/7 = 100.00% | 51.09% | Exact NRIC, name, complete address, PNL, religion, PR status and gender |
| Malaysia Passport | 15/15 = 100.00% | 42.27% | Exact printed biodata + both 44-character MRZ lines with check-digit validation |

The low raw confidence on the identity samples is precisely why V30 does not use Tesseract confidence as the final acceptance metric. Profile-specific focused rereads, structural validation, MRZ mathematics and AI verification determine strict-profile production acceptance.

## Public/source-derived references used

- Wikimedia Commons — Malaysia driving licence specimen: https://commons.wikimedia.org/wiki/File:Malaysia_driving_licence.jpg
- CIDB Malaysia — SPKK registration guidance containing example certificate/letter material: https://www.cidb.gov.my/wp-content/uploads/2022/10/1.0-Syarat-Pendaftaran-Sijil-Perolehan-.pdf
- SSM — official Business Certificate sample: https://www.ssm.com.my/Pages/Product/PDF/ROB/BUSINESS%20CERTIFICATE.pdf
- SSM — Company Information product/sample structure: https://www.ssm.com.my/Pages/Product/Company-Information.aspx
- Bank Negara Malaysia — CCRIS/eCCRIS application form: https://www.bnm.gov.my/documents/20124/6190098/CCRIS_eCCRIS_Form.pdf
- Bank Negara Malaysia — Sample Authorisation Letter for Company: https://www.bnm.gov.my/documents/20124/6190098/Sample_Authorisation_Letter_CCRIS_Company_en.pdf
- Bank Negara Malaysia — Annual Report 2025, Our Finances: https://www.bnm.gov.my/documents/20124/21185005/ar2025_en_ch4.pdf
- Public receipt dataset documentation: https://github.com/themurtez/receipt-dataset-standardized

## Go-live acceptance rule

For Malaysia ID/Passport, Driving Licence, CIDB and SSM known profiles, do **not** auto-accept a record solely because raw OCR confidence is high. Accept only when required fields are complete, structural/profile validation passes and production verification is complete. Otherwise keep the result as **REVIEW REQUIRED**.
