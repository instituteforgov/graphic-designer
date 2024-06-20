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
from typing import Literal, TextIO, Union

import drawsvg as draw
import pandas as pd

from draw_element import draw_element

# Import cairosvg from its DLL
# NB: Following the approach described here and in related
# comment: https://stackoverflow.com/a/60220855/4659442
os.environ['path'] += r';C:/Program Files/Inkscape/bin'
import cairosvg     # noqa: E402, F401


def calculate_offset_element_totals(
    elements: int,
    elements_per_row: int,
) -> list[int]:
    """
    For a given total number of elements, produce a list where
    each element is the total number of elements up to the end
    of the corresponding row in a graphic where rows are offset

    Parameters
        - elements: Number of elements in the section
        - elements_per_row: Number of elements to be drawn per row. Where offset_rows is
        True, this will be the number of elements in the odd rows of each section and
        even rows will contain one fewer element

    Returns
        - List of element totals

    Notes
        - None
    """

    # Initialize the sequence with the first term
    sequence = [elements_per_row]

    # Generate the sequence for n terms
    i = 1
    while sequence[-1] < elements:
        if i % 2 != 0:
            next_term = sequence[-1] + elements_per_row - 1
        else:
            next_term = sequence[-1] + elements_per_row
        sequence.append(next_term)
        i += 1

    return sequence


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
    section_head_background_color: str = 'white',
    section_head_padding_dim: dict = {'top': 5, 'right': 5, 'bottom': 5, 'left': 5},
    elements_per_row: int = 5,
    offset_rows: bool = False,
    element_height: int = 50,
    element_title_position: Literal['top', 'bottom'] = 'bottom',
    element_title_text_size: int = 10,
    element_title_text_weight: int = 400,
    element_title_text_style: str = None,
    element_subtitle_text_size: int = 8,
    element_subtitle_text_weight: int = 400,
    element_subtitle_text_style: str = None,
    element_circle_stroke_width: int = 2,
    element_background_color: str = 'white',
    element_margin_dim: dict = {'top': 2, 'right': 2, 'bottom': 2, 'left': 2},
    element_circle_padding_dim: dict = {'top': 2, 'right': 2, 'bottom': 2, 'left': 2},
    display_section_totals: bool = False,
    merge_sections: list = []
) -> TextIO:
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
        - section_head_background_color: Background color of section heads
        - section_head_padding_dim: Padding dimensions for section heads
        - elements_per_row: Number of elements to be drawn per row. Where offset_rows is
        True, this will be the number of elements in the odd rows of each section and
        even rows will contain one fewer element
        - offset_rows: Whether every other row should be offset relative to the previous
        row and contain one fewer element
        - element_height: Height of each element
        - element_title_position: Position of element titles. Options are 'top' or 'bottom'
        - element_title_text_size: Font size of element titles
        - element_title_text_weight: Font weight of element titles
        - element_title_text_style: Font style of element titles
        - element_subtitle_text_size: Font size of element subtitles
        - element_subtitle_text_weight: Font weight of element subtitles
        - element_subtitle_text_style: Font style of element subtitles
        - element_circle_stroke_width: Stroke width of circle
        - element_background_color: Background color of elements
        - element_margin_dim: Margin dimensions for each element
        - element_circle_padding_dim: Padding dimensions for element circles
        - display_section_totals: Whether section totals should be displayed
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
                fill=section_head_background_color,
                stroke_width=0
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

        if display_section_totals:
            section_head_text = f"{row['section']}: {row['elements']}"
        else:
            section_head_text = row['section']

        draw_area.append(
            draw.Text(
                section_head_text,
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

        # Calculate list of element totals
        if offset_rows:
            element_totals = calculate_offset_element_totals(
                elements=row['elements'],
                elements_per_row=elements_per_row
            )

        # Draw elements
        for j, element_row in df_element.loc[
            df_element['section'] == row['section']
        ].iterrows():

            # Iterate counter
            element_i += 1

            # Draw element
            draw_area.append(
                draw_element(
                    x=element_x,
                    y=element_y,
                    width=element_dim['width'],
                    height=element_dim['height'],
                    background_color=element_background_color,
                    title=element_row['element_title'],
                    title_text_size=element_title_text_size,
                    title_text_weight=element_title_text_weight,
                    title_text_style=element_title_text_style,
                    subtitle=element_row['element_subtitle'],
                    subtitle_text_size=element_subtitle_text_size,
                    subtitle_text_weight=element_subtitle_text_weight,
                    subtitle_text_style=element_subtitle_text_style,
                    font_family=font,
                    text_color='black',
                    title_position=element_title_position,
                    text_anchor='middle',
                    image=element_row['element_image'],
                    margin_dim=element_margin_dim,
                    circle_stroke_width=element_circle_stroke_width,
                    circle_stroke_color=section_head_text_color[element_row['section']],
                    circle_padding_dim=element_circle_padding_dim
                )
            )

            # Check if row is complete
            if offset_rows:

                if element_i in element_totals:

                    # After odd rows (0-based indexing), apply offset
                    if element_totals.index(element_i) % 2 != 0:
                        element_x = x
                        element_y += element_dim['height']

                    # After even rows, don't apply offset
                    else:
                        element_x = x + element_dim['width'] / 2
                        element_y += element_dim['height']

                else:
                    element_x += element_dim['width']

            else:
                if element_i % elements_per_row == 0:
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
