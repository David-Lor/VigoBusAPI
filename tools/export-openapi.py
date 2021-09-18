"""EXPORT OPENAPI Script
Export the OpenAPI schema of the app into a JSON file.
Requires Python >= 3.6

Usage (from cwd = repository root)
$ python tools/export-openapi.py docs/openapi.json
This will export the schema on a file inside docs/openapi.json

.json and .yaml files are supported (yaml requires pyyaml, not loaded until asked).
Multiple exporting files can be given as args, e.g.:
$ python tools/export-openapi.py docs/openapi.json docs/openapi.yaml
This will export the schema to two files, docs/openapi.json and docs/openapi.yaml, with JSON and YAML formats respectively
"""

import os
import sys
from typing import List

try:
    from vigobusapi import app
except ModuleNotFoundError:
    sys.path.append(os.getcwd())
    from vigobusapi import app


def filename_is_json(filename: str) -> bool:
    return filename.endswith(".json")


def filename_is_yaml(filename: str) -> bool:
    return filename.endswith(".yaml") or filename.endswith(".yml")


def get_filenames_from_args() -> List[str]:
    """Retrieve the output filename/s from called args. They must be files with .json, .yaml or .yml extension.
    Raise exception if no valid files found/given."""
    valid_files_names = list()
    for i, filename in enumerate(sys.argv):
        if i == 0:
            continue
        if filename_is_json(filename) or filename_is_yaml(filename):
            valid_files_names.append(filename)

    if not valid_files_names:
        raise ValueError("Output file/s not given or not .json/.yaml file/s")
    return valid_files_names


def get_schema() -> dict:
    """Get the OpenAPI schema as JSON (dict)."""
    return app.openapi()


def schema_to_json(schema: dict, indent: int = 2) -> str:
    """Convert the given JSON schema (dict) into a JSON string."""
    import json
    return json.dumps(schema, indent=indent)


def schema_to_yaml(schema: dict, indent: int = 2) -> str:
    """Convert the given JSON schema (dict) into a YAML string."""
    import yaml
    return yaml.dump(schema, indent=indent)


def save_to_file(filename: str, content: str):
    """Save the given content (str) into a filename with the given filename.
    Contents on existing file will be replaced."""
    with open(filename, "w") as schema_file:
        schema_file.write(content)


def main():
    files_names = get_filename_from_args()
    schema = get_schema()

    for filename in files_names:
        if filename_is_json(filename):
            schema_exported = schema_to_json(schema)
        elif filename_is_yaml(filename):
            schema_exported = schema_to_yaml(schema)
        else:
            continue

        save_to_file(filename=filename, content=schema_exported)


if __name__ == "__main__":
    main()
