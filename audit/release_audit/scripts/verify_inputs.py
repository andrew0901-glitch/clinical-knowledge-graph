"""Fail-closed SHA-256 verification of the manifest-listed graph files BEFORE reading any graph content.
Checks the 107 node/edge files of the release folder (CLINICAL_KG_DATA); sources.jsonl and metadata files are
checked only if present. python verify_inputs.py [--input DIR]"""
import argparse,concurrent.futures,hashlib,json,os,pathlib,subprocess,sys,datetime
P=pathlib.Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input',type=pathlib.Path,default=pathlib.Path(os.environ.get('CLINICAL_KG_DATA',str(P.parents[1]/'data'/'clinical_kg_release_v0.2.1'))));a=ap.parse_args();root=a.input.resolve();raw=(root/'manifest.json').read_bytes();m=json.loads(raw);jobs=[]
 for family in ['nodes','edges']:
  for entry in m[family]:jobs.append(dict(entry,family=family))
 optional=[dict(m['sources'],family='sources')]+[dict(path=path,sha256=value,family='metadata') for path,value in m['metadata'].items()]
 jobs+=[j for j in optional if (root/j['path']).exists()]
 def check(r):
  p=(root/r['path']).resolve();assert p.is_relative_to(root),r['path'];h=hashlib.sha256()
  with p.open('rb') as inp:
   while b:=inp.read(8*1024*1024):h.update(b)
  actual=h.hexdigest();return dict(r,actual_sha256=actual,actual_bytes=p.stat().st_size,passed=actual==r['sha256'] and ('bytes' not in r or r['bytes']==p.stat().st_size))
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:verified=list(pool.map(check,jobs))
 result=dict(input_root='<CLINICAL_KG_DATA>',manifest_sha256=hashlib.sha256(raw).hexdigest(),verified=verified,passed=all(r['passed'] for r in verified) and sum(r['family'] in ('nodes','edges') for r in verified)==107,manifest_claims=dict(version=m.get('version'),scope=m.get('scope'),totals=m.get('totals'),exporter_git_commit=m.get('exporter_git_commit')),code_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True,cwd=P).strip(),verified_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),optional_files_not_present=[j['path'] for j in optional if not (root/j['path']).exists()])
 (P/'results/input_verification.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');assert result['passed'],[r for r in verified if not r['passed']]
 (P/'results/source_manifest.json').write_bytes(raw);print('VERIFIED',len(verified),'manifest-listed files;',result['manifest_sha256'])
if __name__=='__main__':main()
