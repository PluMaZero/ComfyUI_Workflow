@echo off
chcp 65001 > nul
setlocal

echo ========================================================
echo  [AI Toolkit] 프로세스 초기화 및 재시작 도구
echo ========================================================

echo.
echo [1단계] 실행 중인 모든 Node.js 프로세스(node.exe)를 종료합니다...
:: /F: 강제 종료, /IM: 이미지 이름, /T: 자식 프로세스 포함
taskkill /F /IM node.exe /T 2>nul

if %ERRORLEVEL% EQU 0 (
    echo  -> Node.js 프로세스를 성공적으로 종료했습니다.
) else (
    echo  -> 실행 중인 Node.js 프로세스가 없거나 이미 종료되었습니다.
)

echo.
echo [2단계] 파일 잠금 해제를 위해 2초간 대기합니다...
timeout /t 2 /nobreak > nul

echo.
echo [3단계] AI Toolkit 빌드 및 시작 명령어를 실행합니다...
echo (npm install && npm run update_db && npm run build && npm run start)
echo --------------------------------------------------------
echo.

:: 원래 실행하려던 명령어
call npm install
if %ERRORLEVEL% NEQ 0 goto ErrorHandler

call npm run update_db
if %ERRORLEVEL% NEQ 0 goto ErrorHandler

call npm run build
if %ERRORLEVEL% NEQ 0 goto ErrorHandler

call npm run start
if %ERRORLEVEL% NEQ 0 goto ErrorHandler

goto End

:ErrorHandler
echo.
echo !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
echo  오류가 발생했습니다. 위 메시지를 확인해주세요.
echo !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
pause
exit /b 1

:End
echo.
echo ========================================================
echo  프로그램이 종료되었습니다.
echo ========================================================
pause