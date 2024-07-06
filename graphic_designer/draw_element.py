# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Purpose
        Define function to draw graphic element
    Inputs
        None
    Outputs
        None
    Parameters
        None
    Notes
        None
"""

import drawsvg as draw


# DEFINE FUNCTION
def draw_element(
    x: int,
    y: int,
    width: int,
    height: int,
    background_color: str,
    title: str,
    title_text_size: int,
    title_text_weight: int,
    title_text_color: str,
    title_text_style: str,
    subtitle: str,
    subtitle_text_size: int,
    subtitle_text_weight: int,
    subtitle_text_color: str,
    subtitle_text_style: str,
    font_family: str,
    title_position: str,
    text_anchor: str,
    image: str,
    margin_dim: dict,
    circle_padding_dim: dict,
    circle_stroke_color: str,
    circle_stroke_width: int = 0,
) -> draw.Drawing:
    """
    Draw graphic element

    Parameters
        - x: x-coordinate of top-left corner of element
        - y: y-coordinate of top-left corner of element
        - width: Width of element
        - height: Height of element
        - background_color: Background colour of element
        - title: Title of element
        - title_text_size: Font size of title
        - title_text_weight: Font weight of title
        - title_text_color: Text colour
        - title_text_style: Font style of title
        - subtitle: Subtitle of element
        - subtitle_text_size: Font size of subtitle
        - subtitle_text_weight: Font weight of subtitle
        - subtitle_text_color: Text colour
        - subtitle_text_style: Font style of subtitle
        - font_family: Font family
        - title_position: Position of title
        - text_anchor: Text anchor
        - image: Image to be displayed in element
        - margin_dim: Margin dimensions
        - circle_padding_dim: Padding dimensions for circle
        - circle_stroke_color: Stroke colour of circle
        - circle_stroke_width: Stroke width of circle

    Returns
        - element: Graphic element

    Notes
        - None
    """

    # Create element group
    element = draw.Group()

    # Add background
    element.append(
        draw.Rectangle(
            x,
            y,
            width,
            height,
            fill=background_color,
        ),
    )

    # Add circle clip path
    circle_radius = min(
        (
            width -
            margin_dim['left'] -
            margin_dim['right'] -
            circle_padding_dim['left'] -
            circle_padding_dim['right']
        ) / 2,
        (
            height -
            margin_dim['top'] -
            margin_dim['bottom'] -
            circle_padding_dim['top'] -
            circle_padding_dim['bottom'] -
            title_text_size -
            subtitle_text_size
        ) / 2,
    )

    clip_circle = draw.ClipPath()
    clip_circle.append(
        draw.Circle(
            cx=x + width / 2,
            cy=y + margin_dim['top'] + circle_padding_dim['top'] + circle_radius,
            r=circle_radius,
            stroke_width=circle_stroke_width,
        )
    )

    # Add circle
    element.append(
        draw.Circle(
            cx=x + width / 2,
            cy=y + margin_dim['top'] + circle_padding_dim['top'] + circle_radius,
            r=circle_radius,
            stroke=circle_stroke_color,
            stroke_width=circle_stroke_width,
            fill=circle_stroke_color
        ),
    )

    # Add image
    element.append(
        draw.Image(
            clip_path=clip_circle,
            x=x + width / 2 - circle_radius,
            y=y + margin_dim['top'] + circle_padding_dim['top'],
            path=image,
            embed=True,
            width=2 * circle_radius,
            height=2 * circle_radius,
        ),
    )

    # Calculate title x-coordinate
    if text_anchor == 'start':
        title_x = x + margin_dim['left']
    elif text_anchor == 'middle':
        title_x = x + width / 2
    elif text_anchor == 'end':
        title_x = x + width - margin_dim['right']

    # Calculate title y-coordinate
    if title_position == 'top':
        title_y = y + margin_dim['top']
        subtitle_y = y + margin_dim['top'] + title_text_size
        dominant_baseline = 'hanging'
    elif title_position == 'bottom':
        title_y = y + height - margin_dim['bottom'] - subtitle_text_size
        subtitle_y = y + height - margin_dim['bottom']
        dominant_baseline = 'auto'

    # Add title
    element.append(
        draw.Text(
            title,
            x=title_x,
            y=title_y,
            font_size=title_text_size,
            font_weight=title_text_weight,
            font_family=font_family,
            font_style=title_text_style,
            fill=title_text_color,
            text_anchor=text_anchor,
            dominant_baseline=dominant_baseline,
        ),
    )

    # Add subtitle
    element.append(
        draw.Text(
            subtitle,
            x=title_x,
            y=subtitle_y,
            font_size=subtitle_text_size,
            font_weight=subtitle_text_weight,
            font_family=font_family,
            font_style=subtitle_text_style,
            fill=subtitle_text_color,
            text_anchor=text_anchor,
            dominant_baseline=dominant_baseline,
        ),
    )

    # Return element
    return element
