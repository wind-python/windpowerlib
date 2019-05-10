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
import os


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
        coefficient curve) is loaded from the OpenEnergy Database ('oedb') or
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
    OpenEnergy Database (oedb) or want to read a csv file that you provide.
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
                 data_source='oedb', **kwargs):

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
            power coefficient curve) is loaded from the OpenEnergy Database
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
        if fetch_curve not in ['power_curve', 'power_coefficient_curve']:
            raise ValueError("'{0}' is an invalid value for ".format(
                fetch_curve) + "`fetch_curve`. Must be " +
                             "'power_curve' or 'power_coefficient_curve'.")
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
    turbine_type : str
        Specifies the turbine type data is fetched for.
    file_ : str
        Specifies the source of the turbine data.
        See the example below for how to use the example data.

    Returns
    -------
    tuple(pandas.DataFrame, float)
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
        except ValueError:
            return False

    try:
        df = pd.read_csv(file_, index_col=0)
    except FileNotFoundError:
        raise FileNotFoundError("The file '{}' was not found.".format(file_))
    # todo: note: this try except statement will be removed in 0.2.0 and only
    #  the exception will stay. The example power (coefficient) curve files
    #  will then be adapted
    try:
        wpp_df = df[df['turbine_id'] == turbine_type]
    except KeyError:
        wpp_df = df[df.index == turbine_type]
    # if turbine not in data file
    if wpp_df.shape[0] == 0:
        pd.set_option('display.max_rows', len(df))
        logging.info('Possible types: \n{0}'.format(df['turbine_id']))
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
    # todo: note: this try except statement will be removed in 0.2.0 and only
    #  the exception will stay. The example power (coefficient) curve files
    #  will then be adapted
    try:
        nominal_power = wpp_df['p_nom'].iloc[0]
    except KeyError:
        nominal_power = float(wpp_df['nominal_power'].iloc[0])
    return df, nominal_power


def get_turbine_data_from_oedb(turbine_type, fetch_curve, overwrite=False):
    r"""
    Fetches wind turbine data from the OpenEnergy database (oedb).

    If turbine data exists in local repository it is loaded from this file. The
    file is created when turbine data is loaded from oedb in
    :py:func:`~.load_turbine_data_from_oedb`. Use this function with
    `overwrite=True` to overwrite your file with newly fetched data.

    Parameters
    ----------
    turbine_type : str
        Specifies the turbine type data is fetched for.
        Use :py:func:`~.get_turbine_types` to see a table of all wind turbines
        in oedb containing information about whether power (coefficient) curve
        data is provided.
    fetch_curve : str
        Parameter to specify whether a power or power coefficient curve
        should be retrieved from the provided turbine data. Valid options are
        'power_curve' and 'power_coefficient_curve'. Default: None.
    overwrite : bool
        If True local file is overwritten by newly fetched data from oedb, if
        False turbine data is fetched from previously saved file.

    Returns
    -------
    tuple(pandas.DataFrame, float)
        Power curve or power coefficient curve (pandas.DataFrame) and nominal
        power (float) of one wind turbine type. Power (coefficient) curve
        DataFrame contains power coefficient curve values (dimensionless) or
        power curve values in W with the corresponding wind speeds in m/s.

    """
    filename = os.path.join(os.path.dirname(__file__), 'data',
                            'oedb_{}s.csv'.format(fetch_curve))
    if not os.path.isfile(filename) or overwrite:
        # Load data from oedb and save to csv file
        load_turbine_data_from_oedb()
    else:
        logging.debug("Turbine data is fetched from {}".format(filename))
    # turbine_data = pd.read_csv(filename, index_col=0)
    df, nominal_power = get_turbine_data_from_file(turbine_type=turbine_type,
                                                   file_=filename)

    # nominal power and power curve values in W
    nominal_power = nominal_power * 1000
    if fetch_curve == 'power_curve':
        # power in W
        df['value'] = df['value'] * 1000
    return df, nominal_power


