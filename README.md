# Scrivo: My Personal Website Generator

```
$ ./bin/dev.sh
2020-06-21 14:10:52,933 symlink_directory() finished in 0.005 sec
2020-06-21 14:10:52,934 find_pages() finished in 0.001 sec
2020-06-21 14:10:53,340 fetch_pages() finished in 0.407 sec
2020-06-21 14:10:53,770 page_similarities() finished in 0.430 sec
2020-06-21 14:10:53,796 render_markdown_pages() finished in 0.025 sec
2020-06-21 14:10:53,810 Rendered index page in 0.014 s
2020-06-21 14:10:53,903 Rendered archive pages in 0.093 s
2020-06-21 14:10:53,911 Rendered tags pages in 0.008 s
2020-06-21 14:10:53,922 Rendered feeds in 0.011 s
2020-06-21 14:10:53,923 compile_site() finished in 0.995 sec
```

## To do

The idea, as I see it, is to have template inheritance.
Everything uses the template "closest" to it in the hierarchy, so
everything uses the main template unless it specifies something
in its meta or unless there's a template closer to it. E.g.,
there's a "main.html" template and a "blog/main.html" template.
But there might be "index.html" templates for each, too, which
we'd dispatch to because they have the same basename (sans
extension).

Number one, I think, is to move the Markdown parsing utility to
its own file and see if we can parallelize it effectively to be
even faster.

Number two, maybe, is to simplify a lot of my types -- making
them dataclasses or something.

---


- [ ] Add "clear all" functionality on regenerate
- [ ] Update config?
- [ ] Add debug section
- [ ] Compute time per page, etc.
