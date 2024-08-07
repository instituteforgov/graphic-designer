# %%
# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Purpose
        Produce graphic
    Inputs
        - img: <parliament_id>-<name>.<format>
            - Portrait photos
        - xlsm: 'MPs standing down GE24 main data.xlsm'
    Outputs
        - svg: <graphic-filename>.svg
    Parameters
        - ifg_dark_grey: Colour used for text
        - dict_party_colours: Party colours
        - image_filepath_stub: Stub of image filepaths
        - image_source: Non-default image sources
        - See format_graphic_data(), lay_out_body(),
        add_header_footer() docstrings for description of
        further parameters
    Notes
        None
    Bugs
        - When switching from section_head_position='left' to section_head_position='top' and
        vice versa, images are not displayed correctly. Clearing the VSCode interactive window
        fixes this - there's no need to restart the kernel, so it's unclear why this happens
"""

import os

from IPython.display import display
import pandas as pd

from format_graphic_data import format_graphic_data
from lay_out_body import lay_out_body

# %%
# SET PARAMETERS
# Colours
ifg_dark_grey = '#333f48'

dict_party_colours = {
    'Conservative': '#00539f',
    'Labour': '#ee3224',
    'Liberal Democrat': '#ffb703',
    'Scottish National\nParty': '#fff95d',
    'Plaid Cymru': '#3f8429',
    'Green': '#6ab023',
    'Reform UK': '#3bb7ce',
    'Democratic Unionist Party': '#8f1d20',
    'Sinn Féin': '#006837',
    'Independent': '#c1c5c8',
}

# Image locations
image_filepath_stub = (
    'C:/Users/' + os.getlogin() + '/'
    'Institute for Government/Data - General/'
    'Parliament/Member portraits/Images/'
)

# Set parameter specifying non-default image sources
image_source = {
    'Francie Molloy': 'Alamy/',
    'Mickey Brady': 'Alamy/',
}

# Graphic parameters
elements_per_row = 5
offset_rows = False

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
    {'SNP': 'Scottish National\nParty'}
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

# Add image filepaths
for i, row in df.iterrows():

    # Identify filepath
    if row['Name'] in image_source:
        image_filepath = (
            image_filepath_stub + image_source[row['Name']]
        )
    else:
        image_filepath = (
            image_filepath_stub + 'Parliament/'
        )

    try:
        image_filename = [
            filename for filename in os.listdir(image_filepath)
            if filename.startswith(str(int(row['Parliament ID'])) + '-')
        ][-1]
    except IndexError:
        print(i, row['Parliament ID'], row['Name'])
        pass

    # Add to df
    df.loc[i, 'Image filepath'] = image_filepath + image_filename

# %%
# PRODUCE GRAPHIC DATA
df_element, df_section = format_graphic_data(
    df,
    section_col='Party',
    element_title_col='Name',
    element_subtitle_col='Constituency',
    element_image_col='Image filepath',
    elements_per_row=elements_per_row,
    offset_rows=offset_rows,
    section_sort_by='elements',
    section_sort_order='descending',
)

# PRODUCE GRAPHIC
body = lay_out_body(
    df_element,
    df_section,
    body_width=800,
    draw_area_margin_dim={'top': 10, 'right': 10, 'bottom': 10, 'left': 10},
    font='Open Sans',
    section_head_position='left',
    section_head_width=225,
    section_head_height=None,
    # section_head_position='top',
    # section_head_width=None,
    # section_head_height=35,
    section_head_vertical_text_align='top',
    section_head_text_size=20,
    section_head_text_weight=600,
    section_head_text_color=dict_party_colours,
    section_head_background_color='white',
    section_head_padding_dim={'top': 5, 'right': 5, 'bottom': 5, 'left': 5},
    elements_per_row=elements_per_row,
    offset_rows=offset_rows,
    element_height=(800-225-10-10)/5,
    # element_height=(800-10-10)/5,
    element_title_position='bottom',
    element_title_text_size=10,
    element_title_text_weight=400,
    element_title_text_color=dict_party_colours,
    element_subtitle_text_size=8,
    element_subtitle_text_weight=400,
    element_subtitle_text_color=dict_party_colours,
    element_subtitle_text_style='italic',
    element_circle_stroke_width=5,
    element_background_color='white',
    element_margin_dim={'top': 5, 'right': 2, 'bottom': 5, 'left': 2},
    element_circle_padding_dim={'top': 2, 'right': 2, 'bottom': 2, 'left': 2},
    display_section_totals=True,
    merge_sections=['Sinn Féin', 'Green', 'Plaid Cymru'],
)

# DISPLAY GRAPHIC
display(graphic)

# %%
