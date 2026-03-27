import os
import csv
import json

base_dir = r"s:\MISSION FIELD\AI - ALGOMA\FINAL PROJECT\DATABASE"
results = {}

for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith('.csv'):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    header = next(reader)
                    # store relative path as key
                    rel_path = os.path.relpath(path, base_dir)
                    results[rel_path] = header
            except Exception as e:
                try:
                    with open(path, 'r', encoding='latin1') as f:
                        reader = csv.reader(f)
                        header = next(reader)
                        rel_path = os.path.relpath(path, base_dir)
                        results[rel_path] = header
                except Exception as e2:
                    results[os.path.relpath(path, base_dir)] = f"Error: {e2}"

out_path = os.path.join(base_dir, "csv_headers_dump.json")
with open(out_path, "w", encoding='utf-8') as f:
    json.dump(results, f, indent=2)

print(f"Dumped headers for {len(results)} CSVs to {out_path}")
