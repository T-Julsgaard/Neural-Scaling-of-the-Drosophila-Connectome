"""Run EXP-005 with a frozen prospective contract."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

if __name__ == '__main__':
    import argparse
    from exp005.campaign import validate, run, audit
    p = argparse.ArgumentParser()
    p.add_argument('command',choices=('validate','development','evaluation','audit-development','audit-evaluation'))
    p.add_argument('--workers',type=int,choices=(1,2,3),default=3)
    args = p.parse_args()
    if args.command == 'validate': validate()
    elif args.command.startswith('audit-'): audit(args.command[6:])
    else: run(args.command,args.workers)
