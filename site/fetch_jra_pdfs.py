#!/usr/bin/env python3
"""Discover and download JRA annual-result PDFs from the official annual results page.
Only public PDF links found on the requested JRA page are followed. Existing files are skipped.
"""
from __future__ import annotations
import argparse, re, time
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

BASE='https://www.jra.go.jp'
UA='KEIBA-DATA-LAB/0.12 (+local research prototype; respectful sequential fetch)'

def discover(year:int):
    url=f'{BASE}/datafile/seiseki/report/{year}.html'
    r=requests.get(url,headers={'User-Agent':UA},timeout=30); r.raise_for_status()
    if not r.encoding or r.encoding.lower() in ('iso-8859-1','ascii'):
        r.encoding=r.apparent_encoding
    soup=BeautifulSoup(r.text,'html.parser')
    found=[]; seen=set()
    # Source of truth is the links JRA actually publishes. Do not guess filename structure.
    for a in soup.find_all('a',href=True):
        raw=a['href']; href=urljoin(url,raw)
        name=href.rsplit('/',1)[-1].split('?',1)[0].split('#',1)[0]
        label=' '.join(a.stripped_strings)
        if not name.lower().endswith('.pdf'): continue
        if f'/datafile/seiseki/report/{year}/' not in href: continue
        if '発売票数' in label or '票数' in label: continue
        if name in seen: continue
        seen.add(name); found.append((href,name,label))
    return url,found

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--year',type=int,default=2026)
    ap.add_argument('--out',default='data/jra_pdf')
    ap.add_argument('--limit',type=int,default=0,help='0 = all discovered result PDFs')
    ap.add_argument('--delay',type=float,default=1.0,help='seconds between downloads')
    ap.add_argument('--dry-run',action='store_true')
    a=ap.parse_args(); out=Path(__file__).resolve().parent/a.out; out.mkdir(parents=True,exist_ok=True)
    index,items=discover(a.year)
    if a.limit: items=items[:a.limit]
    print(f'Official index: {index}\nDiscovered {len(items)} result PDFs')
    if not items:
        raise RuntimeError(f'No JRA result PDFs discovered for {a.year}; official index layout may have changed: {index}')
    for i,(url,name,label) in enumerate(items,1):
        dst=out/name
        if dst.exists() and dst.stat().st_size>10000:
            print(f'[{i}/{len(items)}] skip {name}'); continue
        print(f'[{i}/{len(items)}] {name} {label}')
        if a.dry_run: continue
        rr=requests.get(url,headers={'User-Agent':UA},timeout=60); rr.raise_for_status()
        if 'pdf' not in rr.headers.get('content-type','').lower() and not rr.content.startswith(b'%PDF'):
            raise RuntimeError(f'Not a PDF: {url}')
        dst.write_bytes(rr.content)
        if i<len(items): time.sleep(max(0,a.delay))
if __name__=='__main__': main()
,href,re.I): continue
        # Exclude sales-ticket PDFs; keep result PDFs only. JRA result filenames normally include a track name.
        name=href.rsplit('/',1)[-1]
        if name in seen: continue
        text=' '.join(a.stripped_strings)
        if '発売票数' in text or 'hyo' in name.lower(): continue
        seen.add(name); found.append((href,name,text))
    return url,found

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--year',type=int,default=2026)
    ap.add_argument('--out',default='data/jra_pdf')
    ap.add_argument('--limit',type=int,default=0,help='0 = all discovered result PDFs')
    ap.add_argument('--delay',type=float,default=1.0,help='seconds between downloads')
    ap.add_argument('--dry-run',action='store_true')
    a=ap.parse_args(); out=Path(__file__).resolve().parent/a.out; out.mkdir(parents=True,exist_ok=True)
    index,items=discover(a.year)
    if a.limit: items=items[:a.limit]
    print(f'Official index: {index}\nDiscovered {len(items)} result PDFs')
    for i,(url,name,label) in enumerate(items,1):
        dst=out/name
        if dst.exists() and dst.stat().st_size>10000:
            print(f'[{i}/{len(items)}] skip {name}'); continue
        print(f'[{i}/{len(items)}] {name} {label}')
        if a.dry_run: continue
        rr=requests.get(url,headers={'User-Agent':UA},timeout=60); rr.raise_for_status()
        if 'pdf' not in rr.headers.get('content-type','').lower() and not rr.content.startswith(b'%PDF'):
            raise RuntimeError(f'Not a PDF: {url}')
        dst.write_bytes(rr.content)
        if i<len(items): time.sleep(max(0,a.delay))
if __name__=='__main__': main()
