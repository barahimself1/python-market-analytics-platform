"""Limited public-tree heuristic scan. Not a complete security assessment."""
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
SKIP={'.git','.openai','__pycache__','.venv','node_modules','private','raw','archives','logs'}
PATTERNS=[re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
          re.compile(r'gh[pousr]_[A-Za-z0-9]{30,}'),
          re.compile(r'AKIA[0-9A-Z]{16}'),
          re.compile(r'sk-[A-Za-z0-9]{35,}')]


def scan(root:Path=ROOT)->list[str]:
    findings=[]
    for path in root.rglob('*'):
        relative=path.relative_to(root)
        if not path.is_file() or any(part in SKIP for part in relative.parts):
            continue
        if path.suffix in {'.pem','.key','.p12','.sqlite','.db'} or path.name=='.env' or path.name.startswith('.env.'):
            findings.append(f'Private file type: {relative}')
        if path.stat().st_size>25*1024*1024:
            findings.append(f'Large public file: {relative}')
        if path.suffix in {'.jpg','.png','.zip','.pyc'}:
            continue
        try:text=path.read_text(encoding='utf-8')
        except (UnicodeDecodeError,OSError):continue
        if any(pattern.search(text) for pattern in PATTERNS):
            findings.append(f'Possible credential pattern: {relative}')
    return findings

if __name__=='__main__':
    found=scan()
    print('\n'.join(found) if found else 'No matches in the limited public-tree scan.')
    sys.exit(bool(found))
