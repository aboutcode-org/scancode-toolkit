A ScanCode post-scan plugin to filter scanned URLS from whitelist 

To use, run this from an activated ScanCode virtualenv::

    pip install -e plugins/scancode-filter-urls

Then you can see the help for the new option::
```
$ ./scancode -h

....
  post-scan:
    --is-license-text        Set the "is_license_text" flag to true for files
                             that contain mostly license texts and notices (e.g
                             over 90% of the content). [EXPERIMENTAL]
....
    --whitelisted-urls FILE  Load a list of white-listed URLs, one per line and
                             remove URLs that match any such URL from the
                             scanned data.
```

Create a new file named wl.url with this content::
``` 
https://github.com/nexB/scancode-toolkit/
http://apache.org/licenses/LICENSE-2.0
```

And run this first scan::

```
$ scancode --url --quiet --json-pp - NOTICE
{
....
  "files": [
    {
      "path": "NOTICE",
      "type": "file",
      "urls": [
        {
          "url": "http://nexb.com/",
          "start_line": 5,
          "end_line": 5
        },
        {
          "url": "https://github.com/nexB/scancode-toolkit/",
          "start_line": 5,
          "end_line": 5
        },
        {
          "url": "http://apache.org/licenses/LICENSE-2.0",
          "start_line": 11,
          "end_line": 11
        },
        {
          "url": "https://github.com/nexB/scancode-thirdparty-src/",
          "start_line": 39,
          "end_line": 39
        },
        {
          "url": "http://creativecommons.org/publicdomain/zero/1.0/",
          "start_line": 56,
          "end_line": 56
        }
      ],
      "scan_errors": []
    }
  ]
}
```

And then this other command and you can see fewer URLs
```
$ scancode --url --json-pp - NOTICE --quiet  --whitelisted-urls wl.url 
{
...

  ],
  "files": [
    {
      "path": "NOTICE",
      "type": "file",
      "urls": [
        {
          "url": "http://nexb.com/",
          "start_line": 5,
          "end_line": 5
        },
        {
          "url": "https://github.com/nexB/scancode-thirdparty-src/",
          "start_line": 39,
          "end_line": 39
        },
        {
          "url": "http://creativecommons.org/publicdomain/zero/1.0/",
          "start_line": 56,
          "end_line": 56
        }
      ],
      "scan_errors": []
    }
  ]
}
```

