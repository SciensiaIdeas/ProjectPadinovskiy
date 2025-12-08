cd ..

python module11.py task4b.json pessimism -v task4b_p.json || goto :error
python module11.py task4b.json optimism -v task4b_o.json || goto :error
python module11.py task4b.json hurwich -v task4b_h.json -u 0.5 || goto :error
python module11.py task4b.json savage -v task4b_s.json || goto :error
python module11.py task4b.json bernulli_laplace -v task4b_bl.json || goto :error

goto :exit

:error
echo ERROR: validation failed!
pause
exit /b 1

:exit
echo Success: validation passed!
pause
exit /b 0