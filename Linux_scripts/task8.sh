#!/usr/bin/env bash
set -Eeu pipefail

error() {
    echo "ERROR: validation failed!"
    exit 1
}

trap error ERR
cd ..

python3 module11.py task8.json pessimism -v task8_p.json
python3 module11.py task8.json savage -v task8_s.json
python3 module11.py task8.json bernulli_laplace -v task8_bl.json

echo "Success: validation passed!"
exit 0