#!/usr/bin/env python3
"""One-command local pipeline after PDFs are placed in data/jra_pdf/."""
import subprocess,sys
from pathlib import Path
r=Path(__file__).resolve().parent; pdfs=sorted((r/'data/jra_pdf').glob('*.pdf'))
if not pdfs: raise SystemExit('Put JRA result PDFs in data/jra_pdf/ first.')
def run(*a): subprocess.check_call([sys.executable,*map(str,a)],cwd=r)
run('jra_pdf_adapter.py',*pdfs);run('import_csv.py');run('build_site_data.py')
print('DONE: open index.html')
