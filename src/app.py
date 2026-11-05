"""CLI for the integrated reliable recommendation assistant."""
import argparse
import json
from pathlib import Path
from .assistant import RecommendationAssistant

DEFAULT_CATALOG = Path(__file__).resolve().parents[1] / 'data' / 'songs.csv'


def main():
    """Read one explicit JSON request and print a reproducible response."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request', required=True, help='JSON object containing genre, mood, and energy')
    parser.add_argument('--catalog', type=Path, default=DEFAULT_CATALOG)
    parser.add_argument('--trace-file', type=Path, help='Optional local JSON output log')
    args = parser.parse_args()
    try:
        request = json.loads(args.request)
        result = RecommendationAssistant(args.catalog).answer(request)
    except (ValueError, OSError) as exc:
        result = {'status': 'error', 'message': str(exc), 'recommendations': [], 'trace': []}
    output = json.dumps(result, indent=2, allow_nan=False)
    print(output)
    if args.trace_file:
        args.trace_file.parent.mkdir(parents=True, exist_ok=True)
        args.trace_file.write_text(output + '\n', encoding='utf-8')
    return 1 if result['status'] == 'error' else 0


if __name__ == '__main__':
    raise SystemExit(main())
