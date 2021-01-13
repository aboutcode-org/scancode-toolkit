In general compiling DBD:Oracle for 64 bit machines has been a hit or miss operation.  
The main thing to remember is you will have to compile using 32 bit Perl and compile DBD::Oracle against a 32bit client
which sort of defeats the purpose of having a 64bit box.  
So until 64bit Perl comes out we will be posing in this README any success stories we have come across

-------- Original Message --------
From: 	Alex Buttery, OCA, MCTS
	Director, Database Architecture and Operations
	Impact Rx, Inc.


I needed to get perl working on a 64-bit Windows Server so I got creative. Since I was unable to build DBD::Oracle on the Windows Server
(even with Visual Studio 6 installed), I decided that I would try another approach. Here are the steps I took to get it working 
(yes, this is a hack and I'm not even sure that it does not violate someone's license agreements but I'm not going to be asking anyone 
else to support this configuration). 

 Step 1: Install 32-bit Perl 5.8.8 from Activestate on the Server to the C: drive.

 Step 2: Install the 32-bit Oracle client on the server (I'm assuming the 64-bit client has already been installed and is working) to 
 	 the c:\oracle\product\10.2.0\client32 directory in the OraHome_Client32 Home.

 Step 3: Locate Oracle.dll in the new Oracle Home directory, it should be located somewhere close to 
 	 c:\oracle\product\10.2.0\client32\perl\site\5.8.3\MSWin32-x86-multi-thread\auto\DBD\Oracle.

 Step 4: Locate Oracle.dll in the Perl 5.8.8 directory. (C:\Perl) It should be somewhere close to c:\Perl\site\lib\auto\DBD\Oracle.

 Step 5: Copy the contents of the Oracle directory found in Step 3 to the Perl directory found in Step 4.

 Step 6: Copy GetInfo.pm from C:\oracle\product\10.2.0\client32\perl\site\5.8.3\lib\MSWin32-x86-multi-thread\DBD\Oracle to C:\Perl\site\lib\DBD\Oracle

 Step 7: Locate Oracle.pm in the new Oracle Home directory, it should be located somewhere close to 
 	 c:\oracle\product\10.2.0\client32\perl\site\5.8.3\MSWin32-x86-multi-thread\auto\DBD.

 Step 8: Locate Oracle.pm in the Perl 5.8.8 directory. (C:\Perl) It should be somewhere close to c:\Perl\site\lib\auto\DBD.

 Step 9: Copy Oracle.pm from the Oracle directory found in Step 7 to the Perl directory found in Step 8.

 Step 10: Set up required ODBC connections using the 32-bit ODBC applet (odbcad32.exe) located in the C:\Windows\SysWOW64 directory.  
 	  Note: The ODBC applet in the Administrative Tools menu points to the odbcad32.exe located in the C:\Windows\system32 directory 
 	  and is actually the 64 bit version of the ODBC applet This cannot be used by Perl

 Step 11: Create batch scripts to run Perl programs and include the following SET statements to point Perl to the correct Oracle Home:

 	SET ORACLE_HOME=c:\oracle\product\10.2.0\client32 <== 32-bit Oracle Home

	SET ORACLE_SID=xyz123                             <== SID of Production Database

	SET NLS_LANG=.WE8ISO8859P1                        <== Default Language from Database   (preceeding "." Is required)

	SET PATH=%ORACLE_HOME%\bin;%PATH%                 <== Add 32-bit Oracle Home to beginning of default PATH

 

Hopefully, you will be able to include these instructions in the next build of DBD::Oracle to help out other poor souls that are fighting
this same battle.

 

 
