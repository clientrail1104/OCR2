# Public web sample sources used for V29 validation

The production-readiness suite separates **remote source inspection** from **locally executable regression fixtures** so it does not pretend a remote image was tested when its bytes were not available inside the restricted test container.

## Official Malaysian passport reference

- Council of the European Union PRADO — Malaysia ordinary passport (`MYS-AO-03001`), biodata image/reference.
- Source page: https://www.consilium.europa.eu/prado/en/MYS-AO-03001/image-315879.html
- The supplied `tests/fixtures/malaysia_passport_reference.jpg` visually matches this public specimen. It is executed locally by `passport-real-image-proof.py` and all 15 canonical fields must match exactly with valid MRZ check digits.

## Public invoice sample content

- GitHub project: `devinaur/ocr-document-reader`
- Source: https://github.com/devinaur/ocr-document-reader
- Published sample anchors include `INV-001`, `26/08/2026`, `Jane Doe`, `Tech Store Inc.` and `Rp 1450000`.
- `web-sample-derived-ocr-proof.py` renders the published sample content locally and verifies the OCR anchors exactly/normalised.

## Public receipt sample content

- GitHub project: `SimformSolutionsPvtLtd/tesseract-OCR-iOS-demo`
- Source: https://github.com/SimformSolutionsPvtLtd/tesseract-OCR-iOS-demo
- Published receipt anchors include `Store #05666`, `SAN DIEGO, CA 92130`, `Transaction #571140`, `Total 2.14`, `Ref # 05639E` and `Entry Method: Chip`.
- `web-sample-derived-ocr-proof.py` renders the published sample content locally and verifies the OCR anchors exactly/normalised.

## Important limitation

The execution container cannot resolve external hosts, so additional remote GitHub image binaries cannot be cloned/downloaded during this run. Those sources were inspected through web search, while executable OCR tests use the supplied/local fixture bytes and deterministic web-source-derived images. Production CI with network access should add more original remote fixtures before claiming population-level accuracy.
