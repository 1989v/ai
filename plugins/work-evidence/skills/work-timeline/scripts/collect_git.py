#!/usr/bin/env python3
"""Read approved local Git commit timestamps; emit only minimized evidence items.

Local scope JSON (never paste into a model):
{"collection_confirmed":true,"repository":"/local/repo","ref":"HEAD",
 "author_identity":"Exact Name <local-email>","start":"2026-01-01",
 "end":"2026-01-31","timezone":"Asia/Seoul","source_alias":"Source A",
 "owner_role":"Maintainer","observed_at":"2026-02-01"}

Counts commits reachable from the named ref, selected by exact Git author identity
and committed timestamp, including the entire local end day. Does not collect
messages, diffs, paths, hashes, remote URLs, collaborator identities or outcomes.
The result is an items array, not a complete reviewed render input.
"""
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from zoneinfo import ZoneInfo
from render import Invalid, SafeParser, date, obj, require, string, load, scan, safe_write

def main():
    p=SafeParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter); p.add_argument('--scope',required=True,type=Path); p.add_argument('--output',required=True,type=Path); a=p.parse_args()
    try:
        s=load(a.scope); obj(s,['collection_confirmed','repository','ref','author_identity','start','end','timezone','source_alias','owner_role','observed_at'])
        require(s['collection_confirmed'] is True,'Confirm the specific local collection scope first')
        require(isinstance(s['repository'],str) and Path(s['repository']).is_dir(),'Repository unavailable')
        require(isinstance(s['ref'],str) and bool(re.fullmatch(r'(?:HEAD|refs/heads/[A-Za-z0-9_.\-/]+|refs/tags/[A-Za-z0-9_.\-/]+)',s['ref'])) and '..' not in s['ref'],'Specify HEAD or a single explicit local branch/tag ref')
        author=s['author_identity']; require(isinstance(author,str) and 1<=len(author)<=300 and '\n' not in author and '\x00' not in author,'Invalid local author identity')
        for key in ['source_alias','owner_role']: string(s[key])
        date(s['observed_at']); start=date(s['start']); end=date(s['end']); require(start<=end,'Reversed period'); tz=ZoneInfo(s['timezone'])
        first=dt.datetime.combine(start,dt.time.min,tz); limit=dt.datetime.combine(end+dt.timedelta(days=1),dt.time.min,tz)
        # POSIX extended author expression matches the complete Name <email> identity.
        escaped=re.sub(r'([.\[\]\\*^$()+?{}|])',r'\\\1',author)
        cmd=['git','-C',s['repository'],'--no-pager','log','--no-show-signature','--format=%cI','--extended-regexp','--author=^'+escaped+'$', '--since-as-filter='+first.astimezone(dt.timezone.utc).isoformat(), '--until='+(limit-dt.timedelta(seconds=1)).astimezone(dt.timezone.utc).isoformat(),s['ref'],'--']
        env=dict(os.environ,GIT_TERMINAL_PROMPT='0',GIT_PAGER='cat',GIT_NO_REPLACE_OBJECTS='1')
        result=subprocess.run(cmd,capture_output=True,text=True,timeout=60,env=env)
        require(result.returncode==0,'Git read failed; inspect local scope and Git version without exposing raw data')
        rows=result.stdout.splitlines(); require(len(rows)<=500,'More than 500 commits: narrow the authorized scope')
        dates=[]
        for row in rows:
            instant=dt.datetime.fromisoformat(row).astimezone(tz)
            if first<=instant<limit: dates.append(instant.date().isoformat())
        items=[]
        for index,day in enumerate(sorted(dates),1):
            items.append({'id':f'E{index}','kind':'commit','title':'기록된 변경','date':day,'end_date':day,'status':'done','summary':'승인한 작성자와 기간에 해당하는 변경 메타데이터입니다. 내용과 결과는 수집하지 않았습니다.','owner_role':s['owner_role'],'evidence':{'source_alias':s['source_alias'],'locator':f'change-{index}','observed_at':s['observed_at'],'detail':'선택한 로컬 참조에서 작성자 일치 및 커밋 시각으로 확인했습니다. 상세 내용과 결과는 별도 검토가 필요합니다.'}})
        require(not a.output.exists(),'Refusing to overwrite existing output')
        require(bool(re.fullmatch(r'[A-Za-z0-9_-]+\.json',a.output.name)),'Use neutral ASCII JSON filename')
        text=json.dumps(items,ensure_ascii=False,indent=2); scan(text)
        safe_write([a.output],[text])
        print('PASS: minimized commit metadata only; review and complete evidence before rendering.')
    except (Invalid,ValueError,TypeError,KeyError,OSError,subprocess.SubprocessError):
        print('ERROR: local collection failed; inspect scope locally without sharing private values.',file=sys.stderr); sys.exit(2)
if __name__=='__main__': main()
