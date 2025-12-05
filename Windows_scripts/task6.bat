cd ..

python module11.py task6.txt pessimism -v task6_p.txt || goto :error
python module11.py task6.txt optimism -v task6_o.txt || goto :error
python module11.py task6.txt hurwich -v task6_h.txt -u 0.5 || goto :error
python module11.py task6.txt savage -v task6_s.txt || goto :error
python module11.py task6.txt bernulli_laplace -v task6_bl.txt || goto :error

goto :exit

:error
echo ERROR: validation failed!
pause
exit /b 1

:exit
echo Success: validation passed!
pause
exit /b 0