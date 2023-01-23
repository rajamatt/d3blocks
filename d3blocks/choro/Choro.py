"""Choropleth block.

Library     : d3blocks
Author      : R.Sacchi
Github      : https://github.com/d3blocks/d3blocks
License     : GPL3
"""
from ismember import ismember
import colourmap
import numpy as np
from jinja2 import Environment, PackageLoader
import country_converter as coco
from country_converter import CountryConverter
from pathlib import Path
import os
import time
from collections import defaultdict

list_countries = CountryConverter().ISO2["ISO2"].values.tolist()

try:
    from .. utils import set_colors, pre_processing, convert_dataframe_dict, set_path, update_config, set_labels, create_unique_dataframe, write_html_file
except:
    from utils import set_colors, pre_processing, convert_dataframe_dict, set_path, update_config, set_labels, create_unique_dataframe, write_html_file


# %% Set configuration properties
def set_config(config={}, **kwargs):
    """Set the default configuration setting."""
    logger = kwargs.get('logger', None)
    config['chart'] ='Choro'
    config['title'] = kwargs.get('title', 'Chord - D3blocks')
    config['unit'] = kwargs.get('unit', 'unitless')
    config['filepath'] = set_path(kwargs.get('filepath', 'chord.html'), logger)
    config['figsize'] = kwargs.get('figsize', [900, 900])
    config['showfig'] = kwargs.get('showfig', True)
    config['overwrite'] = kwargs.get('overwrite', True)
    config['cmap'] = kwargs.get('cmap', 'tab20')
    config['fontsize'] = kwargs.get('fontsize', 10)
    config['notebook'] = kwargs.get('notebook', False)
    # return
    return config


def show(_, **kwargs):
    """Show the Choropleth chart.

    Parameters
    ----------
    df : pd.DataFrame()
        Input data.
    title : String, (default: None)
        Title of the figure.
    filepath : String, (Default: user temp directory)
        File path to save the output.
        'c://temp//Violin.html'
    figsize : tuple, (default: [None, None])
        Size of the figure in the browser, [width, height].
        [None, None]: The width is auto-determined based on the #labels.
    showfig : bool, (default: True)
        True: Open browser-window.
        False: Do not open browser-window.
    overwrite : bool, (default: True)
        True: Overwrite the html in the destination directory.
        False: Do not overwrite destination file but show warning instead.

    Returns
    -------
    config : dict
        Dictionary containing updated configuration keys.

    """

    # Convert dict/frame.
    config = update_config(kwargs)
    config = config.copy()
    X, Y = get_data_ready_for_d3(config["data"])

    # Write to HTML
    return write_html(X, Y, config)


def write_html(X, Y, config, logger=None):
    """Write html.

    Parameters
    ----------
    X : list of str
        Input data for javascript.
    config : dict
        Dictionary containing configuration keys.

    Returns
    -------
    None.

    """
    unit = config["data"].loc[:, "unit"].iloc[0]
    title = f"{config['title']}, {unit}"
    content = {
        'json_data': "[" + X + "]",
        'json_data2': "[" + Y + "]",
        'impact_sum': config["data"].loc[:, "weight"].sum(),
        'TITLE': '"' + title + '"',
        'WIDTH': config['figsize'][0],
        'HEIGHT': config['figsize'][1],
        'FONTSIZE': config['fontsize'],
    }

    try:
        jinja_env = Environment(loader=PackageLoader(package_name=__name__, package_path='d3js'))
    except:
        jinja_env = Environment(loader=PackageLoader(package_name='d3blocks.choro', package_path='d3js'))

    index_template = jinja_env.get_template('choro.html.j2')

    # Generate html content
    html = index_template.render(content)
    write_html_file(config, html, logger)
    # Return html
    return html



