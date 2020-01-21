"""
The ``wind_turbine`` module contains the class WindTurbine that implements
a wind turbine in the windpowerlib and functions needed for the modelling of a
wind turbine.

SPDX-FileCopyrightText: 2019 oemof developer group <contact@oemof.org>
SPDX-License-Identifier: MIT
"""
import pandas as pd
import logging
import warnings
import requests
import os
from windpowerlib.tools import WindpowerlibUserWarning
from typing import NamedTuple


class WindTurbine(object):
    r"""
    Defines a standard set of wind turbine attributes.

    Parameters
    ----------
    hub_height : float
        Hub height of the wind turbine in m.
    power_curve : :pandas:`pandas.DataFrame<frame>` or dict (optional)
        If provided directly sets the power curve. DataFrame/dictionary must
        have 'wind_speed' and 'value' columns/keys with wind speeds in m/s and
        the corresponding power curve value in W. If not set the value is
        retrieved from 'power_curve.csv' file in `path`. In that case a
        `turbine_type` is needed. Default: None.
    power_coefficient_curve : :pandas:`pandas.DataFrame<frame>` or dict (optional)
        If provided directly sets the power coefficient curve.
        DataFrame/dictionary must have 'wind_speed' and 'value' columns/keys
        with wind speeds in m/s and the corresponding power coefficient curve
        value. If not set the value is retrieved from
        'power_coefficient_curve.csv' file in `path`. In that case a
        `turbine_type` is needed. Default: None.
    turbine_type : str (optional)
        Name of the wind turbine type. Must be provided if power (coefficient)
        curve, nominal power or rotor diameter is retrieved from self-provided
        or oedb turbine library csv files. If turbine_type is None it is not
        possible to retrieve turbine data from file.
        Use :py:func:`~.get_turbine_types` to see a table of all wind turbines
        for which power (coefficient) curve data and other turbine data is
        provided in the oedb turbine library.
        Default: None.
    rotor_diameter : float (optional)
        Diameter of the rotor in m. If not set the value is
        retrieved from 'turbine_data.csv' file in `path`. In that case a
        `turbine_type` is needed.
        The rotor diameter only needs to be set if power output
        is calculated using the power coefficient curve. Default: None.
    nominal_power : float (optional)
        The nominal power of the wind turbine in W. If not set the value is
        retrieved from 'turbine_data.csv' file in `path`. In that case a
        `turbine_type` is needed. Default: None.
    path : str (optional)
        Directory where the turbine database files are located. The files need
        to be named 'power_coefficient_curve.csv', 'power_curve.csv', and
        'turbine_data.csv'. By default the oedb turbine library files are used.
        Set path to `None` to ignore turbine data from files. Default: 'oedb'.

    Attributes
    ----------
    turbine_type : str
        Name of the wind turbine.
    hub_height : float
        Hub height of the wind turbine in m.
    rotor_diameter : None or float
        Diameter of the rotor in m. Default: None.
    power_coefficient_curve : None, pandas.DataFrame or dictionary
        Power coefficient curve of the wind turbine. DataFrame/dictionary
        containing 'wind_speed' and 'value' columns/keys with wind speeds
        in m/s and the corresponding power coefficients. Default: None.
    power_curve : None, pandas.DataFrame or dictionary
        Power curve of the wind turbine. DataFrame/dictionary containing
        'wind_speed' and 'value' columns/keys with wind speeds in m/s and the
        corresponding power curve value in W. Default: None.
    nominal_power : None or float
        The nominal output of the wind turbine in W. Default: None.
   
    Notes
    ------
    Your wind turbine object needs to have a power coefficient or power curve.
    By default they are fetched from the oedb turbine library that is provided
    along with the windpowerlib. In that case `turbine_type` must be specified.
    You can also set the curves directly or provide your own csv files with
    power coefficient and power curves. See `example_power_curves.csv',
    `example_power_coefficient_curves.csv` and `example_turbine_data.csv`
    in example/data for the required format of such csv files.

    Examples
    --------
    >>> import os
    >>> from windpowerlib import WindTurbine
    >>> enerconE126={
    ...    'hub_height': 135,
    ...    'turbine_type': 'E-126/4200'}
    >>> e126=WindTurbine(**enerconE126)
    >>> print(e126.nominal_power)
    4200000.0
    >>> # Example with own path
    >>> path=os.path.join(os.path.dirname(__file__), '../example/data')
    >>> example_turbine={
    ...    'hub_height': 100,
    ...    'rotor_diameter': 70,
    ...    'turbine_type': 'DUMMY 3',
    ...    'path' : path}
    >>> e_t_1=WindTurbine(**example_turbine)
    >>> print(e_t_1.power_curve['value'][7])
    18000.0
    >>> print(e_t_1.nominal_power)
    1500000.0
    """

    def __init__(
        self,
        hub_height,
        nominal_power=None,
        path="oedb",
        power_curve=None,
        power_coefficient_curve=None,
        rotor_diameter=None,
        turbine_type=None,
        **kwargs
    ):

        self.hub_height = hub_height
        self.turbine_type = turbine_type
        self.rotor_diameter = rotor_diameter
        self.nominal_power = nominal_power
        self.power_curve = power_curve
        self.power_coefficient_curve = power_coefficient_curve

        if path == "oedb":
            path = os.path.join(os.path.dirname(__file__), "oedb")

        if turbine_type is not None and path is not None:
            if power_curve is None:
                try:
                    fn = os.path.join(path, "power_curves.csv")
                    self.power_curve = get_turbine_data_from_file(
                        self.turbine_type, fn
                    )
                except KeyError:
                    msg = "No power curve found for {0}"
                    logging.debug(msg.format(self.turbine_type))
            if power_coefficient_curve is None:
                try:
                    fn = os.path.join(path, "power_coefficient_curves.csv")
                    self.power_coefficient_curve = get_turbine_data_from_file(
                        self.turbine_type, fn
                    )
                except KeyError:
                    msg = "No power coefficient curve found for {0}"
                    logging.debug(msg.format(self.turbine_type))

            if nominal_power is None or (
                rotor_diameter is None
                and self.power_coefficient_curve is not None
            ):
                turbine_data = None
                try:
                    fn = os.path.join(path, "turbine_data.csv")
                    turbine_data = get_turbine_data_from_file(
                        self.turbine_type, fn
                    )
                except KeyError:
                    msg = "No turbine data found for {0}"
                    logging.debug(msg.format(self.turbine_type))

                if self.nominal_power is None and turbine_data is not None:
                    self.nominal_power = float(turbine_data["nominal_power"])
                if self.rotor_diameter is None and turbine_data is not None:
                    self.rotor_diameter = float(turbine_data["rotor_diameter"])

        if self.rotor_diameter:
            if self.hub_height <= 0.5*self.rotor_diameter:
                msg = "1/2rotor_diameter cannot be greater than hub_height"
                raise ValueError(msg)

        if self.power_curve is None and self.power_coefficient_curve is None:
            msg = (
                "The WindTurbine has been initialised without a power curve"
                " and without a power coefficient curve.\nYou will not be"
                " able to calculate the power output.\n"
                " Check if the turbine type {0} is in your database file"
                " or if you passed a valid curve."
            )
            warnings.warn(msg.format(turbine_type), WindpowerlibUserWarning)
        else:
            # power (coefficient) curve to pd.DataFrame in case of being dict
            if isinstance(self.power_curve, dict):
                self.power_curve = pd.DataFrame(self.power_curve)
            if isinstance(self.power_coefficient_curve, dict):
                self.power_coefficient_curve = pd.DataFrame(
                    self.power_coefficient_curve
                )
            # sort power (coefficient) curve by wind speed
            if isinstance(self.power_curve, pd.DataFrame):
                self.power_curve.sort_values(by="wind_speed")
            elif self.power_curve is not None:
                msg = (
                    "Type of power curve of {} is {} but should be "
                    "pd.DataFrame or dict."
                )
                raise TypeError(
                    msg.format(self.__repr__(), type(self.power_curve))
                )
            if isinstance(self.power_coefficient_curve, pd.DataFrame):
                self.power_coefficient_curve.sort_values(by="wind_speed")
            elif self.power_coefficient_curve is not None:
                msg = (
                    "Type of power coefficient curve of {} is {} but "
                    "should be pd.DataFrame or dict."
                )
                raise TypeError(
                    msg.format(
                        self.__repr__(), type(self.power_coefficient_curve)
                    )
                )

    def __repr__(self):
        info = []
        if self.nominal_power is not None:
            info.append("nominal power={} W".format(self.nominal_power))
        if self.hub_height is not None:
            info.append("hub height={} m".format(self.hub_height))
        if self.rotor_diameter is not None:
            info.append("rotor diameter={} m".format(self.rotor_diameter))
        if self.power_coefficient_curve is not None:
            info.append("power_coefficient_curve={}".format("True"))
        else:
            info.append("power_coefficient_curve={}".format("False"))
        if self.power_curve is not None:
            info.append("power_curve={}".format("True"))
        else:
            info.append("power_curve={}".format("False"))

        if self.turbine_type is not None:
            turbine_repr = "Wind turbine: {name} {info}".format(
                name=self.turbine_type, info=info
            )
        else:
            turbine_repr = "Wind turbine: {info}".format(info=info)

        return turbine_repr

    def to_group(self, number_turbines=None, total_capacity=None):
        r"""
        Creates a :class:`~windpowerlib.wind_turbine.WindTurbineGroup`, a
        NamedTuple data container with the fields 'number_of_turbines' and
        'wind_turbine'. If no parameter is passed the number of turbines is
        set to one.

        It can be used to calculate the number of turbines for a given total
        capacity or to create a namedtuple that can be used to define a
        :class:`~windpowerlib.wind_farm.WindFarm` object.

        Parameters
        ----------
        number_turbines : float
            Number of turbines of the defined type. Default: 1
        total_capacity : float
            Total capacity of the group of wind turbines of the same type.

        Returns
        -------
        :class:`~windpowerlib.wind_turbine.WindTurbineGroup`
            A namedtuple with two fields: 'number_of_turbines' and
            'wind_turbine'.

        Examples
        --------
        >>> from windpowerlib import WindTurbine
        >>> enerconE126={
        ...    'hub_height': 135,
        ...    'turbine_type': 'E-126/4200'}
        >>> e126=WindTurbine(**enerconE126)
        >>> e126.to_group(5).number_of_turbines
        5
        >>> e126.to_group().number_of_turbines
        1
        >>> e126.to_group(number_turbines=7).number_of_turbines
        7
        >>> e126.to_group(total_capacity=12600000).number_of_turbines
        3.0
        >>> e126.to_group(total_capacity=14700000).number_of_turbines
        3.5
        >>> e126.to_group(total_capacity=12600000).wind_turbine.nominal_power
        4200000.0
        >>> type(e126.to_group(5))
        <class 'windpowerlib.wind_turbine.WindTurbineGroup'>
        >>> e126.to_group(5)  # doctest: +NORMALIZE_WHITESPACE
        WindTurbineGroup(wind_turbine=Wind turbine: E-126/4200 ['nominal
        power=4200000.0 W', 'hub height=135 m', 'rotor diameter=127.0 m',
        'power_coefficient_curve=True', 'power_curve=True'],
        number_of_turbines=5)
        """

        if number_turbines is not None and total_capacity is not None:
            raise ValueError(
                "The 'number' and the 'total_capacity' parameter "
                "are mutually exclusive. Use just one of them."
            )
        elif total_capacity is not None:
            number_turbines = total_capacity / self.nominal_power
        elif number_turbines is None:
            number_turbines = 1

        return WindTurbineGroup(
            wind_turbine=self, number_of_turbines=number_turbines
        )


