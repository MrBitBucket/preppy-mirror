@echo OFF
set NAME=preppy
if exist %NAME%.exe del %NAME%.exe
..\distro\tools\Installer\Builder.py exe_stub_%NAME%.cfg
if not exist %NAME%.exe goto LFAIL
echo Created EXE
dir %NAME%.exe
echo Contents of the exe ZArchive
..\distro\tools\Installer\ArchiveViewer.py %NAME%.exe

:LFAIL
