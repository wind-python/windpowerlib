"""
The ``wind_turbine`` module contains the class WindTurbine that implements
a wind turbine in the windpowerlib and functions needed for the modelling of a
wind turbine.

"""

import pandas as pd
import logging
import sys
import os
import numpy as np

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"


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
    d_rotor : float
        Diameter of the rotor in m.
    cp_values : pandas.DataFrame
        Power coefficient curve of the wind turbine.
        The indices of the DataFrame are the corresponding wind speeds of the
        power coefficient curve, the power coefficient values are listed in
        the column 'cp'. Default: None.
    p_values : pandas.DataFrame
        Power curve of the wind turbine.
        The indices of the DataFrame are the corresponding wind speeds of the
        power curve, the power values are listed in the column 'P'.
        Default: None.
    nominal_power : float
        The nominal output of the wind turbine in kW.
    fetch_curve : string
        Parameter to specify whether the power or power coefficient curve
        should be retrieved from the provided turbine data

    Attributes
    ----------
    turbine_name : string
        Name of the wind turbine type.
        Use get_turbine_types() to see a list of all wind turbines for which
        power (coefficient) curve data is provided.
    hub_height : float
        Hub height of the wind turbine in m.
    d_rotor : float
        Diameter of the rotor in m.
    cp_values : pandas.DataFrame
        Power coefficient curve of the wind turbine.
        The indices of the DataFrame are the corresponding wind speeds of the
        power coefficient curve, the power coefficient values are listed in
        the column 'cp'. Default: None.
    p_values : pandas.DataFrame
        Power curve of the wind turbine.
        The indices of the DataFrame are the corresponding wind speeds of the
        power curve, the power values are listed in the column 'P'.
        Default: None.
    nominal_power : float
        The nominal output of the wind turbine.
    power_output : pandas.Series
        The calculated power output of the wind turbine.

    Examples
    --------
    >>> from windpowerlib import wind_turbine
    >>> enerconE126 = {
    ...    'hub_height': 135,
    ...    'd_rotor': 127,
    ...    'turbine_name': 'ENERCON E 126 7500'}
    >>> e126 = wind_turbine.WindTurbine(**enerconE126)
    >>> print(e126.d_rotor)
    127

    """

    def __init__(self, turbine_name, hub_height, d_rotor, cp_values=None,
                 p_values=None, nominal_power=None, fetch_curve='cp'):

        self.turbine_name = turbine_name
        self.hub_height = hub_height
        self.d_rotor = d_rotor
        self.cp_values = cp_values
        self.p_values = p_values
        self.nominal_power = nominal_power
        self.fetch_curve = fetch_curve

        self.power_output = None

        if (self.cp_values is None and self.p_values is None):
            p_nom = self.fetch_turbine_data()
            if self.nominal_power is None:
                self.nominal_power = p_nom

    def fetch_turbine_data(self):
        r"""
        Fetches data of the requested wind turbine.

        Method fetches nominal power as well as power coefficient curve or
        power curve from a data file provided along with the windpowerlib.

        Returns
        -------
        tuple of pandas.DataFrame and float
            Cp or P values and the nominal power
            of the requested wind converter.

        Examples
        --------
        >>> from windpowerlib import wind_turbine
        >>> enerconE126 = {
        ...    'hub_height': 135,
        ...    'd_rotor': 127,
        ...    'turbine_name': 'ENERCON E 126 7500'}
        >>> e126 = wind_turbine.WindTurbine(**enerconE126)
        >>> print(e126.cp_values.cp[5.0])
        0.423
        >>> print(e126.nominal_power)
        7500000.0

        """

        def restructure_data():
            df = read_turbine_data(filename=filename)
            wpp_df = df[df.turbine_id == self.turbine_name]
            if wpp_df.shape[0] == 0:
                pd.set_option('display.max_rows', len(df))
                logging.info('Possible types: \n{0}'.format(df.turbine_id))
                pd.reset_option('display.max_rows')
                sys.exit('Cannot find the wind converter type: {0}'.format(
                    self.turbine_name))

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
            df.set_index('v_wind', drop=True, inplace=True)
            nominal_power = wpp_df['p_nom'].iloc[0] * 1000
            return df, nominal_power
        if self.fetch_curve == 'P':
            filename = 'P_curves.csv'
            self.p_values, p_nom = restructure_data()
        else:
            filename = 'cp_curves.csv'
            self.cp_values, p_nom = restructure_data()
        return p_nom


def read_turbine_data(**kwargs):
    r"""
    Fetches power coefficient curve or power curve from a file.

    The data files are provided along with the windpowerlib and are located in
    the directory windpowerlib/data.

    Other Parameters
    ----------------
    datapath : string, optional
        Path where the data file is stored. Default: './data'
    filename : string, optional
        Name of data file. Default: 'cp_curves.csv'

    Returns
    -------
    pandas.DataFrame
        Power coefficient curve values or power curve values with the
        corresponding wind speeds as indices.

    """
    if 'datapath' not in kwargs:
        kwargs['datapath'] = os.path.join(os.path.dirname(__file__), 'data')

    if 'filename' not in kwargs:
        kwargs['filename'] = 'cp_curves.csv'

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
    >>> valid_types_df = wind_turbine.get_turbine_types(print_out=False)
    >>> print(valid_types_df.iloc[5])
    turbine_id    DEWIND D8 2000
    p_nom                   2000
    Name: 5, dtype: object

    """
    df = read_turbine_data(**kwargs)

    if print_out:
        pd.set_option('display.max_rows', len(df))
        print(df[['turbine_id', 'p_nom']])
        pd.reset_option('display.max_rows')
    return df[['turbine_id', 'p_nom']]
