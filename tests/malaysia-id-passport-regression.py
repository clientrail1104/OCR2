#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
API = (ROOT / "api" / "ocr.js").read_text(encoding="utf-8")
DATA = json.loads((TESTS / "malaysia-id-passport-regression.json").read_text(encoding="utf-8"))


def mrz_value(c: str) -> int:
    if c.isdigit():
        return int(c)
    if "A" <= c <= "Z":
        return ord(c) - 55
    return 0


def mrz_check(text: str) -> str:
    weights = (7, 3, 1)
    return str(sum(mrz_value(c) * weights[i % 3] for i, c in enumerate(text)) % 10)


fixtures = {x["document_type"]: x for x in DATA["fixtures"]}
required = {"Malaysia MyPR", "Malaysia MyKad", "Malaysia Passport"}
assert set(fixtures) == required, f"Missing regression profiles: {required - set(fixtures)}"

for item in DATA["fixtures"]:
    path = TESTS / item["file"]
    assert path.exists(), f"Fixture missing: {path}"
    with Image.open(path) as img:
        assert img.width >= 500 and img.height >= 300, f"Unexpectedly small fixture: {path.name} {img.size}"
    assert item["expected_fields"], f"No expected fields for {item['document_type']}"

mypr = fixtures["Malaysia MyPR"]["expected_fields"]
assert mypr["Identity Number"] == "901231-10-6789"
assert mypr["Name"] == "TAN AH KON"
assert mypr["Address"].endswith("88400 KIANABALL")
assert "JILAN MERAH" in mypr["Address"]
assert mypr["Country of Origin"] == "PNL"
assert mypr["Religion"] == "ISLAM"
assert mypr["Citizenship"] == "PEMASTAUTIN TETAP / PR"
assert mypr["Gender"] == "LELAKI"

mykad = fixtures["Malaysia MyKad"]["expected_fields"]
assert mykad["Identity Number"] == "950830-05-5465"
assert mykad["Name"] == "MUHAMAD HASHIF BIN ALI"
assert "TAMAN SRI ULU BENDUL" in mykad["Address"]
assert mykad["Address"].endswith("NEGERI SEMBILAN")
assert mykad["Religion"] == "ISLAM"
assert mykad["Citizenship"] == "WARGANEGARA"
assert mykad["Gender"] == "LELAKI"

passport = fixtures["Malaysia Passport"]["expected_fields"]
l1, l2 = passport["MRZ Line 1"], passport["MRZ Line 2"]
assert len(l1) == 44 and l1.startswith("P<MYS")
assert len(l2) == 44
assert mrz_check(l2[0:9]) == l2[9], "Passport-number check digit mismatch"
assert mrz_check(l2[13:19]) == l2[19], "DOB check digit mismatch"
assert mrz_check(l2[21:27]) == l2[27], "Expiry check digit mismatch"
assert mrz_check(l2[28:42]) == l2[42], "Optional-data check digit mismatch"
assert mrz_check(l2[0:10] + l2[13:20] + l2[21:43]) == l2[43], "Composite check digit mismatch"
assert passport["Passport Number"] == "A00000000"
assert passport["Nama / Name"] == "MAHATHIR BIN IDRUS"
assert passport["No. Pengenalan / Identity No."] == "930216146007"

# Static guards: these ensure future edits do not silently remove the dedicated
# focused zones and deterministic reconciliation rules added for these samples.
for needle in [
    'identity:{x:.0350,y:.1900,w:.3300,h:.1050',
    'status:{x:.6500,y:.8350,w:.3400,h:.1550',
    'status:{x:.6350,y:.7250,w:.3500,h:.1450',
    'function focusedIdentityStatuses(documentType,...texts)',
    'setProfileField(doc,"Religion",status.religion',
    'setProfileField(doc,"Citizenship",status.citizenship',
    'setProfileField(doc,"Gender",status.gender',
    'passportNumber:{x:.7450,y:.0900,w:.2350,h:.1200',
    'function focusedPassportNumber(...texts)',
    'Focused passport recovery V29'
]:
    assert needle in INDEX, f"Front-end regression guard missing: {needle}"

for needle in [
    'function applyCanonicalEvidenceFallbacks(result,type)',
    'function passportMrzFromEvidence(text)',
    'For MyPR, a card may legitimately end the address at postcode + locality with no state line',
    'Read the NRIC from the upper-left number band',
    'PNL/religion/gender from the lower-right status block'
]:
    assert needle in API, f"API regression guard missing: {needle}"

print("PASS: Malaysian MyPR, MyKad and Passport reference fixtures and extraction safeguards validated")
