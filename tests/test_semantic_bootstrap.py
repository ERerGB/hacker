"""Synthetic parser/vector regressions; never call an Ollama server."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/semantic_bootstrap_ollama.py'
spec = importlib.util.spec_from_file_location('semantic_bootstrap', SCRIPT)
helper = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = helper
spec.loader.exec_module(helper)


class BootstrapTests(unittest.TestCase):
    def test_help_does_not_contact_server(self):
        with patch.object(sys, 'argv', [str(SCRIPT), '--help']), patch.object(helper.urllib.request, 'urlopen') as request:
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as result:
                helper.main()
            self.assertEqual(result.exception.code, 0)
            request.assert_not_called()

    def test_invalid_options_fail_before_server_access(self):
        for args in (['--typo'], ['--core-file'], ['model', 'extra']):
            with self.subTest(args=args), patch.object(sys, 'argv', [str(SCRIPT), *args]), patch.object(helper.urllib.request, 'urlopen') as request:
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as result:
                    helper.main()
                self.assertEqual(result.exception.code, 2)
                request.assert_not_called()

    def test_core_file_and_explicit_model(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'core.txt'
            path.write_text(' synthetic core \n')
            self.assertEqual(helper.parse_args(['example', '--core-file', str(path)]), ('example', 'synthetic core'))

    def test_invalid_embeddings_do_not_become_scores(self):
        for vector in ([], [0, 0], [True, 1], ['1'], [float('nan')], [float('inf')], {'x': 1}):
            with self.subTest(vector=vector):
                response = io.BytesIO(json.dumps({'embedding': vector}).encode())
                with patch.object(helper.urllib.request, 'urlopen', return_value=response), self.assertRaises(ValueError):
                    helper.embed('synthetic', 'fixture')

    def test_zero_or_mismatched_vectors_are_not_orthogonality(self):
        for a, b in (([0, 0], [1, 0]), ([1], [1, 2]), ([float('nan')], [1])):
            with self.subTest(a=a, b=b), self.assertRaises(ValueError):
                helper.cosine(a, b)

    def test_cosine_supports_valid_and_large_finite_vectors(self):
        self.assertEqual(helper.cosine([1, 0], [0, 1]), 0)
        self.assertAlmostEqual(helper.cosine([1e200, 1e200], [1e200, 1e200]), 1)
        self.assertAlmostEqual(helper.cosine([1, 2], [-1, -2]), -1)


if __name__ == '__main__':
    unittest.main()
