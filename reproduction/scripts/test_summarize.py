import csv
from pathlib import Path
import tempfile
import unittest
from summarize_estimates import summarize

class SummaryTests(unittest.TestCase):
    def test_mean_filter_time_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'source.csv'
            output = Path(directory) / 'output.csv'
            source.write_text('cell_group,gene1,timepoint,estimate\nmelanophore,a,18,-2\niridophore,a,18,4\nfin,a,18,100\nxanthophore,a,24,5\n', encoding='utf-8')
            self.assertEqual(2, summarize(source, output))
            with output.open(newline='') as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(['1.0', '5.0'], [row['mean_model_estimate'] for row in rows])
            self.assertEqual(['2', '1'], [row['source_rows'] for row in rows])
            original = output.read_bytes()
            with self.assertRaises(FileExistsError):
                summarize(source, output)
            self.assertEqual(original, output.read_bytes())

if __name__ == '__main__':
    unittest.main()
