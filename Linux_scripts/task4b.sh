#!/usr/bin/env bash
set -Eeu pipefail

error() {
    echo "ERROR: validation failed!"
    exit 1
}

trap error ERR
cd ..

python3 module11.py task4b.txt pessimism -v task4b_p.txt
python3 module11.py task4b.txt optimism -v task4b_o.txt
python3 module11.py task4b.txt hurwich -v task4b_h.txt -u 0.5
python3 module11.py task4b.txt savage -v task4b_s.txt
python3 module11.py task4b.txt bernulli_laplace -v task4b_bl.txt

echo "Success: validation passed!"
exit 0