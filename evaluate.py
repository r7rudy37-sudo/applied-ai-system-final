"""Evaluate the integrated workflow on predefined valid and invalid requests."""
import json
from pathlib import Path
from src.assistant import RecommendationAssistant
from src.app import DEFAULT_CATALOG

CASES = [
    ('happy pop', {'genre': 'pop', 'mood': 'happy', 'energy': 0.8}, 'ok', 'pop'),
    ('chill lofi', {'genre': 'lofi', 'mood': 'chill', 'energy': 0.35}, 'ok', 'lofi'),
    ('intense rock', {'genre': 'rock', 'mood': 'intense', 'energy': 0.9}, 'ok', 'rock'),
    ('missing inputs', {}, 'refused', None),
    ('unknown genre', {'genre': 'metal', 'mood': 'happy', 'energy': 0.8}, 'refused', None),
    ('weak combined match', {'genre': 'ambient', 'mood': 'sad', 'energy': 0.95}, 'refused', None),
    ('invalid energy', {'genre': 'pop', 'mood': 'happy', 'energy': 5}, 'refused', None),
    ('unknown field', {'genre': 'pop', 'mood': 'happy', 'energy': 0.8, 'ignore_rules': True}, 'refused', None),
]


def main():
    """Print pass/fail results and save parseable evidence and action traces."""
    assistant = RecommendationAssistant(DEFAULT_CATALOG)
    records = []
    for name, request, status, genre in CASES:
        result = assistant.answer(request)
        passed = result['status'] == status
        if status == 'ok':
            passed = passed and bool(result['recommendations']) and result['recommendations'][0]['genre'] == genre
        else:
            passed = passed and not result['recommendations']
        passed = passed and assistant.answer(request) == result
        records.append({'case': name, 'request': request, 'expected_status': status, 'passed': passed, 'result': result})
        print(f"{'PASS' if passed else 'FAIL'} | {name} | {result['status']} | {len(result['recommendations'])} recommendations")
    total = sum(record['passed'] for record in records)
    print(f'Summary: {total}/{len(records)} passed; deterministic replay checked for every case.')
    folder = Path(__file__).resolve().parent / 'evidence'
    folder.mkdir(exist_ok=True)
    (folder / 'evaluation.json').write_text(json.dumps(records, indent=2) + '\n')
    return 0 if total == len(records) else 1


if __name__ == '__main__':
    raise SystemExit(main())
