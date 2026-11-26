import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

SCRIPT=Path(__file__).resolve().parents[1]/'scripts'/'render.py'
spec=importlib.util.spec_from_file_location('artifact_render',SCRIPT); r=importlib.util.module_from_spec(spec); spec.loader.exec_module(r)
MODE='handoff' if SCRIPT.parents[1].name=='project-handoff' else 'timeline'
def fixture():
    d={'schema_version':1,'mode':MODE,'title':'검토한 작업','summary':'확인된 근거를 연결합니다.','audience':'technical','context':'personal','question':'어떤 결과가 확인되었나요?','period':{'start':'2026-01-01','end':'2026-01-31','timezone':'Asia/Seoul'},'approval':{'collection_confirmed':True,'wording_reviewed':True,'quantities_reviewed':True},'scope':{'sources':['Source A'],'roles':['Maintainer']},'items':[{'id':'E1','kind':'commit','title':'검토한 변경','date':'2026-01-02','end_date':'2026-01-03','status':'done','summary':'안전한 설명','owner_role':'Maintainer','evidence':{'source_alias':'Source A','locator':'change-1','observed_at':'2026-02-01','detail':'로컬 검토로 확인함.'},'metric':{'label':'응답 시간','before':30,'after':20,'unit':'ms','baseline':'동일 조건의 변경 전 측정','measurement':'승인한 로컬 확인'}}], 'diagram':{'nodes':[{'id':'N1','label':'변경','evidence_ids':['E1']},{'id':'N2','label':'검증','evidence_ids':['E1']},{'id':'N3','label':'미해결'}],'edges':[{'from':'N1','to':'N2','label':'검사로 확인'},{'from':'N1','to':'N3','label':'추가 확인 필요'}],'caption':'검사 결과와 남은 작업을 구분합니다.'}}
    if MODE=='handoff': d['handoff']={'context':'이어서 확인할 범위','known_state':['검사 결과를 확인함'],'decisions':[{'text':'범위를 유지함','evidence_ids':['E1']}],'unresolved':[{'text':'추가 확인 필요','owner_role':'Maintainer','evidence_ids':[]}],'next_verification':[{'text':'승인된 검사를 실행하고 결과 확인','owner_role':'Maintainer','evidence_ids':['E1']}]}
    return d
