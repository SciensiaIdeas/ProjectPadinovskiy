cd ..

python module11.py task8.txt pessimism -v task8_p.txt || goto :error
python module11.py task8.txt savage -v task8_s.txt || goto :error
python module11.py task8.txt bernulli_laplace -v task8_bl.txt || goto :error

goto :exit

:error
echo ERROR: validation failed!
pause
exit /b 1

:exit
echo Success: validation passed!
pause
exit /b 0