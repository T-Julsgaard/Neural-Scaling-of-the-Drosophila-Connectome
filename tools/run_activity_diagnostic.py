"""Validate, freeze, run and audit the prospective EXP-004 diagnostic."""
import argparse
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['validate','development','audit-development','evaluation','audit-evaluation'])
    parser.add_argument('--workers', type=int, choices=(1,2,3), default=3)
    args = parser.parse_args()
    from exp004.campaign import validate, run
    if args.command == 'validate':
        validate()
    elif args.command.startswith('audit-'):
        from exp004.audit import audit
        audit(args.command.removeprefix('audit-'))
    else:
        run(args.command, args.workers)
