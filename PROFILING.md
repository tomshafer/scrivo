# Profiling Status

  _     ._   __/__   _ _  _  _ _/_   Recorded: 15:06:59  Samples:  1648
 /_//_/// /_\ / //_// / //_'/ //     Duration: 1.748     CPU time: 2.609
/   _/                      v3.1.3

Program: ./bin/profiling.py

1.747 <module>  profiling.py:1
├─ 1.056 wrap  scrivo/utils.py:14
│  └─ 1.056 compile_site  scrivo/build.py:147
│     ├─ 0.968 wrap  scrivo/utils.py:14
│     │  ├─ 0.558 page_similarities  scrivo/ml/page_similarity.py:45
│     │  │  └─ 0.550 fit_transform  sklearn/feature_extraction/text.py:1821
│     │  │        [23 frames hidden]  sklearn, scipy, numpy
│     │  │           0.547 _count_vocab  sklearn/feature_extraction/text.py:1092
│     │  │           ├─ 0.442 _analyze  sklearn/feature_extraction/text.py:75
│     │  │           │  └─ 0.442 tokenize_stop_stem  scrivo/ml/page_similarity.py:32
│     │  │           │     └─ 0.438 stemWords  snowballstemmer/basestemmer.py:322
│     │  │           │           [85 frames hidden]  snowballstemmer
│     │  │           └─ 0.103 get_page_plaintext  scrivo/ml/page_similarity.py:21
│     │  │              └─ 0.101 __init__  bs4/__init__.py:114
│     │  │                    [69 frames hidden]  bs4, html, _markupbase, encodings
│     │  ├─ 0.373 fetch_pages  scrivo/build.py:63
│     │  │  └─ 0.371 <listcomp>  scrivo/build.py:67
│     │  │     └─ 0.371 <genexpr>  scrivo/build.py:66
│     │  │        └─ 0.371 from_path  scrivo/page.py:217
│     │  │           └─ 0.360 __init__  scrivo/page.py:132
│     │  │              └─ 0.360 parse_markdown  scrivo/page.py:96
│     │  │                 └─ 0.357 convert  markdown/core.py:224
│     │  │                       [463 frames hidden]  markdown, mdx_math, pygments, re, sre...
│     │  └─ 0.030 render_markdown_pages  scrivo/build.py:121
│     └─ 0.058 get_template  jinja2/environment.py:862
│           [295 frames hidden]  jinja2, genericpath
└─ 0.688 <module>  scrivo/__init__.py:1
   ├─ 0.568 <module>  scrivo/build.py:1
   │  └─ 0.567 <module>  scrivo/ml/__init__.py:1
   │     └─ 0.567 <module>  scrivo/ml/page_similarity.py:1
   │        ├─ 0.375 <module>  sklearn/__init__.py:1
   │        │     [406 frames hidden]  sklearn, scipy, inspect, numpy, unitt...
   │        ├─ 0.089 <module>  numpy/__init__.py:1
   │        │     [119 frames hidden]  numpy, ctypes, re, sre_compile, conte...
   │        └─ 0.073 <module>  bs4/__init__.py:1
   │              [292 frames hidden]  bs4, soupsieve, re, sre_compile, sre_...
   └─ 0.119 <module>  scrivo/blog.py:1
      ├─ 0.086 <module>  scrivo/page.py:1
      │  ├─ 0.049 <module>  markdown/__init__.py:1
      │  │     [176 frames hidden]  markdown, importlib, configparser, re...
      │  └─ 0.020 <module>  scrivo/markdown.py:1
      │     └─ 0.020 <module>  yaml/__init__.py:2
      │           [51 frames hidden]  yaml, re, sre_compile, sre_parse
      └─ 0.029 <module>  jinja2/__init__.py:2
            [74 frames hidden]  jinja2, re, sre_compile, sre_parse, d...
