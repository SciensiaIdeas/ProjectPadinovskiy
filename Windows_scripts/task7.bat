cd ..

python module11.py task7.json maximum_likelihood -v task7.json || goto :error
goto :exit

:error
echo ERROR: validation failed!
pause
exit /b 1

:exit
echo Success: validation passed!
pause
exit /b 0