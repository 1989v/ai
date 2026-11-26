#!/usr/bin/env python3
"""Render only locally minimized, reviewed evidence. Python standard library only."""
import argparse
import datetime as dt
import html
import os
import tempfile
import json
import math
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

LIMIT = 2_000_000
PATTERNS = [r'(?i)\b(?:sk-[a-z0-9_-]{16,}|gh[pousr]_[a-z0-9_]{20,}|AKIA[A-Z0-9]{16})\b', r'-----BEGIN [A-Z ]*PRIVATE KEY-----', r'(?i)\b(?:password|api[_-]?key|access[_-]?token|authorization)\s*[:=]', r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', r'\b(?:\d{1,3}\.){3}\d{1,3}\b', r'\b\d{6}[- ]?[1-4]\d{6}\b', r'\b\d{3}[- ]\d{3,4}[- ]\d{4}\b', r'(?i)(?:/Users/|/home/|file://|localhost|\.internal\b)', r'\beyJ[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b']
class Invalid(ValueError): pass
class SafeParser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, 'ERROR: invalid command arguments; use --help. Private values are not echoed.\n')

def safe_write(outputs, texts):
    """Stage every complete file, then publish without replacing any destination.

    A multi-file operation cannot be fully crash-atomic across directories. Each
    destination is complete or absent; ordinary failures roll back new outputs.
    """
    staged=[]; published=[]
    try:
        for output,text in zip(outputs,texts):
            fd,name=tempfile.mkstemp(prefix='.work-evidence-',suffix='.tmp',dir=output.parent)
            staged.append(Path(name))
            with os.fdopen(fd,'w',encoding='utf-8') as stream:
                stream.write(text); stream.flush(); os.fsync(stream.fileno())
        for source,output in zip(staged,outputs):
            os.link(source,output)  # Atomic complete file, exclusive no-overwrite.
            published.append(output)
    except BaseException:
        for output in published:
            try: output.unlink()
            except OSError: pass
        raise
    finally:
        for path in staged:
            try: path.unlink()
            except OSError: pass


def require(ok, msg):
    if not ok: raise Invalid(msg)
def obj(x, required, optional=()):
    require(isinstance(x, dict), 'Expected object')
    require(set(required) <= set(x) and set(x) <= set(required)|set(optional), 'Missing or unknown fields')
def string(x):
    require(isinstance(x,str) and 0 < len(x) <= 2400 and not any(ord(c)<32 and c not in '\n\t' for c in x), 'Invalid text')
    require(not re.search(r'https?://|www\.',x,re.I), 'URLs permitted only in reviewed public_url')
    scan(x)
    return x
def strings(x):
    require(isinstance(x,list) and len(x)<=200, 'Expected bounded list')
    for v in x: string(v)
def date(x):
    require(isinstance(x,str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}',x), 'Expected ISO date')
    try: return dt.date.fromisoformat(x)
    except ValueError: raise Invalid('Invalid date') from None
def scan(text):
    require(not any(re.search(p,text) for p in PATTERNS), 'Potential private/secret content: minimize and review locally')
def validate(d, mode):
    obj(d,['schema_version','mode','title','summary','audience','context','question','period','approval','scope','items','diagram'],['handoff','public_reference_hosts'])
    require(type(d['schema_version']) is int and d['schema_version']==1 and d['mode']==mode,'Schema version or mode mismatch')
    require(d['audience'] in ['business','technical','general'] and d['context'] in ['company','personal'],'Invalid audience/context')
    for k in ['title','summary','question']: string(d[k])
    obj(d['approval'],['collection_confirmed','wording_reviewed','quantities_reviewed'])
    require(all(v is True for v in d['approval'].values()),'Explicit scope confirmation and sanitized wording/quantity review required')
    p=d['period']; obj(p,['start','end','timezone']); require(date(p['start'])<=date(p['end']),'Reversed period')
    string(p['timezone'])
    try: ZoneInfo(p['timezone'])
    except (ZoneInfoNotFoundError,ValueError): raise Invalid('Unknown IANA timezone') from None
    obj(d['scope'],['sources','roles']); strings(d['scope']['sources']); strings(d['scope']['roles'])
    hosts=d.get('public_reference_hosts',[]); strings(hosts)
    for host in hosts:
        require(bool(re.fullmatch(r'(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}',host)) and not host.endswith(('.local','.internal','.localhost','.test','.invalid','.example')), 'Invalid public hostname')
    require(isinstance(d['items'],list) and len(d['items'])<=500,'Too many evidence items')
    ids=set()
    for item in d['items']:
        obj(item,['id','kind','title','date','status','summary','owner_role','evidence'],['end_date','outcome','metric'])
        require(re.fullmatch(r'E[1-9][0-9]{0,4}',item['id']) is not None and item['id'] not in ids,'Use unique neutral E1 evidence aliases'); ids.add(item['id'])
        require(item['kind'] in ['ticket','commit','wiki','metric'] and item['status'] in ['new','ongoing','done'],'Invalid kind/status')
        for k in ['title','summary','owner_role']: string(item[k])
        require(item['owner_role'] in d['scope']['roles'],'Owner role outside reviewed scope')
        start=date(item['date']); end=date(item.get('end_date',p['end']))
        require(start<=end and start<=date(p['end']),'Invalid evidence dates')
        require((item['status']=='done') == ('end_date' in item),'Confirmed completion requires done status and end_date together')
        require(end>=date(p['start']),'Evidence does not overlap the report period')
        e=item['evidence']; obj(e,['source_alias','locator','observed_at','detail'],['public_url'])
        for k in ['source_alias','locator','detail']: string(e[k])
        require(e['source_alias'] in d['scope']['sources'],'Source outside reviewed scope')
        require(re.fullmatch(r'(?:ref|change|ticket|page|sample|revision)-[1-9][0-9]{0,5}',e['locator']) is not None,'Locator must be neutral alias, not private key/hash/page ID')
        date(e['observed_at'])
        if 'public_url' in e:
            u=e['public_url']; require(isinstance(u,str) and len(u)<=1000,'Invalid public reference')
            v=urlsplit(u)
            require(v.scheme=='https' and v.hostname in hosts and not any([v.username,v.password,v.query,v.fragment,v.port]) and not re.search(r'[<>"\s%\\]',u),'Public URL requires reviewed public host, clean HTTPS path')
            scan(u)
        if 'outcome' in item: string(item['outcome'])
        if 'metric' in item:
            m=item['metric']; obj(m,['label','before','after','unit','baseline','measurement'])
            for k in ['label','unit','baseline','measurement']: string(m[k])
            for k in ['before','after']: require(type(m[k]) in [float,int] and math.isfinite(m[k]),'Finite numeric measurement required')
    g=d['diagram']; obj(g,['nodes','edges','caption']); string(g['caption'])
    require(isinstance(g['nodes'],list) and 1<=len(g['nodes'])<=20 and isinstance(g['edges'],list) and len(g['edges'])<=40,'Invalid diagram size')
    nodes=set()
    for n in g['nodes']:
        obj(n,['id','label'],['evidence_ids']); string(n['label']); require(isinstance(n['id'],str) and re.fullmatch(r'N[1-9][0-9]?',n['id']) and n['id'] not in nodes,'Unique neutral node aliases required'); nodes.add(n['id'])
        refs(n.get('evidence_ids',[]),ids)
    for e in g['edges']:
        obj(e,['from','to','label']); require(e['from'] in nodes and e['to'] in nodes,'Unknown diagram node'); string(e['label'])
    if mode=='handoff':
        require('handoff' in d,'Handoff sections required'); h=d['handoff']; obj(h,['context','known_state','decisions','unresolved','next_verification']); string(h['context']); strings(h['known_state'])
        for section in ['decisions','unresolved','next_verification']:
            require(isinstance(h[section],list) and len(h[section])<=100,'Invalid handoff section')
            for row in h[section]:
                obj(row,['text','evidence_ids'],['owner_role'] if section=='decisions' else []) if section=='decisions' else obj(row,['text','evidence_ids','owner_role'])
                string(row['text']); refs(row['evidence_ids'],ids)
                if 'owner_role' in row: require(row['owner_role'] in d['scope']['roles'],'Unknown owner role')
    else: require('handoff' not in d,'Timeline cannot contain handoff sections')
    # Explicit safe projection. Unknown fields rejected at every object boundary.
    return json.loads(json.dumps(d,allow_nan=False))
def refs(values,ids):
    require(isinstance(values,list) and all(type(v)==str and v in ids for v in values),'Unknown evidence reference')
def esc(v): return html.escape(str(v),quote=True)
def card(i):
    e=i['evidence']; metric=i.get('metric'); url=''
    if 'public_url' in e: url='<a rel="noreferrer noopener" href="'+esc(e['public_url'])+'">검토한 공개 자료</a>'
    m='' if not metric else '<p class="metric"><strong>'+esc(metric['label'])+': '+esc(metric['before'])+' → '+esc(metric['after'])+' '+esc(metric['unit'])+'</strong><br>기준: '+esc(metric['baseline'])+'<br>측정 방법: '+esc(metric['measurement'])+'</p>'
    return '<article class="item" id="'+esc(i['id'])+'" data-start="'+esc(i['date'])+'" data-end="'+esc(i.get('end_date',''))+'" data-status="'+esc(i['status'])+'"><p class="eyebrow">'+esc(i['id'])+' · '+esc({'ticket':'이슈','commit':'변경','wiki':'위키','metric':'지표'}[i['kind']])+' · '+esc(i['date'])+' → '+esc(i.get('end_date','진행 중'))+'</p><h3>'+esc(i['title'])+'</h3><p>'+esc(i['summary'])+'</p>'+('<p><b>결과:</b> '+esc(i['outcome'])+'</p>' if 'outcome' in i else '')+m+'<details><summary>근거 상세 · '+esc(i['owner_role'])+'</summary><p>'+esc(e['source_alias'])+' / '+esc(e['locator'])+' · 확인일 '+esc(e['observed_at'])+'</p><p>'+esc(e['detail'])+'</p>'+url+'</details></article>'
def diagram(d):
    nodes=d['diagram']['nodes']; edges=d['diagram']['edges']; byid={n['id']:n for n in nodes}
    levels={}; pending=set(byid)
    # Layer acyclic dependencies; remaining cyclic nodes occupy separate rows.
    while pending:
        ready=[n['id'] for n in nodes if n['id'] in pending and all(e['from'] in levels for e in edges if e['to']==n['id'])]
        if not ready:
            for key in sorted(pending): levels[key]=max(levels.values(),default=-1)+1
            break
        for key in ready:
            levels[key]=max((levels[e['from']]+1 for e in edges if e['to']==key),default=0); pending.remove(key)
    rows={}
    for n in nodes: rows.setdefault(levels[n['id']],[]).append(n)
    width=1000; height=(max(rows)+1)*170+40; points={}
    for level,row in rows.items():
        for index,n in enumerate(row): points[n['id']]=(width*(index+1)/(len(row)+1),level*170+55,min(270,860/len(row)))
    svg=['<svg class="flow" viewBox="0 0 '+format(width,'.1f')+' '+format(height,'.1f')+'" role="img" aria-labelledby="diagram-title diagram-desc"><title id="diagram-title">'+esc(d['title'])+'</title><desc id="diagram-desc">'+esc(d['diagram']['caption'])+' 관계의 텍스트 설명이 그림 다음에 있습니다.</desc><defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#426256"/></marker></defs>']
    for e in edges:
        x1,y1,_=points[e['from']]; x2,y2,_=points[e['to']]; y1+=36; y2-=36; mid=(y1+y2)/2
        if y2>y1: path=f'M{x1:.1f} {y1:.1f} C{x1:.1f} {mid:.1f} {x2:.1f} {mid:.1f} {x2:.1f} {y2:.1f}'
        else: path=f'M{x1:.1f} {y1:.1f} C{x1+100:.1f} {y1+90:.1f} {x2+100:.1f} {y2-90:.1f} {x2:.1f} {y2:.1f}'
        svg.append('<path d="'+path+'" fill="none" stroke="#426256" stroke-width="2" marker-end="url(#arrow)"/>')
        label=e['label']; lines=[label[i:i+22] for i in range(0,len(label),22)]
        xx=(x1+x2)/2; yy=mid-7*(len(lines)-1)
        svg.append('<rect x="'+format(xx-140,'.1f')+'" y="'+format(yy-15,'.1f')+'" width="280" height="'+format(22*len(lines),'.1f')+'" rx="4" fill="#f2f3ef"/>')
        for j,line in enumerate(lines): svg.append('<text x="'+format(xx,'.1f')+'" y="'+format(yy+22*j,'.1f')+'" text-anchor="middle" fill="#294c3c" font-size="17">'+esc(line)+'</text>')
    for n in nodes:
        x,y,w=points[n['id']]; label=n['label']; chunks=[label[i:i+18] for i in range(0,len(label),18)]
        # Long labels stay in the accessible text; the diagram keeps a readable synopsis.
        lines=chunks[:2]
        if len(chunks)>2: lines[-1]=lines[-1][:-1]+'…'
        svg.append('<g class="node" data-evidence="'+esc(' '.join(n.get('evidence_ids',[])))+'"><title>'+esc(label)+'</title><rect x="'+format(x-w/2,'.1f')+'" y="'+format(y-36,'.1f')+'" width="'+format(w,'.1f')+'" height="72" rx="7" fill="#163c32"/>')
        for j,line in enumerate(lines): svg.append('<text x="'+format(x,'.1f')+'" y="'+format(y+7+(j-(len(lines)-1)/2)*24,'.1f')+'" text-anchor="middle" fill="white" font-size="20">'+esc(line)+'</text>')
        svg.append('</g>')
    svg.append('</svg>')
    equivalent='<details class="diagram-text"><summary>그림의 관계를 텍스트로 읽기</summary><ul>'+''.join('<li>'+esc(n['label'])+'</li>' for n in nodes)+''.join('<li>'+esc(byid[e['from']]['label'])+' → '+esc(e['label'])+' → '+esc(byid[e['to']]['label'])+'</li>' for e in edges)+'</ul></details>'
    mobile=[]
    for e in edges:
        lane=[]
        for key in [e['from'],e['to']]:
            n=byid[key]; lane.append('<div class="node mobile-node" data-evidence="'+esc(' '.join(n.get('evidence_ids',[])))+'">'+esc(n['label'])+'</div>')
        mobile.append('<div class="mobile-edge">'+lane[0]+'<p class="mobile-arrow">↓ '+esc(e['label'])+'</p>'+lane[1]+'</div>')
    linked={e[k] for e in edges for k in ['from','to']}
    for n in nodes:
        if n['id'] not in linked: mobile.append('<div class="node mobile-node" data-evidence="'+esc(' '.join(n.get('evidence_ids',[])))+'">'+esc(n['label'])+'</div>')
    return '<figure><div class="diagram">'+''.join(svg)+'<div class="mobile-diagram">'+''.join(mobile)+'</div>'+'</div><figcaption>'+esc(d['diagram']['caption'])+'</figcaption><p class="muted">필터에 근거가 없으면 해당 노드가 흐려집니다. 연결선과 근거 미지정 노드는 전체 기간의 맥락입니다.</p>'+equivalent+'</figure>'
CSS='''*{box-sizing:border-box}body{margin:0;background:#f2f3ef;color:#182722;font:17px/1.55 system-ui,sans-serif}main{max-width:1100px;margin:auto;padding:48px 28px}h1{font-size:clamp(2.2rem,5vw,4rem);line-height:1.06;letter-spacing:-.05em;margin:.3em 0}h2{font-size:1.6rem;margin-top:2em}h3{margin:.2em 0}.eyebrow{font-size:.78rem;text-transform:uppercase;letter-spacing:.09em;color:#426256}.intro{max-width:780px;font-size:1.2rem}.muted,figcaption{font-size:.86rem;color:#4a6156}.diagram{width:100%}.mobile-diagram{display:none}.mobile-node{overflow-wrap:anywhere}.mobile-arrow{margin:8px 0;text-align:center;color:#294c3c;overflow-wrap:anywhere}.mobile-edge{padding:12px;border:1px solid #a7b6ad;border-radius:8px}.flow{display:block;width:100%;min-width:620px;height:auto;font-family:system-ui,sans-serif}.node{flex:1 1 200px;background:#163c32;color:white;padding:22px;border-radius:8px}.relation{font-size:.88rem;border-top:1px solid #71968a;padding-top:10px}.dim{opacity:.35}figure{margin:28px 0}figcaption{margin-top:12px}form{display:flex;gap:18px;flex-wrap:wrap;padding:18px 0}label{display:flex;flex-direction:column;font-size:.88rem}input,select,button{font:inherit;padding:9px;border:1px solid #a7b6ad;border-radius:4px;background:white}.item,.handoff-row{background:white;border:1px solid #cfdbd1;padding:22px;margin:14px 0;border-radius:6px}.metric{padding:14px;border-left:4px solid #467d59;background:#eff7ed}a{color:#245e42}summary{cursor:pointer;font-size:.9rem}.items{border-left:2px solid #769b83;padding-left:20px}[hidden]{display:none!important}:focus-visible{outline:3px solid #b66823;outline-offset:3px}@media(max-width:650px){main{padding:24px 18px}.diagram .flow{display:none}.mobile-diagram{display:grid;gap:16px}.mobile-node{padding:14px;border-radius:5px}.items{padding-left:12px}.item,.handoff-row{padding:16px}form{gap:10px}}@media print{body{background:white;font-size:11pt}main{padding:0}form,.interactive-only{display:none}details>*{display:block}article,.handoff-row,figure{break-inside:avoid}.node{color:black;background:white;border:1px solid black}.dim{opacity:1}a{color:black}}'''
JS='''const f=document.querySelector('form'),items=[...document.querySelectorAll('.item')],reportEnd=f.dataset.end;function update(){const start=f.elements.start.value,end=f.elements.end.value,status=f.elements.status.value;if(!start||!end||start>end){document.querySelector('#count').textContent='시작일과 종료일을 확인해 주세요.';return}let visible=new Set();items.forEach(i=>{let a=i.dataset.start,b=i.dataset.end||reportEnd,overlap=a<=end&&b>=start;let pass=status==='all'||status==='new'&&a>=start&&a<=end||status==='ongoing'&&a<start&&b>=start||status==='done'&&i.dataset.status==='done';i.hidden=!(overlap&&pass);if(!i.hidden)visible.add(i.id)});document.querySelector('#count').textContent=visible.size+'개 근거가 선택되었습니다. 지표는 해당 근거와 함께 바뀌며 기준 조건은 전체 보고서에 유지됩니다.';document.querySelectorAll('.node').forEach(n=>{const ids=n.dataset.evidence.split(' ').filter(Boolean);n.classList.toggle('dim',ids.length>0&&!ids.some(id=>visible.has(id)))});document.querySelectorAll('.availability').forEach(s=>{const ids=s.dataset.ids.split(' ').filter(Boolean);s.textContent=ids.length?ids.filter(id=>visible.has(id)).length+'/'+ids.length+'개 근거가 현재 필터에 포함됨':'기록된 근거 없음'})}f.addEventListener('input',update);update();'''
def render(d, printable=False):
    p=d['period']; title=esc(d['title']); mode=d['mode']; form=''
    if not printable:
        form='<form data-end="'+esc(p['end'])+'"><label>시작일 (포함)<input type="date" name="start" value="'+esc(p['start'])+'" min="'+esc(p['start'])+'" max="'+esc(p['end'])+'"></label><label>종료일 (포함)<input type="date" name="end" value="'+esc(p['end'])+'" min="'+esc(p['start'])+'" max="'+esc(p['end'])+'"></label><label>근거 필터<select name="status"><option value="all">기간에 걸친 전체</option><option value="new">기간 내 새로 시작</option><option value="ongoing">기간 이전부터 진행</option><option value="done">기간에 걸친 완료 항목</option></select></label></form><p id="count" role="status"></p><p class="muted">새 작업은 기간 내 시작한 항목, 진행 중은 시작일 이전부터 이어진 항목, 완료는 기간과 겹치며 완료가 확인된 항목입니다. 미완료 항목은 보고서 종료일까지로 계산합니다. 날짜 기준: '+esc(p['timezone'])+'.</p>'
    handoff=''
    if mode=='handoff':
        h=d['handoff']; handoff='<section><h2>맥락과 확인된 상태</h2><p>'+esc(h['context'])+'</p><ul>'+''.join('<li>'+esc(s)+'</li>' for s in h['known_state'])+'</ul>'
        for k,label in [('decisions','결정 사항'),('unresolved','미해결 작업'),('next_verification','다음 검증')]:
            handoff+='<h2>'+label+'</h2>'
            if not h[k]: handoff+='<p>검토된 항목이 없습니다.</p>'
            for row in h[k]:
                handoff+='<div class="handoff-row"><p>'+esc(row['text'])+'</p>'+('<p>담당 역할: '+esc(row['owner_role'])+'</p>' if 'owner_role' in row else '')+'<p>'+''.join('<a href="#'+esc(i)+'">'+esc(i)+'</a> ' for i in row['evidence_ids'])+'</p><small class="availability" data-ids="'+esc(' '.join(row['evidence_ids']))+'">'+('관련 근거는 아래에 있습니다.' if row['evidence_ids'] else '기록된 근거가 없습니다.')+'</small></div>'
        handoff+='</section>'
    csp="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src 'none'; connect-src 'none'; font-src 'none'; base-uri 'none'; form-action 'none'"
    return '<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="'+csp+'"><title>'+title+'</title><style>'+CSS+'</style></head><body><main><p class="eyebrow">'+esc({'timeline':'작업 타임라인','handoff':'인수인계'}[mode])+' · '+esc({'technical':'기술 동료','business':'의사결정자','general':'일반 독자'}[d['audience']])+' 대상 · '+esc(p['start'])+' — '+esc(p['end'])+'</p><h1>'+title+'</h1><p class="intro">'+esc(d['summary'])+'</p><p>'+esc(d['question'])+'</p>'+diagram(d)+form+handoff+'<h2>'+('작업 타임라인' if mode=='timeline' else '근거와 결과')+'</h2><div class="items">'+''.join(card(i) for i in sorted(d['items'],key=lambda i:(i['date'],i['id'])))+'</div><footer><p class="muted">검토하고 최소화한 근거만 포함합니다. 확인할 수 없는 자료는 추정하지 않았습니다. 패턴 검사는 익명화를 보장하지 않습니다. 지표는 명시된 측정 방법과 기준을 유지하며 인과관계를 뜻하지 않습니다.</p></footer></main>'+('' if printable else '<script>'+JS+'</script>')+'</body></html>'
def check(output):
    scan(output)
    require('<!doctype html>' in output and 'Content-Security-Policy' in output,'Missing document safety policy')
    require(not re.search(r'(?i)(?:src\s*=|@import|url\s*\((?!#arrow\))|<iframe|<object|<embed|<!--)',output),'Unexpected embedded resource or hidden comment')
    # Only reviewed external references and internal fragment anchors may occur.
    for link in re.findall(r'href="([^"]*)"',output): require(link.startswith('#E') or link.startswith('https://'),'Unexpected link scheme')
def load(path):
    require(path.stat().st_size<=LIMIT,'Input exceeds 2 MB')
    def unique(pairs):
        d={}
        for k,v in pairs:
            require(k not in d,'Duplicate JSON key'); d[k]=v
        return d
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique,parse_constant=lambda _: (_ for _ in ()).throw(Invalid('Non-finite JSON number')))
def main():
    parser=SafeParser(description=__doc__); parser.add_argument('--input',type=Path); parser.add_argument('--output',type=Path); parser.add_argument('--print-output',type=Path); parser.add_argument('--check',type=Path); args=parser.parse_args()
    try:
        if args.check:
            require(not any([args.input,args.output,args.print_output]),'Use --check alone'); require(args.check.stat().st_size<=LIMIT*5,'Output too large'); check(args.check.read_text(encoding='utf-8')); print('PASS: static artifact scan (human privacy and visual review still required)'); return
        require(args.input and args.output,'--input and --output required')
        skill_name=Path(__file__).resolve().parents[1].name
        require(skill_name in ['project-handoff','work-timeline'],'Unexpected skill installation directory')
        mode={'project-handoff':'handoff','work-timeline':'timeline'}[skill_name]
        require(mode=='handoff' or not args.print_output,'Print companion supported for handoff only')
        if mode=='handoff': require(args.print_output is not None,'Handoff requires --print-output')
        outputs=[args.output]+([args.print_output] if args.print_output else [])
        require(len({p.resolve() for p in outputs})==len(outputs),'Outputs must be distinct')
        for p in outputs:
            require(not p.exists(),'Refusing to overwrite existing output'); require(p.parent.exists(),'Output parent must exist'); require(re.fullmatch(r'[A-Za-z0-9_-]+\.html',p.name),'Use a neutral ASCII HTML filename')
        d=validate(load(args.input),mode)
        rendered=[render(d,False)]+([render(d,True)] if args.print_output else [])
        for text in rendered: check(text)
        safe_write(outputs,rendered)
        print('PASS: validated safe projection; wrote '+str(len(outputs))+' offline artifact(s). Human privacy and visual review still required.')
    except (Invalid,ValueError,TypeError,KeyError,OSError) as e:
        # Do not echo rejected raw values or input filenames into model-visible output.
        print('ERROR: '+str(e) if isinstance(e,Invalid) else 'ERROR: invalid input or unavailable file; inspect locally without exposing raw content',file=sys.stderr); sys.exit(2)
if __name__=='__main__': main()
