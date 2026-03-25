#!/usr/bin/env python
# coding: utf-8

import os, re
import pandas as pd
from jinja2 import Environment, FileSystemLoader

env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=False
)
etemplate = env.get_template('entry.tex')

global_cols = ['headword', 'pronunciation', 'translation']

# Get the sheet ID from the URL (the long string between /d/ and /edit)
sheet_id = os.environ['SHEET_ID']
sheets = {
    'Nouns': {
        'cols': ['obj_moro', 'obj_ipa', 'pl_moro', 'pl_ipa', 'nounclass'],
        'pos': 'n.',
        'template': env.get_template('noun.tex')
    },
    'Verbs': {
        'cols': ['imp_moro', 'imp_ipa', 'ipfv_moro', 'ipfv_ipa', 'pfv_moro', 'pfv_ipa'],
        'pos': 'v.',
        'template': env.get_template('verb.tex')
    },
    'Adjectives': {
        'cols': ['imp_moro', 'imp_ipa', 'ipfv_moro', 'ipfv_ipa', 'predadj_moro', 'predadj_ipa'],
        'pos': 'adj.',
        'template': env.get_template('adjective.tex')
    },
    'Other': {
        'cols': ['pos', 'pfv_moro', 'pfv_ipa'],
        'template': env.get_template('other.tex'),
        'pos': None # Set by 'pos' column from google sheet instead
    }
}

letters = [
    'a',
    'b',
    'c',
    'd',
    'e',
    'f',
    'g',
    'i',
    'j',
    'k',
    'l',
    'm',
    'n',
    'o',
    'p',
    'r',
    's',
    't',
    'u',
    'v',
    'w',
    'y',
    'ë',
    'ð',
    'ñ',
    'đ',
    'ŋ',
    'ə',
    'ɽ',
    'ḏ',
    'ṯ'
]


def render_entry(e, cols, pos, template):
    tparams = {c: getattr(e, c) for c in cols}
    try:
        # Double replace() is so that '[' and ']' can be present or not in the spreadsheet.
        tparams['pronunciation'] = tparams['pronunciation'].replace('] or [', ' or ').replace(' or ', '] or [')
    except KeyError:
        pass
    if pos is not None:
        tparams['pos'] = pos
    return template.render(tparams)

entries = {c: [] for c in letters}
for sheet_name, cfg in sheets.items():
    # Construct the URL for CSV export
    url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'

    cols = global_cols + cfg['cols']

    # Load data using pd.read_csv().
    df = pd.read_csv(url, usecols=cols, keep_default_na=False)
    df['chapter'] = df['headword'].str.lower().str.strip('(').str.strip('-').str[0]

    drop = df.query('chapter.isna()')
    if len(drop) > 0:
        print('Dropping entries with missing headword')
        print(drop)
    df = df.query('not chapter.isna()').copy()

    for e in df.itertuples():
        entry = render_entry(e, cols=cols, pos=cfg['pos'], template=cfg['template'])
        entries[e.chapter].append({'headword': e.headword, 'tex': entry})

chaptertemplate = env.get_template('chapter.tex')

chapters = []
for ltr in letters:
    chapters.append(chaptertemplate.render(ltr=ltr, entries=entries[ltr]))

tex = '\n'.join(chapters)

print(tex)

