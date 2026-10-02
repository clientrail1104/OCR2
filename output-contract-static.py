#!/usr/bin/env python3
from pathlib import Path
import re, subprocess, tempfile, shutil

ROOT = Path(__file__).resolve().parents[1]
html = (ROOT / 'index.html').read_text(encoding='utf-8')
api = (ROOT / 'api' / 'ocr.js').read_text(encoding='utf-8')

for tab in ['form', 'markdown', 'text', 'json', 'html']:
    assert f'data-tab="{tab}"' in html, f'missing {tab} output tab'
    assert tab in html, f'missing {tab} renderer/export support'

for ext in ['.pdf', '.docx', '.xlsx', '.xls', '.ods', '.pptx', '.odt', '.odp', '.txt', '.md', '.csv', '.tsv', '.json', '.xml', '.html', '.htm', '.rtf']:
    assert ext in html, f'missing input extension {ext}'

for token in ['canonicalOutputData', 'buildCanonicalMarkdown', 'buildCanonicalText', 'buildCanonicalHtml', 'validateOutputContract', 'production_verified', 'RAW OCR CONFIDENCE', 'PRODUCTION VERIFICATION', 'mrz-check-digit-failed']:
    assert token in html, f'missing output-contract function {token}'

assert 'validateStructuredResultShape' in api
assert 'strict_schema_contract:true' in api
assert 'minimum:0,maximum:1' in api

node = shutil.which('node')
if node:
    blocks = re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>', html, re.S)
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
        f.write(blocks[-1]); browser_js = f.name
    with tempfile.NamedTemporaryFile('w', suffix='.mjs', delete=False, encoding='utf-8') as f:
        f.write(api); api_js = f.name
    try:
        subprocess.run([node, '--check', browser_js], check=True)
        subprocess.run([node, '--check', api_js], check=True)
    finally:
        Path(browser_js).unlink(missing_ok=True)
        Path(api_js).unlink(missing_ok=True)

print('PASS: five-format output contract, expanded input formats, browser JS syntax and API JS syntax')
