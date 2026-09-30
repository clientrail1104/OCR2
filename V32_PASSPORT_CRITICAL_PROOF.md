# NeuroOCR V32 — Malaysia Passport Critical-Field Validation

## Scope

V32 hardens two Malaysia Passport fields that are especially sensitive to OCR noise:

1. **Tempat Lahir / Place of Birth**
2. **MRZ Line 1**

## Changes made

### Tempat Lahir / Place of Birth

- Added four independent focused reads: gray, red-channel, tight-value and Otsu-binary wide crop.
- Added location-specific consensus scoring.
- Added a strict rule preventing Issuing Office, date, sex, height or label text from being accepted as Place of Birth.
- If visual support is insufficient the field remains unresolved and strict validation returns **REVIEW REQUIRED** instead of guessing.

### MRZ Line 1

- Added three dedicated first-MRZ-line reads plus the existing full MRZ-block reads.
- Enforces an exact 44-character TD3 first line beginning `P<MYS`.
- Restricts the post-prefix content to `A-Z` and `<`.
- Reconciles OCR character errors against the independently captured printed passport name while preserving visible MRZ separator structure.
- Rejects a candidate when its MRZ name letters disagree with the printed name and cannot be reconciled from the visible MRZ evidence.
- Server-side normalization has the same strict `P<MYS` + 44-character rule.

## Executed real-image proof

Reference passport fixture:

- Expected Place of Birth: `KUALA LUMPUR`
- Expected MRZ Line 1: `P<MYSMAHATHIR<BIN<IDRUS<<<<<<<<<<<<<<<<<<<<<`

The V32 critical-field stress test used the actual passport fixture and four image conditions:

| Variant | Place of Birth | MRZ Line 1 | Result |
|---|---|---|---|
| Original | Exact | Exact | PASS |
| JPEG quality 55 | Exact | Exact | PASS |
| 70% downscale + blur | Exact | Exact | PASS |
| Darkened + JPEG quality 65 | Exact | Exact | PASS |

**Measured result: 8/8 exact critical checks = 100.00%.**

The standard full passport regression also remains **15/15 exact fields** on the reference fixture.

## Evidence

- `evidence/V32_PASSPORT_CRITICAL_PROOF.png`
- `tests/V32_PASSPORT_CRITICAL_RESULTS.json`
- `tests/v32_passport_critical_proof.py`
- `tests/passport-real-image-proof.py`

## Accuracy statement

The executed corpus measured **100.00% exact matching** for these two critical fields under the tested conditions. This is stronger evidence than displaying an artificial 99.99% confidence value, but it is not a statistical guarantee that every unseen passport image will achieve 99.99% accuracy. V32 therefore uses strict validation and fail-closed review behavior when evidence is insufficient.
