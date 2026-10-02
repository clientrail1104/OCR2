# V31.1 QA Hardening Patch Notes

- Portable validation root resolution in `v31_external_profile_proof.py` and `render_v31_proof_screenshots.py`.
- Driving licence name parser tolerates leading OCR border punctuation.
- CIDB STB `No. K/P` preserves canonical Malaysian NRIC formatting.
- SSM registration renewal parses explicit `Nama Perniagaan / Business Name` labels.
- SSM Business Profile strict validation accepts modern 12-digit registration numbers as well as legacy forms.
- Added independent 17-profile image stress suite and five-format contract harness.
