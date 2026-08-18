from pathlib import Path
import json, sys, yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
errors = []

# Load canonical architecture reference.
arch = yaml.safe_load((ROOT / 'governance' / 'architecture-reference.yaml').read_text())

# Validate each work-item mandate and architecture binding.
work_schema = json.loads((ROOT / 'schemas' / 'work-item.schema.json').read_text())
for mandate_path in (ROOT / 'work').glob('*/mandate.yaml'):
    data = yaml.safe_load(mandate_path.read_text())
    try:
        validate(instance=data, schema=work_schema)
    except Exception as exc:
        errors.append(f'{mandate_path}: schema validation failed: {exc}')
        continue
    a = data.get('architecture', {})
    if a.get('id') != arch.get('architecture_id'):
        errors.append(f'{mandate_path}: architecture id mismatch')
    if str(a.get('version')) != str(arch.get('version')):
        errors.append(f'{mandate_path}: architecture version mismatch')
    if a.get('hash') != arch.get('sha256'):
        errors.append(f'{mandate_path}: architecture hash mismatch')
    if data.get('task_class') in ('T2','T3') and not data.get('approval_ref'):
        errors.append(f'{mandate_path}: T2/T3 requires approval_ref')

# Check required collaboration files.
for rel in ['AGENTS.md','schemas/work-item.schema.json','schemas/handoff.schema.json','schemas/evidence.schema.json']:
    if not (ROOT / rel).exists():
        errors.append(f'missing required file: {rel}')

if errors:
    print('\n'.join(errors))
    sys.exit(1)
print('Agent workspace validation PASS')
