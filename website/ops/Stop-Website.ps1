$ErrorActionPreference = 'Stop'
# Disabling first prevents Task Scheduler recovery during maintenance.
Disable-ScheduledTask -TaskName 'ELVIA Website' | Out-Null
Stop-ScheduledTask -TaskName 'ELVIA Website'
Get-ScheduledTask -TaskName 'ELVIA Website' | Select-Object TaskName,State
