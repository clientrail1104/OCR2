#!/usr/bin/env python3
"""OCR smoke tests derived from public web sample content.

The source projects publish the sample text/expected values. This test renders
that published content into deterministic images locally and runs Tesseract on
those images. It is a robustness smoke test for generic invoice/receipt OCR,
not a claim that the original remote image bytes were downloaded.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import pytesseract, re, tempfile

FONT_CANDIDATES=[
    '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
    '/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf',
]
font_path=next((p for p in FONT_CANDIDATES if Path(p).exists()),None)
if not font_path: raise SystemExit('No monospaced font available')
font=ImageFont.truetype(font_path,30)

SAMPLES=[
('github_invoice', '''INVOICE
Invoice No: INV-001
Date: 26/08/2026

Customer: Jane Doe
Vendor: Tech Store Inc.

Items Purchased:
Keyboard    2    Rp 500000
Mouse       3    Rp 150000

Total: Rp 1450000
''', ['INVOICE','INV-001','26/08/2026','Jane Doe','Tech Store Inc.','Keyboard','Rp 1450000']),
('github_receipt', '''Store #05666
3515 DEL MAR HTS, RD
SAN DIEGO, CA 92130
(858) 792-7040

Register #4 Transaction #571140
Cashier #56661020 8/20/17 5:45PM

wellness+ with Plenti
1 G2 RETRACT BOLD BLK 2PK            1.99 T
SALE 1/1.99, Reg 1/4.69
Discount 2.70-

1 Items                         Subtotal  1.99
                                      Tax  .15
                                    Total  2.14

*MASTER*                              2.14
App #AA APPROVAL AUTO
Ref # 05639E
Entry Method: Chip
''', ['Store #05666','SAN DIEGO, CA 92130','Transaction #571140','Total  2.14','Ref # 05639E','Entry Method: Chip'])]

def fold(s): return re.sub(r'\s+',' ',str(s)).strip().lower()

passed=0; total=0
with tempfile.TemporaryDirectory() as td:
    for name,text,needles in SAMPLES:
        lines=text.splitlines(); width=1500; height=max(600,80+len(lines)*46)
        img=Image.new('RGB',(width,height),'white'); d=ImageDraw.Draw(img)
        y=40
        for line in lines:
            d.text((45,y),line,fill='black',font=font); y+=46
        path=Path(td)/f'{name}.png'; img.save(path)
        got=pytesseract.image_to_string(Image.open(path),config='--psm 6',lang='eng')
        print(f'\n[{name}]\n{got.strip()}')
        fg=fold(got)
        for needle in needles:
            total+=1; ok=fold(needle) in fg; passed+=int(ok)
            print(('PASS' if ok else 'FAIL'),needle)
            if not ok: raise SystemExit(f'Web-derived sample failed: {name} missing {needle!r}')
print(f'\nPASS: web-source-derived invoice/receipt OCR anchors {passed}/{total} exact/normalized = 100.00%')
