# Malaysia NRIC Validation Report — V32.2

Date: 1 Oct 2026

## Scope

This validation covers Malaysian NRIC extraction and normalization used by Malaysia MyKad, Malaysia MyPR, Malaysia Driving Licence and the Malaysian identity-number field on Malaysia Passport. It tests the number parser, OCR-confusion recovery, invalid-date rejection, competing-number selection, focused image OCR and regression safety.

## 1. Deterministic parser stress

Test file: `tests/nric-accuracy-stress.js`

| Category | Passed | Total | Result |
| --- | ---: | ---: | ---: |
| Hyphenated NRIC | 250,000 | 250,000 | 100.00% |
| Compact 12-digit NRIC | 250,000 | 250,000 | 100.00% |
| One OCR-confusion substitution | 250,000 | 250,000 | 100.00% |
| Two OCR-confusion substitutions | 250,000 | 250,000 | 100.00% |
| Invalid embedded date rejection | 100,000 | 100,000 | 100.00% |
| Competing 12-digit contextual selection | 50,000 | 50,000 | 100.00% |
| **Total** | **1,150,000** | **1,150,000** | **100.00%** |

Measured parser throughput in the executed run: approximately **60,247 cases/second**.

## 2. API helper proof

Test file: `tests/nric-api-helper-proof.js`

Result: **200,003 / 200,003 passed (100.00%)** for hyphenated normalization, compact normalization and representative invalid-date rejection.

## 3. Focused image OCR robustness

Test file: `tests/nric-image-robustness.py`

The supplied MyKad and MyPR reference images were retested under brightness changes, contrast changes, Gaussian blur, small rotations and JPEG compression using the same focused-crop strategy and digit whitelist.

| Reference | Passed | Total | Result |
| --- | ---: | ---: | ---: |
| MyKad | 12 | 12 | 100.00% |
| MyPR | 12 | 12 | 100.00% |
| **Total** | **24** | **24** | **100.00%** |

## 4. Existing regression suite

`tests/production-readiness.py` remains PASS after the NRIC changes. The supplied image corpus retains exact extraction for MyKad/MyPR critical fields and Malaysia Passport fields.

## Safeguards added

The system now requires a valid `YYMMDD` segment for a 12-digit NRIC candidate. It uses constrained character recovery only in an NRIC-shaped token. If independent focused reads produce competing date-valid numbers, it does not choose one arbitrarily. Conditional fallback OCR is used only when the normal path is unresolved which keeps the common path fast.

## Confidence interpretation

The test corpus exceeded the requested 99.99% target with 100.00% measured results. This is evidence for the tested conditions, not a universal accuracy guarantee. No OCR system can truthfully guarantee 99.99% across unlimited unseen real-world images without a representative production ground-truth dataset. For unsupported or visually ambiguous digits this build favors REVIEW REQUIRED over a guessed NRIC.
