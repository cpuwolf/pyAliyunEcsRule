call env.cmd

rmdir /s /q dist

::pause

python.exe -m PyInstaller  --clean --noconfirm update_security_group.spec

pause

::"C:\Program Files (x86)\NSIS\makensisw.exe" nsis\winloginspect.nsi