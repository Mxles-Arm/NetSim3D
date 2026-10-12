param([switch]$ValidateOnly, [switch]$PortsOnly)
$ErrorActionPreference = 'Stop'
$taskAssetRoot = Split-Path -Parent $PSScriptRoot
if (-not $taskAssetRoot.StartsWith('D:\Game Network\', [StringComparison]::OrdinalIgnoreCase)) { throw 'D: project storage is required.' }
$taskTemp = Join-Path $taskAssetRoot 'temp\printer'
foreach ($taskDirectory in @('blend','exports','renders','temp\printer','temp\printer\blender_user\config','temp\printer\blender_user\scripts','temp\printer\blender_user\datafiles','temp\printer\blender_user\extensions','temp\printer\cache')) {
    New-Item -ItemType Directory -Path (Join-Path $taskAssetRoot $taskDirectory) -Force | Out-Null
}
$env:TEMP = $taskTemp
$env:TMP = $taskTemp
$env:TMPDIR = $taskTemp
$env:BLENDER_USER_RESOURCES = Join-Path $taskTemp 'blender_user'
$env:BLENDER_USER_CONFIG = Join-Path $taskTemp 'blender_user\config'
$env:BLENDER_USER_SCRIPTS = Join-Path $taskTemp 'blender_user\scripts'
$env:BLENDER_USER_DATAFILES = Join-Path $taskTemp 'blender_user\datafiles'
$env:BLENDER_USER_EXTENSIONS = Join-Path $taskTemp 'blender_user\extensions'
$env:XDG_CACHE_HOME = Join-Path $taskTemp 'cache'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONPYCACHEPREFIX = Join-Path $taskTemp 'cache\python'
$env:CUDA_CACHE_PATH = Join-Path $taskTemp 'cache\cuda'
$env:OPTIX_CACHE_PATH = Join-Path $taskTemp 'cache\optix'
$taskScript = if ($ValidateOnly) { 'validate_network_printer.py' } else { 'build_network_printer.py' }
$taskLog = if ($ValidateOnly) { 'validate_printer.log' } else { 'build_printer.log' }
$taskExtraArguments = @()
if ($PortsOnly -and -not $ValidateOnly) { $taskExtraArguments = @('--','--ports-only') }
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --factory-startup --disable-autoexec --threads 8 --python-exit-code 1 --python (Join-Path $PSScriptRoot $taskScript) @taskExtraArguments 2>&1 | Tee-Object -FilePath (Join-Path $taskTemp $taskLog)
if ($LASTEXITCODE -ne 0) { throw "Printer task failed: $LASTEXITCODE" }
