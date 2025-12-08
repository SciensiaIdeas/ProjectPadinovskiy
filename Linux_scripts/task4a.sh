#!/usr/bin/env bash
set -Eeu pipefail

error() {
    echo "ERROR: validation failed!"
    exit 1
}

trap error ERR
cd ..

python3 module11.py task4a.json pessimism -v task4a_p.json
python3 module11.py task4a.json optimism -v task4a_o.json
python3 module11.py task4a.json hurwich -v task4a_h.json -u 0.75
python3 module11.py task4a.json savage -v task4a_s.json
python3 module11.py task4a.json bernulli_laplace -v task4a_bl.json

echo "Success: validation passed!"
exit 0