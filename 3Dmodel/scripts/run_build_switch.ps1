param([switch]$ValidateOnly)
$ErrorActionPreference = 'Stop'
$taskAssetRoot = Split-Path -Parent $PSScriptRoot
if (-not $taskAssetRoot.StartsWith('D:\Game Network\', [StringComparison]::OrdinalIgnoreCase)) {
    throw 'All generated files must remain in the D: project.'
}
$taskTemp = Join-Path $taskAssetRoot 'temp'
$taskDirectories = @('blend','exports','scripts','textures','renders','temp','temp\blender_user','temp\blender_user\config','temp\blender_user\scripts','temp\blender_user\datafiles','temp\blender_user\extensions','temp\cache')
foreach ($taskDirectory in $taskDirectories) {
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
$taskScriptName = if ($ValidateOnly) { 'validate_office_switch.py' } else { 'build_office_switch.py' }
$taskLogName = if ($ValidateOnly) { 'validate_switch.log' } else { 'build_switch.log' }
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --factory-startup --disable-autoexec --threads 8 --python-exit-code 1 --python (Join-Path $PSScriptRoot $taskScriptName) 2>&1 | Tee-Object -FilePath (Join-Path $taskTemp $taskLogName)
if ($LASTEXITCODE -ne 0) { throw "Blender build failed: $LASTEXITCODE" }
