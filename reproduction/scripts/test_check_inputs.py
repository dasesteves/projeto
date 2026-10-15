import tempfile
import unittest
from pathlib import Path
from check_inputs import inspect_table

class PreflightTests(unittest.TestCase):
    def check(self, content):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'input.csv'
            if content is not None:
                path.write_text(content, encoding='utf-8')
            return inspect_table(path, {'cell_group', 'gene1', 'timepoint', 'estimate'})

    def test_missing(self):
        self.assertTrue(self.check(None)['errors'])

    def test_missing_columns(self):
        self.assertTrue(self.check('gene1\na\n')['errors'])

    def test_empty(self):
        self.assertTrue(self.check('cell_group,gene1,timepoint,estimate\n')['errors'])

    def test_invalid_number(self):
        self.assertTrue(self.check('cell_group,gene1,timepoint,estimate\nmelanophore,a,18,NA\n')['errors'])

    def test_wrong_shape(self):
        self.assertTrue(self.check('cell_group,gene1,timepoint,estimate\nmelanophore,a,18\n')['errors'])

    def test_no_matching_group(self):
        self.assertTrue(self.check('cell_group,gene1,timepoint,estimate\nfin,a,18,1\n')['errors'])

    def test_valid_filter_and_negative_estimate(self):
        report = self.check('cell_group,gene1,timepoint,estimate\nMelanophore,a,18,-0.2\npigmented cells,b,24,1\nfin,c,18,NA\n')
        self.assertEqual([], report['errors'])
        self.assertEqual(2, report['pigment_rows'])
        self.assertEqual(3, report['rows'])

if __name__ == '__main__':
    unittest.main()
