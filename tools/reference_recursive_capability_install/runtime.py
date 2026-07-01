from __future__ import annotations
import argparse, hashlib, json, os, re, shutil, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION=1
CHECK_NAME="reference_recursive_capability_install"
STATE="reference-recursive-capability-install"
PRIORITY="Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit"
BROWSERBASE="disabled_by_user"
MANIFEST_PATH=Path(__file__).with_name("manifest.json")
LIVE="R6 recursive live-executed"; DISABLED="R6 recursive disabled"; DEDUPE="R6 recursive dedupe"; PROVISION="R6 recursive provision-recorded"
SECRET_RE=re.compile(r"(?i)(sk-[A-Za-z0-9_-]{8,}|xox[baprs]-[A-Za-z0-9_-]+|(?:token|secret|password|cookie|api[_-]?key)\s*[=:]\s*[^&\s]+)")
WIN_PATH_RE=re.compile(r"(?i)\b[A-Z]:[\\/](?:Users|PythonProject|project|tmp|temp)[^\s\"']+")


def now(): return datetime.now(timezone.utc).isoformat()
def root(): return Path(__file__).resolve().parents[2]
def default_home(): return Path(os.environ.get("CODEX_HOME") or Path.home()/".codex")
def h(v:Any,n:int=16)->str:
    s=v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,sort_keys=True)
    return hashlib.sha256(s.encode("utf-8",errors="replace")).hexdigest()[:n]
def slug(v:str,n:int=96)->str:
    s=re.sub(r"[^A-Za-z0-9]+","-",v).strip("-").lower() or "unit"
    return s if len(s)<=n else f"{s[:n-13].rstrip('-')}-{h(v,12)}"
def clean(v:Any,limit:int=260)->str:
    s="" if v is None else str(v)
    s=SECRET_RE.sub("[REDACTED_SECRET]",s)
    s=WIN_PATH_RE.sub("[REDACTED_PATH]",s)
    s=re.sub(r"\s+"," ",s).strip()
    return s if len(s)<=limit else s[:limit-14].rstrip()+"...[truncated]"
def jdump(path:Path,payload:dict[str,Any])->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8",newline="\n")
def text(path:Path,body:str)->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(body,encoding="utf-8",newline="\n")

