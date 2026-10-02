# V32.2 Malaysia NRIC Hardening

Date: 1 Oct 2026

## What changed

- Added Malaysian NRIC `YYMMDD` birth-date validation before a 12-digit candidate can be accepted.
- Supports both `YYMMDD-PB-####` and `YYMMDDPB####` representations.
- Added constrained OCR-confusion recovery for NRIC-shaped tokens: `O/Q/D→0`, `I/L/|/!→1`, `Z→2`, `S→5`, `G→6`, `T→7`, `B→8`.
- OCR-confusion recovery is accepted only when the resulting token is exactly 12 digits and the `YYMMDD` segment is structurally valid.
- Added contextual ranking that favors `NRIC`, `MyKad`, `No. K/P`, `No. Pengenalan` and `Identity Number` lines over unrelated 12-digit registration numbers.
- MyKad/MyPR focused OCR now uses fast primary + alternate reads, then a conditional strong read and wider fallback only when the normal path is unresolved.
- Conflicting date-valid NRIC reads are not silently resolved by picking the first candidate. The field is left unresolved so AI verification or REVIEW REQUIRED can handle it.
- NRIC-derived gender fallback is now allowed only after a structurally valid NRIC has been confirmed and only for the MyKad/MyPR profiles where that rule is explicitly enabled.
- Malaysia Passport and Malaysia Driving Licence identity-number normalization now use the same date-valid NRIC checks.
- The server/API canonicalization path now applies the same NRIC validation and constrained OCR recovery rules.

## Measured validation

- Front-end NRIC parser stress: **1,150,000 / 1,150,000 passed (100.00%)**.
- API helper validation: **200,003 / 200,003 passed (100.00%)**.
- MyKad/MyPR degraded reference-image focused OCR: **24 / 24 variants passed (100.00%)**.
- Existing production-readiness suite: **PASS**.
- Existing supplied MyKad + MyPR critical fields: **13 / 13 exact (100.00%)**.
- Existing Malaysia Passport fields: **15 / 15 exact (100.00%)**.

## Accuracy statement

The build is hardened toward a 99.99% production target but the executed tests cannot prove universal 99.99% accuracy on every unseen Malaysian NRIC image. Camera glare, extreme blur, occlusion, non-front-card layouts and damaged print can still make a digit visually unsupported. In those cases the system is intentionally fail-closed: it should return an unresolved field / REVIEW REQUIRED rather than invent a digit.
