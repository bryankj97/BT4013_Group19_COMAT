[CmdletBinding()] Param(
    $pythonVersion = "3.7.0",
    $pythonUrl = "https://www.python.org/ftp/python/$pythonVersion/python-$pythonVersion-amd64.exe",
    $pythonDownloadPath =  $env:USERPROFILE + '\AppData\Roaming\Python\python-' + $pythonVersion + '-amd64.exe',
    $pythonInstallDir =  $env:USERPROFILE + "\AppData\Roaming\Python\Python$pythonVersion")

$path = $env:USERPROFILE + '\AppData\Roaming\Python'
$filepath= $path + '\python-' + $pythonVersion + '-amd64.exe'
If(!(test-path $path))
{
        New-Item -ItemType Directory -Force -Path $path
}

If(!(test-path $filepath))
{
    (New-Object Net.WebClient).DownloadFile($pythonUrl, $pythonDownloadPath)
    & $pythonDownloadPath /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 TargetDir=$pythonInstallDir
    if ($? -eq $false) {
        throw "The python installer at '$pythonDownloadPath' exited with error code '$LASTEXITCODE'"
    }
    # Set the PATH environment variable for the entire machine (that is, for all users) to include the Python install dir
    [Environment]::SetEnvironmentVariable("PATH", "${env:path};${pythonInstallDir}\Scripts", "Machine")
    [Environment]::SetEnvironmentVariable("PATH", "${env:path};${pythonInstallDir}", "Machine")
}