class Tests(unittest.TestCase):
    def test_real_render_and_standalone_print(self):
        d=r.validate(fixture(),MODE); output=r.render(d); r.check(output)
        self.assertIn('lang="ko"',output); self.assertIn('marker-end="url(#arrow)"',output); self.assertIn('data-evidence="E1"',output); self.assertIn('datetime',str(r.date('2026-01-01').__class__))
        self.assertIn('name="status"',output)
        if MODE=='handoff':
            plain=r.render(d,True); r.check(plain); self.assertNotIn('<script>',plain); self.assertIn('다음 검증',plain); self.assertIn('change-1',plain)
    def test_unknown_nested_raw_data_rejected(self):
        for place in ['top','evidence','metric','node']:
            d=fixture(); target={'top':d,'evidence':d['items'][0]['evidence'],'metric':d['items'][0]['metric'],'node':d['diagram']['nodes'][0]}[place]; target['raw_private']='do not propagate'
            with self.assertRaises(r.Invalid): r.validate(d,MODE)
    def test_scope_review_required(self):
        for key in fixture()['approval']:
            d=fixture(); d['approval'][key]=False
            with self.assertRaises(r.Invalid): r.validate(d,MODE)
    def test_private_patterns_and_locators(self):
        for value in ['person@example.org','password=private','/Users/private/doc','192.168.1.1']:
            d=fixture(); d['items'][0]['summary']=value
            with self.assertRaises(r.Invalid): r.validate(d,MODE)
        d=fixture(); d['items'][0]['evidence']['locator']='PRIVATE-123'
        with self.assertRaises(r.Invalid): r.validate(d,MODE)
    def test_escaping(self):
        d=fixture(); d['items'][0]['title']='<img onerror="x()">'; out=r.render(r.validate(d,MODE)); r.check(out); self.assertIn('&lt;img',out); self.assertNotIn('<img onerror',out)
    def test_public_opt_in_and_clean_paths(self):
        for url in ['https://docs.python.org/3/','https://docs.python.org/3/?private=1','https://docs.python.org/3/#private','https://user:pass@docs.python.org/3/']:
            d=fixture(); d['items'][0]['evidence']['public_url']=url
            with self.assertRaises(r.Invalid): r.validate(d,MODE)
        d=fixture(); d['public_reference_hosts']=['docs.python.org']; d['items'][0]['evidence']['public_url']='https://docs.python.org/3/'; r.check(r.render(r.validate(d,MODE)))
    def test_references_dates_and_metrics(self):
        for transform in [lambda d:d['diagram']['edges'][0].update(to='N9'),lambda d:d['items'][0]['metric'].update(after=float('nan')),lambda d:d['items'][0].update(end_date='2026-01-01'),lambda d:d['items'][0].pop('end_date')]:
            d=fixture(); transform(d)
            with self.assertRaises(r.Invalid): r.validate(d,MODE)
    def test_cli_writes_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory(prefix='artifact-test-') as directory:
            root=Path(directory); input=root/'safe.json'; output=root/'artifact.html'; input.write_text(json.dumps(fixture()),encoding='utf-8'); cmd=[sys.executable,str(SCRIPT),'--input',str(input),'--output',str(output)]
            if MODE=='handoff': cmd+=['--print-output',str(root/'print.html')]
            done=subprocess.run(cmd,capture_output=True,text=True); self.assertEqual(done.returncode,0,done.stderr); self.assertTrue(output.exists())
            done=subprocess.run(cmd,capture_output=True,text=True); self.assertEqual(done.returncode,2); self.assertIn('overwrite',done.stderr)
            done=subprocess.run([sys.executable,str(SCRIPT),'--check',str(output)],capture_output=True,text=True); self.assertEqual(done.returncode,0,done.stderr)
    def test_mode_mismatch_no_output(self):
        with tempfile.TemporaryDirectory(prefix='artifact-mode-test-') as directory:
            root=Path(directory); inp=root/'safe.json'; out=root/'artifact.html'; d=fixture(); d['mode']='timeline' if MODE=='handoff' else 'handoff'; inp.write_text(json.dumps(d))
            cmd=[sys.executable,str(SCRIPT),'--input',str(inp),'--output',str(out)]
            if MODE=='handoff': cmd+=['--print-output',str(root/'print.html')]
            result=subprocess.run(cmd,capture_output=True,text=True)
            self.assertEqual(result.returncode,2); self.assertFalse(out.exists()); self.assertFalse((root/'print.html').exists())
    def test_raw_unknown_argument_is_not_echoed(self):
        sentinel='private-argument-marker'
        for script in [SCRIPT,SCRIPT.with_name('collect_git.py')]:
            result=subprocess.run([sys.executable,str(script),'--unknown='+sentinel],capture_output=True,text=True)
            self.assertEqual(result.returncode,2); self.assertNotIn(sentinel,result.stdout+result.stderr)
    def test_staging_rollback_and_exclusive_write(self):
        with tempfile.TemporaryDirectory(prefix='artifact-stage-test-') as directory:
            root=Path(directory); first=root/'one.html'; second=root/'two.html'; real_link=r.os.link; calls=[]
            def fail_second(source,target):
                calls.append(target)
                if len(calls)==2: raise OSError('fixture failure')
                real_link(source,target)
            with mock.patch.object(r.os,'link',side_effect=fail_second):
                with self.assertRaises(OSError): r.safe_write([first,second],['complete first','complete second'])
            self.assertEqual(list(root.iterdir()),[])
            first.write_text('existing content')
            with self.assertRaises(FileExistsError): r.safe_write([first],['replacement'])
            self.assertEqual(first.read_text(),'existing content'); self.assertEqual(list(root.iterdir()),[first])
            first.unlink(); r.safe_write([first,second],['complete first','complete second'])
            self.assertEqual(first.read_text(),'complete first'); self.assertEqual(second.read_text(),'complete second')
            self.assertEqual(first.stat().st_mode & 0o777,0o600)
    def test_git_collection_inclusive_timezone_and_author(self):
        collector=SCRIPT.with_name('collect_git.py')
        with tempfile.TemporaryDirectory(prefix='artifact-git-test-') as directory:
            root=Path(directory); repo=root/'repo'; repo.mkdir()
            def git(*args,env=None): return subprocess.run(['git','-C',str(repo),*args],env=env,capture_output=True,text=True,check=True)
            git('init'); git('config','user.name','Fixture Author'); git('config','user.email','fixture@example.org')
            for stamp in ['2026-01-01T00:00:00+09:00','2026-01-31T23:59:59+09:00','2026-02-01T00:00:00+09:00']:
                env=dict(os.environ,GIT_AUTHOR_DATE=stamp,GIT_COMMITTER_DATE=stamp); git('commit','--allow-empty','-m','private fixture text',env=env)
            scope={'collection_confirmed':True,'repository':str(repo),'ref':'HEAD','author_identity':'Fixture Author <fixture@example.org>','start':'2026-01-01','end':'2026-01-31','timezone':'Asia/Seoul','source_alias':'Source A','owner_role':'Maintainer','observed_at':'2026-02-01'}
            inp=root/'scope.json'; inp.write_text(json.dumps(scope)); out=root/'git-items.json'
            done=subprocess.run([sys.executable,str(collector),'--scope',str(inp),'--output',str(out)],capture_output=True,text=True); self.assertEqual(done.returncode,0,done.stderr); items=json.loads(out.read_text()); self.assertEqual([i['date'] for i in items],['2026-01-01','2026-01-31']); self.assertNotIn('fixture@example.org',out.read_text()); self.assertNotIn('private fixture text',out.read_text())
if __name__=='__main__': unittest.main()
