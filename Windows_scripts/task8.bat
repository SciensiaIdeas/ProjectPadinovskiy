cd ..

python module11.py task8.json pessimism -v task8_p.json || goto :error
python module11.py task8.json savage -v task8_s.json || goto :error
python module11.py task8.json bernulli_laplace -v task8_bl.json || goto :error

goto :exit

:error
echo ERROR: validation failed!
pause
exit /b 1

:exit
echo Success: validation passed!
pause
exit /b 0