#!/usr/bin/env python3
"""JRA annual-results PDF -> normalized race/runner CSV.
Runner popularity is left blank unless an official popularity value is explicitly verified; odds are never converted into an asserted official popularity rank.
Designed so the acquisition source can later be swapped without changing DB/UI.
"""
from __future__ import annotations
import argparse,csv,re,sys
from pathlib import Path
from pypdf import PdfReader
try:
    import pymupdf
except ImportError:
    pymupdf=None
TRACKS='札幌|函館|福島|新潟|東京|中山|中京|京都|阪神|小倉'
FW=str.maketrans('０１２３４５６７８９，．：','0123456789,.:' )
def norm(s): return s.translate(FW).replace('\u3000',' ').replace('，',',').replace('．','.').replace('：',':')
def _text_score(s):
    if not s: return -1
    tokens=('競走','発走','中山','東京','阪神','京都','中京','札幌','函館','福島','新潟','小倉','3連単')
    return sum(s.count(t) for t in tokens) + 20*len(re.findall(r'第\s*(?:1[0-2]|[1-9])\s*競走',s))

def pdf_text(path):
    """Try independent PDF engines and keep the extraction that best matches JRA race text."""
    candidates=[]
    try:
        pages=[]
        for p in PdfReader(str(path)).pages:
            try: pages.append(p.extract_text(extraction_mode='layout') or '')
            except Exception: pages.append(p.extract_text() or '')
        candidates.append(('pypdf-layout','\\n'.join(pages)))
    except Exception as e:
        print(f'WARN pypdf {path}: {e}',file=sys.stderr)
    if pymupdf is not None:
        try:
            with pymupdf.open(str(path)) as doc:
                candidates.append(('pymupdf','\\n'.join(page.get_text('text',sort=True) or '' for page in doc)))
        except Exception as e:
            print(f'WARN pymupdf {path}: {e}',file=sys.stderr)
    if not candidates: return ''
    engine,text=max(candidates,key=lambda x:_text_score(norm(x[1])))
    score=_text_score(norm(text))
    print(f'PDF_EXTRACT {Path(path).name}: engine={engine} score={score}',file=sys.stderr)
    return text

def race_chunks(text,path=None):
    # Annual PDFs often omit the Gregorian year and/or venue from repeated page
    # headers. Recover those two stable fields from the official PDF filename.
    fallback_year=''
    fallback_track=''
    if path is not None:
        fn=Path(path).name.lower()
        ym=re.match(r'(20\d{2})-',fn)
        if ym: fallback_year=ym.group(1)
        track_map={'sapporo':'札幌','hakodate':'函館','fukushima':'福島','niigata':'新潟','tokyo':'東京','nakayama':'中山','chukyo':'中京','kyoto':'京都','hanshin':'阪神','kokura':'小倉'}
        fallback_track=next((jp for en,jp in track_map.items() if en in fn),'')
    race_pat=re.compile(r'(?:第\s*)?(?P<r>1[0-2]|[1-9])\s*(?:競走|レース|Ｒ|R|race)(?![A-Za-z0-9])',re.I)
    ms=list(race_pat.finditer(text))
    if not ms:
        # Last-resort layout: JRA result PDFs can extract the race number as a
        # standalone digit immediately before the start-time/header block.
        alt=re.compile(r'(?m)^\s*(?P<r>1[0-2]|[1-9])\s*$')
        ms=[m for m in alt.finditer(text) if re.search(r'発走|芝|ダート|障害',text[m.end():m.end()+500])]
    if not ms:
        sample=re.sub(r'\s+',' ',text[:1200])
        print(f'WARN no race anchors; sample={sample[:1000]}',file=sys.stderr)
    for i,m in enumerate(ms):
        left=text[max(0,m.start()-1800):m.start()]
        dm=list(re.finditer(r'(?P<m>\d{1,2})月(?P<d>\d{1,2})日',left))
        ym=list(re.finditer(r'(?P<year>20\d{2})年',left))
        tm=list(re.finditer(r'(?P<track>'+TRACKS+r')',left))
        if not dm:
            # Some annual-result PDFs suppress the date around individual race
            # anchors. Use the first date found in the document/page context.
            all_dm=list(re.finditer(r'(?P<m>\d{1,2})月(?P<d>\d{1,2})日',text))
            if not all_dm: continue
            dm=all_dm
        year=ym[-1].group('year') if ym else fallback_year
        track=tm[-1].group('track') if tm else fallback_track
        if not (year and track): continue
        d=dm[-1]
        meta={'m':d.group('m'),'d':d.group('d'),'year':year,'track':track,'r':m.group('r')}
        class Match:
            def group(self,k): return meta[k]
        end=ms[i+1].start() if i+1<len(ms) else len(text)
        yield Match(),text[m.start():end]

