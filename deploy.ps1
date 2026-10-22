<#
    Публикует фан-сайт FunTime на GitHub Pages.

    Требуется:
      git  ->  winget install --id Git.Git -e
      gh   ->  winget install --id GitHub.cli -e
      и один раз войти: gh auth login

    Запуск из папки сайта:
      powershell -ExecutionPolicy Bypass -File .\deploy.ps1
      pwsh -File .\deploy.ps1 -RepoName "funtime" -Branch main

    Файл сохранён в UTF-8 с BOM, чтобы русский текст читали и PowerShell 5.1, и pwsh 7.
#>
[CmdletBinding()]
param(
    [string]$RepoName = "funtime-fan-site",
    [string]$Branch = "main",
    [switch]$Private
)

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

function Require-Tool {
    param([string]$Name, [string]$Install)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Не найден '$Name'. Установи: $Install"
    }
}

Require-Tool -Name "git" -Install "winget install --id Git.Git -e"
Require-Tool -Name "gh" -Install "winget install --id GitHub.cli -e"

# --- авторизация -----------------------------------------------------------
& gh auth status 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Нужно один раз войти в GitHub (откроется браузер):" -ForegroundColor Yellow
    & gh auth login --hostname github.com --git-protocol https --web
    if ($LASTEXITCODE -ne 0) { throw "Вход в GitHub не выполнен." }
}

$login = (& gh api user --jq .login).Trim()
if (-not $login) { throw "Не удалось получить логин GitHub." }
Write-Host "Аккаунт: $login"

# --- локальный репозиторий -------------------------------------------------
if (-not (Test-Path -LiteralPath ".git")) {
    & git init -b $Branch 2>&1 | Out-Null
    Write-Host "Создан локальный репозиторий, ветка $Branch."
}

$email = (& git config user.email) 2>$null
if (-not $email) {
    & git config user.name $login 2>&1 | Out-Null
    & git config user.email ($login + "@users.noreply.github.com") 2>&1 | Out-Null
    Write-Host "Настроен автор коммитов: $login"
}

& git add -A 2>&1 | Out-Null
$changes = & git status --porcelain
if ($changes) {
    & git commit -m "FunTime fan site: anarchy only, gallery, guides" 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "git commit не удался." }
    Write-Host "Сделан коммит."
}

# --- репозиторий на GitHub -------------------------------------------------
& gh repo view $RepoName 2>&1 | Out-Null
$repoExists = ($LASTEXITCODE -eq 0)

if ($repoExists) {
    & git push -u origin $Branch
    if ($LASTEXITCODE -ne 0) { throw "git push не удался." }
    Write-Host "Репозиторий уже был — отправил изменения."
} else {
    $visibility = if ($Private) { "--private" } else { "--public" }
    $createArgs = @(
        "repo", "create", $RepoName, $visibility,
        "--source", ".", "--remote", "origin", "--push",
        "--description", "Фан-сайт анархического сервера FunTime (mc.funtime.su)"
    )
    & gh @createArgs
    if ($LASTEXITCODE -ne 0) { throw "Не удалось создать репозиторий $RepoName." }
    Write-Host "Репозиторий создан и запушен."
}

# --- GitHub Pages из корня ветки -------------------------------------------
$pagesArgs = @(
    "api", "-X", "POST", "repos/{owner}/{repo}/pages",
    "-f", "source[branch]=$Branch",
    "-f", "source[path]=/"
)
& gh @pagesArgs 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    $pagesArgs[2] = "PUT"
    & gh @pagesArgs 2>&1 | Out-Null
}

$url = "https://" + $login + ".github.io/" + $RepoName + "/"
Write-Host ""
Write-Host "Готово. Сайт: $url" -ForegroundColor Green
Write-Host "Первый билд GitHub Pages занимает 1-2 минуты."
if ($Private) {
    Write-Host "Внимание: Pages для приватного репозитория требует платный аккаунт." -ForegroundColor Yellow
}
