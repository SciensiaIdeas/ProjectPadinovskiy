#!/usr/bin/env bash
set -Eeu pipefail

error() {
    echo "ERROR: validation failed!"
    exit 1
}

trap error ERR
cd ..

python3 module11.py task6.json pessimism -v task6_p.json
python3 module11.py task6.json optimism -v task6_o.json
python3 module11.py task6.json hurwich -v task6_h.json -u 0.5
python3 module11.py task6.json savage -v task6_s.json
python3 module11.py task6.json bernulli_laplace -v task6_bl.json

echo "Success: validation passed!"
exit 0