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
import requests


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
        Diameter of the rotor in m. Default: None.
    power_coefficient_curve : None, pandas.DataFrame or dictionary
        Power coefficient curve of the wind turbine. DataFrame/dictionary must
        have 'wind_speed' and 'value' columns/keys with wind speeds
        in m/s and the corresponding power coefficients. Default: None.
    power_curve : None, pandas.DataFrame or dictionary
        Power curve of the wind turbine. DataFrame/dictionary must have
        'wind_speed' and 'value' columns/keys with wind speeds in m/s and the
        corresponding power curve value in W. Default: None.
    nominal_power : None or float
        The nominal output of the wind turbine in W. Default: None.
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
        from a csv file ('<path including file name>'). Default: 'oedb'.
        See `example_power_curves.csv' and
        `example_power_coefficient_curves.csv` in example/data for the required
        form of a csv file (more columns can be added).

    Attributes
    ----------
    name : string
        Name of the wind turbine type.
        Use :py:func:`~.get_turbine_types` to see a table of all wind turbines
        for which power (coefficient) curve data is provided.
    hub_height : float
        Hub height of the wind turbine in m.
    rotor_diameter : None or float
        Diameter of the rotor in m. Default: None.
    power_coefficient_curve : None, pandas.DataFrame or dictionary
        Power coefficient curve of the wind turbine. DataFrame/dictionary must
        have 'wind_speed' and 'value' columns/keys with wind speeds
        in m/s and the corresponding power coefficients. Default: None.
    power_curve : None, pandas.DataFrame or dictionary
        Power curve of the wind turbine. DataFrame/dictionary must have
        'wind_speed' and 'value' columns/keys with wind speeds in m/s and the
        corresponding power curve value in W. Default: None.
    nominal_power : None or float
        The nominal output of the wind turbine in W. Default: None.
    coordinates : list or None
        List of coordinates [lat, lon] of location for loading data.
        Default: None.
    power_output : pandas.Series
        The calculated power output of the wind turbine. Default: None.

    Notes
    ------
    Your wind turbine object should have a power coefficient or power curve.
    You can set the `fetch_curve` parameter and the `data_source` parameter if
    you want to automatically fetch a curve from a data set provided in the
    Open Energy Database (oedb) or want to read a csv file that you provide.
    See `example_power_curves.csv' and `example_power_coefficient_curves.csv`
    in example/data for the required form of such a csv file (more columns can
    be added).

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
        power curve from a data set provided in the OpenEnergy Database
        (oedb). You can also import your own power (coefficient) curves from a
        file. For that the wind speeds in m/s have to be in the first row and
        the corresponding power coefficient curve values or power curve values
        in W in a row where the first column contains the turbine name.
        See `example_power_curves.csv' and
        `example_power_coefficient_curves.csv` in example/data for the required
        form of a csv file (more columns can be added). See
        :py:func:`~.get_turbine_data_from_file` for an example reading data
        from a csv file.

        Parameters
        ----------
        fetch_curve : string
            Parameter to specify whether a power or power coefficient curve
            should be retrieved from the provided turbine data. Valid options
            are 'power_curve' and 'power_coefficient_curve'. Default: None.
        data_source : string
            Specifies whether turbine data (f.e. nominal power, power curve,
            power coefficient curve) is loaded from the Open Energy Database
            ('oedb') or from a csv file ('<path including file name>').
            Default: 'oedb'.

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
        >>> print(e126.power_coefficient_curve['value'][5])
        0.44
        >>> print(e126.nominal_power)
        4200000.0

        """
        if data_source == 'oedb':
            curve_df, nominal_power = get_turbine_data_from_oedb(
                turbine_type=self.name, fetch_curve=fetch_curve)
        else:
            curve_df, nominal_power = get_turbine_data_from_file(
                turbine_type=self.name, file_=data_source)
        if fetch_curve == 'power_curve':
            self.power_curve = curve_df
        elif fetch_curve == 'power_coefficient_curve':
            self.power_coefficient_curve = curve_df
        else:
            raise ValueError("'{0}' is an invalid value. ".format(
                             fetch_curve) + "`fetch_curve` must be " +
                             "'power_curve' or 'power_coefficient_curve'.")
        if self.nominal_power is None:
            self.nominal_power = nominal_power
        return self


def get_turbine_data_from_file(turbine_type, file_):
    r"""
    Fetches power (coefficient) curve data from a csv file.

    See `example_power_curves.csv' and `example_power_coefficient_curves.csv`
    in example/data for the required format of a csv file. The self-provided
    csv file may contain more columns than the example files. Only columns
    containing wind speed and the corresponding power or power coefficient as
    well as the column 'nominal_power' are taken into account.

    Parameters
    ----------
    turbine_type : string
        Specifies the turbine type data is fetched for.
    file_ : string
        Specifies the source of the turbine data.
        See the example below for how to use the example data.

    Returns
    -------
    Tuple (pandas.DataFrame, float)
        Power curve or power coefficient curve (pandas.DataFrame) and nominal
        power (float). Power (coefficient) curve DataFrame contains power
        coefficient curve values (dimensionless) or power curve values in W
        as column names with the corresponding wind speeds in m/s.

    Examples
    --------
    >>> from windpowerlib import wind_turbine
    >>> import os
    >>> source = os.path.join(os.path.dirname(__file__), '../example/data',
    ...                       'example_power_curves.csv')
    >>> example_turbine = {
    ...    'hub_height': 100,
    ...    'rotor_diameter': 70,
    ...    'name': 'DUMMY 3',
    ...    'fetch_curve': 'power_curve',
    ...    'data_source': source}
    >>> e_t_1 = wind_turbine.WindTurbine(**example_turbine)
    >>> print(e_t_1.power_curve['value'][7])
    18000.0
    >>> print(e_t_1.nominal_power)
    150000

    """
    def isfloat(x):
        try:
            float(x)
            return x
        except:
            return False

    try:
        df = pd.read_csv(file_, index_col=0)
    except FileNotFoundError:
        raise FileNotFoundError("The file '{}' was not found.".format(file_))
    wpp_df = df[df.turbine_id == turbine_type]
    # if turbine not in data file
    if wpp_df.shape[0] == 0:
        pd.set_option('display.max_rows', len(df))
        logging.info('Possible types: \n{0}'.format(df.turbine_id))
        pd.reset_option('display.max_rows')
        sys.exit('Cannot find the wind converter type: {0}'.format(
            turbine_type))
    # if turbine in data file select power (coefficient) curve columns and
    # drop nans
    cols = [_ for _ in wpp_df.columns if isfloat(_)]
    curve_data = wpp_df[cols].dropna(axis=1)
    df = curve_data.transpose().reset_index()
    df.columns = ['wind_speed', 'value']
    df['wind_speed'] = df['wind_speed'].apply(lambda x: float(x))
    nominal_power = wpp_df['p_nom'].iloc[0]
    return df, nominal_power


def get_turbine_data_from_oedb(turbine_type, fetch_curve):
    r"""
    Gets turbine data from the OpenEnergy Database (oedb).

    Parameters
    ----------
    turbine_type : string
        Specifies the turbine type data is fetched for.
        Use :py:func:`~.get_turbine_types` to see a table of all wind turbines
        for which power (coefficient) curve data is provided.
    fetch_curve : string
        Parameter to specify whether a power or power coefficient curve
        should be retrieved from the provided turbine data. Valid options are
        'power_curve' and 'power_coefficient_curve'. Default: None.

    Returns
    -------
    Tuple (pandas.DataFrame, float)
        Power curve or power coefficient curve (pandas.DataFrame) and nominal
        power (float). Power (coefficient) curve DataFrame contains power
        coefficient curve values (dimensionless) or power curve values in W
        with the corresponding wind speeds in m/s.

    """
    # Extract data
    turbine_data = load_turbine_data_from_oedb()
    turbine_data.set_index('turbine_type', inplace=True)
    # Set `curve` depending on `fetch_curve` to match names in oedb
    curve = ('cp_curve' if fetch_curve == 'power_coefficient_curve'
             else fetch_curve)
    # Select curve and nominal power of turbine type
    try:
        df = pd.DataFrame(turbine_data.loc[turbine_type][curve])
    except KeyError:
        raise KeyError("Turbine type '{}' not in database. ".format(
            turbine_type) + "Use 'get_turbine_types()' to see a table of " +
                       "possible wind turbine types.")
    nominal_power = turbine_data.loc[turbine_type][
                        'installed_capacity_kw'] * 1000
    df.columns = ['wind_speed', 'value']
    if fetch_curve == 'power_curve':
        # power in W
        df['value'] = df['value'] * 1000
    return df, nominal_power


def load_turbine_data_from_oedb():
    r"""
    Loads turbine data from the OpenEnergy Database (oedb).

    Returns
    -------
    turbine_data : pd.DataFrame
        Contains turbine data of different turbines such as 'manufacturer',
        'turbine_type', nominal power ('installed_capacity_kw').

    """
    # url of OpenEnergy Platform that contains the oedb
    oep_url = 'http://oep.iks.cs.ovgu.de/'
    # location of data
    schema = 'model_draft'
    table = 'openfred_windpower_powercurve'
    # load data
    result = requests.get(
        oep_url + '/api/v0/schema/{}/tables/{}/rows/?'.format(
            schema, table), )
    if result.status_code == 200:
        logging.info("Database connection successful.")
    else:
        raise ConnectionError("Database connection not successful. " +
                              "Error: ".format(result.status_code))
    # extract data
    turbine_data = pd.DataFrame(result.json())
    return turbine_data


def get_turbine_types(print_out=True):
    r"""
    Get the names of all possible wind turbine types for which the power
    coefficient curve or power curve is provided in the OpenEnergy Data Base
    (oedb).

    Parameters
    ----------
    print_out : boolean
        Directly prints a tabular containing the turbine types in column
        'turbine_type', the manufacturer in column 'manufacturer' and
        information about whether a power (coefficient) curve exists (True) or
        not (False) in columns 'has_power_curve' and 'has_cp_curve'.
        Default: True.

    Returns
    -------
    curves_df : pd.DataFrame
        Contains turbine types in column 'turbine_type', the manufacturer in
        column 'manufacturer' and information about whether a power
        (coefficient) curve exists (True) or not (False) in columns
        'has_power_curve' and 'has_cp_curve'.

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
