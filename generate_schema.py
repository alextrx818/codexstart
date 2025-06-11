#!/usr/bin/env python3
"""
Generate JSON Schema from existing step2.json data
"""
import json
from genson import SchemaBuilder
from pathlib import Path

def generate_schema():
    # Load step2.json
    with open('step2.json', 'r') as f:
        data = json.load(f)
    
    # Create schema builder
    builder = SchemaBuilder()
    builder.add_schema({"type": "object"})
    
    # Add samples to build schema
    summaries = data.get('summaries', [])
    for summary in summaries[:5]:  # Use first 5 samples
        builder.add_object(summary)
    
    # Generate schema
    schema = builder.to_schema()
    
    # Add metadata
    schema['$schema'] = "http://json-schema.org/draft-07/schema#"
    schema['$id'] = "https://github.com/alextrx818/codexstart/schemas/match-summary/v2025-06-11"
    schema['title'] = "Match Summary"
    schema['description'] = "Sports match data from step2 processing"
    schema['version'] = "2025-06-11"
    
    # Save schema
    with open('schemas/match-summary.schema.json', 'w') as f:
        json.dump(schema, f, indent=2)
    
    print("✅ Generated schema: schemas/match-summary.schema.json")
    
    # Also create a sample for code generation
    sample = {
        "summaries": summaries[:2],
        "version": "2025-06-11",
        "$schema": "https://github.com/alextrx818/codexstart/schemas/match-summary/v2025-06-11"
    }
    
    with open('schemas/step2-sample.json', 'w') as f:
        json.dump(sample, f, indent=2)
    
    print("✅ Created sample: schemas/step2-sample.json")

if __name__ == "__main__":
    # Create schemas directory
    Path("schemas").mkdir(exist_ok=True)
    generate_schema()
