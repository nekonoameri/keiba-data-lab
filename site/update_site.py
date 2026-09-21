#!/usr/bin/env python3
"""One command: optionally fetch official JRA PDFs, parse, import, aggregate, and generate pages."""
import argparse, subprocess, sys
from pathlib import Path
R=Path(__file__).resolve().parent
def run(*args): subprocess.check_call([sys.executable,*map(str,args)],cwd=R)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--historical-csv',default=''); ap.add_argument('--year',type=int,default=2026); ap.add_argument('--years',default='',help='comma-separated years, e.g. 2024,2025,2026'); ap.add_argument('--fetch',action='store_true'); ap.add_argument('--limit',type=int,default=0); ap.add_argument('--result-urls',default=''); ap.add_argument('--base-url',default=''); a=ap.parse_args()
    years=[int(x) for x in a.years.split(',') if x.strip()] or [a.year]
    if a.fetch:
        for year in years: run('fetch_jra_pdfs.py','--year',year,'--limit',a.limit)
    pdfs=sorted((R/'data/jra_pdf').glob('*.pdf'))
    if a.historical_csv:
        run('import_historical_dataset.py',a.historical_csv,'--out','runners.csv')
        run('import_csv.py'); run('validate_data.py'); run('build_site_data.py'); run('generate_db_race_pages.py'); run('generate_sitemap.py')
        return
    if not pdfs: raise SystemExit('No PDFs in data/jra_pdf/. Run: python update_site.py --fetch')
    run('jra_pdf_adapter.py',*pdfs); run('import_csv.py');
    if a.result_urls: run('jra_result_adapter.py',a.result_urls)
    run('validate_data.py'); run('build_site_data.py'); run('generate_db_race_pages.py')
    if a.base_url: run('build_sitemap.py','--base-url',a.base_url)
    print(f'DONE: {len(pdfs)} PDFs processed. Open index.html')
if __name__=='__main__': main()
