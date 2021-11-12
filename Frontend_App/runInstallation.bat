Powershell.exe -ExecutionPolicy Bypass -NoLogo -NonInteractive -NoProfile -File %0\..\installPython.ps1

cd %~dp0

vs_community.exe --installPath "C:\Program Files (x86)\Microsoft Visual Studio\2019\VStudio" ^
--add Microsoft.VisualStudio.Workload.CoreEditor ^
--passive --norestart --wait

vs_buildtools.exe --installPath "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools" --add Microsoft.VisualStudio.Workload.VCTools;includeRecommended --passive --wait

pause
exit