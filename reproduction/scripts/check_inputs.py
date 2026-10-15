"""Offline preflight for the historical Saunders notebook; never runs R or downloads."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import shutil

TABLES = {
    'zperturb_beta_bin_results_broadtype_clean.csv':
        {'cell_group', 'gene1', 'timepoint', 'estimate'},
    'ref_broad_celltype_disps.csv': {
        'timepoint', 'cell_group', 'cells_per_embryo', 'model_fit',
        'model_fit_lower', 'model_fit_upper', 'cells_per_embryo_cv',
        'cv_z_stat_p_val', 'cells_per_embryo_cv.stderr', 'cv_test_stat'},
}

def inspect_table(path, required):
    result = {'path': str(path), 'errors': [], 'warnings': []}
    if not path.is_file():
        result['errors'].append('Ficheiro em falta')
        return result
    result['bytes'] = path.stat().st_size
    result['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    rows = pigments = 0
    groups = set()
    try:
        with path.open(encoding='utf-8-sig', newline='') as handle:
            reader = csv.DictReader(handle)
            missing = sorted(required - set(reader.fieldnames or []))
            if missing:
                result['errors'].append('Colunas em falta: ' + ', '.join(missing))
                return result
            for row in reader:
                rows += 1
                if None in row or any(value is None for value in row.values()):
                    result['errors'].append(f'Linha {reader.line_num}: número de campos inválido')
                    break
                group = row['cell_group']
                if 'estimate' in required and ('phore' in group.lower() or 'pigmented' in group.lower()):
                    pigments += 1
                    groups.add(group)
                    for field in ('estimate', 'timepoint'):
                        try:
                            valid = math.isfinite(float(row[field]))
                        except ValueError:
                            valid = False
                        if not valid:
                            result['errors'].append(f'Linha {reader.line_num}: {field} ausente/não finito no subconjunto de pigmentação')
                    if not row['gene1'].strip() or row['gene1'] == 'NA':
                        result['errors'].append(f'Linha {reader.line_num}: gene1 ausente')
    except (OSError, UnicodeError, csv.Error) as error:
        result['errors'].append(str(error))
    result['rows'] = rows
    if not rows:
        result['errors'].append('Tabela sem dados')
    if 'estimate' in required:
        result['pigment_rows'] = pigments
        result['pigment_groups'] = sorted(groups)
        if not pigments:
            result['errors'].append('Sem linhas que correspondam ao filtro histórico phore|pigmented')
    else:
        result['warnings'].append('Apenas estrutura: valores ausentes e pressupostos estatísticos da dispersão não foram validados')
    return result

def inspect(data):
    tables = [inspect_table(data / name, columns) for name, columns in TABLES.items()]
    binary = {}
    for name in ('reference_cds.RDS', 'raw_counts_file.RDS', 'cell_metadata_file.csv'):
        path = data / name
        binary[name] = {'present_nonempty': path.is_file() and path.stat().st_size > 0,
                        'content_validated': False}
    return {
        'scope': 'Verificação offline de entradas; não reproduz a análise nem certifica resultados',
        'tables': tables,
        'table_checks_passed': not any(table['errors'] for table in tables),
        'additional_inputs': binary,
        'Rscript_on_PATH': shutil.which('Rscript'),
        'analysis_reproduced': False,
        'limits': ['Sem execução de R, downloads ou instalações',
                   'Objetos RDS e alinhamento entre contagens e metadados não verificados',
                   'Versões originais de R/pacotes desconhecidas; presença de Rscript não garante dependências'],
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True, help='Pasta data do notebook Saunders')
    args = parser.parse_args()
    report = inspect(args.data)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report['table_checks_passed'] else 1)
