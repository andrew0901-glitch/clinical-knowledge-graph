"""Scan the audit/ tree (or any paths) for secrets, credentials, internal hostnames and personal machine paths
before committing. Exits non-zero on any finding. This file is excluded from its own scan (it contains the patterns).

  python audit/tools/safety_scan.py [paths...]          (default: audit/)
"""
import json, pathlib, re, sys

PATTERNS = {
    'personal_or_machine_path': r'(/home/[A-Za-z0-9_.-]+|/Users/[A-Za-z0-9_.-]+|/mnt/[a-z]/|[A-Za-z]:\\Users|OneDrive|/root/|/tmp/claude)',
    'username_or_owner_name': r'ldeveza|ldeve\b|Lunas AI/Manuscripts',
    'aws_access_key': r'\b(AKIA|ASIA)[0-9A-Z]{16}\b',
    'aws_secret_or_token_assignment': r'(?i)(aws_secret_access_key|aws_session_token|secret[_-]?access[_-]?key)\s*[:=]',
    'private_key_block': r'-----BEGIN [A-Z ]*PRIVATE KEY-----',
    'huggingface_token': r'\bhf_[A-Za-z0-9]{30,}\b',
    'github_token': r'\b(ghp|gho|ghu|ghs|ghr|github_pat)_[A-Za-z0-9_]{30,}\b',
    'api_key_like': r'\b(sk|pk|rk)-[A-Za-z0-9]{20,}\b|\bxox[abprs]-[A-Za-z0-9-]{10,}',
    'bearer_token': r'(?i)\bbearer\s+[A-Za-z0-9._~+/=-]{20,}',
    'password_or_key_assignment': r'(?i)\b(password|passwd|pwd|api[_-]?key|secret|token)\b\s*[:=]\s*["\']?[A-Za-z0-9/+_.-]{8,}',
    'internal_host': r'(?i)(\.rds\.amazonaws\.com|\.elb\.amazonaws\.com|\.compute\.amazonaws\.com|\.internal\b|\.corp\b|\.local\b|lunasai-pg|neo4j\+s://|bolt://|postgres(ql)?://)',
    'private_ip': r'\b(10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b',
    'ssh_or_pem': r'(?i)\.pem\b|ssh -i|id_rsa',
    'email_address': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z0-9.-]+\b',
    'annotation_layer_file': r'jev_[a-z_]+\.(jsonl|json)',
}
ALLOW_EMAIL = re.compile(r'(noreply@|@users\.noreply\.github\.com|@example\.)')
SKIP_SUFFIX = {'.png', '.gz', '.parquet', '.duckdb', '.pdf', '.pyc'}
me = pathlib.Path(__file__).resolve()
roots = [pathlib.Path(p) for p in sys.argv[1:]] or [me.parents[1]]
findings, scanned = [], 0
for root in roots:
    for f in sorted([root] if root.is_file() else root.rglob('*')):
        if not f.is_file() or f.resolve() == me or f.suffix in SKIP_SUFFIX or '.git' in f.parts:
            continue
        try:
            text = f.read_text(errors='strict')
        except UnicodeDecodeError:
            findings.append(dict(file=str(f), pattern='non_text_file', line=0, excerpt='binary content not scanned')); continue
        scanned += 1
        for i, line in enumerate(text.splitlines(), 1):
            for name, rx in PATTERNS.items():
                for m in re.finditer(rx, line):
                    if name == 'email_address' and ALLOW_EMAIL.search(m.group(0)):
                        continue
                    findings.append(dict(file=str(f), pattern=name, line=i, excerpt=line[max(0, m.start() - 30):m.end() + 30]))
report = dict(files_scanned=scanned, patterns=sorted(PATTERNS), findings=len(findings), details=findings[:200])
print(json.dumps({k: v for k, v in report.items() if k != 'details'}, indent=1))
for x in findings[:60]:
    print(f"{x['pattern']:32s} {x['file']}:{x['line']}  {x['excerpt'][:110]!r}")
sys.exit(1 if findings else 0)
