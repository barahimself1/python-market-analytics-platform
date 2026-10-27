"""Run python -m marketlab --help for the local workflow."""
import argparse
import json
from pathlib import Path
from .build import ROOT,build
from .demo import generate
from .ingest import ingest,export


def main() -> None:
    parser = argparse.ArgumentParser(description='MarketLab public research compiler')
    sub = parser.add_subparsers(dest='command',required=True)
    demo = sub.add_parser('demo',help='Generate deterministic fictional data')
    demo.add_argument('--output',type=Path,default=ROOT/'data/public/demo.json')
    compile_cmd = sub.add_parser('build',help='Compile the static workstation')
    compile_cmd.add_argument('--input',type=Path,default=None)
    compile_cmd.add_argument('--output',type=Path,default=ROOT/'dist')
    import_cmd = sub.add_parser('ingest',help='Stream a local CSV/JSONL into private SQLite')
    import_cmd.add_argument('input',type=Path)
    import_cmd.add_argument('--database',type=Path,default=ROOT/'data/private/research.sqlite')
    import_cmd.add_argument('--mapping',type=Path)
    export_cmd = sub.add_parser('export',help='Export a small public allowlisted sample')
    export_cmd.add_argument('--database',type=Path,default=ROOT/'data/private/research.sqlite')
    export_cmd.add_argument('--output',type=Path,default=ROOT/'data/public/imported.json')
    export_cmd.add_argument('--limit',type=int,default=5000)
    args = parser.parse_args()
    try:
        if args.command == 'demo':
            generate(args.output)
            print('Synthetic demonstration created.')
        elif args.command == 'build':
            source = args.input or ROOT/json.loads((ROOT/'research/build-config.json').read_text())['dataset']
            print(json.dumps(build(source,args.output)))
        elif args.command == 'ingest':
            print(json.dumps(ingest(args.input,args.database,json.loads(args.mapping.read_text()) if args.mapping else None),indent=2))
        else:
            print(json.dumps(export(args.database,args.output,args.limit)))
    except (OSError,ValueError,KeyError) as error:
        parser.exit(1,f'Unable to complete {args.command}: {error}\n')

if __name__ == '__main__':
    main()
