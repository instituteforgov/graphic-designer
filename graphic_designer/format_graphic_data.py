# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Purpose
        Define function to format graphic data
    Inputs
        None
    Outputs
        None
    Parameters
        None
    Notes
        None
"""

from typing import Literal, Optional, Union

import pandas as pd


def calculate_offset_rows(
    elements: int,
    elements_per_row: int,
) -> int:
    """
    Calculate number of rows needed for a section with an offset

    Parameters
        - elements: Number of elements in the section
        - elements_per_row: Number of elements to be drawn per row. Where offset_rows is
        True, this will be the number of elements in the odd rows of each section and
        even rows will contain one fewer element

    Returns
        - Number of rows needed for the section

    Notes
        - None
    """
    complete_row_pairs = elements // (2 * elements_per_row - 1)
    complete_row_pair_elements = complete_row_pairs * (2 * elements_per_row - 1)
    remaining_elements = elements - complete_row_pair_elements
    if remaining_elements == 0:
        return 2 * complete_row_pairs
    elif remaining_elements <= elements_per_row:
        return 2 * complete_row_pairs + 1
    else:
        return 2 * complete_row_pairs + 2


def format_graphic_data(
    df: pd.DataFrame,
    section_col: str,
    element_title_col: str,
    element_subtitle_col: str,
    element_image_col: str,
    elements_per_row: int,
    offset_rows: bool = False,
    section_sort_by: Union[Literal['section', 'elements'], list] = 'elements',
    section_sort_order: Optional[Literal['ascending', 'descending']] = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Produce graphic data

    Parameters
        - df: Data to be used in the graphic
        - section_col: Column in df giving which section each row belongs to. This should
        be a column in df and should not contain any missing values
        - element_title_col: Column in df of element titles
        - element_subtitle_col: Column in df of element subtitles
        - element_image_col: Column in df of element image filepaths
        - elements_per_row: Number of elements to be drawn per row. Where offset_rows is
        True, this will be the number of elements in the odd rows of each section and
        even rows will contain one fewer element
        - offset_rows: Whether ever other row should be offset relative to the previous row
        and contain one fewer element
        - section_sort_by: Order by which to sort the sections. Either 'section', 'elements'
        or a list of section names. If 'section' this will sort by the section names. If
        'elements' this will sort by the number of elements in each section. If a list of
        section names this will sort by the specified order. If a list is used, all sections
        in section_col must be included
        - section_sort_order: Order in which to sort the sections. Not applied if section_sort_by
        is a list

    Returns
        - df_element: DataFrame of element data with columns section, element_title,
        element_subtitle and element_image
        - df_section: DataFrame of section subtotals with columns section, elements and
        rows

    Notes
        - None
    """
    # Check that section_col doesn't contain any missing values
    if df[section_col].isnull().any():
        raise ValueError(f"Missing values found in {section_col}")

    # Check that if section_sort_by is a list all elements are in df['section_col']
    if isinstance(section_sort_by, list):
        if not all([x in df[section_col].unique() for x in section_sort_by]):
            values_not_found = [x for x in section_sort_by if x not in df[section_col].unique()]
            raise ValueError(
                f"Values in section_sort_by not found in {section_col}: {values_not_found}"
            )

    # Check that if section_sort_by is a list all elements in df['section_col'] are
    # in section_sort_by
    if isinstance(section_sort_by, list):
        if not all([x in section_sort_by for x in df[section_col].unique()]):
            values_not_found = [x for x in df[section_col].unique() if x not in section_sort_by]
            raise ValueError(
                f"Values in section_col not found in section_sort_by: {values_not_found}"
            )

    # Create DataFrame of elements
    df_element = df[[
        section_col, element_title_col, element_subtitle_col, element_image_col
    ]].copy()

    # Rename columns
    df_element = df_element.rename(
        columns={
            section_col: 'section',
            element_title_col: 'element_title',
            element_subtitle_col: 'element_subtitle',
            element_image_col: 'element_image',
        }
    )

    # Drop rows with missing values in section_col
    df_element = df_element.dropna(subset='section')

    # Calculate subtotals by section
    df_section = pd.DataFrame(
        df_element.groupby('section').size(),
        columns=['elements']
    ).reset_index()

    # Sort df_section
    if section_sort_by in ['section', 'elements']:

        df_section = df_section.sort_values(
            by=section_sort_by,
            ascending=section_sort_order == 'ascending',
        ).reset_index(drop=True)

    elif isinstance(section_sort_by, list):

        # Make section column categorical with ordering
        df_section['section'] = pd.Categorical(
            df_section['section'],
            categories=section_sort_by,
            ordered=True,
        )

        # Sort
        df_section = df_section.sort_values(
            by='section',
            ascending=True,
        ).reset_index(drop=True)

    # Calculate number of rows needed for each section
    if offset_rows:
        df_section['rows'] = df_section['elements'].apply(
            lambda x: calculate_offset_rows(x, elements_per_row)
        )
    else:
        df_section['rows'] = df_section['elements'].apply(lambda x: -(-x // elements_per_row))

    # Make df_element section column categorical with ordering, following ordering of df_section
    df_element['section'] = pd.Categorical(
        df_element['section'],
        categories=df_section['section'],
        ordered=True,
    )

    # Sort elements
    # NB: Since section is a categorical column this sorts by the pre-defined order
    # NB: Sorting by 'index' applies the original order as a secondary ordering
    df_element = df_element.reset_index().sort_values(
        by=['section', 'index'],
        ascending=[True, True],
    ).reset_index(drop=True).drop(columns='index')

    return df_element, df_section
