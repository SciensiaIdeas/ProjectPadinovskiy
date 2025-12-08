cd ..

python module11.py example.json pessimism -v example1.json || goto :error
python module11.py example.json optimism -v example2.json || goto :error
python module11.py example.json hurwich -v example3.json -u 0.75 || goto :error
python module11.py example.json savage -v example4.json || goto :error
python module11.py example.json bernulli_laplace -v example5.json || goto :error
python module11.py example_ml.json maximum_likelihood_2d -v example6.json || goto :error

:: Check 2d Max-Likelihood and MC
python module11.py example_ml.json maximum_likelihood_mc -v example6.json || goto :error
:: Eval MC for usual example
python module11.py example.json maximum_likelihood -e example_mc.json || goto :error

goto :exit

:error
echo ERROR: validation failed!
pause
exit /b 1

:exit
echo Success: validation passed!
pause
exit /b 0