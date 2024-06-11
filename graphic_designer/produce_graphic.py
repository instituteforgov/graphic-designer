# %%
# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Purpose
        Produce graphic
    Inputs
        None
    Outputs
        None
    Parameters
        - ifg_dark_grey: Colour used for text
        - dict_party_colours: Party colours
        - See lay_out_body()
    Notes
        None
"""

import os

from IPython.display import display
import pandas as pd

from lay_out_body import lay_out_body
from format_graphic_data import format_graphic_data

# %%
# SET PARAMETERS
# Colours
ifg_dark_grey = '#333f48'

dict_party_colours = {
    'Conservative': '#00539f',
    'Labour': '#ee3224',
    'Liberal Democrat': '#ffb703',
    'Scottish National Party': '#fff95d',
    'PC': '#3f8429',
    'Green': '#6ab023',
    'Reform UK': '#3bb7ce',
    'Democratic Unionist Party': '#8f1d20',
    'Sinn Féin': '#006837',
    'Independent': '#c1c5c8',
}

elements_per_row = 5

# %%
# READ IN DATA AND EDIT
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

# %%
# PRODUCE GRAPHIC DATA
df_element, df_section = format_graphic_data(
    df,
    section_col='Party',
    element_title_col='Name',
    element_subtitle_col='Constituency',
    elements_per_row=elements_per_row,
    section_sort_by='elements',
    section_sort_order='descending',
)

# PRODUCE GRAPHIC
graphic = lay_out_body(
    df_element,
    df_section,
    body_width=800,
    draw_area_margin_dim={'top': 10, 'right': 10, 'bottom': 10, 'left': 10},
    font='Open Sans',
    section_head_position='left',
    section_head_width=200,
    section_head_height=None,
    # section_head_position='top',
    # section_head_width=None,
    # section_head_height=100,
    section_head_vertical_text_align='top',
    section_head_text_size=20,
    section_head_text_weight=600,
    section_head_text_color=dict_party_colours,
    section_head_padding_dim={'top': 5, 'right': 5, 'bottom': 5, 'left': 5},
    elements_per_row=elements_per_row,
    element_height=50,
    element_margin_dim={'top': 2, 'right': 2, 'bottom': 2, 'left': 2},
)

# DISPLAY GRAPHIC
display(graphic)

# %%