def load_turbine_data_from_oedb():
    r"""
    Loads turbine data from the OpenEnergy database (oedb).

    Turbine data is saved to csv files ('oedb_power_curves.csv' and
    'oedb_power_coefficient_curves.csv') for offline usage of windpowerlib.
    If the files already exist they are overwritten.

    Returns
    -------
    pd.DataFrame
        Contains turbine data of different turbines such as 'manufacturer',
        'turbine_type', 'nominal_power'.

    """
    # url of OpenEnergy Platform that contains the oedb
    oep_url = 'http://oep.iks.cs.ovgu.de/'
    # location of data
    schema = 'supply'
    table = 'turbine_library'
    # load data
    result = requests.get(
        oep_url + '/api/v0/schema/{}/tables/{}/rows/?'.format(
            schema, table), )
    if not result.status_code == 200:
        raise ConnectionError("Database connection not successful. "
                              "Response: [{}]".format(result.status_code))
    # extract data to dataframe
    turbine_data = pd.DataFrame(result.json())
    # standard file name for saving data
    filename = os.path.join(os.path.dirname(__file__), 'data',
                            'oedb_{}.csv')
    # get all power (coefficient) curves and save to file
    # for curve_type in ['power_curve', 'power_coefficient_curve']:
    for curve_type in ['power_curve', 'power_coefficient_curve']:
        curves_df = pd.DataFrame(columns=['wind_speed'])
        for index in turbine_data.index:
            if (turbine_data['{}_wind_speeds'.format(curve_type)][index]
                    and turbine_data['{}_values'.format(curve_type)][index]):
                df = pd.DataFrame(data=[
                    eval(turbine_data['{}_wind_speeds'.format(curve_type)][
                             index]),
                    eval(turbine_data['{}_values'.format(curve_type)][
                             index])]).transpose().rename(
                    columns={0: 'wind_speed',
                             1: turbine_data['turbine_type'][index]})
                curves_df = pd.merge(left=curves_df, right=df, how='outer',
                                     on='wind_speed')
        curves_df = curves_df.set_index('wind_speed').sort_index().transpose()
        curves_df['turbine_type'] = curves_df.index
        # add nominal power to power (coefficient) data frame
        curves_df = pd.merge(
            left=curves_df, right=turbine_data[['turbine_type',
                                                'installed_capacity']],
            on='turbine_type').set_index('turbine_type').rename(
                columns={'installed_capacity': 'nominal_power'})
        curves_df.to_csv(filename.format('{}s'.format(curve_type)))

    return turbine_data


def get_turbine_types(print_out=True, filter_=True):
    r"""
    Get all wind turbine types provided in the OpenEnergy database (oedb).

    By default only turbine types for which a power coefficient curve or power
    curve is provided are returned. Set `filter_=False` to see all turbine
    types for which any data (f.e. hub height, rotor diameter, ...) is
    provided.

    Parameters
    ----------
    print_out : bool
        Directly prints a tabular containing the turbine types in column
        'turbine_type', the manufacturer in column 'manufacturer' and
        information about whether a power (coefficient) curve exists (True) or
        not (False) in columns 'has_power_curve' and 'has_cp_curve'.
        Default: True.
    filter_ : bool
        If True only turbine types for which a power coefficient curve or
        power curve is provided in the OpenEnergy database (oedb) are
        returned. Default: True.

    Returns
    -------
    pd.DataFrame
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
    `the data base <https://openenergy-platform.org/dataedit/view/model_draft/openfred_windpower_powercurve>`_.

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
    if filter_:
        cp_curves_df = df.loc[df['has_cp_curve']][
            ['manufacturer', 'turbine_type', 'has_cp_curve']]
        p_curves_df = df.loc[df['has_power_curve']][
            ['manufacturer', 'turbine_type', 'has_power_curve']]
        curves_df = pd.merge(p_curves_df, cp_curves_df, how='outer',
                             sort=True).fillna(False)
    else:
        curves_df = df[['manufacturer', 'turbine_type', 'has_power_curve',
                        'has_cp_curve']]
    if print_out:
        pd.set_option('display.max_rows', len(curves_df))
        print(curves_df)
        pd.reset_option('display.max_rows')
    return curves_df
