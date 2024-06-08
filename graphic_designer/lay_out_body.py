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
    df: pd.DataFrame,
    df_subtotal: pd.DataFrame = None,
    body_width: int = 800,
    draw_area_margin_dim: dict = {'top': 10, 'right': 10, 'bottom': 10, 'left': 10},
    font: str = 'Open Sans',
    section_head_position: Union[Literal['left'], Literal['top']] = 'top',
    section_head_width: int = 100,
    section_head_height: int = None,
    section_head_vertical_text_align: Literal['top', 'center', 'bottom'] = 'top',
    section_head_text_size: int = 20,
    section_head_text_color: str = 'black',
    section_head_padding_dim: dict = {'top': 5, 'right': 5, 'bottom': 5, 'left': 5},
    elements_per_row: int = 5,
    element_height: int = 50,
    element_margin_dim: dict = {'top': 2, 'right': 2, 'bottom': 2, 'left': 2},

):
    """
    Lay out graphic body

    Parameters
        - df: Data to be displayed in the graphic body
        - df_subtotal: Subtotals for each section in df
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
        - section_head_text_color: Color of text in section heads
        - elements_per_row: Number of elements to be displayed in each row
        - element_height: Height of each element
        - element_margin_dim: Margin dimensions for each element

    Returns
        - body: Graphic body

    Notes
        - None
    """

    # Calculate draw area, body dimensions
    if section_head_position == 'left':
        draw_area_dim = {
            'width': body_width - draw_area_margin_dim['left'] - draw_area_margin_dim['right'],
            'height': df_subtotal['rows'].sum() * element_height
        }
    elif section_head_position == 'top':
        draw_area_dim = {
            'width': body_width - draw_area_margin_dim['left'] - draw_area_margin_dim['right'],
            'height': (
                df_subtotal['rows'].sum() * element_height + len(df_subtotal) * section_head_height
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
    for i, row in df_subtotal.iterrows():

        # Reset x
        x = 0

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

        # Draw section head
        draw_area.append(
            draw.Rectangle(
                x=x, y=y,
                width=section_head_dim['width'], height=section_head_dim['height'],
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
        draw_area.append(
            draw.Text(
                row['section'],
                x=text_x, y=text_y,
                font_size=section_head_text_size, font_family=font, fill=section_head_text_color,
                text_anchor='start'
            )
        )

        x += left_section_head_dim['width']
        y += top_section_head_dim['height']

        # Draw section body
        draw_area.append(
            draw.Rectangle(
                x=x, y=y,
                width=section_body_dim['width'], height=section_body_dim['height'],
                fill=f"#{random.randint(0, 0xFFFFFF):06x}", stroke_width=0
            )
        )

        y += section_body_dim['height']

        # Draw elements
        # Calculate element dimensions
        # TODO
        # element_dim = {
        #     'width': section_body_dim['width'] / elements_per_row,
        #     'height': element_height
        # }

    # Add draw_area to body
    body.append(draw_area)

    return body
