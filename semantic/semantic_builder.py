# semantic/semantic_builder.py
import json
import os
from pathlib import Path

def load_semantic_layer(path="semantic/semantic_layer.json"):
    with open(path) as f:
        return json.load(f)

def extract_dbt_metadata(manifest_path="dbt/target/manifest.json"):
    if not os.path.exists(manifest_path):
        raise FileNotFoundError(f"manifest.json not found at {manifest_path}. Run `dbt compile` first.")
    with open(manifest_path) as f:
        manifest = json.load(f)
    models = {}
    for key, val in manifest.get("nodes", {}).items():
        if val.get("resource_type") == "model":
            models[val["name"]] = {
                "database": val.get("database"),
                "schema": val.get("schema"),
                "description": val.get("description", ""),
                "columns": {c: info.get("description", "") for c, info in val.get("columns", {}).items()}
            }
    return models

def merge_semantic_with_dbt(semantic, dbt_models):
    merged = {"entities": {}}
    for entity_name, entity in semantic["entities"].items():
        model_name = entity["model"]
        model_meta = dbt_models.get(model_name, {})
        merged["entities"][entity_name] = {
            **entity,
            "columns": model_meta.get("columns", {}),
            "schema": model_meta.get("schema")
        }
    merged["metrics"] = semantic["metrics"]
    merged["dimensions"] = semantic["dimensions"]
    merged["joins"] = semantic.get("joins", [])
    return merged

if __name__ == "__main__":
    dbt_models = extract_dbt_metadata()
    semantic = load_semantic_layer()
    merged = merge_semantic_with_dbt(semantic, dbt_models)
    out_path = Path("semantic/merged_semantic.json")
    out_path.write_text(json.dumps(merged, indent=2))
    print(f"Merged semantic layer written to {out_path}")
