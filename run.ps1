$ErrorActionPreference = "Stop"

# Переходим в папку проекта
Set-Location $PSScriptRoot

# Запускаем автоматические тесты
Write-Host "Running tests..."
python -m unittest discover -s tests -v

if ($LASTEXITCODE -ne 0) {
    Write-Host "Tests failed!"
    exit 1
}

Write-Host "All tests passed!"