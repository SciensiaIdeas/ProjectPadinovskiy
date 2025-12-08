#!/usr/bin/env bash
set -Eeu pipefail

error() {
    echo "ERROR: validation failed!"
    exit 1
}

trap error ERR
cd ..

python3 module11.py example.json pessimism -v example1.json
python3 module11.py example.json optimism -v example2.json
python3 module11.py example.json hurwich -v example3.json -u 0.75
python3 module11.py example.json savage -v example4.json
python3 module11.py example.json bernulli_laplace -v example5.json
python3 module11.py example_ml.json maximum_likelihood_2d -v example6.json

# Check 2d Max-Likelihood and MC
python3 module11.py example_ml.json maximum_likelihood_mc -v example6.json
# Eval MC for usual example
python3 module11.py example.json maximum_likelihood -e example_mc.json

echo "Success: validation passed!"
exit 0