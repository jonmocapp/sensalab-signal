# setup_autopilot.ps1
# Registra The Signal Autopilot en el Programador de Tareas de Windows: corre SOLO, local, sin
# proceso vivo ni n8n. Ejecutar UNA vez en PowerShell (como tu usuario):
#     powershell -ExecutionPolicy Bypass -File setup_autopilot.ps1
#
# Requisitos previos (una vez, en .env del repo):
#   ANTHROPIC_API_KEY = tu key (para que redacte las notas)
#   NETLIFY_AUTH_TOKEN / NETLIFY_SITE_ID = para publicar en vivo (opcional; si faltan, solo construye)

$ErrorActionPreference = "Stop"
$repo = "C:\Dev\SensaLab-Newsletter-Bot"
$py = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $py) { $py = (Get-Command py -ErrorAction SilentlyContinue).Source }
if (-not $py) { Write-Error "No encuentro python en el PATH."; exit 1 }

$taskName = "SensaLab Signal Autopilot"
$action = New-ScheduledTaskAction -Execute $py -Argument "autopilot.py --once" -WorkingDirectory $repo
# Corre diario a las 7:00 am. Cambia -At si quieres otra hora, o agrega más triggers.
$trigger = New-ScheduledTaskTrigger -Daily -At 7:00am
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable `
    -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Hours 1)

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings `
    -Description "Autonomo local: busca noticias, redacta con voz SensaLab, setea imagen y publica The Signal. Puro Python, sin n8n." -Force | Out-Null

Write-Host "OK. Tarea '$taskName' registrada: corre diario 7:00am." -ForegroundColor Green
Write-Host "Correr ahora mismo:  Start-ScheduledTask -TaskName '$taskName'"
Write-Host "Ver estado:          Get-ScheduledTask -TaskName '$taskName' | Get-ScheduledTaskInfo"
Write-Host "Quitarla:            Unregister-ScheduledTask -TaskName '$taskName' -Confirm:`$false"
