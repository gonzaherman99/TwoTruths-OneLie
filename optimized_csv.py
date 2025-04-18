import csv
import hashlib
import json
import zipfile
import os
import sys
from collections import defaultdict


class CSVOptimizer:
    def __init__(self, input_file, write_files=True):
        """
        input_file: path to the CSV file
        write_files: if False, skips writing JSONL, ZIP, index, and report
        """
        self.input_file = input_file
        self.write_files = write_files
        self.data = self._load_csv()
        self.duplicates = 0
        self.invalid_entries = 0
        self._identify_columns()

    def _load_csv(self):
        if not os.path.exists(self.input_file):
            raise FileNotFoundError(f"Input file not found: {self.input_file}")

        with open(self.input_file, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)

        if not data:
            raise ValueError(f"CSV file is empty: {self.input_file}")

        return data

    def _identify_columns(self):
        first_row = self.data[0]
        self.truth_cols = []
        self.lie_col = None

        for col in first_row.keys():
            lower_col = col.strip().lower()
            if 'truth' in lower_col:
                self.truth_cols.append(col)
            elif 'lie' in lower_col:
                self.lie_col = col

        if not self.truth_cols or not self.lie_col:
            available = list(first_row.keys())
            raise KeyError(
                f"Couldn't identify truth/lie columns. Available columns: {available}."
                f" Expected columns containing 'truth' and 'lie'."
            )

    def _create_statements_list(self, row):
        statements = [row.get(col, '').strip() for col in self.truth_cols]
        statements.append(row.get(self.lie_col, '').strip())
        return statements

    def validate_entries(self):
        seen_hashes = set()
        valid_data = []

        for row in self.data:
            try:
                statements = self._create_statements_list(row)
                statement_hash = hashlib.sha256(
                    json.dumps(statements, ensure_ascii=False).encode('utf-8')
                ).hexdigest()

                if statement_hash in seen_hashes:
                    self.duplicates += 1
                    continue

                seen_hashes.add(statement_hash)

                valid_data.append({
                    'id': len(valid_data) + 1,
                    'statements': statements,
                    'lie_position': len(statements) - 1,
                    'entry_hash': statement_hash,
                    'original_columns': row
                })

            except Exception as e:
                print(f"Skipping invalid row: {e}")
                self.invalid_entries += 1

        self.data = valid_data
        return self

    def optimize_storage(self):
        if not self.write_files:
            return self

        jsonl_path = 'optimized_data.jsonl'
        zip_path = 'data.zip'

        with open(jsonl_path, 'w', encoding='utf-8') as f:
            for entry in self.data:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(jsonl_path, arcname=os.path.basename(jsonl_path))

        return self

    def create_index(self):
        if not self.write_files:
            return self

        index = {}
        for entry in self.data:
            index[entry['id']] = {
                'statements': entry['statements'],
                'lie_position': entry['lie_position'],
                'hash': entry['entry_hash']
            }

        with open('data_index.json', 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

        return self

    def generate_report(self):

        if not self.write_files:
            return {
                'original_file': self.input_file,
                'processed_entries': len(self.data),
                'duplicates_removed': self.duplicates,
                'invalid_entries': self.invalid_entries,
                'output_files': []
            }

        report = {
            'original_file': self.input_file,
            'processed_entries': len(self.data),
            'duplicates_removed': self.duplicates,
            'invalid_entries': self.invalid_entries,
            'output_files': [
                'optimized_data.jsonl',
                'data.zip',
                'data_index.json',
                'validation_report.json'
            ]
        }

        with open('validation_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        return report


if __name__ == '__main__':
    try:
        print('Starting CSV optimization...')
        # default write_files=True
        optimizer = CSVOptimizer('lies.csv')
        print(f"Detected columns: Truths={optimizer.truth_cols}, Lie={optimizer.lie_col}")

        optimizer.validate_entries() \
                 .optimize_storage() \
                 .create_index()

        report = optimizer.generate_report()
        print('\nOptimization Complete!')
        print('Generated Files:')
        for fname in report['output_files']:
            print(f"- {fname}")

    except Exception as e:
        print(f" Error: {e}")
        sys.exit(1)
