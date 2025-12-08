#!/usr/bin/env bash
set -Eeu pipefail

error() {
    echo "ERROR: validation failed!"
    exit 1
}

trap error ERR
cd ..

python3 module11.py task4b.json pessimism -v task4b_p.json
python3 module11.py task4b.json optimism -v task4b_o.json
python3 module11.py task4b.json hurwich -v task4b_h.json -u 0.5
python3 module11.py task4b.json savage -v task4b_s.json
python3 module11.py task4b.json bernulli_laplace -v task4b_bl.json

echo "Success: validation passed!"
exit 0