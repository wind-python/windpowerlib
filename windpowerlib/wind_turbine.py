"""
The ``wind_turbine`` module contains the class WindTurbine that implements
a wind turbine in the windpowerlib and functions needed for the modelling of a
wind turbine.

"""

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"

import pandas as pd
import logging
import sys
import os
import numpy as np


class WindTurbine(object):
    r"""
    Defines a standard set of wind turbine attributes.

    Parameters
    ----------
    turbine_name : string
        Name of the wind turbine type.
        Use get_turbine_types() to see a list of all wind turbines for which
        power (coefficient) curve data is provided.
    hub_height : float
        Hub height of the wind turbine in m.
    rotor_diameter : None or float
        Diameter of the rotor in m.
    power_coefficient_curve : None, pandas.DataFrame or dictionary
        Power coefficient curve of the wind turbine. DataFrame/dictionary must
        have 'wind_speed' and 'values' columns/keys with wind speeds in m/s
        and the corresponding power coefficients. Default: None.
    power_curve : None, pandas.DataFrame or dictionary
        Power curve of the wind turbine. DataFrame/dictionary must have
        'wind_speed' and 'values' columns/keys with wind speeds in m/s and the
        corresponding power curve value in W. Default: None.
    nominal_power : None or float
        The nominal output of the wind turbine in W.
    fetch_curve : string
        Parameter to specify whether the power or power coefficient curve
        should be retrieved from the provided turbine data. Valid options are
        'power_curve' and 'power_coefficient_curve'. Default: 'power_curve'.

    Attributes
    ----------
    turbine_name : string
        Name of the wind turbine type.
        Use get_turbine_types() to see a list of all wind turbines for which
        power (coefficient) curve data is provided.
    hub_height : float
        Hub height of the wind turbine in m.
    rotor_diameter : None or float
        Diameter of the rotor in m.
    power_coefficient_curve : None, pandas.DataFrame or dictionary
        Power coefficient curve of the wind turbine. DataFrame/dictionary must
        have 'wind_speed' and 'values' columns/keys with wind speeds in m/s
        and the corresponding power coefficients. Default: None.
    power_curve : None, pandas.DataFrame or dictionary
        Power curve of the wind turbine. DataFrame/dictionary must have
        'wind_speed' and 'values' columns/keys with wind speeds in m/s and the
        corresponding power curve value in W. Default: None.
    nominal_power : None or float
        The nominal output of the wind turbine in W.
    fetch_curve : string
        Parameter to specify whether the power or power coefficient curve
        should be retrieved from the provided turbine data. Valid options are
        'power_curve' and 'power_coefficient_curve'. Default: 'power_curve'.
    power_output : pandas.Series
        The calculated power output of the wind turbine.

    Examples
    --------
    >>> from windpowerlib import wind_turbine
    >>> enerconE126 = {
    ...    'hub_height': 135,
    ...    'rotor_diameter': 127,
    ...    'turbine_name': 'ENERCON E 126 7500'}
    >>> e126 = wind_turbine.WindTurbine(**enerconE126)
    >>> print(e126.nominal_power)
    7500000

    """

    def __init__(self, turbine_name, hub_height, rotor_diameter=None,
                 power_coefficient_curve=None, power_curve=None,
                 nominal_power=None, fetch_curve='power_curve'):

        self.turbine_name = turbine_name
        self.hub_height = hub_height
        self.rotor_diameter = rotor_diameter
        self.power_coefficient_curve = power_coefficient_curve
        self.power_curve = power_curve
        self.nominal_power = nominal_power
        self.fetch_curve = fetch_curve

        self.power_output = None

        if self.power_coefficient_curve is None and self.power_curve is None:
            self.fetch_turbine_data()

    def fetch_turbine_data(self):
        r"""
        Fetches data of the requested wind turbine.

        Method fetches nominal power as well as power coefficient curve or
        power curve from a data file provided along with the windpowerlib.
        You can also use this function to import your own power (coefficient)
        curves. Therefore the wind speeds in m/s have to be in the first row
        and the corresponding power coefficient curve values or power
        curve values in W in a row where the first column contains the turbine
        name (See directory windpowerlib/data as reference).

        Returns
        -------
        self

        Examples
        --------
        >>> from windpowerlib import wind_turbine
        >>> enerconE126 = {
        ...    'hub_height': 135,
        ...    'rotor_diameter': 127,
        ...    'turbine_name': 'ENERCON E 126 7500',
        ...    'fetch_curve': 'power_coefficient_curve'}
        >>> e126 = wind_turbine.WindTurbine(**enerconE126)
        >>> print(e126.power_coefficient_curve['values'][5])
        0.423
        >>> print(e126.nominal_power)
        7500000

        """

        def restructure_data():
            r"""
            Restructures data read from a csv file.

            Method creates a two-dimensional DataFrame containing the power
            coefficient curve or power curve of the requested wind turbine.

            Returns
            -------
            Tuple (pandas.DataFrame, float)
                Power curve or power coefficient curve (pandas.DataFrame)
                and nominal power (float).
                Power (coefficient) curve DataFrame contains power coefficient
                curve values (dimensionless) or power curve values in W with
                the corresponding wind speeds in m/s.

            """
            df = read_turbine_data(filename=filename)
            wpp_df = df[df.turbine_id == self.turbine_name]
            # if turbine not in data file
            if wpp_df.shape[0] == 0:
                pd.set_option('display.max_rows', len(df))
                logging.info('Possible types: \n{0}'.format(df.turbine_id))
                pd.reset_option('display.max_rows')
                sys.exit('Cannot find the wind converter type: {0}'.format(
                    self.turbine_name))
            # if turbine in data file write power (coefficient) curve values
            # to 'data' array
            ncols = ['turbine_id', 'p_nom', 'source', 'modificationtimestamp']
            data = np.array([0, 0])
            for col in wpp_df.keys():
                if col not in ncols:
                    if wpp_df[col].iloc[0] is not None and not np.isnan(
                            float(wpp_df[col].iloc[0])):
                        data = np.vstack((data, np.array(
                            [float(col), float(wpp_df[col])])))
            data = np.delete(data, 0, 0)
            df = pd.DataFrame(data, columns=['wind_speed', 'values'])
            nominal_power = wpp_df['p_nom'].iloc[0]
            return df, nominal_power
        if self.fetch_curve == 'power_curve':
            filename = 'power_curves.csv'
            self.power_curve, p_nom = restructure_data()
        elif self.fetch_curve == 'power_coefficient_curve':
            filename = 'power_coefficient_curves.csv'
            self.power_coefficient_curve, p_nom = restructure_data()
        else:
            raise ValueError("'{0}' is an invalid value. ".format(
                             self.fetch_curve) + "`fetch_curve` must be " +
                             "'power_curve' or 'power_coefficient_curve'.")
        if self.nominal_power is None:
            self.nominal_power = p_nom
        return self


