#!/usr/bin/env bash
set -Eeu pipefail

error() {
    echo "ERROR: validation failed!"
    exit 1
}

trap error ERR
cd ..

python3 module11.py task4a.txt pessimism -v task4a_p.txt
python3 module11.py task4a.txt optimism -v task4a_o.txt
python3 module11.py task4a.txt hurwich -v task4a_h.txt -u 0.75
python3 module11.py task4a.txt savage -v task4a_s.txt
python3 module11.py task4a.txt bernulli_laplace -v task4a_bl.txt

echo "Success: validation passed!"
exit 0