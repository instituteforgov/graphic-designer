# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Purpose
        Define function to lay out graphic body
    Inputs
        None
    Outputs
        None
    Parameters
        None
    Notes
        None
"""

import os
import random
from typing import Literal, Union

import drawsvg as draw
import pandas as pd

# Import cairosvg from its DLL
# NB: Following the approach described here and in related
# comment: https://stackoverflow.com/a/60220855/4659442
os.environ['path'] += r';C:/Program Files/Inkscape/bin'
import cairosvg     # noqa: E402, F401


# DEFINE FUNCTION
def lay_out_body(
    df_element: pd.DataFrame,
    df_section: pd.DataFrame,
    body_width: int = 800,
    draw_area_margin_dim: dict = {'top': 10, 'right': 10, 'bottom': 10, 'left': 10},
    font: str = 'Open Sans',
    section_head_position: Union[Literal['left'], Literal['top']] = 'top',
    section_head_width: int = 100,
    section_head_height: int = None,
    section_head_vertical_text_align: Literal['top', 'center', 'bottom'] = 'top',
    section_head_text_size: int = 20,
    section_head_text_weight: int = 600,
    section_head_text_color: Union[str, dict] = 'black',
    section_head_padding_dim: dict = {'top': 5, 'right': 5, 'bottom': 5, 'left': 5},
    elements_per_row: int = 5,
    element_height: int = 50,
    element_margin_dim: dict = {'top': 2, 'right': 2, 'bottom': 2, 'left': 2},
    merge_sections: list = []
) -> draw.Drawing:
    """
    Lay out graphic body

    Parameters
        - df_element: DataFrame of data to be used when drawing graphic elements
        - df_section: DataFrame of section subtotals
        - body_width: Width of the graphic body
        - draw_area_margin_dim: Margin dimensions for the draw area
        - font: Font to be used in the graphic body
        - section_head_position: Whether section heads should be drawn above
        or to the left of the section body. Options are 'top' or 'left'
        - section_head_width: Width of section heads when section_head_position
        is 'left'. This is ignored when section_head_position is 'top'
        - section_head_height: Height of section heads when section_head_position
        is 'top'. This is ignored when section_head_position is 'left'
        - section_head_vertical_text_align: Vertical alignment of text in section heads
        - section_head_text_size: Font size of text in section heads
        - section_head_text_weight: Font weight of text in section heads
        - section_head_text_color: Color of text in section heads. If a string, this
        color is applied to all section heads. If a dictionary, each key should be a
        section name and the corresponding value should be the color for that section
        - section_head_padding_dim: Padding dimensions for section heads
        - elements_per_row: Number of elements to be displayed in each row
        - element_height: Height of each element
        - element_margin_dim: Margin dimensions for each element
        - merge_sections: List of sections to merge. Only applicable where
        section_head_position is 'top', as sections can't be merged where
        section_head_position is 'left'. Sections to merge must fit onto
        a single row, and be supplied in the order they appear in the data.

    Returns
        - body: Graphic body

    Notes
        - None
    """

    # Calculate total row count
    total_rows = df_section['rows'].sum()
    section_heads = len(df_section)

    # Handle merge_sections
    if section_head_position == 'top' and merge_sections:

        # Check sections to be merged fit onto a single row
        merge_sections_elements = df_section.loc[
            df_section['section'].isin(merge_sections),
            'elements'
        ].sum()
        if merge_sections_elements > elements_per_row:
            raise ValueError(
                'Sections to merge must fit onto a single row. Sections supplied in ' +
                f'merge_sections have {merge_sections_elements} elements, but ' +
                f'elements_per_row is {elements_per_row}'
            )

        # Check sections to be merged are in the correct order
        if df_section.loc[
            df_section['section'].isin(merge_sections),
            'section'
        ].tolist() != merge_sections:
            raise ValueError(
                'Sections to merge must be supplied in the order they appear in the data'
            )

        # Adjust total row count
        merge_rows_initial = df_section.loc[
            df_section['section'].isin(merge_sections)
        ]['rows'].sum()
        merge_rows_final = - (
            - df_section.loc[
                df_section['section'].isin(merge_sections)
            ]['elements'].sum() // elements_per_row
        )
        total_rows = total_rows - merge_rows_initial + merge_rows_final

        # Adjust section_heads count
        section_heads = section_heads - len(merge_sections) + 1

    # Calculate draw area, body dimensions
    if section_head_position == 'left':
        draw_area_dim = {
            'width': body_width - draw_area_margin_dim['left'] - draw_area_margin_dim['right'],
            'height': total_rows * element_height
        }
    elif section_head_position == 'top':
        draw_area_dim = {
            'width': body_width - draw_area_margin_dim['left'] - draw_area_margin_dim['right'],
            'height': (
                total_rows * element_height + section_heads * section_head_height
            )
        }

    body_height = (
        draw_area_dim['height'] + draw_area_margin_dim['top'] + draw_area_margin_dim['bottom']
    )

    # Create graphic body
    body = draw.Drawing(body_width, body_height)

    # Add font
    body.embed_google_font(font)

    # Add background
    body.append(
        draw.Rectangle(
            x=0, y=0,
            width=body_width, height=body_height,
            fill='white'
        )
    )

    # Create draw_area
    # NB: transform means that elements appended to draw_area use the top-left of
    # the draw_area as the origin. Elements are not constrained to the dimensions of
    # the draw_area though - this still needs to be managed as part of drawing elements
    # Ref: https://gist.github.com/mbostock/3019563
    draw_area = draw.Group(
        transform=(
            'translate(' +
            str(draw_area_margin_dim['left']) + ',' +
            str(draw_area_margin_dim['top']) +
            ')'
        )
    )

    # Initialise pointers used to position SVG components
    x = 0
    y = 0

    # Create sections
    for i, row in df_section.iterrows():

        # Calculate section dimensions
        # NB: By calculating left_section_head_dim, top_section_head_dim for both
        # section_head_position options, this simplifies the logic that comes after
        if section_head_position == 'left':
            left_section_head_dim = {
                'width': section_head_width,
                'height': row['rows'] * element_height
            }
            top_section_head_dim = {
                'width': 0,
                'height': 0
            }
        elif section_head_position == 'top':
            left_section_head_dim = {
                'width': 0,
                'height': 0
            }
            top_section_head_dim = {
                'width': draw_area_dim['width'],
                'height': section_head_height
            }

        section_head_dim = {
            'width': left_section_head_dim['width'] + top_section_head_dim['width'],
            'height': left_section_head_dim['height'] + top_section_head_dim['height']
        }
        section_body_dim = {
            'width': draw_area_dim['width'] - left_section_head_dim['width'],
            'height': row['rows'] * element_height
        }

        # Calculate element dimensions
        element_dim = {
            'width': section_body_dim['width'] / elements_per_row,
            'height': element_height
        }

        # Draw section head
        draw_area.append(
            draw.Rectangle(
                x=x, y=y,
                width=section_head_dim['width'] - x, height=section_head_dim['height'],
                fill='lightgrey', stroke_width=0
            )
        )

        # Calculate text position
        if section_head_vertical_text_align == 'top':
            text_x = x + section_head_padding_dim['left']
            text_y = y + section_head_padding_dim['top'] + section_head_text_size
        elif section_head_vertical_text_align == 'center':
            text_x = x + section_head_padding_dim['left']
            text_y = (
                y + section_head_padding_dim['top'] +
                (section_head_dim['height'] + section_head_text_size) / 2 -
                section_head_padding_dim['bottom']
            )
        elif section_head_vertical_text_align == 'bottom':
            text_x = x + section_head_padding_dim['left']
            text_y = y + section_head_dim['height'] - section_head_padding_dim['bottom']

        # Draw section head text
        if isinstance(section_head_text_color, dict):
            if row['section'] in section_head_text_color:
                text_color = section_head_text_color[row['section']]
            else:
                text_color = 'black'
        else:
            text_color = section_head_text_color

        draw_area.append(
            draw.Text(
                row['section'],
                x=text_x, y=text_y,
                font_size=section_head_text_size,
                font_weight=section_head_text_weight,
                font_family=font,
                fill=text_color,
                text_anchor='start'
            )
        )

        x += left_section_head_dim['width']
        y += top_section_head_dim['height']

        # Initialise counter and pointers
        # NB: A seperate counter is used to track the element number, as iterrows()'s
        # j tracks all rows in df_element, not just the rows for the current section
        element_i = 0

        element_x = x
        element_y = y

        # Draw elements
        for j, element_row in df_element.loc[
            df_element['section'] == row['section']
        ].iterrows():

            # Iterate counter
            element_i += 1

            # Draw element
            draw_area.append(
                draw.Rectangle(
                    x=element_x, y=element_y,
                    width=element_dim['width'],
                    height=element_dim['height'],
                    fill=f"#{random.randint(0, 0xFFFFFF):06x}",
                    stroke_width=0
                )
            )
            draw_area.append(
                draw.Text(
                    str(element_i),
                    x=element_x, y=element_y,
                    font_size=section_head_text_size,
                    font_weight=section_head_text_weight,
                    font_family=font,
                    fill='black',
                    text_anchor='start',
                    dominant_baseline='hanging'
                )
            )

            # Check if row is complete
            if (element_i) % elements_per_row == 0:
                element_x = x
                element_y += element_dim['height']
            else:
                element_x += element_dim['width']

        y += section_body_dim['height']

        # Reset y pointer where section is merged
        # NB: This moves the y pointer back to the top of the previous section
        # head and pre-emptively resets x back the end of the previous row
        if section_head_position == 'top' and row['section'] in merge_sections:
            y -= top_section_head_dim['height']
            y -= section_body_dim['height']

        # Set x pointer
        if not (section_head_position == 'top' and row['section'] in merge_sections):
            x = 0
        else:
            x += element_i * element_dim['width']

    # Add draw_area to body
    body.append(draw_area)

    return body
