cd ..

python module11.py task7.txt maximum_likelihood -v task7.txt || goto :error
goto :exit

:error
echo ERROR: validation failed!
pause
exit /b 1

:exit
echo Success: validation passed!
pause
exit /b 0