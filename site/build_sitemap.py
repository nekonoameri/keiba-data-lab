#!/usr/bin/env python3
from pathlib import Path
from urllib.parse import quote
import argparse, html
ROOT=Path(__file__).resolve().parent
EXCLUDE={'README.md'}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--base-url',required=True,help='e.g. https://example.jp'); a=ap.parse_args(); base=a.base_url.rstrip('/')
    files=sorted(p for p in ROOT.rglob('*.html') if '.git' not in p.parts)
    urls=[]
    for p in files:
        rel=p.relative_to(ROOT).as_posix(); loc=base+'/' if rel=='index.html' else base+'/'+quote(rel)
        urls.append(f'  <url><loc>{html.escape(loc)}</loc></url>')
    xml='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+'\n'.join(urls)+'\n</urlset>\n'
    (ROOT/'sitemap.xml').write_text(xml,encoding='utf-8'); (ROOT/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n',encoding='utf-8')
    print(f'wrote sitemap.xml with {len(urls)} URLs + robots.txt')
if __name__=='__main__': main()
