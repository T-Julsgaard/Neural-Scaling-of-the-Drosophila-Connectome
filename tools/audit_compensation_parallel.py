"""I/O-only acceleration of frozen EXP-009 audit; scientific runner unchanged.

Historical hashes are recomputed once with 16 file-reading threads, then supplied
to the unmodified auditor. All new scientific files are still hashed live.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import time
from tools import run_compensation as audit

def main():
    start=time.perf_counter(); cpu=time.process_time()
    history=json.loads((audit.ROOT/'research/exp009_historical_hashes.json').read_text())
    def check(item):
        name,expected=item; path=audit.ROOT/name
        actual=hashlib.sha256(path.read_bytes()).hexdigest()
        if actual!=expected: raise ValueError('Historical drift: '+name)
        return path.resolve(),actual
    with ThreadPoolExecutor(max_workers=16) as pool:
        hashes=dict(pool.map(check,history.items()))
    metrics=dict(files=len(hashes),wall_seconds=time.perf_counter()-start,cpu_seconds=time.process_time()-cpu,io_threads=16,
                 wrapper_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    original=audit.sha
    def cached_historical(path):
        value=hashes.get(path.resolve())
        return original(path) if value is None else value
    audit.sha=cached_historical
    audit.audit()
    metrics['total_audit_wall_seconds']=time.perf_counter()-start
    metrics['total_audit_cpu_seconds']=time.process_time()-cpu
    audit.write(audit.OUT/'historical_parallel_audit.json',metrics)
    print(json.dumps(metrics))

if __name__=='__main__': main()
