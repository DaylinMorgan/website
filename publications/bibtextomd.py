import argparse
import os
import textwrap
import bibtexparser
import shutil

metadata = [
        'title',
        'authors',
        'journal',
        'year',
        'month',
        'doi',
        'ID'
]

bibfile_path = 'mypublications.bib'

def parse_bibtex(bibfile_path):
    print(f'Parsing bibtex file: {bibfile_path}')
    parser = bibtexparser.bparser.BibTexParser(common_strings=True)

    with open(bibfile_path,'r') as bibfile:
        bib_db = parser.parse_file(bibfile)

    return bib_db

def parse_authors(author_list):
    authors = []

    for name in author_list.split(' and '):
        last_name = name.split(', ')[0]
        # first_name should try or check for second initial 
        first_name = name.split(', ')[1]
        last_firstinitial = f'{last_name}, {first_name[0]}.'
        authors.append(last_firstinitial)
    
    return authors

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

def make_markdown_strs(bib_db):
    markdown_dict = {}
    
    for entry in bib_db.entries:

        entry = entry_parser(entry)

        markdown_dict[entry['ID']] = textwrap.dedent(
        f'''
        ---
        title: "{entry['title']}"
        authors: {entry['authors']}
        journal: "{entry['journal']}"
        volume: "{entry['volume']}"
        month: "{entry['month']}"
        year: "{entry['year']}"
        doi: "{entry['doi']}"
        id: "{entry['ID']}"
        ---
        '''
        ).strip()

    return markdown_dict

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

def main():
     
    if not os.path.isdir('publications'):
        os.mkdir('publications')

    bib_db = parse_bibtex(bibfile_path)
    
    markdown_dict = make_markdown_strs(bib_db)

    make_publications_dir(markdown_dict)

    copy_directory_to_content()


if __name__ == '__main__':
    main()

