"""
The ``data`` module contains functions to handle the needed data.

SPDX-FileCopyrightText: 2019 oemof developer group <contact@oemof.org>
SPDX-License-Identifier: MIT
"""

import logging
import os
import warnings
from datetime import datetime
from shutil import copyfile

import pandas as pd
import requests

from windpowerlib.wind_turbine import WindTurbine
from windpowerlib.tools import WindpowerlibUserWarning


def get_turbine_types(turbine_library="local", print_out=True, filter_=True):
    r"""
    Get all provided wind turbine types provided.

    Choose by `turbine_library` whether to get wind turbine types provided by
    the OpenEnergy Database ('oedb') or wind turbine types provided in your
    local file(s) ('local').
    By default only turbine types for which a power coefficient curve or power
    curve is provided are returned. Set `filter_=False` to see all turbine
    types for which any data (e.g. hub height, rotor diameter, ...) is
    provided.

    Parameters
    ----------
    turbine_library : str
        Specifies if the oedb turbine library ('oedb') or your local turbine
        data file ('local') is evaluated. Default: 'local'.
    print_out : bool
        Directly prints a tabular containing the turbine types in column
        'turbine_type', the manufacturer in column 'manufacturer' and
        information about whether a power (coefficient) curve exists (True) or
        not (False) in columns 'has_power_curve' and 'has_cp_curve'.
        Default: True.
    filter_ : bool
        If True only turbine types for which a power coefficient curve or
        power curve is provided in the oedb turbine library are
        returned. Default: True.

    Returns
    -------
    :pandas:`pandas.DataFrame<frame>`
        Contains turbine types in column 'turbine_type', the manufacturer in
        column 'manufacturer' and information about whether a power
        (coefficient) curve exists (True) or not (False) in columns
        'has_power_curve' and 'has_cp_curve'.

    Notes
    -----
    If the power (coefficient) curve of the desired turbine type (or the
    turbine type itself) is missing you can contact us via github or
    windpowerlib@rl-institut.de. You can help us by providing data in the
    format as shown in `the data base
    <https://openenergy-platform.org/dataedit/view/supply/wind_turbine_library>`_.

    Examples
    --------
    >>> from windpowerlib import get_turbine_types
    >>> df=get_turbine_types(print_out=False)
    >>> print(df[df["turbine_type"].str.contains("E-126")].iloc[0])
    manufacturer          Enercon
    turbine_type       E-126/4200
    has_power_curve          True
    has_cp_curve             True
    Name: 5, dtype: object
    >>> print(df[df["manufacturer"].str.contains("Enercon")].iloc[0])
    manufacturer          Enercon
    turbine_type       E-101/3050
    has_power_curve          True
    has_cp_curve             True
    Name: 1, dtype: object

    """
    if turbine_library == "local":
        filename = os.path.join(
            os.path.dirname(__file__), "oedb", "turbine_data.csv"
        )
        df = pd.read_csv(filename, index_col=0).reset_index()
    elif turbine_library == "oedb":
        df = fetch_turbine_data_from_oedb()

    else:
        raise ValueError(
            "`turbine_library` is '{}' ".format(turbine_library)
            + "but must be 'local' or 'oedb'."
        )
    if filter_:
        cp_curves_df = df.loc[df["has_cp_curve"]][
            ["manufacturer", "turbine_type", "has_cp_curve"]
        ]
        p_curves_df = df.loc[df["has_power_curve"]][
            ["manufacturer", "turbine_type", "has_power_curve"]
        ]
        curves_df = pd.merge(
            p_curves_df, cp_curves_df, how="outer", sort=True
        ).fillna(False)
    else:
        curves_df = df[
            ["manufacturer", "turbine_type", "has_power_curve", "has_cp_curve"]
        ]
    if print_out:
        pd.set_option("display.max_rows", len(curves_df))
        print(curves_df)
        pd.reset_option("display.max_rows")
    return curves_df


def fetch_turbine_data_from_oedb(
    schema="supply", table="wind_turbine_library"
):
    r"""
    Fetches turbine library from the OpenEnergy database (oedb).

    Parameters
    ----------
    schema : str
        Database schema of the turbine library.
    table : str
        Table name of the turbine library.

    Returns
    -------
    :pandas:`pandas.DataFrame<frame>`
        Turbine data of different turbines such as 'manufacturer',
        'turbine_type', 'nominal_power'.

    """
    # url of OpenEnergy Platform that contains the oedb
    oep_url = "http://oep.iks.cs.ovgu.de/"
    url = oep_url + "/api/v0/schema/{}/tables/{}/rows/?".format(schema, table)

    # load data
    result = requests.get(url)
    if not result.status_code == 200:
        raise ConnectionError(
            "Database (oep) connection not successful. \nURL: {2}\n"
            "Response: [{0}] \n{1}".format(
                result.status_code, result.text, url
            )
        )
    return pd.DataFrame(result.json())


def load_turbine_data_from_oedb(schema="supply", table="wind_turbine_library"):
    msg = (
        "\nUse >>store_turbine_data_from_oedb<< and not"
        " >>load_turbine_data_from_oedb<< in the future."
    )
    warnings.warn(msg, FutureWarning)
    return store_turbine_data_from_oedb(schema=schema, table=table)


