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

import pandas as pd


def format_graphic_data(
    df: pd.DataFrame,
    count_col: str,
    section_col: str,
    elements_per_row: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Produce graphic data

    Parameters
        - df: Data to be used in the graphic
        - count_col: Column in df of element values. If this contains any missing values
        these rows will be dropped
        - section_col: Column in df giving which section each row belongs to. This should
        be a column in df and should not contain any missing values
        - elements_per_row: Number of elements to be drawn per row

    Returns
        - df_element: DataFrame of data to be used when drawing graphic elements
        - df_section: DataFrame of section subtotals

    Notes
        - None
    """
    # Check that section_col doesn't contain any missing values
    if df[section_col].isnull().any():
        raise ValueError(f"Missing values found in {section_col}")

    # Create DataFrame of elements
    df_element = df.copy()

    # Drop rows with missing values in count_col
    df_element = df_element.dropna(subset=[count_col])

    # Calculate subtotals by section
    df_section = df_element.groupby(
        by=section_col,
        as_index=False,
        observed=True,
    ).agg({
        count_col: 'count'
    }).rename(
        columns={
            section_col: 'section',
            count_col: 'elements'
        }
    ).sort_values(
        by='elements',
        ascending=False,
    ).reset_index(drop=True)

    # Calculate number of rows needed for each section
    df_section['rows'] = df_section['elements'].apply(lambda x: -(-x // elements_per_row))

    # Make section column categorical with ordering, following the ordering of df_section
    df_element[section_col] = pd.Categorical(
        df_element[section_col],
        categories=df_section['section'],
        ordered=True,
    )

    # Sort elements
    # NB: Since section is a categorical column this sorts by the pre-defined order
    # NB: Sorting by 'index' applies the original order as a secondary ordering
    df_element = df_element.reset_index().sort_values(
        by=[section_col, 'index'],
        ascending=[True, True],
    ).reset_index(drop=True)

    return df_element, df_section
