"""Validate on stage-zero data only, before confirmation contract freeze."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from exp002.campaign import atomic_json, environment, now, read_json
from exp003.confirmation import FOLDER, snapshot, verify_development

if __name__ == '__main__':
    if (FOLDER/'contract.json').exists():
        raise SystemExit('Cannot replace validation after confirmation freeze')
    prerequisites = verify_development(full=True)
    print('All audited development artifact hashes verified', flush=True)
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.discover(str(ROOT/'tests'), pattern='test_*.py', top_level_dir=str(ROOT)))
    report = {'status': 'passed' if result.wasSuccessful() and not result.skipped else 'failed',
              'created_utc': now(), 'tests_run': result.testsRun,
              'failures': [{'test': str(t), 'traceback': tb} for t, tb in result.errors+result.failures],
              'skipped': [str(t) for t, _ in result.skipped], 'code_snapshot': snapshot(),
              'environment': environment(), 'development': prerequisites,
              'scope': 'Stage-zero tests only; confirmation inputs not generated'}
    atomic_json(ROOT/'research/exp003_confirmation_validation.json', report)
    print({k: report[k] for k in ('status', 'tests_run', 'failures')})
    raise SystemExit(report['status'] != 'passed')
