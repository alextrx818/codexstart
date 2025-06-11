# Development Best Practices for AI-Assisted Coding
## How to Avoid Common Pitfalls

### 1. **File Naming Convention**
```
✅ GOOD:
- step1_fetch_data.py
- step2_process_data.py  
- step7_filter_matches.py
- config_odds.py

❌ BAD:
- step7.py, step7_new.py, step7_final.py, step7_test.py
- log.txt, log2.txt, log_new.txt
```

### 2. **Project Structure Template**
```
project/
├── src/               # Source code
│   ├── step1.py
│   ├── step2.py
│   └── step7.py
├── config/            # Configuration files
│   ├── .env
│   └── oddsconfig.py
├── data/              # Data files
│   ├── step1.json
│   └── step2.json
├── logs/              # Log files
│   └── step7_simple.log
├── tools/             # Utility scripts
│   └── pipeline_health_check.py
└── docs/              # Documentation
```

### 3. **Configuration Management**
Create a central config file to avoid hardcoded paths:

```python
# config.py
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"

# File paths
STEP1_JSON = DATA_DIR / "step1.json"
STEP2_JSON = DATA_DIR / "step2.json"
STEP7_LOG = LOG_DIR / "step7_simple.log"
```

### 4. **AI Assistant Instructions Template**
When working with AI assistants, use clear instructions:

```
"I need to modify the logging in step7.py. 
Current behavior: [describe what happens now]
Desired behavior: [describe what you want]
Important: 
- The file is located at /path/to/step7.py
- It should read from step2.json
- It should write to step7_simple.log
- Do NOT create new files unless explicitly asked"
```

### 5. **Version Control Best Practices**
```bash
# Before making changes
git status                    # Check current state
git branch feature/new-log    # Create feature branch

# After changes
git add -p                    # Review changes piece by piece
git commit -m "fix: update step7 to use correct log path"
```

### 6. **Testing Changes**
Always test in isolation first:
```bash
# Test individual components
python step7.py              # Run standalone
tail -f logs/step7_simple.log  # Watch output

# Use the health check tool
python pipeline_health_check.py
```

### 7. **Common Pitfalls to Avoid**

#### Pitfall 1: Multiple Similar Files
**Problem**: step7.py, step7_new.py, step7_final.py all exist
**Solution**: Use version control instead of creating new files

#### Pitfall 2: Hardcoded Paths
**Problem**: "/home/user/project/step2.json" breaks when moved
**Solution**: Use relative paths or config file

#### Pitfall 3: Silent Failures
**Problem**: Code runs but uses wrong file, no error shown
**Solution**: Add validation and logging

#### Pitfall 4: Cached Imports
**Problem**: Changes don't take effect due to Python caching
**Solution**: Restart the pipeline or use importlib.reload()

### 8. **Debugging Checklist**
When something isn't working:
1. ✓ Check file paths are correct
2. ✓ Verify data files exist and have content
3. ✓ Look for error messages in logs
4. ✓ Run the health check tool
5. ✓ Test each component separately
6. ✓ Check if old processes are still running

### 9. **AI Assistant Best Practices**
1. **Be Specific**: "Update line 47 in step7.py" not "fix the logging"
2. **Provide Context**: Share relevant code snippets
3. **Set Boundaries**: "Do not create new files"
4. **Verify Changes**: Always review what the AI did
5. **Use Tools**: Request file listings, grep searches, etc.

### 10. **Quick Commands Reference**
```bash
# Find all Python files
find . -name "*.py" -type f | grep -v venv

# Search for specific function
grep -n "def run_step7" *.py

# Check what's using a file
grep -r "step7_matches.log" . --include="*.py"

# See recent changes
ls -lt *.py | head -10

# Check running processes
ps aux | grep python
```

### Remember:
- **One source of truth**: Each piece of data should have ONE authoritative location
- **Explicit is better than implicit**: Clear file names and paths
- **Test incrementally**: Small changes, test, commit
- **Document decisions**: Why did you choose this approach?
