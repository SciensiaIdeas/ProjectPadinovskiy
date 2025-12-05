cd ..

python module11.py task4b.txt pessimism -v task4b_p.txt || goto :error
python module11.py task4b.txt optimism -v task4b_o.txt || goto :error
python module11.py task4b.txt hurwich -v task4b_h.txt -u 0.5 || goto :error
python module11.py task4b.txt savage -v task4b_s.txt || goto :error
python module11.py task4b.txt bernulli_laplace -v task4b_bl.txt || goto :error

goto :exit

:error
echo ERROR: validation failed!
pause
exit /b 1

:exit
echo Success: validation passed!
pause
exit /b 0