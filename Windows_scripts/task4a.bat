cd ..

python module11.py task4a.txt pessimism -v task4a_p.txt || goto :error
python module11.py task4a.txt optimism -v task4a_o.txt || goto :error
python module11.py task4a.txt hurwich -v task4a_h.txt -u 0.75 || goto :error
python module11.py task4a.txt savage -v task4a_s.txt || goto :error
python module11.py task4a.txt bernulli_laplace -v task4a_bl.txt || goto :error

goto :exit

:error
echo ERROR: validation failed!
pause
exit /b 1

:exit
echo Success: validation passed!
pause
exit /b 0