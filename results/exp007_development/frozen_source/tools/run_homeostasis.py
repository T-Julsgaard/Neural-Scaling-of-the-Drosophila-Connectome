"""EXP-007 command line."""
import os
import sys
from pathlib import Path
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

if __name__ == '__main__':
    import argparse
    from exp007.campaign import validate, run, audit, analyze
    p = argparse.ArgumentParser()
    p.add_argument('command', choices=('validate', 'development', 'confirmation', 'audit-development', 'audit-confirmation', 'analyze-confirmation'))
    p.add_argument('--workers', type=int, choices=(1, 2, 3), default=3)
    a = p.parse_args()
    if a.command == 'validate': validate()
    elif a.command.startswith('audit-'): audit(a.command[6:])
    elif a.command.startswith('analyze-'): analyze(a.command[8:])
    else: run(a.command, a.workers)
