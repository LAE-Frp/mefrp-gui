@ECHO off
color 2F
ECHO. 欢迎使用 ME Frp Winodws amd64 启动器核心，启动器核心版本SNASHOT 1.0
ECHO.     __  __ ___   ___
ECHO.    /  \/  / __/ / __/ _ ___
ECHO.   / /\// / _/  / _/ '_/ '_\
ECHO.  /_/  /_/___/ /_//_/ / .__/
ECHO.                     /_/
ECHO. ME Frp 服务即将启动
ECHO.下方出现 start proxy success 即为隧道启动成功，否则隧道尚未启动。地址已复制到剪贴板。
@REM %1是根据程序传入的ini名称参数自动生成路径
frpc.exe -c temp/%1.ini
pause
exit