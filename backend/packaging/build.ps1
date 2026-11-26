# Build the backend into a Windows executable (onedir).
# Output: backend/dist/campus-market-backend/
Set-Location (Split-Path $PSScriptRoot -Parent)   # go to the backend directory

& ".\.venv\Scripts\python.exe" -m PyInstaller "packaging\backend.spec" --noconfirm --clean
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed with exit code $LASTEXITCODE" }

# Put the config template next to the artifact so another machine can run it:
# copy .env.example to .env and fill in the database settings.
Copy-Item ".env.example" "dist\campus-market-backend\.env.example" -Force

Write-Host ""
Write-Host "Build finished: dist\campus-market-backend\campus-market-backend.exe"
Write-Host "Before running, copy .env.example to .env in that folder and fill in the DB settings."
