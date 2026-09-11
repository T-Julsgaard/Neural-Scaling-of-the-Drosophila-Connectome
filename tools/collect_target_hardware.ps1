param(
    [string]$OutputPath = (Join-Path $PSScriptRoot '../research/target_hardware.json')
)
# Run on the actual experiment workstation. This script has not been run here.
# Read-only hardware inspection; writes only the requested manifest.
$ErrorActionPreference = 'Stop'
$researchOs = Get-CimInstance Win32_OperatingSystem
$researchSystem = Get-CimInstance Win32_ComputerSystem
$researchCpu = @(Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors)
$researchGpu = @(Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion)
$researchDisks = @(Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3' | Select-Object DeviceID, Size, FreeSpace)
$researchSmi = Get-Command nvidia-smi -ErrorAction SilentlyContinue
$researchNvidia = $null
if ($researchSmi) {
    $researchNvidia = @(& $researchSmi.Source --query-gpu=name,memory.total,driver_version --format=csv,noheader)
}
$researchPython = Get-Command python -ErrorAction SilentlyContinue
$researchPythonVersion = $null
if ($researchPython) { $researchPythonVersion = & $researchPython.Source --version 2>&1 | Out-String }
$researchRecord = [ordered]@{
    collected_at_utc = [DateTime]::UtcNow.ToString('o')
    role = 'candidate_target_machine_requires_identity_confirmation'
    os = $researchOs.Caption
    os_version = $researchOs.Version
    physical_ram_bytes = $researchSystem.TotalPhysicalMemory
    cpu = $researchCpu
    gpu = $researchGpu
    nvidia_smi_name_vram_mib_driver = $researchNvidia
    local_disks = $researchDisks
    python_version = $researchPythonVersion
    limitation = 'Does not establish model throughput, CUDA compatibility, or user confirmation that this is the intended workstation.'
}
$researchRecord | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $OutputPath -Encoding utf8
Write-Output "Wrote hardware manifest to $OutputPath"
