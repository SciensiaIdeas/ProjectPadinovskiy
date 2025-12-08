cd ..

python module11.py task6.json pessimism -v task6_p.json || goto :error
python module11.py task6.json optimism -v task6_o.json || goto :error
python module11.py task6.json hurwich -v task6_h.json -u 0.5 || goto :error
python module11.py task6.json savage -v task6_s.json || goto :error
python module11.py task6.json bernulli_laplace -v task6_bl.json || goto :error

goto :exit

:error
echo ERROR: validation failed!
pause
exit /b 1

:exit
echo Success: validation passed!
pause
exit /b 0