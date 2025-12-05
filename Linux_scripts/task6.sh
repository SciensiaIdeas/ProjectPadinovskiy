#!/usr/bin/env bash
set -Eeu pipefail

error() {
    echo "ERROR: validation failed!"
    exit 1
}

trap error ERR
cd ..

python3 module11.py task6.txt pessimism -v task6_p.txt
python3 module11.py task6.txt optimism -v task6_o.txt
python3 module11.py task6.txt hurwich -v task6_h.txt -u 0.5
python3 module11.py task6.txt savage -v task6_s.txt
python3 module11.py task6.txt bernulli_laplace -v task6_bl.txt

echo "Success: validation passed!"
exit 0