"""Check BOM hierarchy boundaries and malformed-row handling."""

from pathlib import Path
import tempfile
import unittest

from import_library import bom_rows


class BomTests(unittest.TestCase):
    def parse(self, text):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bom.csv"
            path.write_text(text, encoding="utf-8")
            return bom_rows(path)

    def test_module_and_alternative_references_do_not_become_main_board(self):
        records = self.parse('ID,Description,Quantity,底数,Designator,MPN,Manufactor\n'
                             '2.1,Module,1,1,U25,MOD,TEST\n'
                             '2.1.1,Internal IC,1,1,U1,INTERNAL,TEST\n'
                             '2.2,Main IC,1,1,U1,MAIN,TEST\n'
                             '2.2.D,Alternative IC,1,1,U1,ALT,TEST\n'
                             '2.130,PCB,1,1,,,\n\x0c\n')
        self.assertEqual([r['Scope'] for r in records],
                         ['main_board', 'subassembly', 'main_board', 'alternative', 'non_pcb'])
        self.assertEqual([r['MPN'] for r in records if r['Scope']=='main_board'], ['MOD', 'MAIN'])

    def test_nonblank_truncated_row_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Malformed'):
            self.parse('ID,Description,Quantity,底数,Designator,MPN,Manufactor\n2.1,Truncated\n')


if __name__ == '__main__':
    unittest.main()
