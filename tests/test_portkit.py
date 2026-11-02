import csv
import json
import tempfile
import unittest
from pathlib import Path
from portkit.analyze import analyze_rpgmaker, inspect_png
from portkit.profile import analyze_frames, percentile
from portkit.cli import main
from portkit.runtime import (EventInstruction, EventProgram, InputState, MapLifecycle,
                             ResourceBudget, SaveSnapshot, renderer_diagnostics)


class PortKitTests(unittest.TestCase):
    def test_rpg_maker_structure_only(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); (root/'data').mkdir()
            sample = {'events': [None, {'name': 'Never copy this text', 'pages': [
                {'list': [{'code': 355, 'parameters': ['secret protected script']}, {'code': 0}]}]}]}
            (root/'data'/'Map001.json').write_text(json.dumps(sample), encoding='utf-8')
            report = analyze_rpgmaker(root)
            self.assertEqual(report['map_count'], 1)
            self.assertEqual(report['script_command_count'], 1)
            self.assertNotIn('secret protected', json.dumps(report))

    def test_profile(self):
        with tempfile.TemporaryDirectory() as td:
            f = Path(td)/'frames.csv'
            f.write_text('scene,work_ms,total_ms\nwalk,16,33.3\nwalk,34,50\n')
            report = analyze_frames(f)
            self.assertEqual(report['scenes']['walk']['work_ms']['over_budget_count'], 1)
            self.assertEqual(report['scenes']['walk']['total_ms']['max_ms'], 50)

    def test_invalid_profile_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            f = Path(td)/'bad.csv'; f.write_text('work_ms,total_ms\n45,20\n')
            with self.assertRaises(ValueError):
                analyze_frames(f)

    def test_png_header(self):
        with tempfile.TemporaryDirectory() as td:
            f = Path(td)/'tiny.png'; import struct
            f.write_bytes(b'\x89PNG\r\n\x1a\n' + b'\x00\x00\x00\rIHDR' + struct.pack('>II', 2048, 16))
            self.assertTrue(inspect_png(f)['exceeds_1024_dimension'])

    def test_init(self):
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td)/'test'
            main(['init', str(dest), '--name', 'My demo'])
            self.assertIn('My demo', (dest/'Makefile').read_text())
            with self.assertRaises(SystemExit):
                main(['init', str(dest)])

    def test_prepare_texture(self):
        from PIL import Image
        from portkit.textures import prepare_texture
        with tempfile.TemporaryDirectory() as td:
            src = Path(td)/'input.png'; dest = Path(td)/'out.png'
            Image.new('RGBA', (10, 5)).save(src)
            manifest = Path(td)/'out.manifest.json'
            report = prepare_texture(src, dest, manifest_path=manifest)
            self.assertEqual(report['output_dimensions'], (16, 8))
            self.assertTrue(dest.is_file())
            self.assertTrue(manifest.is_file())
            with self.assertRaises(ValueError):
                prepare_texture(src, dest)

    def test_percentile(self):
        self.assertEqual(percentile([1, 2, 3, 4, 5], 95), 5)

    def test_generic_runtime_contracts(self):
        event = EventProgram('gate', (EventInstruction('set_flag', {'open': True}),))
        world = MapLifecycle('synthetic-map', 2, 2, (0, 1, 0, 0), (event,))
        world.validate()
        SaveSnapshot(1, 'synthetic-map', (0, 0), {'open': True}).validate()
        self.assertEqual(InputState(pressed=frozenset({'A'})).pressed, frozenset({'A'}))
        diagnostics = renderer_diagnostics(12, 33, 1024, ResourceBudget(max_texture_bytes=2048))
        self.assertTrue(diagnostics['resident_within_texture_budget'])
        with self.assertRaises(ValueError):
            EventProgram('unsafe', (EventInstruction('script'),)).validate()

if __name__ == '__main__':
    unittest.main()
