$ErrorActionPreference = 'Stop'
$task = Get-ScheduledTask -TaskName 'ELVIA Website'
$configMatch = [regex]::Match($task.Actions[0].Arguments, '--config "([^"]+)"')
if (-not $configMatch.Success) { throw 'Inspect the registered task configuration.' }
Push-Location $task.Actions[0].WorkingDirectory
try {
    & $task.Actions[0].Execute -m website.supervisor --config $configMatch.Groups[1].Value --check
    if ($LASTEXITCODE -ne 0) { throw 'Production validation failed; task remains disabled.' }
} finally { Pop-Location }
Enable-ScheduledTask -TaskName 'ELVIA Website' | Out-Null
Start-ScheduledTask -TaskName 'ELVIA Website'
Get-ScheduledTask -TaskName 'ELVIA Website' | Select-Object TaskName,State
