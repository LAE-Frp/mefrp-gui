@ECHO off
color 2F
ECHO. ��ӭʹ�� ME Frp Winodws amd64 ���������ģ����������İ汾SNASHOT 1.0
ECHO.     __  __ ___   ___
ECHO.    /  \/  / __/ / __/ _ ___
ECHO.   / /\// / _/  / _/ '_/ '_\
ECHO.  /_/  /_/___/ /_//_/ / .__/
ECHO.                     /_/
ECHO. ME Frp ���񼴽�����
ECHO.�·����� start proxy success ��Ϊ��������ɹ������������δ��������ַ�Ѹ��Ƶ������塣
@REM %1�Ǹ��ݳ������ini���Ʋ����Զ�����·��
frpc.exe -c temp/%1.ini
pause
exit