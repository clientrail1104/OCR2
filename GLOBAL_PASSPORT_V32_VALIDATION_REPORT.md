# NeuroOCR V32 — Global Passport ICAO TD3 Validation Report

## Scope
V32 extends the passport engine from a Malaysia-specific implementation to a country-independent ICAO TD3 machine-readable passport engine while preserving the existing Malaysia Passport profile.

The test target is the two-line 44-character TD3 passport MRZ used by machine-readable passports. Country-specific visual artwork, language, label placement and optional-data meaning are not assumed. Core identity fields are recovered from the MRZ and can be supplemented by page OCR / AI Vision.

## Production changes
- Added `International Passport / ICAO TD3` auto-detection and selectable profile.
- Replaced `P<MYS`-only detection with country-independent `P<XXX` TD3 detection.
- Removed the Malaysian one-letter + eight-digit passport-number assumption from the international profile.
- Issuing country and nationality are kept as separate 3-character MRZ fields and are no longer assumed to be identical.
- Optional data is preserved as country-defined data and is not treated as a national ID unless a country-specific profile explicitly defines that meaning.
- Added ICAO document-number, DOB, expiry, optional-data and composite check-digit validation.
- Added support for `M`, `F` and unspecified sex (`<`, reported as `X`).
- Added safe handling of filler-only optional data where the optional-data check position is `<`.
- Added calendar-range validation for MRZ dates.
- Added adaptive MRZ OCR rereads: primary, alternate, stronger contrast, dedicated Line 1 and dedicated Line 2.
- Added constrained OCR repair for common O/0, I/1, L/1, B/8, G/6, S/5 and related MRZ confusions. A repair is accepted only when the ICAO check-digit structure validates.
- Added protection against unsafe issuer/nationality rewriting: correction is only allowed when the OCR issuer code is not a known country/territory code and a structurally supported valid code is available.
- Malaysia Passport regression behaviour remains intact.

## Acceptance results

| Test | Result |
|---|---:|
| ISO country/territory codes exercised | **249** |
| Synthetic ICAO TD3 cases | **19,920 / 19,920 — 100%** |
| Country/profile auto-detection | **249 / 249 — 100%** |
| Synthetic structured-field checks | **1,736 / 1,736 — 100%** |
| Generated country image → OCR → exact full MRZ | **249 / 249 — 100%** |
| Image structured checks | **747 / 747 — 100%** |
| Cases requiring adaptive OCR retry | **12 / 249** |
| Cases ending with MRZ structural confidence `0.9999` | **249 / 249** |
| Existing Malaysia Passport visible fixture | **15 / 15 exact** |
| Existing MyKad/MyPR/Passport regression | **28 / 28 exact** |
| Existing production-readiness suite | **PASS** |
| API contract/runtime validation | **PASS** |

## Performance
The 100,000-record parser benchmark completed at approximately **3,800 TD3 parses/second** in the sandbox after the additional safety and repair checks (about **0.26 ms per parse**). Image OCR speed depends on image size, browser/device and whether adaptive rereads are triggered.

## What `0.9999` means in V32
`0.9999` is used as a **structural MRZ validation confidence flag**, not as a claim that every camera image in the real world has a 99.99% probability of being read correctly. It is assigned when the engine has both MRZ lines and Line 2 passes the ICAO component and composite check-digit rules after constrained reconciliation.

The executed acceptance corpora measured **100% exact match**, which is above 99.99% on those corpora. A universal 99.99% production SLA still requires a statistically representative real-world passport-image dataset across camera blur, glare, occlusion, damage, unusual fonts, counterfeit documents and country-specific page designs. V32 does not fabricate unreadable data to manufacture a confidence target.

## Country-level proof
`GLOBAL_PASSPORT_COUNTRY_RESULTS.csv` contains one acceptance row for every tested country/territory code. `GLOBAL_PASSPORT_IMAGE_ACCEPTANCE_RESULTS.json` contains the complete machine-readable acceptance result. `GLOBAL_PASSPORT_TD3_STRESS_RESULTS.json` contains the 19,920-case parser stress run and 100,000-parse benchmark.

## Remaining boundary
This global profile is specifically for **ICAO TD3 machine-readable passport biodata pages**. Visas, national ID cards, residence permits and other MRZ document sizes (TD1/TD2/MRV-A/MRV-B) remain separate document classes and should not be silently treated as passports.