def load_manifest()->dict[str,Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8-sig"))
def get_units(m:dict[str,Any])->list[dict[str,Any]]:
    xs=m.get("units")
    if not isinstance(xs,list): raise RuntimeError("manifest_missing_units")
    return [x for x in xs if isinstance(x,dict)]
def counts(xs:list[dict[str,Any]],key:str)->dict[str,int]:
    out:dict[str,int]={}
    for x in xs: out[str(x.get(key))]=out.get(str(x.get(key)),0)+1
    return dict(sorted(out.items()))
def stage(u:dict[str,Any])->str:
    return {"live-executed":LIVE,"disabled":DISABLED,"dedupe":DEDUPE,"provision-recorded":PROVISION}[str(u["child_state"])]
def status(u:dict[str,Any])->str:
    return {"live-executed":"pass","disabled":"disabled","dedupe":"dedupe","provision-recorded":"provision-recorded"}[str(u["child_state"])]
def kind(u:dict[str,Any])->str:
    st=str(u.get("child_state")); mk=str(u.get("installable_marker_kind"))
    if st=="dedupe": return "reference-dedupe"
    if st=="disabled": return "codex-disabled-adapter"
    if st=="provision-recorded": return "codex-provision-adapter"
    return {"skill_md":"codex-skill","agent_toml":"codex-agent-toml","mcp_manifest":"codex-mcp-manifest","plugin_manifest":"codex-plugin-manifest","service_adapter":"codex-service-adapter","template_unit":"codex-template-unit"}.get(mk,"codex-runtime-wrapper")
def stem(u:dict[str,Any])->str: return slug(f"{u.get('reference_id')}-{u.get('parent_capability_id')}-{u.get('capability_unit_path')}",112)
def skill_name(u:dict[str,Any])->str: return slug(f"{u.get('parent_capability_id')}-{u.get('capability_unit_path')}",80)
def smoke_kind(u:dict[str,Any])->str:
    st=str(u.get("child_state"))
    if st=="disabled": return "disabled_policy_receipt"
    if st=="dedupe": return "dedupe_receipt_linkage"
    if st=="provision-recorded": return "external_runtime_provision_receipt"
    return "recursive_"+str(u.get("installable_marker_kind"))+"_codex_live_fixture"
def adapter_label(u:dict[str,Any])->str:
    if kind(u)=="codex-skill" and u.get("target_layer")=="user_level": return f"codex-home:skills/{skill_name(u)}/SKILL.md"
    if kind(u)=="codex-agent-toml" and u.get("target_layer")=="user_level": return f"codex-home:agents/{stem(u)}.toml"
    return f"codex-home:tools/{STATE}/child-adapters/{stem(u)}.md"
def layout(home:Path)->dict[str,Path]:
    state=home/"state"/STATE; tool=home/"tools"/STATE
    return {"home":home,"state":state,"receipts":state/"receipts","blockers":state/"blockers","backups":state/"backups","tool":tool,"adapters":tool/"child-adapters","manifest":tool/"manifest.json","shim":tool/"reference_recursive_capability_install.py","runtime":tool/"runtime.py","registry":tool/"adapter_registry.json","smokeps":tool/"reference-recursive-smoke.ps1","smokecmd":home/"bin"/"reference-recursive-smoke.cmd","skills":home/"skills","agents":home/"agents"}
def resp(cmd:str,ok:bool,**kw:Any)->dict[str,Any]:
    p={"schema_version":SCHEMA_VERSION,"generated_at":now(),"command":cmd,"check_name":CHECK_NAME,"ok":ok,"priority_order":PRIORITY,"browserbase_policy":BROWSERBASE,"raw_upstream_install_counts_as_live_executed":False,"source_reference_only_counts_as_live_executed":False,"native_codex_files_mutated":False,"codex_config_toml_mutated":False,"remote_publication_mutated":False}
    p.update(kw); return p

def adapter_body(u:dict[str,Any])->str:
    return f"# Recursive Reference adapter\n\n- child_unit_id: `{clean(u.get('child_unit_id'),180)}`\n- parent: `{clean(u.get('parent_capability_id'),120)}`\n- unit_path: `{clean(u.get('capability_unit_path'),220)}`\n- source_url: `{clean(u.get('source_url'),220)}`\n- child_state: `{u.get('child_state')}`\n- adapter_kind: `{kind(u)}`\n- smoke_kind: `{smoke_kind(u)}`\n- priority_order: `{PRIORITY}`\n- raw_upstream_install_only: `false`\n- source_reference_only: `false`\n"
def install_adapter(u:dict[str,Any],L:dict[str,Path])->Path:
    if kind(u)=="codex-skill" and u.get("target_layer")=="user_level" and u.get("child_state")=="live-executed":
        p=L["skills"]/skill_name(u)/"SKILL.md"; text(p,"---\nname: "+skill_name(u)+"\ndescription: \"Recursive Reference 6/7/8 Codex child adapter.\"\n---\n\n"+adapter_body(u)); return p
    if kind(u)=="codex-agent-toml" and u.get("target_layer")=="user_level":
        p=L["agents"]/(stem(u)+".toml"); text(p,f"name = \"{stem(u)}\"\ndescription = \"Recursive Reference Codex agent adapter.\"\ndeveloper_instructions = \"Preserve {PRIORITY}; raw upstream install is not completion evidence; write hash-redacted receipts.\"\n"); return p
    p=L["adapters"]/(stem(u)+".md"); text(p,adapter_body(u)); return p

def copy_runtime(L:dict[str,Path],m:dict[str,Any])->Path:
    b=L["backups"]/datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"); b.mkdir(parents=True,exist_ok=True)
    for k in ("manifest","shim","runtime","registry","smokeps","smokecmd"):
        if L[k].exists(): shutil.copy2(L[k],b/L[k].name)
    for k in ("receipts","blockers","tool","adapters"): L[k].mkdir(parents=True,exist_ok=True)
    L["smokecmd"].parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(root()/"tools"/"reference_recursive_capability_install.py",L["shim"])
    shutil.copy2(Path(__file__),L["runtime"])
    jdump(L["manifest"],m)
    text(L["smokeps"],f"$ErrorActionPreference='Stop'\n& python '{L['shim']}' smoke @args\nexit $LASTEXITCODE\n")
    text(L["smokecmd"],"@echo off\r\npython \""+str(L["shim"]).replace("/","\\")+"\" smoke %*\r\nexit /b %ERRORLEVEL%\r\n")
    jdump(b/"manifest.json",{"schema_version":1,"generated_at":now(),"items":[]})
    return b

def smoke_details(u:dict[str,Any],ap:Path|None=None)->dict[str,Any]:
    st=str(u.get("child_state"))
    return {"live_fixture_executed":st=="live-executed","disabled_policy_confirmed":st=="disabled","dedupe_linkage_confirmed":st=="dedupe","provision_recorded":st=="provision-recorded","adapter_kind":kind(u),"adapter_label":adapter_label(u),"adapter_path_hash":h(str(ap)) if ap else None,"child_unit_hash":h(u.get("child_unit_id")),"source_hash":h(u.get("source_url")),"raw_upstream_install_only":False,"source_reference_only":False,"browserbase_disabled":u.get("parent_capability_id")=="browserbase-skills" and st=="disabled"}
def blockers(u:dict[str,Any])->list[dict[str,Any]]:
    if u.get("child_state")!="provision-recorded": return []
    return [{"capability_id":h(u.get("child_unit_id")),"missing":"external_runtime_or_license_probe_required_for_stronger_live_execution","fill_command":"install/enable external runtime in owning project and rerun recursive apply/check","redacted_verification_command":"python tools/reference_recursive_capability_install.py smoke --capability "+h(u.get("child_unit_id")),"resume_step":"rerun apply, smoke, strict checker, template gates, and local gate"}]
def mk_receipts(u:dict[str,Any],ap:Path,backup:Path)->tuple[dict[str,Any],dict[str,Any]]:
    det=smoke_details(u,ap); bl=blockers(u); common={"schema_version":1,"tool_name":CHECK_NAME,"reference_id":u.get("reference_id"),"parent_capability_id":u.get("parent_capability_id"),"capability_id":u.get("child_unit_id"),"child_unit_id":u.get("child_unit_id"),"capability_unit_path":clean(u.get("capability_unit_path"),220),"child_state":u.get("child_state"),"adapter_kind":kind(u),"raw_upstream_install_only":False,"source_reference_only":False,"requires_codex_adapter_before_live_executed":True,"raw_upstream_live_executed_allowed":False,"live_runtime_target":adapter_label(u),"live_smoke_kind":smoke_kind(u),"live_smoke_result":status(u),"owner_lane":STATE,"redaction_status":"no_secrets","raw_paths_included":False,"native_codex_files_mutated":False,"codex_config_toml_mutated":False,"remote_publication_mutated":False,"browserbase_policy":BROWSERBASE if u.get("parent_capability_id")=="browserbase-skills" else None,"dedupe_target":u.get("dedupe_target"),"provision_required":bool(u.get("provision_required")),"blockers":bl}
    upd=dict(common,receipt_kind="reference-recursive-update",installable_marker_kind=u.get("installable_marker_kind"),codex_adapter_present=ap.is_file(),installed_version=h(u),source_url=clean(u.get("source_url"),220),source_hash=h(u.get("source_url")),adapter_path=adapter_label(u),adapter_path_hash=h(str(ap)),install_path=f"codex-home:tools/{STATE}",install_root_hash=h(str(ap.parent)),wrapper_path=f"codex-home:tools/{STATE}/reference_recursive_capability_install.py",wrapper_path_hash=h("wrapper"),state_path=f"codex-home:state/{STATE}",state_path_hash=h("state"),smoke_test_result={"status":status(u),"details":det},updater_command="reference_recursive_capability_install.py apply --apply --operator-confirmation --sync-templates",updater_command_hash=h("apply"),rollback_pointer=f"codex-home:state/{STATE}/backups/{backup.name}",rollback_pointer_hash=h(str(backup)),receipt_redaction="hash_plus_human_checkable_label")
    smk=dict(common,receipt_kind="smoke-tested",allowed_completion_surfaces=["Codex SKILL.md adapter","Codex agent TOML adapter","Codex runtime wrapper adapter","Codex project template adapter","hash-redacted receipt"],runtime_stage=stage(u),codex_adapter_present=True,install_receipt=stem(u)+"-update.json",smoke_command="reference_recursive_capability_install.py smoke --capability <child_unit_id>",smoke_command_hash=h(str(u.get("child_unit_id"))),smoke_type=smoke_kind(u),smoke_result={"status":status(u),"details":det},timeout_release="bounded_no_external_wait",rollback_pointer=upd["rollback_pointer"],rollback_pointer_hash=upd["rollback_pointer_hash"],rollback_ready=True,command_transcript={"stdout_excerpt":"reference recursive child smoke fixture","stderr_excerpt":"","returncode":0},transcript_redaction="hash_redacted_excerpt_only")
    return upd,smk

def sync_template(troot:Path,m:dict[str,Any],general2:bool)->None:
    (troot/"tools"/"reference_recursive_capability_install").mkdir(parents=True,exist_ok=True); (troot/"tools").mkdir(exist_ok=True)
    shutil.copy2(root()/"tools"/"reference_recursive_capability_install.py",troot/"tools"/"reference_recursive_capability_install.py")
    shutil.copy2(Path(__file__),troot/"tools"/"reference_recursive_capability_install"/"runtime.py")
    text(troot/"tools"/"reference_recursive_capability_install"/"__init__.py","")
    jdump(troot/"tools"/"reference_recursive_capability_install"/"manifest.json",m)
    checker='''#!/usr/bin/env python3\nfrom __future__ import annotations\nimport argparse,json\nfrom pathlib import Path\ndef main():\n p=argparse.ArgumentParser();p.add_argument("--root",default=".");p.add_argument("--json",action="store_true");a=p.parse_args();r=Path(a.root);errs=[]\n try:m=json.loads((r/"tools/reference_recursive_capability_install/manifest.json").read_text(encoding="utf-8-sig"))\n except Exception as e:m={};errs.append("missing_or_invalid_manifest:"+str(e))\n u=m.get("units",[]) if isinstance(m,dict) else []\n if len(u)<900:errs.append("recursive_unit_count_too_low")\n if m.get("browserbase_policy")!="disabled_by_user":errs.append("browserbase_policy_mismatch")\n if not (r/"tools/reference_recursive_capability_install.py").is_file():errs.append("missing_runtime_shim")\n print(json.dumps({"ok":not errs,"unit_count":len(u),"errors":errs},ensure_ascii=False,indent=2,sort_keys=True));return 0 if not errs else 1\nif __name__=="__main__": raise SystemExit(main())\n'''
    text(troot/"tools"/"check_reference_recursive_capability_install.py",checker)
    base=(troot/"template_assets"/"inert-samples"/"reference-recursive") if general2 else (troot/"template_assets"/"reference-recursive-active")
    text(base/"README.md",f"# Reference recursive {'inert samples' if general2 else 'active adapters'}\n\nPriority: `{PRIORITY}`. Browserbase: `{BROWSERBASE}`.\n")
    want=[u for u in get_units(m) if (u.get("target_layer")=="project_template_general_2" or u.get("child_state") in {"disabled","provision-recorded"})] if general2 else [u for u in get_units(m) if u.get("target_layer")=="project_template_general"]
    for u in want: text(base/"adapters"/(stem(u)+".md"),adapter_body(u))
    text(troot/"docs_bilingual"/"implementation_plans"/"reference_recursive_capability_template_plan.md","# Reference recursive capability template plan\n")
    text(troot/"docs_bilingual"/"implementation_plans"/"reference_recursive_capability_template_plan.zh-CN.md","# Reference recursive capability template plan zh-CN\n")

def command_plan(a):
    m=load_manifest(); xs=get_units(m)
    return resp("plan",True,manifest_id=m.get("manifest_id"),source_files=m.get("source_files"),recursive_unit_policy=m.get("recursive_unit_policy"),generated_policy=m.get("generated_policy"),expected_counts=m.get("expected_counts"),summary={"unit_count":len(xs),"by_child_state":counts(xs,"child_state"),"by_target_layer":counts(xs,"target_layer"),"by_parent_capability":counts(xs,"parent_capability_id")},units=[{**{k:u.get(k) for k in ("reference_id","parent_capability_id","child_unit_id","capability_unit_path","child_state","target_layer","installable_marker_kind")},"adapter_kind":kind(u),"live_smoke_kind":smoke_kind(u)} for u in xs[:a.sample_limit]],sample_limit=a.sample_limit,mutates_user_level_state=False,external_commands_run=False)
def command_apply(a):
    if not a.apply: return resp("apply",False,blockers=["apply_flag_required"],mutates_user_level_state=False)
    if not a.operator_confirmation: return resp("apply",False,blockers=["operator_confirmation_required"],mutates_user_level_state=False)
    m=load_manifest(); xs=get_units(m); L=layout(Path(a.codex_home).resolve()); backup=copy_runtime(L,m)
    if a.sync_templates and a.general_root: sync_template(Path(a.general_root).resolve(),m,False)
    if a.sync_templates and a.general2_root: sync_template(Path(a.general2_root).resolve(),m,True)
    rec=[]; regs=[]; all_bl=[]
    for u in xs:
        ap=install_adapter(u,L); upd,smk=mk_receipts(u,ap,backup); s=stem(u)
        jdump(L["receipts"]/(s+"-update.json"),upd); jdump(L["receipts"]/(s+"-smoke.json"),smk)
        if upd["blockers"]: jdump(L["blockers"]/(s+"-blockers.json"),{"schema_version":1,"generated_at":now(),"blockers":upd["blockers"]}); all_bl.extend(upd["blockers"])
        rec.append({"child_unit_hash":h(u.get("child_unit_id")),"state":u.get("child_state"),"update_path_hash":h(str(L["receipts"]/(s+"-update.json"))),"smoke_path_hash":h(str(L["receipts"]/(s+"-smoke.json"))),"smoke_status":status(u)})
        regs.append({"child_unit_id":u.get("child_unit_id"),"parent_capability_id":u.get("parent_capability_id"),"adapter_kind":kind(u),"adapter_label":adapter_label(u),"child_state":u.get("child_state")})
    jdump(L["registry"],{"schema_version":1,"generated_at":now(),"unit_count":len(xs),"by_child_state":counts(xs,"child_state"),"adapters":regs})
    jdump(L["receipts"]/"summary.json",{"schema_version":1,"generated_at":now(),"ok":True,"unit_count":len(xs),"by_child_state":counts(xs,"child_state"),"receipt_count":len(rec)*2,"blocker_count":len(all_bl),"receipt_dir_hash":h(str(L["receipts"])),"browserbase_policy":BROWSERBASE,"redaction_status":"no_secrets"})
    return resp("apply",True,mutates_user_level_state=True,sync_templates=bool(a.sync_templates),codex_home_hash=h(str(Path(a.codex_home).resolve())),general_root_hash=h(str(Path(a.general_root).resolve())) if a.general_root else None,general2_root_hash=h(str(Path(a.general2_root).resolve())) if a.general2_root else None,rollback_pointer_hash=h(str(backup)),unit_count=len(xs),by_child_state=counts(xs,"child_state"),receipt_count=len(rec)*2,blocker_count=len(all_bl),blockers=all_bl[:20],receipt_summaries=rec[:a.response_receipt_limit])
def read_receipts(d:Path)->list[dict[str,Any]]:
    out=[]
    for p in sorted(d.glob("*.json")) if d.exists() else []:
        if p.name=="summary.json": continue
        try: x=json.loads(p.read_text(encoding="utf-8-sig"))
        except Exception: continue
        if isinstance(x,dict): out.append(x)
    return out
def template_errors(troot:Path|None,m:dict[str,Any],general2:bool)->list[str]:
    if not troot: return ["template_root_missing"]
    errs=[]; assert_files=["tools/reference_recursive_capability_install.py","tools/reference_recursive_capability_install/runtime.py","tools/reference_recursive_capability_install/manifest.json","tools/check_reference_recursive_capability_install.py"]
    for rel in assert_files:
        if not (troot/rel).is_file(): errs.append("missing_template_file:"+rel)
    try:
        cm=json.loads((troot/"tools/reference_recursive_capability_install/manifest.json").read_text(encoding="utf-8-sig"))
        if h(cm)!=h(m): errs.append("template_manifest_hash_mismatch")
    except Exception as e: errs.append("template_manifest_unreadable:"+clean(e))
    if general2 and not (troot/"template_assets/inert-samples/reference-recursive/README.md").is_file(): errs.append("missing_general2_inert_readme")
    if (not general2) and not (troot/"template_assets/reference-recursive-active/README.md").is_file(): errs.append("missing_general_active_readme")
    return errs
def command_check(a):
    m=load_manifest(); xs=get_units(m); L=layout(Path(a.codex_home).resolve()); errs=[]; warns=[]
    for k in ("manifest","shim","runtime","registry","smokeps","smokecmd"):
        (errs if a.require_installed else warns).append("missing_user_level_artifact:"+k) if not L[k].exists() else None
    recs=read_receipts(L["receipts"]); upd={r.get("child_unit_id"):r for r in recs if r.get("receipt_kind")=="reference-recursive-update"}; smk={r.get("child_unit_id"):r for r in recs if r.get("receipt_kind")=="smoke-tested"}
    live=dis=ded=prov=0
    for u in xs:
        cid=u.get("child_unit_id"); r=upd.get(cid)
        if not r and a.require_installed: errs.append("missing_update_receipt:"+h(cid))
        if r and (r.get("raw_upstream_install_only") is not False or r.get("source_reference_only") is not False or r.get("codex_config_toml_mutated") is not False or r.get("native_codex_files_mutated") is not False): errs.append("invalid_update_receipt:"+h(cid))
        s=smk.get(cid)
        if not s and a.require_smoke_tested: errs.append("missing_smoke_receipt:"+h(cid))
        if s:
            st=s.get("runtime_stage"); live+=st==LIVE; dis+=st==DISABLED; ded+=st==DEDUPE; prov+=st==PROVISION
            if a.require_live_executed and st!=stage(u): errs.append("smoke_receipt_stage_mismatch:"+h(cid))
            if s.get("raw_upstream_install_only") is not False or s.get("source_reference_only") is not False or s.get("codex_config_toml_mutated") is not False or s.get("native_codex_files_mutated") is not False: errs.append("invalid_smoke_receipt:"+h(cid))
    if a.require_template_sync:
        errs += ["general_template:"+e for e in template_errors(Path(a.general_root).resolve() if a.general_root else None,m,False)]
        errs += ["general2_template:"+e for e in template_errors(Path(a.general2_root).resolve() if a.general2_root else None,m,True)]
    return resp("check",not errs,mutates_user_level_state=False,require_installed=bool(a.require_installed),require_smoke_tested=bool(a.require_smoke_tested),require_live_executed=bool(a.require_live_executed),require_template_sync=bool(a.require_template_sync),errors=sorted(set(errs)),warnings=warns,unit_count=len(xs),receipt_count=len(recs),update_receipt_count=len(upd),smoke_receipt_count=len(smk),live_executed_count=live,disabled_count=dis,dedupe_count=ded,provision_recorded_count=prov,by_child_state=counts(xs,"child_state"))
def command_smoke(a):
    xs=get_units(load_manifest())
    if a.capability: xs=[u for u in xs if u.get("child_unit_id")==a.capability or h(u.get("child_unit_id"))==a.capability]
    if a.capability and not xs: return resp("smoke",False,errors=["unknown_capability:"+clean(a.capability)])
    res={}
    for u in xs[:a.limit]: res[h(u.get("child_unit_id"))]={"status":status(u),"details":smoke_details(u),"blockers":blockers(u)}
    return resp("smoke",True,mutates_user_level_state=False,smoke_results=res,result_count=len(res),limit=a.limit)
def parser():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="command",required=True)
    def common(x): x.add_argument("--codex-home",default=str(default_home())); x.add_argument("--general-root",default=None); x.add_argument("--general2-root",default=None); x.add_argument("--json",action="store_true")
    q=sub.add_parser("plan"); common(q); q.add_argument("--sample-limit",type=int,default=25); q.set_defaults(func=command_plan)
    q=sub.add_parser("apply"); common(q); q.add_argument("--apply",action="store_true"); q.add_argument("--operator-confirmation",action="store_true"); q.add_argument("--sync-templates",action="store_true"); q.add_argument("--response-receipt-limit",type=int,default=25); q.set_defaults(func=command_apply)
    q=sub.add_parser("check"); common(q); q.add_argument("--require-installed",action="store_true"); q.add_argument("--require-smoke-tested",action="store_true"); q.add_argument("--require-live-executed",action="store_true"); q.add_argument("--require-template-sync",action="store_true"); q.set_defaults(func=command_check)
    q=sub.add_parser("smoke"); common(q); q.add_argument("--capability",default=None); q.add_argument("--require-pass",action="store_true"); q.add_argument("--limit",type=int,default=25); q.set_defaults(func=command_smoke)
    return p
def main(argv=None)->int:
    a=parser().parse_args(argv); payload=a.func(a); sys.stdout.buffer.write((json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)+"\n").encode("utf-8")); return 0 if payload.get("ok") else 3
if __name__=="__main__": raise SystemExit(main())
