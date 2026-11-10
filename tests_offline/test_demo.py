import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from codex_demo.core import envelope, run, scenario, verify_receipt

ROOT = Path(__file__).resolve().parents[1]

def changed(**fields):
    event = scenario('routine')['event']
    event.update(fields)
    return envelope(event)

def cli(*args):
    return subprocess.run([sys.executable, '-m', 'codex_demo', *args], cwd=ROOT, capture_output=True, text=True, timeout=10)

class DemoTests(unittest.TestCase):
    def test_routine(self):
        receipt = run(scenario('routine'))
        self.assertTrue(verify_receipt(receipt))
        self.assertEqual(receipt['receipt']['decision'], 'SIMULATED')
        self.assertFalse(receipt['receipt']['executed'])

    def test_deterministic(self):
        self.assertEqual(run(scenario('routine')), run(scenario('routine')))

    def test_tampered(self):
        with self.assertRaises(ValueError):
            run(scenario('tampered'))

    def test_gate_categories(self):
        for field, values in {'domain': ['KINETIC', 'BIO', 'SPACE', 'OT', 'ICS', 'OT/ICS'], 'classification': ['TOP_SECRET', 'TS_SCI'], 'operation': ['master_shard', 'registry_change', 'doctrine_change', 'funding', 'multi_theater_scaleup'], 'shield_impact': [8.51, 9, 10]}.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    result = run(changed(**{field: value}))['receipt']
                    self.assertEqual(result['decision'], 'HUMAN_GATE')
                    self.assertFalse(result['executed'])
                    self.assertFalse(result['trace'][3]['simulation_completed'])

    def test_threshold_boundary(self):
        self.assertEqual(run(changed(shield_impact=8.5))['receipt']['decision'], 'SIMULATED')

    def test_invalid_inputs(self):
        for fields in [{'synthetic': False}, {'domain': 'UNKNOWN'}, {'domain': []}, {'operation': 'approve'}, {'classification': 'unknown'}, {'anomaly_score': True}, {'anomaly_score': -1}, {'anomaly_score': 2}, {'anomaly_score': '0.2'}, {'anomaly_score': float('nan')}, {'shield_impact': 11}, {'approval': True}, {'id': ''}]:
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                run(changed(**fields))

    def test_receipt_tamper(self):
        receipt = run(scenario('routine'))
        receipt['receipt']['executed'] = True
        self.assertFalse(verify_receipt(receipt))

    def test_cli_scenarios(self):
        for name, expected in [('routine', 0), ('human_gate', 3), ('tampered', 2)]:
            with self.subTest(name=name):
                result = cli('run', '--scenario', name)
                self.assertEqual(result.returncode, expected, result.stderr)
                self.assertIsInstance(json.loads(result.stdout or result.stderr), dict)

    def test_cli_receipt_verification(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'receipt.json'
            path.write_text(cli('run', '--scenario', 'routine').stdout)
            self.assertEqual(cli('verify', str(path)).returncode, 0)
            value = json.loads(path.read_text())
            value['receipt']['executed'] = True
            path.write_text(json.dumps(value))
            self.assertEqual(cli('verify', str(path)).returncode, 2)

    def test_cli_malformed_and_oversized(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'input.json'
            for content in ['{', 'x' * 65537]:
                path.write_text(content)
                self.assertEqual(cli('run', '--input', str(path)).returncode, 2)

if __name__ == '__main__':
    unittest.main()
