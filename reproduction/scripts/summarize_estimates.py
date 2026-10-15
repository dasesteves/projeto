"""Independent export of the historical mean-estimate aggregation, not expression."""
import argparse
from collections import defaultdict
import csv
import math
from pathlib import Path
from check_inputs import inspect_table, TABLES

def summarize(source, destination):
    report = inspect_table(source, TABLES['zperturb_beta_bin_results_broadtype_clean.csv'])
    if report['errors']:
        raise ValueError('; '.join(report['errors']))
    grouped = defaultdict(list)
    with source.open(encoding='utf-8-sig', newline='') as handle:
        for row in csv.DictReader(handle):
            group = row['cell_group'].lower()
            if 'phore' in group or 'pigmented' in group:
                grouped[(row['gene1'], row['timepoint'])].append(float(row['estimate']))
    # Exclusive creation: never overwrite a historical or previous result.
    with destination.open('x', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow(['gene1', 'timepoint', 'mean_model_estimate', 'source_rows'])
        for (gene, time), values in sorted(grouped.items(), key=lambda item: (item[0][0], float(item[0][1]))):
            writer.writerow([gene, time, math.fsum(values) / len(values), len(values)])
    return len(grouped)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(f'{summarize(args.input, args.output)} grupos exportados; não são medições de expressão nem testes de expressão diferencial.')
