# Profiling

```
  _     ._   __/__   _ _  _  _ _/_   Recorded: 22:25:43  Samples:  324
 /_//_/// /_\ / //_// / //_'/ //     Duration: 0.367     CPU time: 0.330
/   _/                      v4.4.0

Program: scrivo -s /Users/tomshafer/Sites/Personal/www/source -o output/ -t templates/ -u https://tshafer.com

0.351 <module>  scrivo/__main__.py:1
├─ 0.293 Command.__call__  click/core.py:1128
│     [28 frames hidden]  click, gettext, locale, posixpath, <b...
│        0.291 invoke  click/core.py:709
│        └─ 0.291 present_cli  scrivo/cli.py:16
│           └─ 0.291 compile_site  scrivo/compile.py:19
│              ├─ 0.218 collect_pages  scrivo/compile.py:44
│              │  └─ 0.218 <listcomp>  scrivo/compile.py:53
│              │     └─ 0.213 page.__init__  scrivo/pages.py:22
│              │        └─ 0.211 md2html  scrivo/markdown.py:99
│              │           └─ 0.211 MarkdownWithMetadata.convert  markdown/core.py:225
│              │                 [195 frames hidden]  markdown, <built-in>, html, re, sre_c...
│              │                    0.016 YAMLPreprocessor.run  scrivo/markdown.py:28
│              │                    └─ 0.016 safe_load  yaml/__init__.py:117
│              │                          [78 frames hidden]  yaml, <built-in>
│              ├─ 0.039 rsync  scrivo/compile.py:67
│              │  └─ 0.039 run  subprocess.py:461
│              │        [13 frames hidden]  subprocess, <built-in>
│              └─ 0.032 <genexpr>  scrivo/compile.py:40
│                 ├─ 0.018 render_archive  scrivo/rendering.py:48
│                 │  └─ 0.012 <listcomp>  scrivo/rendering.py:94
│                 │     └─ 0.011 page.date  scrivo/pages.py:55
│                 │        └─ 0.010 datetime._strptime_datetime  _strptime.py:565
│                 │              [16 frames hidden]  _strptime, <built-in>, locale
│                 └─ 0.011 render_pages  scrivo/pages.py:69
│                    └─ 0.008 resolve_page_template  scrivo/pages.py:91
│                       └─ 0.005 Environment.list_templates  jinja2/environment.py:893
│                             [12 frames hidden]  jinja2, os, <built-in>, posixpath
└─ 0.056 <module>  scrivo/cli.py:1
   ├─ 0.050 <module>  scrivo/compile.py:1
   │  ├─ 0.032 <module>  scrivo/pages.py:1
   │  │  └─ 0.032 <module>  scrivo/markdown.py:1
   │  │     ├─ 0.011 <module>  markdown/__init__.py:1
   │  │     │     [73 frames hidden]  markdown, html, re, sre_compile, sre_...
   │  │     ├─ 0.011 <module>  yaml/__init__.py:1
   │  │     │     [34 frames hidden]  yaml, re, sre_compile, sre_parse, <bu...
   │  │     └─ 0.010 MarkdownWithMetadata.__init__  scrivo/markdown.py:22
   │  │        └─ 0.010 MarkdownWithMetadata.__init__  markdown/core.py:51
   │  │              [76 frames hidden]  markdown, importlib, re, sre_compile,...
   │  └─ 0.018 <module>  jinja2/__init__.py:1
   │        [85 frames hidden]  jinja2, re, sre_compile, sre_parse, t...
   └─ 0.006 <module>  click/__init__.py:1
         [34 frames hidden]  click, typing, <built-in>
```
