#!/usr/bin/env bash
set -Eeu pipefail

error() {
    echo "ERROR: validation failed!"
    exit 1
}

trap error ERR
cd ..

python3 module11.py task7.txt maximum_likelihood -v task7.txt

echo "Success: validation passed!"
exit 0