#!/usr/bin/env bash
set -Eeu pipefail

error() {
    echo "ERROR: validation failed!"
    exit 1
}

trap error ERR
cd ..

python3 module11.py example.txt pessimism -v example1.txt
python3 module11.py example.txt optimism -v example2.txt
python3 module11.py example.txt hurwich -v example3.txt -u 0.75
python3 module11.py example.txt savage -v example4.txt
python3 module11.py example.txt bernulli_laplace -v example5.txt
python3 module11.py example_ml.txt maximum_likelihood_2d -v example6.txt

# Check 2d Max-Likelihood and MC
python3 module11.py example_ml.txt maximum_likelihood_mc -v example6.txt
# Eval MC for usual example
python3 module11.py example.txt maximum_likelihood -e example_mc.txt

echo "Success: validation passed!"
exit 0