# This is working for Python >= 3.5.
# There a cleaner solutions for Python >= 3.6, once the support of 3.5 is
# dropped: https://stackoverflow.com/a/50038614
class WindTurbineGroup(
    NamedTuple(
        "WindTurbineGroup",
        [("wind_turbine", WindTurbine), ("number_of_turbines", float)],
    )
):
    """
    A simple data container to define more than one turbine of the same type.
    Use the :func:`~windpowerlib.wind_turbine.WindTurbine.to_group` method to
    easily create a WindTurbineGroup from a
    :class:`~windpowerlib.wind_turbine.WindTurbine` object.

    Parameters
    ----------
    'wind_turbine' : WindTurbine
        A WindTurbine object with all necessary attributes.
    'number_of_turbines' : float
        The number of turbines. The number is not restricted to integer values.
    """

    __slots__ = ()


WindTurbineGroup.wind_turbine.__doc__ = (
    "A :class:`~windpowerlib.wind_farm.WindTurbine` object."
)
WindTurbineGroup.number_of_turbines.__doc__ = (
    "Number of turbines of type WindTurbine"
)


def get_turbine_data_from_file(turbine_type, path):
    r"""
    Fetches turbine data from a csv file.

    See `example_power_curves.csv', `example_power_coefficient_curves.csv` and
    `example_turbine_data.csv` in example/data for the required format of
    a csv file. Make sure to provide wind speeds in m/s and power in W or
    convert units after loading the data.

    Parameters
    ----------
    turbine_type : str
        Specifies the turbine type data is fetched for.
    path : str
        Specifies the source of the turbine data.
        See the example below for how to use the example data.

    Returns
    -------
    :pandas:`pandas.DataFrame<frame>` or float
        Power curve or power coefficient curve (pandas.DataFrame) or nominal
        power (float) of one wind turbine type. Power (coefficient) curve
        DataFrame contains power coefficient curve values (dimensionless) or
        power curve values (in dimension given in file) with the corresponding
        wind speeds (in dimension given in file).

    Examples
    --------
    >>> from windpowerlib import wind_turbine
    >>> import os
    >>> path=os.path.join(os.path.dirname(__file__), '../example/data',
    ...     'power_curves.csv')
    >>> d3=get_turbine_data_from_file('DUMMY 3', path)
    >>> print(d3['value'][7])
    18000.0
    >>> print(d3['value'].max())
    1500000.0
    """

    try:
        df = pd.read_csv(path, index_col=0)
    except FileNotFoundError:
        raise FileNotFoundError("The file '{}' was not found.".format(path))
    wpp_df = df[df.index == turbine_type].copy()
    # if turbine not in data file
    if wpp_df.shape[0] == 0:
        msg = "Wind converter type {0} not provided. Possible types: {1}"
        raise KeyError(msg.format(turbine_type, list(df.index)))
    # if turbine in data file
    # get nominal power or power (coefficient) curve
    if "turbine_data" in path:
        return wpp_df
    else:
        wpp_df.dropna(axis=1, inplace=True)
        wpp_df = wpp_df.transpose().reset_index()
        wpp_df.columns = ["wind_speed", "value"]
        # transform wind speeds to floats
        wpp_df["wind_speed"] = wpp_df["wind_speed"].apply(lambda x: float(x))
        return wpp_df


def load_turbine_data_from_oedb(schema="supply", table="wind_turbine_library"):
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
    # url of OpenEnergy Platform that contains the oedb
    oep_url = "http://oep.iks.cs.ovgu.de/"

    # load data
    result = requests.get(
        oep_url + "/api/v0/schema/{}/tables/{}/rows/?".format(schema, table),
    )
    if not result.status_code == 200:
        raise ConnectionError(
            "Database connection not successful. "
            "Response: [{}]".format(result.status_code)
        )
    # extract data to dataframe
    turbine_data = pd.DataFrame(result.json())
    # standard file name for saving data
    filename = os.path.join(os.path.dirname(__file__), "oedb", "{}.csv")
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
    turbine_data_df["nominal_power"] = turbine_data_df["nominal_power"] * 1000
    turbine_data_df.to_csv(filename.format("turbine_data"))
    return turbine_data


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
    format as shown in
    `the data base <https://openenergy-platform.org/dataedit/view/supply/wind_turbine_library>`_.

    Examples
    --------
    >>> from windpowerlib import wind_turbine
    >>> df=wind_turbine.get_turbine_types(print_out=False)
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
        df = load_turbine_data_from_oedb()
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
