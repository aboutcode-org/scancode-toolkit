set JAVA_HOME=c:\j2sdk1.4.1_02
setlocal
del /s *.obj
del /s *.exe
rmdir /s /q .\.cccc
rmdir /s /q cccc\.cccc
rmdir /s /q test\.cccc

cd ..
%JAVA_HOME%\bin\jar cvf ccccdist.zip ccccdist
dir ccccdist.zip
endlocal
