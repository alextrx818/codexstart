# Schema Enforcement System for Sports Data Pipeline

**Date Added**: 06/10/2025 9:26 PM Eastern Time  
**Added By**: Cascade AI Assistant  
**Purpose**: Eliminate pipeline failures caused by inconsistent field names

## 🎯 Why This Was Created

The sports data pipeline was experiencing frequent breakages due to field name inconsistencies:
- Different parts of the pipeline used different names for the same data (e.g., `money_line` vs `money_line_american`)
- Manual code changes often introduced typos or incorrect field references
- There was no automated way to validate data structure consistency
- AI agents generating code would sometimes use non-standard field names

## 📁 New Files Added

### 1. `models.py` - Pydantic Data Models
- **Purpose**: Single source of truth for all data structures
- **Usage**: Import and use these models to ensure type safety
```python
from models import MatchSummary, Step2Output, validate_step2_json

# Validate existing data
data = validate_step2_json("step2.json")

# Create new match with automatic validation
match = MatchSummary(match_id="123", home="Team A", away="Team B", ...)
```

### 2. `test_contracts.py` - Automated Contract Testing
- **Purpose**: Verify data consistency before deployment
- **Usage**: Run before any pipeline execution
```bash
./venv/bin/python test_contracts.py
```
- **What it checks**:
  - step2.json conforms to schema
  - All field names are canonical
  - step7.py compatibility with current data
  - Provides detailed error messages with fixes

### 3. `schema_enforcer.py` - Development Tool
- **Purpose**: Analyze codebase for non-standard field usage
- **Usage**: Run during development to catch issues
```bash
./venv/bin/python schema_enforcer.py
```
- **Features**:
  - Scans Python files for field references
  - Reports non-canonical field names
  - Generates migration guide
  - Suggests code fixes

### 4. `FIELD_REFERENCE.md` - Quick Reference Guide
- **Purpose**: Developer cheat sheet for exact field names
- **Contents**:
  - All canonical field names with examples
  - Status codes and meanings
  - Odds array structure
  - Environment data fields
  - Critical rules to follow

### 5. `SCHEMA_CONTRACT.md` - Detailed Documentation
- **Purpose**: Comprehensive guide for developers and AI agents
- **Contents**:
  - Complete data model documentation
  - Usage examples
  - Migration instructions
  - Contract testing guide
  - AI agent instructions

### 6. `schemas/` Directory
- **Purpose**: JSON Schema definitions for validation
- **Files**:
  - `match-summary.schema.json` - Formal schema definition
  - `step2-sample.json` - Example data matching schema

## 🔄 How These Files Work in Future Pipeline Runs

### During Development:
1. **Write Code**: Use `models.py` imports to ensure correct field names
2. **Test Locally**: Run `test_contracts.py` to verify compatibility
3. **Check Code**: Use `schema_enforcer.py` to find issues
4. **Reference**: Check `FIELD_REFERENCE.md` for field names

### During Pipeline Execution:
1. **step1.py**: Produces data following schema contract header
2. **step2.py**: Validates input/output using models, ensures field consistency
3. **step7.py**: Reads validated data, handles both field name variants

### For AI Agents:
- AI agents will see schema contracts at the top of each file
- Using `models.py` ensures generated code is always compatible
- Contract tests catch any AI-generated code issues before production

## 🛡️ Benefits

1. **No More Field Name Confusion**: Single source of truth for all field names
2. **Early Error Detection**: Validation catches issues immediately
3. **Backward Compatibility**: Handles both old and new field names
4. **AI-Friendly**: Ensures consistent code generation
5. **Self-Documenting**: Clear contracts in every file

## 📋 Schema Contract Headers

Each pipeline file (step1.py, step2.py, step7.py) now has a prominent header:
```python
# ============================================================================
# SCHEMA CONTRACT - DO NOT MODIFY FIELD NAMES
# ============================================================================
```

These headers lock in the exact field names and data structures, preventing drift.

## 🚀 Result

The pipeline is now protected against field name inconsistencies that previously caused failures. Any developer (human or AI) working on the project will produce compatible code by following the enforced schema contracts.
