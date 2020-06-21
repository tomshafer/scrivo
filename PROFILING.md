# Current Profiling Status

```
  _     ._   __/__   _ _  _  _ _/_   Recorded: 14:09:48  Samples:  2001
 /_//_/// /_\ / //_// / //_'/ //     Duration: 2.101     CPU time: 2.981
/   _/                      v3.1.3

Program: bin/profiling.py

2.101 <module>  profiling.py:1
├─ 1.133 wrap  scrivo/utils.py:14
│  └─ 1.133 compile_site  scrivo/build.py:147
│     ├─ 1.063 wrap  scrivo/utils.py:14
│     │  ├─ 0.532 page_similarities  scrivo/ml/page_similarity.py:45
│     │  │  └─ 0.525 fit_transform  sklearn/feature_extraction/text.py:1821
│     │  │        [26 frames hidden]  sklearn, scipy, numpy
│     │  │           0.521 _count_vocab  sklearn/feature_extraction/text.py:1092
│     │  │           ├─ 0.416 _analyze  sklearn/feature_extraction/text.py:75
│     │  │           │  └─ 0.416 tokenize_stop_stem  scrivo/ml/page_similarity.py:32
│     │  │           │     └─ 0.415 stemWords  snowballstemmer/basestemmer.py:322
│     │  │           │           [86 frames hidden]  snowballstemmer
│     │  │           └─ 0.104 get_page_plaintext  scrivo/ml/page_similarity.py:21
│     │  │              └─ 0.099 __init__  bs4/__init__.py:114
│     │  │                    [72 frames hidden]  bs4, html, _markupbase
│     │  ├─ 0.496 fetch_pages  scrivo/build.py:63
│     │  │  └─ 0.494 <listcomp>  scrivo/build.py:67
│     │  │     └─ 0.494 <genexpr>  scrivo/build.py:66
│     │  │        └─ 0.494 from_path  scrivo/page.py:196
│     │  │           └─ 0.490 __init__  scrivo/page.py:110
│     │  │              ├─ 0.350 parse_markdown  scrivo/page.py:45
│     │  │              │  └─ 0.350 convert  markdown/core.py:224
│     │  │              │        [449 frames hidden]  markdown, mdx_math, pygments, re, sre...
│     │  │              └─ 0.140 check_metadata  scrivo/page.py:64
│     │  │                 └─ 0.140 wrapper  dateparser/conf.py:73
│     │  │                       [324 frames hidden]  dateparser, pytz, genericpath, posixp...
│     │  └─ 0.028 render_markdown_pages  scrivo/build.py:121
│     ├─ 0.034 render_archives_page  scrivo/blog.py:28
│     │  └─ 0.027 wrapper  dateparser/conf.py:73
│     │        [77 frames hidden]  dateparser, tzlocal, pytz, regex, _st...
│     └─ 0.025 get_template  jinja2/environment.py:862
│           [190 frames hidden]  jinja2
└─ 0.964 <module>  scrivo/__init__.py:1
   ├─ 0.554 <module>  scrivo/build.py:1
   │  └─ 0.553 <module>  scrivo/ml/__init__.py:1
   │     └─ 0.553 <module>  scrivo/ml/page_similarity.py:1
   │        ├─ 0.371 <module>  sklearn/__init__.py:1
   │        │     [415 frames hidden]  sklearn, scipy, inspect, numpy, unitt...
   │        ├─ 0.086 <module>  numpy/__init__.py:1
   │        │     [96 frames hidden]  numpy, ctypes, warnings, re, sre_compile
   │        └─ 0.068 <module>  bs4/__init__.py:1
   │              [266 frames hidden]  bs4, soupsieve, re, sre_compile, sre_...
   └─ 0.409 <module>  scrivo/blog.py:1
      ├─ 0.304 <module>  dateparser/__init__.py:2
      │     [406 frames hidden]  dateparser, regex, locale, _bootlocal...
      └─ 0.081 <module>  scrivo/page.py:1
         └─ 0.047 <module>  markdown/__init__.py:1
               [126 frames hidden]  markdown, importlib, configparser, re...
```
