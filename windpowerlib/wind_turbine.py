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
    cp_values : None or pandas.DataFrame
        Power coefficient curve of the wind turbine.
        The indices of the DataFrame are the corresponding wind speeds of the
        power coefficient curve, the power coefficient values are listed in
        the column 'cp'. Default: None.
    p_values : None or pandas.DataFrame
        Power curve of the wind turbine.
        The indices of the DataFrame are the corresponding wind speeds of the
        power curve, the power values are listed in the column 'p'.
        Default: None.
    nominal_power : None or float
        The nominal output of the wind turbine in W.
    fetch_curve : string
        Parameter to specify whether the power or power coefficient curve
        should be retrieved from the provided turbine data. Default: 'p'.

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
    cp_values : None or pandas.DataFrame
        Power coefficient curve of the wind turbine.
        The indices of the DataFrame are the corresponding wind speeds of the
        power coefficient curve, the power coefficient values are listed in
        the column 'cp'. Default: None.
    p_values : None or pandas.DataFrame
        Power curve of the wind turbine.
        Indices are the wind speeds of the power curve in m/s, the
        corresponding power values in W are in the column 'p'.
        Default: None.
    nominal_power : None or float
        The nominal output of the wind turbine in W.
    fetch_curve : string
        Parameter to specify whether the power or power coefficient curve
        should be retrieved from the provided turbine data. Default: 'p'.
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
    >>> print(e126.rotor_diameter)
    127

    """

    def __init__(self, turbine_name, hub_height, rotor_diameter=None,
                 cp_values=None, p_values=None, nominal_power=None,
                 fetch_curve='p'):

        self.turbine_name = turbine_name
        self.hub_height = hub_height
        self.rotor_diameter = rotor_diameter
        self.cp_values = cp_values
        self.p_values = p_values
        self.nominal_power = nominal_power
        self.fetch_curve = fetch_curve

        self.power_output = None

        if self.cp_values is None and self.p_values is None:
            self.fetch_turbine_data()

    def fetch_turbine_data(self):
        r"""
        Fetches data of the requested wind turbine.

        Method fetches nominal power as well as power coefficient curve or
        power curve from a data file provided along with the windpowerlib.
        You can also use this function to import your own power (coefficient)
        curves. Therefore the wind speeds in m/s have to be in the first row
        and the corresponding power coefficient curve values or power
        curve values in kW in a row where the first column contains the turbine
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
        ...    'fetch_curve': 'cp'}
        >>> e126 = wind_turbine.WindTurbine(**enerconE126)
        >>> print(e126.cp_values[5.0])
        0.423
        >>> print(e126.nominal_power)
        7500000000.0

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
                the corresponding wind speeds in m/s as indices.

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
            df = pd.DataFrame(data, columns=['v_wind', self.fetch_curve])
            series = pd.Series(df[self.fetch_curve], index=df['v_wind'])
            nominal_power = wpp_df['p_nom'].iloc[0] * 1000.0  # kW to W
            return series, nominal_power
        if self.fetch_curve == 'p':
            filename = 'p_curves.csv'
            p_values, p_nom = restructure_data()
            self.p_values = p_values * 1000.0  # kW to W
        else:
            filename = 'cp_curves.csv'
            self.cp_values, p_nom = restructure_data()
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
        Name of data file. Provided data files are 'p_curves.csv' containing
        power curves and 'cp_curves.csv' containing power coefficient curves.
        Default: 'p_curves.csv'

    Returns
    -------
    pandas.DataFrame
        Power coefficient curve values (dimensionless) or power curve values
        in kW with the corresponding wind speeds in m/s as indices.

    """
    if 'datapath' not in kwargs:
        kwargs['datapath'] = os.path.join(os.path.dirname(__file__), 'data')

    if 'filename' not in kwargs:
        kwargs['filename'] = 'p_curves.csv'

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
        Directly prints the list of types if set to True. Default: True

    Examples
    --------
    >>> from windpowerlib import wind_turbine
    >>> turbines = wind_turbine.get_turbine_types(print_out=False)
    >>> print(turbines[turbines["turbine_id"].str.contains("ENERCON")].iloc[0])
    turbine_id    ENERCON E 101 3000
    p_nom                       3000
    Name: 25, dtype: object

    """
    df = read_turbine_data(**kwargs)

    if print_out:
        pd.set_option('display.max_rows', len(df))
        print(df[['turbine_id', 'p_nom']])
        pd.reset_option('display.max_rows')
    return df[['turbine_id', 'p_nom']]
