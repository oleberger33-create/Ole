@echo off
setlocal
title Minecraft-Setup: Lunar Client + Speedrun-Server
color 0E
set "SERVER=134.255.208.212:11070"
set "LUNAR=%LOCALAPPDATA%\Programs\lunarclient\Lunar Client.exe"
set "INST=%TEMP%\LunarClientInstaller.exe"

echo ==================================================
echo    Minecraft-Setup fuer den Speedrun-Server
echo ==================================================
echo.

if exist "%LUNAR%" (
  echo [OK] Lunar Client ist schon installiert.
  goto :server
)

echo [1/3] Installiere Lunar Client ...
where winget >nul 2>nul
if %errorlevel%==0 (
  winget install -e --id Moonsworth.LunarClient --silent --accept-package-agreements --accept-source-agreements
  if exist "%LUNAR%" goto :installed
  echo      winget hat nicht geklappt, lade den offiziellen Installer ...
)

curl -L --fail -o "%INST%" "https://api.lunarclientprod.com/site/download?os=windows"
if errorlevel 1 (
  powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri 'https://api.lunarclientprod.com/site/download?os=windows' -OutFile '%INST%'"
)
if not exist "%INST%" (
  echo [FEHLER] Download fehlgeschlagen. Bitte Internet pruefen oder manuell von lunarclient.com laden.
  pause
  exit /b 1
)
echo      Installer startet - bitte durchklicken und danach dieses Fenster offen lassen.
start /wait "" "%INST%"

:installed
echo [OK] Lunar Client installiert.

:server
echo.
echo [2/3] Server-Adresse in die Zwischenablage kopiert:
echo      %SERVER%
<nul set /p "=%SERVER%" | clip
echo.
echo [3/3] Starte Lunar Client ...
if exist "%LUNAR%" (
  start "" "%LUNAR%"
) else (
  echo      Lunar Client bitte ueber das Startmenue oeffnen.
)

echo.
echo ==================================================
echo  So geht es weiter:
echo   1. In Lunar mit deinem Microsoft-Konto einloggen.
echo   2. Version 26.3 waehlen (sonst die neueste) und "Launch".
echo   3. Multiplayer - Server hinzufuegen - Adresse einfuegen
echo      (Strg+V, steht schon in der Zwischenablage).
echo   4. Falls der Server nach einem Passwort fragt:
echo      einmal /register ^<Passwort^> ^<Passwort^>, danach /login ^<Passwort^>
echo ==================================================
echo.
pause
