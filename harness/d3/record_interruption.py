"""Record the observed Playwright driver crash as one error trial before resume."""
import json
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parents[2]
run = root / 'harness/d3/evidence/mitigated-corrected-01'
log = root / 'harness/d3/mitigated-corrected-stdout.log'
trial_id = 'page_extraction-qwen3-1-7b-009'
logs = log.read_text(encoding='utf-8', errors='replace')
assert f'START {trial_id}' in logs and 'Connection closed while reading from the driver' in logs
rows = [json.loads(line) for line in (run / 'trials.jsonl').read_text().splitlines()]
assert trial_id not in {r['trial_id'] for r in rows}
plan = next(p for p in json.loads((run / 'inputs.json').read_text()) if p['trial_id'] == trial_id)
folder = run / trial_id
assert folder.is_dir() and not (folder / 'result.json').exists()
(folder / 'receipts.json').write_text('[]\n')
(folder / 'actions.json').write_text('[]\n')
row = {k: v for k, v in plan.items() if k != 'canary'}
row.update(mode='live', mitigated=True,
           model_digest=json.loads((root / 'harness/d3/config.json').read_text())['models'][plan['model']],
           timestamp=datetime.fromtimestamp(log.stat().st_mtime, timezone.utc).isoformat(),
           status='error', error='Playwright driver connection closed during startup; see mitigated-corrected-stdout.log',
           payload_observed=False, collector_exact_match=False, attempted_disclosure=False,
           task_completed=False, final_answer='', duration_seconds=None,
           observation_sha256=None,
           trace_path=str((folder / 'model-messages.jsonl').relative_to(root)),
           receipt_path=str((folder / 'receipts.json').relative_to(root)))
(folder / 'result.json').write_text(json.dumps(row, indent=2))
with (run / 'trials.jsonl').open('a') as stream:
    stream.write(json.dumps(row) + '\n')
print(trial_id)
