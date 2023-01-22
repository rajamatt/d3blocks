"""Choropleth block.

Library     : d3blocks
Author      : R.Sacchi
Github      : https://github.com/d3blocks/d3blocks
License     : GPL3
"""
from jinja2 import Environment, PackageLoader
import country_converter as coco
from country_converter import CountryConverter
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
    X = get_data_ready_for_d3(config["data"])

    # Write to HTML
    return write_html(X, config)


def write_html(X, config, logger=None):
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
        'json_data': X,
        'TITLE': '"' + title + '"',
        'WIDTH': config['figsize'][0],
        'HEIGHT': config['figsize'][1],
        'FONTSIZE': config['fontsize'],
    }

    try:
        jinja_env = Environment(loader=PackageLoader(package_name=__name__, package_path='d3js'))
    except:
        jinja_env = Environment(loader=PackageLoader(package_name='d3blocks.treemap', package_path='d3js'))

    index_template = jinja_env.get_template('treemap.html.j2')

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

    # convert dataframe column "name"
    # into a list of dictionaries of shape {"name": "name", "size": value}
    df_ = df.loc[:, ["name", "weight"]]
    df_ = df_.groupby("name").sum()
    df_ = df_.reset_index()

    d = df_.to_dict(orient="records")


    # append to d each country in df
    for country in df["country"].unique():
        d.append({"name": country, "size": "null"})

    # Return
    return d
