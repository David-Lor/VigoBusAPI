"""EXPORT OPENAPI Script
Export the OpenAPI schema of the app into a JSON file.

Usage (from cwd = repository root)
$ python tools/export-openapi.py docs/openapi.json

This will export the schema on a file inside docs/openapi.json
"""

import os
import sys
import json

try:
    from vigobusapi import app
except ModuleNotFoundError:
    sys.path.append(os.getcwd())
    from vigobusapi import app


def get_filename_from_args() -> str:
    """Retrieve the output filename from called args.
    Raise exception if no args available."""
    file_path = sys.argv[-1]
    if not file_path.endswith(".json"):
        raise ValueError("Output file not given or not a .json file")


def get_schema() -> dict:
    """Get the OpenAPI schema as JSON (dict)."""
    return app.openapi()


def schema_to_json(schema: dict, indent: int = 2) -> str:
    """Convert the given JSON schema (dict) into a JSON string."""
    return json.loads(schema, indent=indent)


def save_to_file(filename: str, content: str):
    """Save the given content (str) into a filename with the given filename.
    Contents on existing file will be replaced."""
    with open(filename, "w") as schema_file:
        schema_file.write(schema)


def main():
    filename = get_filename_from_args()
    schema = get_schema()
    schema_json = schema_to_json(schema)
    save_to_file(filename=filename, content=schema_json)


if __name__ == "__main__":
    main()
