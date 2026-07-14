#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,subprocess,sys
from dataclasses import asdict,dataclass
from datetime import datetime,timezone
from pathlib import Path
@dataclass(frozen=True)
class StageResult:
    name:str;command:tuple[str,...];returncode:int;stdout:str;stderr:str
def run_stage(name,command,cwd):
    r=subprocess.run(command,cwd=cwd,capture_output=True,text=True);return StageResult(name,tuple(command),r.returncode,r.stdout.strip(),r.stderr.strip())
def write_report(root,path,stages):
    passed=bool(stages) and all(s.returncode==0 for s in stages);p={'passed':passed,'timestamp_utc':datetime.now(timezone.utc).isoformat(),'stopped_at':next((s.name for s in stages if s.returncode!=0),None),'stages':[asdict(s) for s in stages]};path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(p,indent=2),encoding='utf-8');return p
def main():
    ap=argparse.ArgumentParser(description='Run deterministic Heartbeat governance pipeline.');ap.add_argument('--repo-root');ap.add_argument('--stop-after',choices=('proposal','architecture','deployment','validation'),default='validation');ap.add_argument('--publish',action='store_true');ap.add_argument('--execute-publish',action='store_true');ap.add_argument('--drive-root');ap.add_argument('--git',action='store_true');ap.add_argument('--report',default='output/pipeline-report.json');args=ap.parse_args()
    root=Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parents[1];scripts=root/'scripts';py=sys.executable;stages=[]
    for gate,file in [('proposal','approvals/proposal.json'),('architecture','approvals/architecture.json'),('deployment','approvals/deployment.json')]:
        stages.append(run_stage(f'{gate}_approval',[py,str(scripts/'approval_engine.py'),file,'--expected-gate',gate,'--repo-root',str(root)],root))
        if stages[-1].returncode!=0 or args.stop_after==gate:break
    if all(s.returncode==0 for s in stages) and args.stop_after=='validation':stages.append(run_stage('validate_documents',[py,str(scripts/'validate_documents.py'),'--repo-root',str(root)],root))
    if all(s.returncode==0 for s in stages) and args.stop_after=='validation':stages.append(run_stage('traceability',[py,str(scripts/'traceability.py'),'--repo-root',str(root)],root))
    if all(s.returncode==0 for s in stages) and args.publish:
        cmd=[py,str(scripts/'publish.py'),'--repo-root',str(root),'--approval','approvals/deployment.json']
        if args.execute_publish:cmd.append('--execute')
        if args.drive_root:cmd.extend(['--drive-root',args.drive_root])
        if args.git:cmd.append('--git')
        stages.append(run_stage('publish',cmd,root))
    report=root/args.report;p=write_report(root,report,stages)
    ev=run_stage('generate_evidence',[py,str(scripts/'evidence.py'),'--repo-root',str(root),'--pipeline-report',str(report.relative_to(root))],root)
    print(json.dumps({'passed':p['passed'],'stopped_at':p['stopped_at'],'stages':[{'name':s.name,'returncode':s.returncode} for s in stages],'evidence_returncode':ev.returncode,'report':str(report),'evidence':['evidence/tests.xml','evidence/traceability.csv','evidence/build.json','evidence/security.json','evidence/deployment.json']},indent=2));return 0 if p['passed'] and ev.returncode==0 else 1
if __name__=='__main__':raise SystemExit(main())