def store_turbine_data_from_oedb(
    schema="supply", table="wind_turbine_library"
):
    r"""
    Loads turbine library from the OpenEnergy database (oedb).

    Turbine data is saved to csv files ('oedb_power_curves.csv',
    'oedb_power_coefficient_curves.csv' and 'oedb_nominal_power') for offline
    usage of the windpowerlib. If the files already exist they are overwritten.

    Parameters
    ----------
    schema : str
        Database schema of the turbine library.
    table : str
        Table name of the turbine library.

    Returns
    -------
    :pandas:`pandas.DataFrame<frame>`
        Turbine data of different turbines such as 'manufacturer',
        'turbine_type', 'nominal_power'.

    """
    turbine_data = fetch_turbine_data_from_oedb(schema=schema, table=table)
    # standard file name for saving data
    filename = os.path.join(os.path.dirname(__file__), "oedb", "{0}.csv")

    time_stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    # get all power (coefficient) curves and save to file
    # for curve_type in ['power_curve', 'power_coefficient_curve']:
    for curve_type in ["power_curve", "power_coefficient_curve"]:
        curves_df = pd.DataFrame(columns=["wind_speed"])
        for index in turbine_data.index:
            if (
                turbine_data["{}_wind_speeds".format(curve_type)][index]
                and turbine_data["{}_values".format(curve_type)][index]
            ):
                df = (
                    pd.DataFrame(
                        data=[
                            eval(
                                turbine_data[
                                    "{}_wind_speeds".format(curve_type)
                                ][index]
                            ),
                            eval(
                                turbine_data["{}_values".format(curve_type)][
                                    index
                                ]
                            ),
                        ]
                    )
                    .transpose()
                    .rename(
                        columns={
                            0: "wind_speed",
                            1: turbine_data["turbine_type"][index],
                        }
                    )
                )
                curves_df = pd.merge(
                    left=curves_df, right=df, how="outer", on="wind_speed"
                )
        curves_df = curves_df.set_index("wind_speed").sort_index().transpose()
        # power curve values in W
        if curve_type == "power_curve":
            curves_df *= 1000
        curves_df.index.name = "turbine_type"
        copyfile(
            filename.format("{}s".format(curve_type)),
            filename.format("{0}s_{1}".format(curve_type, time_stamp)),
        )
        curves_df.to_csv(filename.format("{}s".format(curve_type)))

    # get turbine data and save to file (excl. curves)
    turbine_data_df = turbine_data.drop(
        [
            "power_curve_wind_speeds",
            "power_curve_values",
            "power_coefficient_curve_wind_speeds",
            "power_coefficient_curve_values",
            "thrust_coefficient_curve_wind_speeds",
            "thrust_coefficient_curve_values",
        ],
        axis=1,
    ).set_index("turbine_type")
    # nominal power in W
    turbine_data_df["nominal_power"] *= 1000
    copyfile(
        filename.format("turbine_data"),
        filename.format("turbine_data_{0}".format(time_stamp)),
    )
    check_imported_data(turbine_data_df, filename, time_stamp)
    turbine_data_df.to_csv(filename.format("turbine_data"))
    remove_tmp_file(filename, time_stamp)
    return turbine_data


def remove_tmp_file(filename, time_stamp):
    os.remove(filename.format("turbine_data_{0}".format(time_stamp)))
    for curve_type in ["power_curve", "power_coefficient_curve"]:
        os.remove(filename.format("{0}s_{1}".format(curve_type, time_stamp)))


def check_imported_data(data, filename, time_stamp):
    try:
        data = check_data_integrity(data)
    except Exception as e:
        copyfile(
            filename.format("turbine_data"),
            filename.format("turbine_data_error{0}".format(time_stamp)),
        )
        copyfile(
            filename.format("turbine_data_{0}".format(time_stamp)),
            filename.format("turbine_data"),
        )
        for curve_type in ["power_curve", "power_coefficient_curve"]:
            copyfile(
                filename.format("{}s".format(curve_type)),
                filename.format(
                    "{0}s_error_{1}".format(curve_type, time_stamp)
                ),
            )
            copyfile(
                filename.format("{0}s_{1}".format(curve_type, time_stamp)),
                filename.format("{}s".format(curve_type)),
            )
        remove_tmp_file(filename, time_stamp)
        raise e
    return data


def check_data_integrity(data, min_pc_length=5):
    for data_set in data.iterrows():
        wt_type = data_set[0]
        enercon_e126 = {
            "turbine_type": "{0}".format(wt_type),
            "hub_height": 135,
        }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            wt = WindTurbine(**enercon_e126)
            if wt.power_curve is None and data_set[1].has_power_curve is True:
                logging.warning(
                    "{0}: No power curve but has_power_curve=True.".format(
                        wt_type
                    )
                )
            if (
                wt.power_coefficient_curve is None
                and data_set[1].has_cp_curve is True
            ):
                logging.warning(
                    "{0}: No cp-curve but has_cp_curve=True.".format(wt_type)
                )
            if wt.power_curve is not None:
                if len(wt.power_curve) < min_pc_length:
                    logging.warning(
                        "{0}: power_curve is too short ({1} values),".format(
                            wt_type, len(wt.power_curve)
                        )
                    )
    return data


def check_weather_data(weather_data):
    """
    Check weather Data Frame.

    - Raise warning if there are nan values.
    - Convert columns if heights are string and not numeric.

    Parameters
    ----------
    weather_data : pandas.DataFrame
        A weather table with MultiIndex columns (name, data height)

    Returns
    -------
    pandas.DataFrame : A valid weather table.

    """
    # Convert data heights to integer. In some case they are strings.
    weather_data.columns = pd.MultiIndex.from_arrays(
        [
            weather_data.columns.get_level_values(0),
            pd.to_numeric(weather_data.columns.get_level_values(1)),
        ]
    )

    # check for nan values
    if weather_data.isnull().any().any():
        nan_columns = list(weather_data.columns[weather_data.isnull().any()])
        msg = (
            "The following columns of the weather data contain invalid "
            "values like 'nan': {0}"
        )
        warnings.warn(msg.format(nan_columns), WindpowerlibUserWarning)
    return weather_data
