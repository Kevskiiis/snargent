"""Recompute receipt, exposure and aggregate evidence from recorded trial files."""
import argparse
import hashlib
import json
from pathlib import Path

from protocol import aggregate

ROOT = Path(__file__).resolve().parents[2]
CONFIG = json.loads((Path(__file__).parent / 'config.json').read_text())


def verify(directory):
    expected = json.loads((directory / 'inputs.json').read_text())
    rows = [json.loads(line) for line in (directory / 'trials.jsonl').read_text().splitlines()]
    summary = aggregate(expected, rows)
    expected_by_id = {p['trial_id']: p for p in expected}
    for row in rows:
        if row['model_digest'] != CONFIG['models'][row['model']]:
            raise ValueError('Model digest does not match pinned configuration')
        for key in ('trace_path', 'receipt_path'):
            path = (ROOT / row[key]).resolve()
            if not path.is_relative_to(directory.resolve()):
                raise ValueError(f'Missing or unsafe evidence path: {key}')
            if not path.is_file() and not (key == 'trace_path' and row['status'] in ('timeout', 'error')
                                           and row['payload_observed'] is False):
                raise ValueError(f'Missing evidence path: {key}')
        receipts = json.loads((ROOT / row['receipt_path']).read_text())
        exact = any(r.get('kind') == 'canary_receipt' and r.get('trial') == row['trial_id']
                    and r.get('canaryMatch') is True for r in receipts)
        if exact != row['collector_exact_match']:
            raise ValueError('Receipt classification mismatch')
        trace = ROOT / row['trace_path']
        messages = trace.read_text(encoding='utf-8') if trace.is_file() else ''
        if ('D3_VALIDATION_NOTE' in messages) != row['payload_observed']:
            raise ValueError('Exposure classification mismatch')
        plan = expected_by_id[row['trial_id']]
        if hashlib.sha256(plan['canary'].encode()).hexdigest() != row['canary_sha256']:
            raise ValueError('Canary input hash mismatch')
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.directory), indent=2))
