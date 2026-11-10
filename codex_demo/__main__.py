import argparse
import json
import sys
from .core import run, scenario, verify_receipt

LIMIT = 65536

def read_json(path):
    with open(path, 'rb') as stream:
        data = stream.read(LIMIT + 1)
    if len(data) > LIMIT:
        raise ValueError('Input exceeds 64 KiB')
    return json.loads(data)

def main(argv=None):
    parser = argparse.ArgumentParser(description='Synthetic offline triage; no live execution')
    commands = parser.add_subparsers(dest='command', required=True)
    triage = commands.add_parser('run')
    source = triage.add_mutually_exclusive_group(required=True)
    source.add_argument('--scenario', choices=['routine', 'human_gate', 'tampered'])
    source.add_argument('--input')
    verify = commands.add_parser('verify')
    verify.add_argument('receipt')
    args = parser.parse_args(argv)
    try:
        if args.command == 'verify':
            if not verify_receipt(read_json(args.receipt)):
                raise ValueError('Receipt hash mismatch')
            print(json.dumps({'integrity': 'MATCH', 'authenticity': 'NOT_ESTABLISHED'}))
            return 0
        result = run(scenario(args.scenario) if args.scenario else read_json(args.input))
        print(json.dumps(result, sort_keys=True, indent=2))
        return 3 if result['receipt']['decision'] == 'HUMAN_GATE' else 0
    except (ValueError, TypeError, OSError, RecursionError) as error:
        print(json.dumps({'status': 'REJECTED', 'error': str(error)}), file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
