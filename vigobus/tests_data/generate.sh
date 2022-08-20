#!/bin/bash

# Run from this directory as workdir

set -ex

OUTPUT_FILENAME="testdata.zip"

zip "$OUTPUT_FILENAME" * -x "$OUTPUT_FILENAME"