def read_turbine_data(**kwargs):
    r"""
    Fetches power (coefficient) curves from a file.

    The data files are provided along with the windpowerlib and are located in
    the directory windpowerlib/data.

    Other Parameters
    ----------------
    datapath : string, optional
        Path where the data file is stored. Default: './data'
    filename : string, optional
        Name of data file. Provided data files are 'power_curves.csv' and
        'power_coefficient_curves.csv'. Default: 'power_curves.csv'.

    Returns
    -------
    pandas.DataFrame
        Power coefficient curve values (dimensionless) or power curve values
        in kW with corresponding wind speeds in m/s of all available wind
        turbines with turbine name in column 'turbine_id', turbine nominal
        power in column 'p_nom'.

    """
    if 'datapath' not in kwargs:
        kwargs['datapath'] = os.path.join(os.path.dirname(__file__), 'data')

    if 'filename' not in kwargs:
        kwargs['filename'] = 'power_curves.csv'

    df = pd.read_csv(os.path.join(kwargs['datapath'], kwargs['filename']),
                     index_col=0)
    return df


def get_turbine_types(print_out=True, **kwargs):
    r"""
    Get the names of all possible wind turbine types for which the power
    coefficient curve or power curve is provided in the data files in
    the directory windpowerlib/data.

    Parameters
    ----------
    print_out : boolean
        Directly prints the list of types if set to True. Default: True.

    Examples
    --------
    >>> from windpowerlib import wind_turbine
    >>> turbines = wind_turbine.get_turbine_types(print_out=False)
    >>> print(turbines[turbines["turbine_id"].str.contains("ENERCON")].iloc[0])
    turbine_id    ENERCON E 101 3000
    p_nom                    3000000
    Name: 25, dtype: object

    """
    df = read_turbine_data(**kwargs)

    if print_out:
        pd.set_option('display.max_rows', len(df))
        print(df[['turbine_id', 'p_nom']])
        pd.reset_option('display.max_rows')
    return df[['turbine_id', 'p_nom']]
