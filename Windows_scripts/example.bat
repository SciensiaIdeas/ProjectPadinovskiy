cd ..

python module11.py example.txt pessimism -v example1.txt || goto :error
python module11.py example.txt optimism -v example2.txt || goto :error
python module11.py example.txt hurwich -v example3.txt -u 0.75 || goto :error
python module11.py example.txt savage -v example4.txt || goto :error
python module11.py example.txt bernulli_laplace -v example5.txt || goto :error
python module11.py example_ml.txt maximum_likelihood_2d -v example6.txt || goto :error

:: Check 2d Max-Likelihood and MC
python module11.py example_ml.txt maximum_likelihood_mc -v example6.txt || goto :error
:: Eval MC for usual example
python module11.py example.txt maximum_likelihood -e example_mc.txt || goto :error

goto :exit

:error
echo ERROR: validation failed!
pause
exit /b 1

:exit
echo Success: validation passed!
pause
exit /b 0