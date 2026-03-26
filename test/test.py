import os
import pytest
import pandas as pd
from spreadsheet_to_tex import sheets, global_cols

def is_balanced_parenlike(s):
   '''Test that '({[]})' characters in a string are properly balanced and nested.'''
   stack = []
   pairs = {')': '(', ']': '[', '}': '{'}
   for char in s:
       if char in '([{':
           stack.append(char)
       elif char in ')]}':
           if not stack or stack[-1] != pairs[char]:
               return False
           stack.pop()
   return not stack

def load_sheetdf(sheet_id, sheet_name, cols):
    # Construct the URL for CSV export
    url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
    
    # Load data using pd.read_csv().
    df = pd.read_csv(url, usecols=cols, keep_default_na=False)
    df['chapter'] = df['headword'].str.lower().str.strip('(').str.strip('-').str[0]
    return df

def test_balanced_parenlike():
    '''Test that any grouping characters '({[]})' are properly matched and nested.'''
    
    errors = []
    for sheet_name, cfg in sheets.items():
        cols = global_cols + cfg['cols']
        df = load_sheetdf(os.environ['SHEET_ID'], sheet_name, cols)
        for row in df.itertuples():
            for col in cols:
                s = getattr(row, col)
                try:
                    assert(is_balanced_parenlike(s))
                except AssertionError:
                    errors.append(f'  sheet {sheet_name}, headword {row.headword}, column {col}, value {s}')
    if errors != []:
        raise ValueError('Unbalanced grouping characters found in:\n' + '\n'.join(errors))
