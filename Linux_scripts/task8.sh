#!/usr/bin/env bash
set -Eeu pipefail

error() {
    echo "ERROR: validation failed!"
    exit 1
}

trap error ERR
cd ..

python3 module11.py task8.txt pessimism -v task8_p.txt
python3 module11.py task8.txt savage -v task8_s.txt
python3 module11.py task8.txt bernulli_laplace -v task8_bl.txt

echo "Success: validation passed!"
exit 0