def get_data_ready_for_d3(df):
    """Convert the source-target data into d3 compatible data.

    Parameters
    ----------
    df : pd.DataFrame()
        Input data.
    labels : dict
        Dictionary containing hex colorlabels for the classes.
        The labels are derived using the function: labels = d3blocks.set_label_properties()

    Returns
    -------
    X : str.
        Converted data into a string that is d3 compatible.

    """

    extra_mapping = {
        "US-HICC": "US",
        "US-SERC": "US",
        "US-RFC": "US",
        "US-NPCC": "US",
        "US-ASCC": "US",
        "US-WECC": "US",
        "US-TRE": "US",
        "US-MRO": "US",
        "US-PR": "US",
        "CA-QC": "CA",
        "CA-AB": "CA",
        "CA-SK": "CA",
        "CA-MB": "CA",
        "CA-NB": "CA",
        "CA-NT": "CA",
        "CA-PE": "CA",
        "CA-NS": "CA",
        "CA-ON": "CA",
        "CA-BC": "CA",
        "CA-YK": "CA",
        "CA-NF": "CA",
        "CA-NU": "CA",
        "CN-SC": "CN",
        "CN-FJ": "CN",
        "CN-NM": "CN",
        "CN-HN": "CN",
        "CN-LN": "CN",
        "CN-GD": "CN",
        "CN-JS": "CN",
        "CN-QH": "CN",
        "CN-GS": "CN",
        "CN-CSG": "CN",
        "CN-JX": "CN",
        "CN-NX": "CN",
        "CN-YN": "CN",
        "CN-SH": "CN",
        "CN-GZ": "CN",
        "CN-HE": "CN",
        "CN-HA": "CN",
        "CN-XJ": "CN",
        "CN-CQ": "CN",
        "CN-SGCC": "CN",
        "CN-ZJ": "CN",
        "CN-HB": "CN",
        "CN-SA": "CN",
        "CN-SD": "CN",
        "CN-HL": "CN",
        "CN-AH": "CN",
        "CN-XZ": "CN",
        "CN-JL": "CN",
        "CN-HU": "CN",
        "CN-BJ": "CN",
        "CN-GX": "CN",
        "CN-TJ": "CN",
        "CN-SX": "CN",
        "IN-MH": "IN",
        "IN-UP": "IN",
        "IN-OR": "IN",
        "IN-DL": "IN",
        "IN-HR": "IN",
        "IN-GJ": "IN",
        "IN-WB": "IN",
        "IN-CT": "IN",
        "IN-PY": "IN",
        "IN-Western": "IN",
        "IN-KL": "IN",
        "IN-TN": "IN",
        "IN-RJ": "IN",
        "IN-Northern": "IN",
        "IN-AS": "IN",
        "IN-North-eastern": "IN",
        "IN-AP": "IN",
        "IN-Southern": "IN",
        "IN-KA": "IN",
        "IN-MP": "IN",
        "IN-UT": "IN",
        "IN-NL": "IN",
        "IN-TR": "IN",
        "IN-Eastern": "IN",
        "IN-HP": "IN",
        "IN-BR": "IN",
        "IN-JH": "IN",
        "IN-GA": "IN",
        "IN-MN": "IN",
        "IN-PB": "IN",
        "IN-ML": "IN",
        "IN-SK": "IN",
        "IN-AR": "IN",
        "IN-JK": "IN",
        "BR-AC": "BR",
        "BR-AL": "BR",
        "BR-AM": "BR",
        "BR-AP": "BR",
        "BR-BA": "BR",
        "BR-CE": "BR",
        "BR-DF": "BR",
        "BR-ES": "BR",
        "BR-GO": "BR",
        "BR-MA": "BR",
        "BR-MG": "BR",
        "BR-Mid-western": "BR",
        "BR-MS": "BR",
        "BR-MT": "BR",
        "BR-North-eastern": "BR",
        "BR-Northern": "BR",
        "BR-PA": "BR",
        "BR-PB": "BR",
        "BR-PE": "BR",
        "BR-PI": "BR",
        "BR-PR": "BR",
        "BR-RJ": "BR",
        "BR-RN": "BR",
        "BR-RO": "BR",
        "BR-RR": "BR",
        "BR-RS": "BR",
        "BR-SC": "BR",
        "BR-SE": "BR",
        "BR-South-eastern": "BR",
        "BR-Southern": "BR",
        "BR-SP": "BR",
        "BR-TO": "BR",
        "BR-North-eastern grid": "BR",
        "BR-South-eastern grid": "BR",
        "BR-Southern grid": "BR",
        "BR-Northern grid": "BR",
        "BR-Mid-western grid": "BR",
        "GB": "GB",
    }

    # create a dictionary with `location` as keys and `weight` as values
    identified_countries = defaultdict(float)
    unidentified_countries = defaultdict(float)
    for i, row in df.iterrows():
        if row["country"] in list_countries:
            loc = coco.convert(row['country'], to='ISOnumeric')
            # if two-digit, add a zero in front
            if len(str(loc)) == 2:
                loc = "0" + str(loc)
            identified_countries[loc] += row["weight"]
        elif row["country"] in extra_mapping:
            loc = coco.convert(extra_mapping[row["country"]], to='ISOnumeric')
            # if two-digit, add a zero in front
            if len(str(loc)) == 2:
                loc = "0" + str(loc)
            identified_countries[loc] += row["weight"]
        else:
            unidentified_countries[row["country"]] += row["weight"]

    X = ""
    for key, val in identified_countries.items():
        X += '{id: "' + str(key) + '", value: ' + str(val) + ', country: "' + coco.convert(format_key(key), to='name_short') + '"}, '

    X = X[:-2]

    Y = ""
    for key, val in unidentified_countries.items():
        Y += '{id: "' + str(key) + '", value: ' + str(val) + ', country: "' + key + '"}, '

    Y = Y[:-2]

    # Return
    return X, Y

def format_key(key):
    """Remove leading zero from key if it exists."""
    if isinstance(key, str):
        if key.startswith("0"):
            key = key[1:]

    return key
