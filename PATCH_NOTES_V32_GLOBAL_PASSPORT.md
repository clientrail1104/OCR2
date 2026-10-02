# V32 Global Passport Patch Notes

V32 upgrades passport handling to country-independent ICAO TD3 processing.

Main fixes: generic `P<XXX` detection, arbitrary TD3 document numbers, separate issuer/nationality codes, optional-data preservation, filler-only optional data, complete ICAO check-digit validation, date sanity checks, adaptive high-contrast and line-level MRZ rereads, constrained OCR-confusion recovery and safe country-code reconciliation.

Validation: 249/249 country image fixtures exact, 19,920/19,920 generated TD3 records exact, 747/747 image structured checks exact and the prior production suite remains PASS.
