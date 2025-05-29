@echo off&setlocal EnableDelayedExpansion
color 0a
echo %date% %time%
echo convert svg to pdf now......
set a=0
for %%i in (*.svg) do (
    echo    %%i  --  %%~ni.pdf 
    inkscape --export-filename=%%~ni.pdf %%i
    set /a a+=1
)
echo convert count:%a%
pause
