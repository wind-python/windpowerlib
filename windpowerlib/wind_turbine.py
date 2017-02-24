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
    r"""Model to determine the output of a wind turbine

    Parameters
    ----------
    turbine_name : string
        Name of the wind turbine type. Use get_wind_pp_types() to see a list
        of all possible wind turbines.
    hub_height : float
        Height of the hub of the wind turbine.
    d_rotor : float
        Diameter of the rotor.
    cp_values : pandas.DataFrame
        Curve of the power coefficient of the wind turbine.
        The indices are the corresponding wind speeds of the power coefficient
        curve, the power coefficient values containing column is called 'cp'.
    p_values : pandas.DataFrame
        Power curve of the wind turbine.
        The indices are the corresponding wind speeds of the power curve, the
        power values containing column is called 'P'.
    nominal_power : float
        The nominal output of the wind power plant.

    Attributes
    ----------
    turbine_name : string
        Name of the wind turbine type. Use get_wind_pp_types() to see a list
        of all possible wind turbines.
    hub_height : float
        Height of the hub of the wind turbine.
    d_rotor : float
        Diameter of the rotor.
    cp_values : pandas.DataFrame
        Curve of the power coefficient of the wind turbine.
        The indices are the corresponding wind speeds of the power coefficient
        curve, the power coefficient values containing column is called 'cp'.
    p_values : pandas.DataFrame
        Power curve of the wind turbine.
        The indices are the corresponding wind speeds of the power curve, the
        power values containing column is called 'P'.
    nominal_power : float
        The nominal output of the wind power plant.

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
                 p_values=None, nominal_power=None):

        self.turbine_name = turbine_name
        self.hub_height = hub_height
        self.d_rotor = d_rotor
        self.cp_values = cp_values
        self.p_values = p_values
        self.nominal_power = nominal_power

        self.power_output = None

        if (self.cp_values is None or self.p_values is None or
                self.nominal_power is None):
            if self.cp_values is None or self.nominal_power is None:
                try:
                    wpp_data = self.fetch_wpp_data()
                    if self.cp_values is None:
                        self.cp_values = wpp_data[0]
                    if self.nominal_power is None:
                        self.nominal_power = wpp_data[1]
                except:
                    logging.info('Missing cp values.If needed for ' +
                                 'calulations: Check if csv file is ' +
                                 'available and named cp_values.csv')
            if self.p_values is None or self.nominal_power is None:
                try:
                    wpp_data = self.fetch_wpp_data(data_name='P',
                                                   filename='P_values.csv')
                    if self.p_values is None:
                        self.p_values = wpp_data[0]
                    if self.nominal_power is None:
                        self.nominal_power = wpp_data[1]
                except:
                    logging.info('Missing p values. If needed for ' +
                                 ' calulations: Check if csv file is ' +
                                 'available and named P_values.csv')

    def fetch_wpp_data(self, **kwargs):
        r"""
        Fetches data of the requested wind converter.

        Other parameters
        ----------------
        data_name : string
            Name of the data for display in DataFrame ('cp' or 'P').

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
        if 'data_name' not in kwargs:
            kwargs['data_name'] = 'cp'

        df = read_wpp_data(**kwargs)
        wpp_df = df[df.rli_anlagen_id == self.turbine_name]
        if wpp_df.shape[0] == 0:
            pd.set_option('display.max_rows', len(df))
            logging.info('Possible types: \n{0}'.format(df.rli_anlagen_id))
            pd.reset_option('display.max_rows')
            sys.exit('Cannot find the wind converter typ: {0}'.format(
                self.turbine_name))
        ncols = ['rli_anlagen_id', 'p_nenn', 'source', 'modificationtimestamp']
        data = np.array([0, 0])
        for col in wpp_df.keys():
            if col not in ncols:
                if wpp_df[col].iloc[0] is not None and not np.isnan(
                        float(wpp_df[col].iloc[0])):
                    data = np.vstack((data, np.array(
                        [float(col), float(wpp_df[col])])))
        data = np.delete(data, 0, 0)
        df = pd.DataFrame(data, columns=['v_wind', kwargs['data_name']])
        df.set_index('v_wind', drop=True, inplace=True)
        nominal_power = wpp_df['p_nenn'].iloc[0] * 1000
        return df, nominal_power


def read_wpp_data(**kwargs):
    r"""
    Fetches cp or P values from a file or downloads it from a server.

    The files are located in the data folder of the package root.

    Other Parameters
    ----------------
    datapath : string, optional
        Path where the cp or P file is stored. Default: '$PACKAGE_ROOT/data'
    filename : string, optional
        Filename of the cp or P file.

    Returns
    -------
    pandas.DataFrame
        Cp or P values with the corresponding wind speeds as indices.

    """
    if 'datapath' not in kwargs:
        kwargs['datapath'] = os.path.join(os.path.dirname(__file__), 'data')

    if 'filename' not in kwargs:
        kwargs['filename'] = 'cp_values.csv'

    file = os.path.join(kwargs['datapath'], kwargs['filename'])

    df = pd.read_csv(file, index_col=0)
    return df


def get_wind_pp_types(print_out=True):
    r"""
    Get the names of all possible wind converter types.

    Parameters
    ----------
    print_out : boolean (default: True)
        Directly prints the list of types if set to True.

    Examples
    --------
    >>> from windpowerlib import modelchain
    >>> valid_types_df = modelchain.get_wind_pp_types(print_out=False)
    >>> valid_types_df.shape
    (91, 2)
    >>> print(valid_types_df.iloc[5])
    rli_anlagen_id    DEWIND D8 2000
    p_nenn                      2000
    Name: 5, dtype: object

    """
    df = read_wpp_data()

    if print_out:
        pd.set_option('display.max_rows', len(df))
        print(df[['rli_anlagen_id', 'p_nenn']])
        pd.reset_option('display.max_rows')
    return df[['rli_anlagen_id', 'p_nenn']]
