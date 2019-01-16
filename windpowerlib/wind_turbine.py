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

try:
    import requests as rq
except ImportError:
    rq = None


class WindTurbine(object):
    r"""
    Defines a standard set of wind turbine attributes.

    Parameters
    ----------
    name : string
        Name of the wind turbine type.
        Use :py:func:`~.get_turbine_types` to see a table of all wind turbines
        for which power (coefficient) curve data is provided.
    hub_height : float
        Hub height of the wind turbine in m.
    rotor_diameter : None or float
        Diameter of the rotor in m.
    power_coefficient_curve : None, pandas.DataFrame or dictionary
        Power coefficient curve of the wind turbine. DataFrame/dictionary must
        have 'wind_speed' and 'power_coefficient' columns/keys with wind speeds
        in m/s and the corresponding power coefficients. Default: None.
    power_curve : None, pandas.DataFrame or dictionary
        Power curve of the wind turbine. DataFrame/dictionary must have
        'wind_speed' and 'power' columns/keys with wind speeds in m/s and the
        corresponding power curve value in W. Default: None.
    nominal_power : None or float
        The nominal output of the wind turbine in W.
    fetch_curve : string
        Parameter to specify whether a power or power coefficient curve
        should be retrieved from the provided turbine data. Valid options are
        'power_curve' and 'power_coefficient_curve'. Default: None.
    coordinates : list or None
        List of coordinates [lat, lon] of location for loading data.
        Default: None.
    data_source : string
        Specifies whether turbine data (f.e. nominal power, power curve, power
        coefficient curve) is loaded from the Open Energy Database ('oedb') or
        from a csv file ('<name of csv file>'). See `example_power_curves.csv'
        and `example_power_coefficient_curves.csv` in windpowerlib/data for
        the required form of a csv file. Default: 'oedb'.

    Attributes
    ----------
    name : string
        Name of the wind turbine type.
        Use :py:func:`~.get_turbine_types` to see a table of all wind turbines
        for which power (coefficient) curve data is provided.
    hub_height : float
        Hub height of the wind turbine in m.
    rotor_diameter : None or float
        Diameter of the rotor in m.
    power_coefficient_curve : None, pandas.DataFrame or dictionary
        Power coefficient curve of the wind turbine. DataFrame/dictionary must
        have 'wind_speed' and 'power coefficient' columns/keys with wind speeds
        in m/s and the corresponding power coefficients. Default: None.
    power_curve : None, pandas.DataFrame or dictionary
        Power curve of the wind turbine. DataFrame/dictionary must have
        'wind_speed' and 'power' columns/keys with wind speeds in m/s and the
        corresponding power curve value in W. Default: None.
    nominal_power : None or float
        The nominal output of the wind turbine in W.
    coordinates : list or None
        List of coordinates [lat, lon] of location for loading data.
        Default: None.
    power_output : pandas.Series
        The calculated power output of the wind turbine.

    Notes
    ------
    Your wind turbine object should have a power coefficient or power curve.
    You can set the `fetch_curve` parameter and the `data_source` parameter if
    you don't want to provide one yourself but want to automatically fetch a
    curve from a data set provided in the Open Energy Database (oedb).

    Examples
    --------
    >>> from windpowerlib import wind_turbine
    >>> enerconE126 = {
    ...    'hub_height': 135,
    ...    'rotor_diameter': 127,
    ...    'name': 'E-126/4200',
    ...    'fetch_curve': 'power_curve',
    ...    'data_source': 'oedb'}
    >>> e126 = wind_turbine.WindTurbine(**enerconE126)
    >>> print(e126.nominal_power)
    4200000.0

    """

    def __init__(self, name, hub_height, rotor_diameter=None,
                 power_coefficient_curve=None, power_curve=None,
                 nominal_power=None, fetch_curve=None, coordinates=None,
                 data_source='oedb'):

        self.name = name
        self.hub_height = hub_height
        self.rotor_diameter = rotor_diameter
        self.power_coefficient_curve = power_coefficient_curve
        self.power_curve = power_curve
        self.nominal_power = nominal_power
        self.coordinates = coordinates

        self.power_output = None

        if self.power_coefficient_curve is None and self.power_curve is None:
            self.fetch_turbine_data(fetch_curve, data_source)

    def fetch_turbine_data(self, fetch_curve, data_source):
        r"""
        Fetches data of the requested wind turbine.

        Method fetches nominal power as well as power coefficient curve or
        power curve from a data set provided in the Open Energy Database
        (oedb). You can also use this function to import your own power
        (coefficient) curves. For that the wind speeds in m/s have to be in the
        first row and the corresponding power coefficient curve values or power
        curve values in W in a row where the first column contains the turbine
        name (see directory windpowerlib/data as reference).

        Parameters
        ----------
        fetch_curve : string
            Parameter to specify whether a power or power coefficient curve
            should be retrieved from the provided turbine data. Valid options
            are 'power_curve' and 'power_coefficient_curve'. Default: None.
        data_source : string
            Specifies whether turbine data (f.e. nominal power, power curve,
            power coefficient curve) is loaded from the Open Energy Database
            ('oedb') or from a csv file ('<name of csv file>'). See
            `example_power_curves.csv` and
            `example_power_coefficient_curves.csv` in windpowerlib/data for the
            required form of a csv file. Default: 'oedb'.

        Returns
        -------
        self

        Examples
        --------
        >>> from windpowerlib import wind_turbine
        >>> enerconE126 = {
        ...    'hub_height': 135,
        ...    'rotor_diameter': 127,
        ...    'name': 'E-126/4200',
        ...    'fetch_curve': 'power_coefficient_curve',
        ...    'data_source': 'oedb'}
        >>> e126 = wind_turbine.WindTurbine(**enerconE126)
        >>> print(e126.power_coefficient_curve['power coefficient'][5])
        0.44
        >>> print(e126.nominal_power)
        4200000.0

        >>> example_turbine = {
        ...    'hub_height': 100,
        ...    'rotor_diameter': 70,
        ...    'name': 'DUMMY 3',
        ...    'fetch_curve': 'power_curve',
        ...    'data_source': 'example_power_curves.csv'}
        >>> e_t_1 = wind_turbine.WindTurbine(**example_turbine)
        >>> print(e_t_1.power_curve['power'][7])
        18000.0
        >>> print(e_t_1.nominal_power)
        150000

        """

        def restructure_data():
            r"""
            Restructures data fetched from oedb or read from a csv file.

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

            if data_source == 'oedb':
                df = load_turbine_data_from_oedb()
                df.set_index('turbine_type', inplace=True)
                # Set `curve` depending on `fetch_curve` to match names in oedb
                curve = ('cp_curve' if fetch_curve == 'power_coefficient_curve'
                         else fetch_curve)
                data = df.loc[self.name][curve]
                nominal_power = df.loc[self.name][
                                    'installed_capacity_kw'] * 1000
            else:
                df = read_turbine_data(filename=data_source)
                wpp_df = df[df.turbine_id == self.name]
                # if turbine not in data file
                if wpp_df.shape[0] == 0:
                    pd.set_option('display.max_rows', len(df))
                    logging.info('Possible types: \n{0}'.format(df.turbine_id))
                    pd.reset_option('display.max_rows')
                    sys.exit('Cannot find the wind converter type: {0}'.format(
                        self.name))
                # if turbine in data file write power (coefficient) curve
                # values to 'data' array
                ncols = ['turbine_id', 'p_nom', 'source',
                         'modificationtimestamp']
                data = np.array([0, 0])
                for col in wpp_df.keys():
                    if col not in ncols:
                        if wpp_df[col].iloc[0] is not None and not np.isnan(
                                float(wpp_df[col].iloc[0])):
                            data = np.vstack((data, np.array(
                                [float(col), float(wpp_df[col])])))
                data = np.delete(data, 0, 0)
                nominal_power = wpp_df['p_nom'].iloc[0]
            if fetch_curve == 'power_curve':
                df = pd.DataFrame(data, columns=['wind_speed', 'power'])
                if data_source == 'oedb':
                    # power values in W
                    df['power'] = df['power'] * 1000
            if fetch_curve == 'power_coefficient_curve':
                df = pd.DataFrame(data, columns=['wind_speed',
                                                 'power coefficient'])
            return df, nominal_power

        if fetch_curve == 'power_curve':
            self.power_curve, p_nom = restructure_data()
        elif fetch_curve == 'power_coefficient_curve':
            self.power_coefficient_curve, p_nom = restructure_data()
        else:
            raise ValueError("'{0}' is an invalid value. ".format(
                             fetch_curve) + "`fetch_curve` must be " +
                             "'power_curve' or 'power_coefficient_curve'.")
        if self.nominal_power is None:
            self.nominal_power = p_nom
        return self


def read_turbine_data(filename, **kwargs):
    r"""
    Fetches power (coefficient) curves from a  or a file.
    Turbine data is provided by the Open Energy Database (oedb) or can be
    provided by the user via a file. In the directory windpowerlib/data example
    files are provided.

    Parameters
    ----------
    filename : string
        Specifies the source of the turbine data.
        Use 'example_power_coefficient_curves.csv' or
        'example_power_curves.csv' to use the example data.

    Other Parameters
    ----------------
    datapath : string, optional
        Path where the data file is stored if `source` is name of a csv file.
        Default: './data'

    Returns
    -------
    pandas.DataFrame
        Power coefficient curve values (dimensionless) or power curve values
        in kW with corresponding wind speeds in m/s of all available wind
        turbines with turbine name in column 'turbine_type', turbine nominal
        power in column 'p_nom'.

    """

    if 'datapath' not in kwargs:
        kwargs['datapath'] = os.path.join(os.path.dirname(__file__),
                                          'data')
    try:
        df = pd.read_csv(os.path.join(kwargs['datapath'], filename),
                         index_col=0)
    except FileNotFoundError:
        raise FileNotFoundError(
            "The file '{}' was not found. Check spelling ".format(filename) +
            "and `datapath` - is '{}' ".format(kwargs['datapath']) +
            "and can be changed in read_turbine_data()")
    return df


def load_turbine_data_from_oedb():
    r"""
    Loads turbine data from the Open Energy Database (oedb).

    Returns
    -------
    turbine_data : pd.DataFrame
        Contains turbine data of different turbine types like 'manufacturer',
        'turbine_type', nominal power ('installed_capacity_kw'), '

    """

    if rq:
        # url of Open Energy Platform that contains the oedb
        oep_url = 'http://oep.iks.cs.ovgu.de/'
        # location of data
        schema = 'model_draft'
        table = 'openfred_windpower_powercurve'
        # load data
        result = rq.get(
            oep_url + '/api/v0/schema/{}/tables/{}/rows/?'.format(
                schema, table), )
        if result.status_code == 200:
            logging.info("Data base connection successful.")
        else:
            raise ConnectionError("Data base connection not successful. " +
                                  "Error: ".format(result.status_code))
        # extract data
        turbine_data = pd.DataFrame(result.json())
    else:
        raise ImportError('If you want to load turbine data from the oedb' +
                          'you have to install the requests package.' +
                          'see https://pypi.org/project/requests/')
    return turbine_data


def get_turbine_types(print_out=True):
    r"""
    Get the names of all possible wind turbine types for which the power
    coefficient curve or power curve is provided in the Open Energy Data Base
    (oedb).

    Parameters
    ----------
    print_out : boolean
        Directly prints a tabular containing the turbine types in column
        'turbine_type'. Default: True.

    Examples
    --------
    >>> from windpowerlib import wind_turbine
    >>> df = wind_turbine.get_turbine_types(print_out=False)
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

    df = load_turbine_data_from_oedb()
    cp_curves_df = df.iloc[df.loc[df['has_cp_curve'] == True].index][
        ['manufacturer', 'turbine_type', 'has_cp_curve']]
    p_curves_df = df.iloc[df.loc[df['has_power_curve'] == True].index][
        ['manufacturer', 'turbine_type', 'has_power_curve']]
    curves_df = pd.merge(p_curves_df, cp_curves_df, how='outer',
                        sort=True).fillna(False)
    if print_out:
        pd.set_option('display.max_rows', len(curves_df))
        print(curves_df)
        pd.reset_option('display.max_rows')
    return curves_df
