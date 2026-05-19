@echo off
REM Hermes Vault Bootstrap — Windows
REM Run once after cloning the vault on a new PC.

setlocal EnableDelayedExpansion

REM --- Config ---
set "VAULT_NAME=hermes-vault"
set "GIT_USER=jasonVPS"
set "GIT_EMAIL=jason.koslowski@outlook.de"

echo.
echo ============================================
echo   Hermes Vault Bootstrap (Windows)
echo ============================================
echo.

REM Find vault directory (current dir or common locations)
if exist ".\.git" (
    set "VAULT_DIR=%CD%"
    goto :found
)
if exist "%USERPROFILE%\Documents\%VAULT_NAME%\.git" (
    set "VAULT_DIR=%USERPROFILE%\Documents\%VAULT_NAME%"
    goto :found
)
if exist "%USERPROFILE%\Obsidian Vaults\%VAULT_NAME%\.git" (
    set "VAULT_DIR=%USERPROFILE%\Obsidian Vaults\%VAULT_NAME%"
    goto :found
)

echo ERROR: Could not find hermes-vault Git repository.
echo Please run this script from inside your vault folder.
pause
exit /b 1

:found
echo [OK] Vault found at: %VAULT_DIR%
cd /d "%VAULT_DIR%"

REM --- 1. Git Identity ---
echo.
echo [1/4] Setting Git identity...
git config --global user.name "%GIT_USER%"
git config --global user.email "%GIT_EMAIL%"
echo [OK] Git identity set: %GIT_USER% <%GIT_EMAIL%>

REM --- 2. Git Remote ---
echo.
echo [2/4] Checking Git remote...
git remote -v > nul 2>>1
if errorlevel 1 (
    echo [WARN] No remote configured.
    echo If you cloned via HTTPS, this is normal.
) else (
    echo [OK] Remote configured:
    git remote -v
)

REM --- 3. Fetch/Pull ---
echo.
echo [3/4] Testing pull...
git fetch origin
git status --short > check_status.txt 2>>1
set /p STATUS=<check_status.txt
del check_status.txt

if "!STATUS!==" (
    echo [OK] Working tree clean. Pulling latest...
    git pull origin main
    if errorlevel 1 (
        echo [WARN] Pull had merge conflicts. Please resolve manually.
    )
) else (
    echo [INFO] You have local changes. Stashing and pulling...
    git stash
    git pull origin main
    git stash pop
    echo [OK] Your local changes were restored.
)

REM --- 4. Push Test ---
echo.
echo [4/4] Testing push permissions...
git push --dry-run origin main > push_test.txt 2>>1
if errorlevel 1 (
    echo [WARN] Push test failed. Check your SSH key or HTTPS token.
    type push_test.txt
) else (
    echo [OK] Push permission OK.
)
del push_test.txt 2>nul

REM --- 5. Obsidian Git Plugin Note ---
echo.
echo ============================================
echo   Manual Step: Obsidian Git Plugin
echo ============================================
echo.
echo In Obsidian:
echo  1. Open Settings -> Community Plugins -> Browse
echo  2. Search "Obsidian Git" and Install/Enable
echo  3. In Git Plugin Settings:
echo      - Turn ON "Pull updates on startup"
echo      - Turn ON "Auto commit and sync"
echo      - Set interval: 60 seconds
echo.
echo Done! Your vault is ready.
pause
