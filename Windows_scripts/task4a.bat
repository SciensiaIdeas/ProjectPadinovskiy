cd ..

python module11.py task4a.json pessimism -v task4a_p.json || goto :error
python module11.py task4a.json optimism -v task4a_o.json || goto :error
python module11.py task4a.json hurwich -v task4a_h.json -u 0.75 || goto :error
python module11.py task4a.json savage -v task4a_s.json || goto :error
python module11.py task4a.json bernulli_laplace -v task4a_bl.json || goto :error

goto :exit

:error
echo ERROR: validation failed!
pause
exit /b 1

:exit
echo Success: validation passed!
pause
exit /b 0