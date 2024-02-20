"""
The ``data`` module contains functions to handle the needed data.

SPDX-FileCopyrightText: 2019 oemof developer group <contact@oemof.org>
SPDX-License-Identifier: MIT
"""

import logging
import os
import warnings
from shutil import copyfile

import pandas as pd
import requests
from windpowerlib.tools import WindpowerlibUserWarning
from windpowerlib.wind_turbine import WindTurbine


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
        cp_curves_df = df.loc[df["has_cp_curve"].fillna(False)][
            ["manufacturer", "turbine_type", "has_cp_curve"]
        ]
        p_curves_df = df.loc[df["has_power_curve"].fillna(False)][
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
    oep_url = "https://oep.iks.cs.ovgu.de/"
    url = oep_url + "/api/v0/schema/{}/tables/{}/rows/?".format(schema, table)

    # load data
    result = requests.get(url, verify=True)
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
    schema="supply", table="wind_turbine_library", threshold=0.2
):
    r"""
    Loads turbine library from the OpenEnergy database (oedb).

    Turbine data is saved to csv files ('oedb_power_curves.csv',
    'oedb_power_coefficient_curves.csv' and 'oedb_nominal_power') for offline
    usage of the windpowerlib. If the files already exist they are overwritten.
    In case the turbine library on the oedb contains too many faulty turbines,
    the already existing files are not overwritten. The accepted percentage of faulty
    turbines can be set through the parameter `threshold`.

    Parameters
    ----------
    schema : str
        Database schema of the turbine library.
    table : str
        Table name of the turbine library.
    threshold : float
        In case there are turbines in the turbine library with faulty data (e.g.
        duplicate wind speed entries in the power (coefficient) curve data), the
        threshold defines the share of accepted faulty turbine ata up to which the
        existing turbine data is overwritten by the newly downloaded data.
        For example, a threshold of 0.1 means that more than 10% of the
        turbines would need to have invalid data in order to discard the downloaded
        data. This is to make sure that in the rare case the oedb data is too buggy,
        the turbine data that is by default provided with the windpowerlib is not
        overwritten by poor data.

    Returns
    -------
    :pandas:`pandas.DataFrame<frame>`
        Turbine data of different turbines such as 'manufacturer',
        'turbine_type', 'nominal_power'.

    """
    turbine_data = fetch_turbine_data_from_oedb(schema=schema, table=table)
    turbine_data = _process_and_save_oedb_data(
        turbine_data, threshold=threshold
    )
    check_turbine_data(
        filename = os.path.join(os.path.dirname(__file__), "oedb", "{0}.csv")
    )
    return turbine_data


def _process_and_save_oedb_data(turbine_data, threshold=0.2):
    """
    Helper function to extract power (coefficient) curve data from the turbine library.

    Parameters
    -----------
    turbine_data : :pandas:`pandas.DataFrame<frame>`
        Raw turbine data downloaded from the oedb with
        :func:`fetch_turbine_data_from_oedb`.
    threshold : float
        See parameter `threshold` in func:`store_turbine_data_from_oedb`
        for more information.

    Returns
    --------
    :pandas:`pandas.DataFrame<frame>`
        Turbine data of different turbines such as 'manufacturer',
        'turbine_type', 'nominal_power'.

    """
    curve_types = ["power_curve", "power_coefficient_curve"]
    # get all power (coefficient) curves
    curve_dict = {}
    broken_turbines_dict = {}
    for curve_type in curve_types:
        broken_turbine_data = []
        curves_df = pd.DataFrame(columns=["wind_speed"])
        for index in turbine_data.index:
            if (
                turbine_data["{}_wind_speeds".format(curve_type)][index]
                and turbine_data["{}_values".format(curve_type)][index]
            ):
                try:
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
                    if not df.wind_speed.duplicated().any():
                        curves_df = pd.merge(
                            left=curves_df, right=df, how="outer", on="wind_speed"
                        )
                    else:
                        broken_turbine_data.append(
                            turbine_data.loc[index, "turbine_type"])
                except:
                    broken_turbine_data.append(turbine_data.loc[index, "turbine_type"])
        curve_dict[curve_type] = curves_df
        broken_turbines_dict[curve_type] = broken_turbine_data

    # check if there are faulty turbines and if so, raise warning
    # if there are too many, don't save downloaded data to disk but keep existing data
    if any(len(_) > 0 for _ in broken_turbines_dict.values()):
        issue_link = ("https://github.com/OpenEnergyPlatform/data-preprocessing"
                      "/issues/28")
        # in case only some data is faulty, only give out warning
        if all(len(_) < threshold * len(turbine_data)
               for _ in broken_turbines_dict.values()):
            save_turbine_data = True
            for curve_type in curve_types:
                if len(broken_turbines_dict[curve_type]) > 0:
                    logging.warning(
                        f"The turbine library data contains faulty {curve_type}s. The "
                        f"{curve_type} data can therefore not be loaded for the  "
                        f"following turbines: {broken_turbine_data}. "
                        f"Please report this in the following issue, in case it hasn't "
                        f"already been reported: {issue_link}"
                    )
                # set has_power_(coefficient)_curve to False for faulty turbines
                for turb in broken_turbines_dict[curve_type]:
                    ind = turbine_data[turbine_data.turbine_type == turb].index[0]
                    col = ("has_power_curve" if curve_type == "power_curve"
                           else "has_cp_curve")
                    turbine_data.at[ind, col] = False
        # in case most data is faulty, do not store downloaded data
        else:
            logging.warning(
                f"The turbine library data contains too many faulty turbine datasets "
                f"wherefore it is not loaded from the oedb. "
                f"In case you want to circumvent this behaviour, you can specify a "
                f"higher tolerance through the parameter 'threshold'."
                f"Please report this in the following issue, in case it hasn't "
                f"already been reported: {issue_link}"
            )
            save_turbine_data = False
    else:
        save_turbine_data = True

    if save_turbine_data:
        # standard file name for saving data
        filename = os.path.join(os.path.dirname(__file__), "oedb", "{0}.csv")
        # save curve data to csv
        for curve_type in curve_types:
            curves_df = curve_dict[curve_type].set_index(
                "wind_speed").sort_index().transpose()
            # power curve values in W
            if curve_type == "power_curve":
                curves_df *= 1000
            curves_df.index.name = "turbine_type"
            curves_df.sort_index(inplace=True)
            curves_df.to_csv(filename.format("{}s".format(curve_type)))

        # save turbine data to file (excl. curves)
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
        turbine_data_df.sort_index(inplace=True)
        turbine_data_df.to_csv(filename.format("turbine_data"))
    return turbine_data


def check_turbine_data(filename):
    try:
        data = check_data_integrity(filename)
    except Exception as e:
        restore_default_turbine_data()
        raise e
    return data


def check_data_integrity(filename, min_pc_length=5):
    data = pd.read_csv(filename.format("turbine_data"), index_col=[0])
    for data_set in data.iterrows():
        wt_type = data_set[0]
        turbine_data_set = {
            "turbine_type": "{0}".format(wt_type),
            "hub_height": 135,
        }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            wt = WindTurbine(**turbine_data_set)
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


def restore_default_turbine_data():
    """

    Returns
    -------

    Examples
    --------
    >>> restore_default_turbine_data()

    """
    src_path = os.path.join(
        os.path.dirname(__file__), "data", "default_turbine_data"
    )
    dst_path = os.path.join(os.path.dirname(__file__), "oedb")

    for file in os.listdir(src_path):
        src = os.path.join(src_path, file)
        dst = os.path.join(dst_path, file)
        copyfile(src, dst)


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
