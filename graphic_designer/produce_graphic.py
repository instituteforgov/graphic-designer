# %%
# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Purpose
        Produce graphic
    Inputs
        XXX
    Outputs
        None
    Parameters
        - See lay_out_body()
    Notes
        None
"""

import os

from IPython.display import display
import pandas as pd

from lay_out_body import lay_out_body

# %%
# SET PARAMETERS
body_width = 800
draw_area_margin_dim = {'top': 10, 'right': 10, 'bottom': 10, 'left': 10}

font = 'Open Sans'

# Positioning
section_head_position = 'left'
section_head_width = 100
section_head_height = None

# section_head_position = 'top'
# section_head_width = None
# section_head_height = 100

elements_per_row = 5
element_height = 50
element_margin_dim = {'top': 2, 'right': 2, 'bottom': 2, 'left': 2}

# %%
# READ IN DATA AND CREATE SUBTOTALS
# Create data
df = pd.read_excel(
    'C:/Users/' + os.getlogin() + '/'
    'Institute for Government/Data - General/'
    'UK government and politics/MPs/'
    'MPs standing down/'
    'MPs standing down GE24 main data.xlsm',
    sheet_name='Data',
)

# Drop rows after blank row separating data and notes
df = df.loc[
    :df.isnull().all(1).idxmax() - 1
]

# Split name into first and last names
df[['First name', 'Last name']] = df['Name'].str.split(
    ' ',
    n=1,
    expand=True,
)

# Expand 'SNP'
# NB: fillna() is needed as this is a non-exhaustive mapping
df['Party'] = df['Party'].map(
    {'SNP': 'Scottish National Party'}
).fillna(df['Party'])

# Abbreviate long constituency names
df['Constituency'] = df['Constituency'].map({
    'Paisley and Renfrewshire South': 'Paisley & Renfrewshire S.',
    'Ross, Skye and Lochaber': 'Ross, Skye & Lochaber',
    'Dunfermline and West Fife': 'Dunfermline and W. Fife',
    'Lanark and Hamilton East': 'Lanark and Hamilton E.',
    'Glenrothes and Central Fife': 'Glenrothes and C. Fife',
    'East Kilbride, Strathaven and Lesmahagow': "E. Kilbride, S'haven and L'gow",
    'Bognor Regis and Littlehampton': "Bognor Regis and L'hampton",
    'Rochford and Southend East': "R'ford and Southend E.",
    'Cities of London and Westminster': "Cit. of London and W'minster",
    'East Worthing and Shoreham': "E. Worthing and S'ham",
    'Central Suffolk and North Ipswich': "C. Suffolk and N. Ipswich",
    'Fermanagh and South Tyrone': "Fermanagh and S. Tyrone",
}).fillna(df['Constituency'])

# Calculate subtotals by party
df_subtotal = df.groupby(
    by='Party',
    as_index=False,
).agg({
    'Name': 'count'
}).rename(
    columns={
        'Name': 'MPs'
    }
).sort_values(
    by='MPs',
    ascending=False,
).reset_index(drop=True)

# Calculate maximum number of rows that will be needed per party
# NB: This is an implementation of ceiling division
# NB: Note that this may not be the number of rows we use in the final graphic - where
# we use horizontal spacing between parties we may end up collapsing some rows
df_subtotal['rows'] = df_subtotal['MPs'].apply(lambda x: -(-x // elements_per_row))

# Make party names column categorical and set order
df['Party'] = pd.Categorical(
    df['Party'],
    categories=df_subtotal['Party'],
    ordered=True,
)

# Sort data
# NB: We sort by party first. Since 'Party' is a categorical column this sorts
# by the pre-defined order
# NB: Sorting by 'index' rather than 'Date announced' so that we get people who announce
# on the same day in the right order
df_sorted = df.reset_index().sort_values(
    by=['Party', 'index'],
    ascending=[True, True],
).reset_index(drop=True)

# %%
# PRODUCE GRAPHIC
graphic = lay_out_body(
    df_sorted,
    df_subtotal,
    body_width,
    draw_area_margin_dim,
    font,
    section_head_position,
    section_head_width,
    section_head_height,
    elements_per_row,
    element_height,
    element_margin_dim,
)

# %%
# DISPLAY GRAPHIC
display(graphic)

# %%
