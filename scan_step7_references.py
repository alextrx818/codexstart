import os
import re
from pathlib import Path

# Configure search
PROJECT_DIR = Path('/root/6-4-2025')
LOG_FILE = PROJECT_DIR / 'step7_references_scan.log'
PATTERN = re.compile(r'step\s*7', re.IGNORECASE)

# Prepare results
results = []

# Scan all Python files
for root, _, files in os.walk(PROJECT_DIR):
    for file in files:
        if file.endswith('.py'):
            file_path = Path(root) / file
            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    for line_num, line in enumerate(lines, 1):
                        if PATTERN.search(line):
                            results.append({
                                'file': str(file_path),
                                'line': line_num,
                                'content': line.strip()
                            })
            except Exception as e:
                results.append({
                    'file': str(file_path),
                    'error': f"Read error: {str(e)}"
                })

# Save results
with open(LOG_FILE, 'w') as log:
    log.write(f"Step7 References Scan Report\n{'='*80}\n")
    log.write(f"Files scanned: {len(results)} files with matches\n")
    log.write(f"Total matches found: {sum(1 for r in results if 'line' in r)}\n\n")
    
    for entry in results:
        if 'line' in entry:
            log.write(f"File: {entry['file']}\n")
            log.write(f"Line {entry['line']}: {entry['content']}\n\n")
        else:
            log.write(f"ERROR in {entry['file']}: {entry['error']}\n\n")

print(f"Scan complete. Results saved to {LOG_FILE}")