def parse_runners(chunk,race_id):
    # Result rows occur before （N頭）. PDF extraction can wrap owner/breeder text, so only parse lines
    # that visibly start with frame + horse number; row order itself is official finish order.
    body=chunk.split('（',1)[0] if False else chunk
    cutoff=re.search(r'（\d+頭）',chunk)
    body=chunk[:cutoff.start()] if cutoff else chunk
    lines=[re.sub(r'\s+',' ',x).strip() for x in body.splitlines()]
    rows=[]
    start=re.compile(r'^(?P<frame>[1-8])\s*(?P<horse>1[0-8]|[1-9])(?:[^\w一-龥ァ-ヶA-Za-z]+)?\s*(?P<name>[ァ-ヶ一-龥A-Za-z0-9ー・\.]+)\s+')
    for ln in lines:
        m=start.match(ln)
        if not m: continue
        # Avoid headers and require an odds-looking decimal near line end.
        odds_all=re.findall(r'(?<!\d)(\d{1,3}\.\d)(?!\d)',ln)
        if not odds_all: continue
        odds=float(odds_all[-1])
        # Jockey is normally immediately after assigned weight (55/57/58/60 etc.), optional apprentice weight line.
        tail=ln[m.end():]
        jm=re.search(r'\b(?:4[89]|5\d|60)(?:\s+\d{2})?\s+(?:[▲△◇]\s*)?(?P<j>[一-龥ァ-ヶA-Za-zＭ．M\.]+(?:\s*[一-龥ァ-ヶA-Za-z]+){0,2})\s+',tail)
        jockey=(jm.group('j').strip() if jm else '')
        # Guard against PDF column-merging: a jockey label must stay compact. If extraction glues adjacent owner/trainer text, leave it blank for later enrichment from official HTML rather than corrupting the DB.
        compact_jockey=re.sub(r'[\\s　]+','',jockey)
        if len(compact_jockey)>8 or len(compact_jockey)<2:
            jockey=''
        # Time appears as M:SS.d; non-finishers get blank.
        tm=re.search(r'(\d:\d{2}\.\d)',ln)
        rows.append(dict(race_id=race_id,finish=len(rows)+1,frame_no=int(m.group('frame')),horse_no=int(m.group('horse')),
                         horse_name=m.group('name'),jockey=jockey,popularity='',odds=odds,finish_time=tm.group(1) if tm else '',last3f=''))
    # PDF text does not expose official popularity reliably for every runner.
    # Keep popularity blank rather than presenting an odds-derived rank as official data.
    return rows

def parse_file(path):
    text=norm(pdf_text(path)); races=[]; runners=[]
    if not text.strip(): raise ValueError(f'No extractable text in official JRA PDF: {path}')
    for m,chunk in race_chunks(text,path):
        track=m.group('track'); rn=int(m.group('r')); date=f'{int(m.group("year")):04d}-{int(m.group("m")):02d}-{int(m.group("d")):02d}'; rid=f'{date.replace("-","")}-{track}-{rn:02d}'
        sm=re.search(r'発走\s*\d+時\d+分\s*（(?P<s>芝|ダート)',chunk); surface=sm.group('s') if sm else ('障害' if '障害' in chunk[:500] else '')
        # Header distance immediately before 発走 is the safest candidate.
        pre=chunk[:chunk.find('発走') if '発走' in chunk else 600]
        ds=re.findall(r'([1234](?:,?\d{3}))[^\d]{0,5}$',pre,re.M); distance=int(ds[-1].replace(',','')) if ds else None
        st=re.search(r'（(\d+)頭）',chunk); tri=re.search(r'3連単[^\n]{0,100}?([\d,]+)円',chunk)
        gm=re.search(r'（\s*(?:芝|ダート)\s*）\s*(良|稍重|重|不良)',chunk[:500]); going=gm.group(1) if gm else ''
        name=''; nh=re.search(r'第\d+競走\s+(.{1,90}?)\s+[\W]*[1234](?:,?\d{3})',chunk[:700],re.S)
        if nh: name=' '.join(nh.group(1).split())
        races.append(dict(race_id=rid,race_date=date,track=track,race_no=rn,race_name=name,surface=surface,distance=distance or '',going=going,starters=int(st.group(1)) if st else '',trifecta_payout=int(tri.group(1).replace(',','')) if tri else '',source_url=''))
        runners.extend(parse_runners(chunk,rid))
    if not races:
        raise ValueError(f'No race anchors parsed from official JRA PDF: {path}')
    if len(races) < 10:
        raise ValueError(f'Only {len(races)} races parsed from {path}; refusing partial import')
    if not runners:
        raise ValueError(f'No runner rows parsed from official JRA PDF: {path}')
    return races,runners

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('pdfs',nargs='+'); ap.add_argument('--races',default='races.csv'); ap.add_argument('--runners',default='runners.csv'); a=ap.parse_args()
    races=[]; runners=[]
    for p in a.pdfs:
        try:
            r,u=parse_file(Path(p)); races+=r; runners+=u
        except Exception as e:
            print('ERROR',p,e,file=sys.stderr)
            raise
    root=Path(__file__).resolve().parent
    rf=['race_id','race_date','track','race_no','race_name','surface','distance','going','starters','trifecta_payout','source_url']
    uf=['race_id','finish','frame_no','horse_no','horse_name','jockey','popularity','odds','finish_time','last3f']
    for path,fields,rows in [(root/a.races,rf,races),(root/a.runners,uf,runners)]:
        with path.open('w',encoding='utf-8-sig',newline='') as f: w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    print(f'Wrote {len(races)} races / {len(runners)} runners')
if __name__=='__main__': main()
