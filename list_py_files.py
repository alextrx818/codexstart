import os
import csv
from pathlib import Path
from datetime import datetime

# Configuration
PROJECT_DIR = Path(__file__).parent.resolve()
LOG_FILE = PROJECT_DIR / f"py_files_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

# Find all Python files
py_files = []
for root, _, files in os.walk(PROJECT_DIR):
    for file in files:
        if file.endswith('.py'):
            file_path = Path(root) / file
            stat = file_path.stat()
            py_files.append({
                'file_path': str(file_path),
                'size_bytes': stat.st_size,
                'last_modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
            })

# Write to CSV log
with open(LOG_FILE, 'w', newline='') as csvfile:
    fieldnames = ['file_path', 'size_bytes', 'last_modified']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    for file_info in py_files:
        writer.writerow(file_info)

print(f"Logged {len(py_files)} Python files to {LOG_FILE}")
