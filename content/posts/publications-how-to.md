---
categories: []
date: "2021-01-17T00:00:00-06:00"
description: ""
draft: false
publishdate: "2021-01-17T00:00:00-06:00"
slug: ""
tags: []
thumbnail: <no value>
title: How I used bibtex and python to automatically generate my publications page
---




# Basic Workflow
1. Generate bibtex using references managed in Zotero
1. Parse and edit metadata as necessary
1. Write markdown documents for each entry in bibtex
1. Transfer these documents to the content/publications directory
1. Generate a list page for each article grouped and ordered by year

----------------------------

The central goal of this [script](https://github.com/DaylinMorgan/website/blob/main/publications/bibtextomd.py) is to take a bibtex file and automatically generate a requisite markdown document per article with the necessary front matter to generate my [publications](/publications) page. My inspiration for this process draws from this [blog post](https://www.r-bloggers.com/2018/03/automatically-importing-publications-from-bibtex-to-a-hugo-academic-blog-2/). Since my preferred scripting language is python, I chose that language to make a simple script to build out the necessary directory and files. 

My python script has only one dependency the [bibtexparser](https://github.com/sciunto-org/python-bibtexparser) project. 

*Disclaimer*: There is essentially no error handling so modifications may be necessary depending on bibtex format or metadata present. 

## 1. Generating the Bibtex file

I recently made the switch from my previous reference manager Mendeley to Zotero. So far I have been pleased with the feature set it offers. Though some of the defaults in bibtex export were not to my liking. Namely the addition of a `file` parameter in each entry. While bibtex support is not the primary aim of Zotero there exists a solution for my use case which is the add-on [Better Bibtex for Zotero](https://retorque.re/zotero-better-bibtex/)

Better Bibtex allows you to more easily specify your citation key style as well as omit fields from your export. In my case, I have no need for the local path of any files associated with a reference. Once generated from Zotero I save this as `publications/mypublications.bib` in the my website repo.

## 2. Parsing and Editing the Metadata

To start processing the bibtex I initially get all the metadata and parse the values using `python-bibtexparser`.

```python
def parse_bibtex(bibfile_path):
    print(f'Parsing bibtex file: {bibfile_path}')
    parser = bibtexparser.bparser.BibTexParser(common_strings=True)

    with open(bibfile_path,'r') as bibfile:
        bib_db = parser.parse_file(bibfile)

    return bib_db
```
This returns a `bibtexparser.database` with the attribute `entries` containing a list of dictionaries, one for each article with the associated metadata. 

Each entry contains at minimum a key,value pair for: title, authors, and id. In my case, as of writing this, I have an accepted book chapter which has not yet been published. In order to accommodate this to my work flow I have made the volume entry in Zotero "Accepted". The metadata I have chosen to include in the front matter of every markdown document is `['title', 'authors', 'journal', 'year', 'month', 'doi', 'ID']`. 

The first transformation to the metadata I apply is to the authors list. By default an author list in the bibtex would return like this: `'Smith, John and Doe, Jane and Morgan, Daylin'`.
Initially I wrote my python script to generate an author string which replaced the "and" delimiter and shortened any author list longer than three authors. In the end though, I decided to use go templates with Hugo to generate the author string in HTML so that I could easily seek out my own name and bold it. Of course, if I publish with another "Morgan, D." I could have some issues. My final code simply returns an author list which is handled further by Hugo. See my comments below about the way the `publications/list.html` was designed. The final output will take our example author list and convert it to `'Smith, J., Doe, J.,Morgan, D.'`


```python
def parse_authors(author_list):
    authors = []

    for name in author_list.split(' and '):
        last_name = name.split(', ')[0]
        # first_name should try or check for second initial 
        first_name = name.split(', ')[1]
        last_firstinitial = f'{last_name}, {first_name[0]}.'
        authors.append(last_firstinitial)
    
    return authors
```


By default the bibtex is parsed and strings can contain curly brackets to force capitalization or escapes for special characters. I handle these instances where necessary using `str.replace`.

Also, with book chapters there is no journal field in the bibtex but instead a booktitle. If I find no journal key I next search for a booktitle and settle for an empty string if neither of these are present in the entry metadata. This may require future edits if a different entry or use case presents itself. 

In instances in which volumes are defined with an integer I use `.isdigit()` and replace the value with a string to make it more clear in my citations. If the volume entry is empty or not a digit, such as Accepted for my book chapter it is left unchanged. This gives me the below function.

```python
def entry_parser(entry):
    print(f"Correcting metadata for entry: {entry['ID']}")

    entry['authors'] = parse_authors(entry['author'])

    entry['title'] = entry['title'].replace('{','').replace('}','')

    if 'journal' not in entry.keys():
        if entry['booktitle']:
            entry['journal'] = entry['booktitle'].replace('{','').replace('}','')
        else:
            print(f"no journal entry found for {entry['title']}")
            entry['journal'] = ''
    else:
        entry['journal'] = entry['journal'].replace('\\','').replace('{','').replace('}','')

    if entry['volume'].isdigit():
        entry['volume'] = f"vol. {entry['volume']}"

    for key in metadata:
        if key not in entry.keys():
            entry[key] = ''

    return entry
```

# 3. Write markdown documents for each entry in bibtex

In order to build the list using Hugo I need to generate a markdown document with front matter defining the metadata Hugo will use to populate fields in the html. I do this by first looping through our bibtex database and applying the parsing functions described above and populate an f-string for each entry. I also make use of the built-in function `textwrap.dedent()` to make my code more readable. 

```python 
def make_markdown_strs(bib_db):
    markdown_dict = {}
    
    for entry in bib_db.entries:

        entry = entry_parser(entry)

        markdown_dict[entry['ID']] = textwrap.dedent(
        f'''
        +++
        title = "{entry['title']}"
        authors = {entry['authors']}
        journal = "{entry['journal']}"
        year = "{entry['year']}"
        month = "{entry['month']}"
        volume = "{entry['volume']}"
        doi = "{entry['doi']}"
        id = "{entry['ID']}"
        +++
        '''
        ).strip()

    return markdown_dict
```

# 4. Transfer these documents to the content/publications directory

With this dictionary containing a complete front matter for each markdown I create markdown documents in our working directory. And transfer them in to `content/publications` using `shutil.copy2()`.

```python
def make_publications_dir(markdown_dict):
    print('Generating markdown documents')

    for id,value in markdown_dict.items():
        with open(f'publications/{id}.md','w') as f:
            f.write(value)

def copy_directory_to_content():
    print('Copying markdown documents to content/publications')
    src = 'publications'
    dst = '../content/publications'

    for md in os.listdir(src):
        shutil.copy2(os.path.join(src,md),os.path.join(dst,md))
```

# 5. Generate a list page for each article grouped and ordered by year

After running `python bibtextomd.py` I have the following directory within `content/` for Hugo to build from. 

```bash
publications
├── _index.md
├── johnsonIntegratingTranscriptomicsBulk2020.md
├── morganFunctionalizedLineageTracing2021.md
├── ramanDefinedScalablePeptideBased2020.md
└── srinivasanIntegratedBiomanufacturingPlatform2018.md
```

My theme coder-portfolio has some default templates it uses to build list pages. However, I wanted to group and arrange my publications list by year. Additionally, I needed to format the author list from the front matter to a comma separated list with my own name bolded. See [here](https://gohugo.io/templates/introduction/) for an intro to Hugo Templating.

To make this layout which will use go templates I started from the `list.html` included with my current theme. The first thing I needed to do was group and arrange the articles by year. To do this, I use `{{ range (.Pages.GroupByParam "year").Reverse}}`. With this line from my layout I take an array `.Pages` and group by the front matter parameter year. By default, this is in ascending order so using `.Reverse()` I can order them latest to oldest. The first keyword `range` essentially exacts like a for loop redefining the so-called context to a dot:`.` and iterating through the array of `.Pages`. 

Next, for each article I need to similarly iterate through the author list and create a string for each article. If I was keeping the list simply comma delimited there is a handy built-in Hugo function `delimit` which will add commas like this `['item1','item2','item3','item4']` -> `"item1, item2, item3, item4"`. However, I also want to bold my name within the list to better highlight it since this is **my** website after all. 

To do this, I utilize variable assignment in the range like so `{{ range $index, $author := .Params.authors }}` and then perform a check on the `$author` variable to see if it is either the last in the list or my own name "Morgan, D." to determine whether to add a comma after it or bold it. Admittedly, the conditionals in Hugo are pretty confusing and it took me quite a bit of trial and error to get it working for this. See below for the complete layout. I also made a `custom.css` to define my own element styling. Separate from the coder-portfolio defaults to have better control over the appearance. 

```html
{{ define "og-title" }}
  {{ .Title }} - {{ .Site.Title }}
{{ end }}
{{ define "title" }}
  {{ .Title }} - {{ .Site.Title }}
{{ end }}
{{ define "content" }}
<section class="container list">
  <h1 class="title">{{ .Title }}</h1>
  <ul>
    {{ range (.Pages.GroupByParam "year").Reverse}}
    <h3> {{ .Key }} </h3>
      {{ range .Pages }}
      <li>
        <publication>
          {{ $authornum := len .Params.authors }}
            {{ range $index, $author := .Params.authors }} 
            {{ if eq ( $author ) "Morgan, D."}}
              <b>{{$author}}</b>,
            {{ else if eq (add $index +1) $authornum}}
              and {{ $author }}
            {{else}}
              {{ $author }},
            {{ end }}
          {{ end }}
          {{ .Title }}. <i> {{ .Params.journal }}.</i> {{ .Params.volume}}  ({{ .Params.year }})
        </publication>
        {{ if .Params.doi }}
        <a href ="https://doi.org/{{.Params.doi}}"> DOI.</a>
        <br><br>
        {{end}}
      </li>
      {{ end }}
    {{ end }}
  </ul>
</section>
{{ end }}
```

Now that I have gone to all this effort for my measly 4 papers future publications will give me minimal headache to update my website. All I need to do is export a new `.bib` run `bibtextomd.py` and rebuild my site. 

