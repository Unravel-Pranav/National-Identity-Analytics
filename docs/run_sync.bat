@echo off
echo ===================================================
echo   Aadhaar Platform Data Migration ^& Sync Tool
echo ===================================================
echo.
echo [1] Migrate Existing Data (Reorganize api_data_* to Year/Month)
echo [2] Sync New Data (Fetch latest from API)
echo.
set /p choice="Enter selection (1 or 2): "

if "%choice%"=="1" (
    echo.
    echo Running Migration...
    python scripts/sync_monthly_data.py
) else if "%choice%"=="2" (
    echo.
    echo Running Sync...
    python scripts/sync_monthly_data.py sync
) else (
    echo Invalid choice.
)

pause
