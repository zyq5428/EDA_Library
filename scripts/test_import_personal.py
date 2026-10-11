"""Check exact reference extraction and protection against ambiguous inputs."""
from pathlib import Path
import tempfile
import unittest
from import_personal import files_by_name, script_references
from capture_library import package_streams

class PersonalImportTests(unittest.TestCase):
    def test_script_references_keep_exact_names(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'model.scr'
            p.write_text('newdrawfillin "MODEL.dra" "Package Symbol"\nFORM mini pad_name r116_181r20\nFORM pkgmap3d stplist MODEL-LQ.step\n',encoding='utf-8')
            result=script_references([p])['model']
            self.assertEqual(result['pads'],{'r116_181r20'})
            self.assertEqual(result['steps'],{'MODEL-LQ.step'})
            self.assertNotIn('MODEL.step',result['steps'])

    def test_different_bytes_same_casefold_name_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            a=Path(directory)/'SOT23.dra'; b=Path(directory)/'sot23.dra'
            a.write_bytes(b'first');b.write_bytes(b'second')
            with self.assertRaisesRegex(ValueError,'Conflicting input names'):
                files_by_name([a,b])

    def test_invalid_compound_file_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'invalid.olb';p.write_bytes(b'not a library')
            with self.assertRaises(ValueError):package_streams(p)

if __name__=='__main__':unittest.main()
