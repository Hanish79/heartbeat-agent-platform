#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,re,xml.etree.ElementTree as ET
from datetime import datetime,timezone
from pathlib import Path
from typing import Any
from approval_engine import evaluate_approval
SECURITY_ROW=re.compile(r"^\|\s*(SEC-\d+)\s*\|\s*([A-Z]+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*$")
def now_utc(): return datetime.now(timezone.utc).isoformat()
def load_json(path:Path,default:Any):
    try:return json.loads(path.read_text(encoding='utf-8'))
    except (FileNotFoundError,json.JSONDecodeError):return default
def write_tests_xml(repo_root:Path,pipeline_report:dict[str,Any]):
    stages=pipeline_report.get('stages',[])
    suite=ET.Element('testsuite',{'name':'heartbeat-demo','tests':str(len(stages)),'failures':str(sum(1 for s in stages if s.get('returncode')!=0)),'errors':'0','skipped':'0','timestamp':pipeline_report.get('timestamp_utc',now_utc())})
    props=ET.SubElement(suite,'properties');ET.SubElement(props,'property',{'name':'pipeline_passed','value':str(bool(pipeline_report.get('passed'))).lower()})
    for stage in stages:
        tc=ET.SubElement(suite,'testcase',{'classname':'heartbeat.pipeline','name':str(stage.get('name','unknown')),'time':'0'})
        if stage.get('returncode')!=0:
            f=ET.SubElement(tc,'failure',{'message':f"Stage failed with return code {stage.get('returncode')}",'type':'PipelineStageFailure'});f.text=(stage.get('stderr') or stage.get('stdout') or '')[:4000]
        so=ET.SubElement(tc,'system-out');so.text=(stage.get('stdout') or '')[:4000]
    tree=ET.ElementTree(suite);ET.indent(tree,space='  ');tree.write(repo_root/'evidence/tests.xml',encoding='utf-8',xml_declaration=True)
def write_traceability_csv(repo_root:Path,traceability:dict[str,Any]):
    with (repo_root/'evidence/traceability.csv').open('w',newline='',encoding='utf-8') as h:
        w=csv.writer(h);w.writerow(['identifier','type','defined','reference_count','files','status'])
        for ident,locs in sorted(traceability.get('matrix',{}).items()):
            pref=ident.split('-',1)[0];defined=any(i.get('defined') for i in locs);files=sorted({i.get('file','') for i in locs});w.writerow([ident,pref,str(defined).lower(),len(locs),';'.join(files),'OK' if defined else 'UNDEFINED'])
def write_build_json(repo_root:Path,pipeline_report:dict[str,Any]):
    p={'schema_version':'1.0','status':'PASSED' if pipeline_report.get('passed') else 'FAILED','pipeline':'Heartbeat deterministic pipeline','started_at':pipeline_report.get('timestamp_utc'),'completed_at':now_utc(),'result':bool(pipeline_report.get('passed')),'stopped_at':pipeline_report.get('stopped_at'),'stages':[{'name':s.get('name'),'returncode':s.get('returncode'),'passed':s.get('returncode')==0} for s in pipeline_report.get('stages',[])]}
    (repo_root/'evidence/build.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8')
def parse_security(path:Path):
    if not path.exists():return [],None
    text=path.read_text(encoding='utf-8');findings=[]
    for line in text.splitlines():
        m=SECURITY_ROW.match(line)
        if m:
            i,s,f,r=m.groups();findings.append({'id':i,'severity':s,'finding':f.strip(),'recommendation':r.strip(),'status':'OPEN'})
    rec=next((c for c in ('PASS_WITH_CONDITIONS','PASS','FAIL') if c in text),None)
    return findings,rec
def write_security_json(repo_root:Path):
    src=repo_root/'demo/shipment-validation-api/expected/security-review.md';findings,rec=parse_security(src)
    p={'schema_version':'1.0','status':'REVIEW_COMPLETE' if rec else 'MISSING','recommendation':rec,'finding_count':len(findings),'findings':findings,'source':str(src.relative_to(repo_root)) if src.exists() else str(src),'generated_at':now_utc()}
    (repo_root/'evidence/security.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8')
def write_deployment_json(repo_root:Path,publish_report:dict[str,Any]):
    a=evaluate_approval(repo_root/'approvals/deployment.json','deployment')
    p={'schema_version':'1.0','status':'APPROVED' if a.valid else 'BLOCKED','approval_gate':'deployment','approval_valid':a.valid,'approval_status':a.status,'approved_by':a.approver_name,'approver_role':a.approver_role,'approved_at':a.approved_at,'expires_at':a.expires_at,'published':bool(publish_report.get('published')),'dry_run':bool(publish_report.get('dry_run',True)),'target':'local-demo','local_file_count':len(publish_report.get('local_files',[])),'drive_file_count':len(publish_report.get('drive_files',[])),'generated_at':now_utc(),'errors':list(a.errors)}
    (repo_root/'evidence/deployment.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo-root');ap.add_argument('--pipeline-report',default='output/pipeline-report.json');ap.add_argument('--traceability-report',default='output/traceability.json');ap.add_argument('--publish-report',default='output/publish-report.json');args=ap.parse_args()
    root=Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parents[1];(root/'evidence').mkdir(parents=True,exist_ok=True)
    pr=load_json(root/args.pipeline_report,{'passed':False,'timestamp_utc':now_utc(),'stopped_at':'pipeline_report_missing','stages':[]});tr=load_json(root/args.traceability_report,{'valid':False,'matrix':{},'findings':[{'severity':'ERROR','message':'Traceability report missing.'}]});pub=load_json(root/args.publish_report,{'published':False,'dry_run':True,'local_files':[],'drive_files':[]})
    write_tests_xml(root,pr);write_traceability_csv(root,tr);write_build_json(root,pr);write_security_json(root);write_deployment_json(root,pub)
    print(json.dumps({'generated':['evidence/tests.xml','evidence/traceability.csv','evidence/build.json','evidence/security.json','evidence/deployment.json'],'build_status':'PASSED' if pr.get('passed') else 'FAILED','timestamp_utc':now_utc()},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
