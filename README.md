# website

This is the repo for my personal website built using [Hugo](https://gohugo.io/) and the [coder-portfolio theme](https://github.com/naro143/hugo-coder-portfolio) with minimal edits. 

## Updating Publications

To update publications from Zotero or another reference manager, export your selected publications and save it under `publications/mypublications.bib`

with `publications/` as your working directory use `python bibtextomd.py` to generate a fresh set of markdowns. 

Following this use run `hugo` to rebuild with updated publications.
