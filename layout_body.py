# %%
# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Purpose
        XXX
    Inputs
        XXX
    Outputs
        XXX
    Parameters
        XXX
    Notes
        XXX
"""

# flake8: noqa

import os

import drawsvg as draw
from IPython.display import display
import pandas as pd

# %%
# Import cairosvg from its DLL
# NB: Following the approach described here and in related
# comment: https://stackoverflow.com/a/60220855/4659442
os.environ['path'] += r';C:/Program Files/Inkscape/bin'
import cairosvg     # noqa: E402, F401

# %%
# SET PARAMETERS
body_dim = {'width': 1000, 'height': 500}
margin_dim = {'top': 10, 'right': 10, 'bottom': 10, 'left': 10}

font = 'Open Sans'

# Positioning
# section_head_position = 'top'
section_head_key_dim = 100      # XXX

section_head_position = 'left'

section_row_height = 50


elements_per_row = 5
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
# CREATE GRAPHIC
# Create body
body = draw.Drawing(body_dim['width'], body_dim['height'])

# Add font
body.embed_google_font(font)

# Add background
body.append(
    draw.Rectangle(
        x=0, y=0,
        width=body_dim['width'], height=body_dim['height'],
        fill='white'
    )
)

# Create draw_area
# NB: transform means that elements appended to draw_area use the top-left of
# the draw_area as the origin. Elements are not constrained to the dimensions of
# the draw_area though - this still needs to be managed as part of drawing elements
# Ref: https://gist.github.com/mbostock/3019563
draw_area_dim = {
    'width': body_dim['width'] - margin_dim['left'] - margin_dim['right'],
    'height': body_dim['height'] - margin_dim['top'] - margin_dim['bottom']
}

draw_area = draw.Group(
    transform='translate(' + str(margin_dim['left']) + ',' + str(margin_dim['top']) + ')'
)

# Create sections
section_dim = {
    'width': draw_area_dim['width'],
    'height': draw_area_dim['height'] / sections
}

if section_head_position == 'left':
    pass

# Draw elements
element_dim = {
    'width': (draw_area_dim['width'] - (elements_per_row - 1) * element_margin_dim['left'] - element_margin_dim['right']) / elements_per_row,
    'height': (draw_area_dim['height'] - (number_of_elements / elements_per_row - 1) * element_margin_dim['top'] - element_margin_dim['bottom']) / (number_of_elements / elements_per_row)
}
for i in range(number_of_elements):
    row = i // elements_per_row
    col = i % elements_per_row
    x = col * (element_dim['width'] + element_margin_dim['left'])
    y = row * (element_dim['height'] + element_margin_dim['top'])
    draw_area.append(
        draw.Rectangle(
            x=x, y=y,
            width=element_dim['width'], height=element_dim['height'],
            fill='orange', stroke_width=0, stroke='blue'
        )
    )

# Add draw_area to body
body.append(draw_area)

# %%
# Display body
display(body)

# %%
body.save_svg('MPs standing down graphic inner.svg')

# %%
