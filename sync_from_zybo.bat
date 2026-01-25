@echo off
setlocal

set "LOCAL_DIR=/mnt/c/_Vorlesungen/RTC_2025/01_GIT/zybo-audio-tdoa-starter/"
set "ZYBO_USER=debian"
set "ZYBO_IP=192.168.1.103"
set "ZYBO_DIR=~/rtc-audio-student/"

echo Sync Zybo -> PC ...
wsl rsync -rv --delete ^
  --no-times --no-perms --no-owner --no-group --omit-dir-times ^
  --exclude ".git/" ^
  --exclude "__pycache__/" ^
  --exclude "*.pyc" ^
  --exclude ".pytest_cache/" ^
  --exclude ".mypy_cache/" ^
  --exclude ".vscode/" ^
  --exclude ".idea/" ^
  --exclude "*.bat" ^
  --exclude "*.cmd" ^
  --exclude "*.ps1" ^
  --exclude "*.doc" ^
  --exclude "*.docx" ^
  --exclude "*.pdf" ^
  --exclude "cfg_local.py" ^
  %ZYBO_USER%@%ZYBO_IP%:%ZYBO_DIR% ^
  %LOCAL_DIR%

echo Done.
pause
