import json
from pathlib import Path
import tempfile
import unittest
from allegro_export import devices, pin_mapping

DEVICE = '''(DEVICE FILE: TEST)
PACKAGE TEST_PKG
PINCOUNT 4
PINORDER UNIT_A "IN A",
    "OUT A"
PINUSE UNIT_A IN,
    OUT
PINORDER UNIT_B "IN B" "OUT B"
PINUSE UNIT_B IN OUT
FUNCTION G1 UNIT_A 1,
    2
FUNCTION G2 UNIT_B 3 4
PACKAGEPROP PART_NAME TEST_SYMBOL
PACKAGEPROP VALUE TEST_MPN
'''

class DeviceExportTests(unittest.TestCase):
    def parse(self, content=DEVICE):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "devices.map").write_text("'ORIGINAL_NAME' 'test.txt';\n")
            (root / "test.txt").write_text(content)
            # The map lists only some files: also import unmapped device files.
            (root / "unmapped.txt").write_text(content)
            return devices(root)

    def test_multiline_multiunit_and_unmapped_files(self):
        rows = self.parse()
        self.assertEqual({r["Device"] for r in rows}, {"ORIGINAL_NAME", "UNMAPPED"})
        self.assertEqual(json.loads(rows[0]["Pin_Order"])["UNIT_A"], ["IN A", "OUT A"])
        pins = pin_mapping(rows)
        self.assertEqual(len(pins), 8)
        self.assertEqual([(p["Gate"], p["Pin_Name"], p["Physical_Pin"], p["Pin_Use"])
                          for p in pins[:4]],
                         [("G1", "IN A", "1", "IN"), ("G1", "OUT A", "2", "OUT"),
                          ("G2", "IN B", "3", "IN"), ("G2", "OUT B", "4", "OUT")])

    def test_mismatched_gate_rejected(self):
        with self.assertRaisesRegex(ValueError, "Inconsistent pin mapping"):
            pin_mapping(self.parse(DEVICE.replace("FUNCTION G2 UNIT_B 3 4", "FUNCTION G2 UNIT_B 3")))

    def test_declared_pin_count_rejected(self):
        with self.assertRaisesRegex(ValueError, "PINCOUNT mismatch"):
            pin_mapping(self.parse(DEVICE.replace("PINCOUNT 4", "PINCOUNT 5")))

if __name__ == "__main__":
    unittest.main()
