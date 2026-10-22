param(
    [Parameter(Mandatory=$true)][string]$Configuration,
    [string]$UserId = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name,
    [switch]$Start,
    [switch]$PrepareDisabled
)
$ErrorActionPreference = 'Stop'
$repository = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$python = Join-Path $repository '.venv\Scripts\python.exe'
$configurationPath = [IO.Path]::GetFullPath($Configuration)
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) { throw 'Install the locked website environment first.' }
if ($Start -and $PrepareDisabled) { throw 'A prepared task cannot be started before production validation.' }
if (-not $PrepareDisabled) {
    Push-Location $repository
    try {
        & $python -m website.supervisor --config $configurationPath --check
        if ($LASTEXITCODE -ne 0) { throw 'Production configuration validation failed.' }
    } finally { Pop-Location }
}
$taskName = 'ELVIA Website'
$existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existing) { throw 'ELVIA Website already exists. Inspect it before replacing its startup configuration.' }
$action = New-ScheduledTaskAction -Execute $python -Argument ('-m website.supervisor --config "' + $configurationPath + '"') -WorkingDirectory $repository
$trigger = New-ScheduledTaskTrigger -AtStartup
$trigger.Delay = 'PT30S'
# S4U runs as the maintainer without storing a Windows password or waiting for
# an interactive login. HTTP/Tunnel networking uses local application secrets.
$principal = New-ScheduledTaskPrincipal -UserId $UserId -LogonType S4U -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit ([TimeSpan]::Zero) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
$task = New-ScheduledTask -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description 'Start ELVIA and its dedicated Tunnel after boot; recover failed processes; no interactive sign-in required.'
if ($PrepareDisabled) { $task.Settings.Enabled = $false }
Register-ScheduledTask -TaskName $taskName -InputObject $task -ErrorAction Stop | Out-Null
# The same limited principal may start/stop its task without repeated elevation.
$ownerSid = (New-Object Security.Principal.NTAccount($UserId)).Translate([Security.Principal.SecurityIdentifier]).Value
$scheduler = New-Object -ComObject 'Schedule.Service'
$scheduler.Connect()
$registered = $scheduler.GetFolder('\').GetTask($taskName)
$registered.SetSecurityDescriptor(('D:P(A;;FA;;;SY)(A;;FA;;;BA)(A;;FA;;;' + $ownerSid + ')'), 0)
if ($Start) { Start-ScheduledTask -TaskName $taskName }
Get-ScheduledTask -TaskName $taskName | Select-Object TaskName,State,@{Name='LogonType';Expression={$_.Principal.LogonType}},@{Name='RunLevel';Expression={$_.Principal.RunLevel}}
