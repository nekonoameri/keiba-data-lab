#!/usr/bin/env python3
"""Download JRA annual result PDFs from the official annual-results index.
Usage: python fetch_jra_reports.py --year 2026 --limit 2
Respect the source site's terms and use a conservative delay.
"""
from __future__ import annotations
import argparse, time, re
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

BASE='https://www.jra.go.jp'

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--year',type=int,default=2026)
    ap.add_argument('--out',default='data/jra_pdf')
    ap.add_argument('--limit',type=int,default=0,help='0 = all result PDFs found')
    ap.add_argument('--delay',type=float,default=1.5)
    args=ap.parse_args()
    out=Path(__file__).resolve().parent/args.out; out.mkdir(parents=True,exist_ok=True)
    index=f'{BASE}/datafile/seiseki/report/{args.year}.html'
    s=requests.Session(); s.headers.update({'User-Agent':'Mozilla/5.0 (compatible; KeibaDataResearch/0.1)'})
    r=s.get(index,timeout=30); r.raise_for_status()
    soup=BeautifulSoup(r.text,'html.parser')
    links=[]
    for a in soup.find_all('a',href=True):
        href=a['href']
        # Exclude sales-volume PDFs; result files conventionally contain venue names, not "hyo" sales files.
        if href.lower().endswith('.pdf') and f'/report/{args.year}/' in urljoin(index,href):
            label=' '.join(a.stripped_strings)
            if '発売票数' in label: continue
            url=urljoin(index,href)
            if url not in links: links.append(url)
    if args.limit: links=links[:args.limit]
    print(f'Found {len(links)} result PDFs')
    for i,url in enumerate(links,1):
        name=re.sub(r'[^A-Za-z0-9._-]','_',url.rsplit('/',1)[-1])
        dest=out/name
        if dest.exists() and dest.stat().st_size>1000:
            print(f'[{i}/{len(links)}] exists {name}'); continue
        rr=s.get(url,timeout=60); rr.raise_for_status(); dest.write_bytes(rr.content)
        print(f'[{i}/{len(links)}] saved {name} ({len(rr.content):,} bytes)')
        time.sleep(args.delay)
if __name__=='__main__': main()
