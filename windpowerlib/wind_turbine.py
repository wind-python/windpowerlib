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
    hub_height : float
        Hub height of the wind turbine in m.
    power_curve : bool, str, :pandas:`pandas.DataFrame<frame>` or dict (optional)
        Specifies power curve of the wind turbine or where to retrieve it from.
        Possible options are:

        * bool
          If set to True power curve is retrieved from oedb turbine library.
          Additionally, the parameter `turbine_type` must be provided to
          specify which turbine to retrieve the power curve for. The default is
          False in which case no power curve is set.
        * str
          File name of self-provided csv file the power curve is retrieved
          from. Additionally, the path pointing to the files directory must be
          provided through the parameter `path`. See
          `example_power_curves.csv` in example/data directory for the
          required format of the csv file.
        * :pandas:`pandas.DataFrame<frame>` or dict
          Directly sets the power curve. DataFrame/dictionary must have
          'wind_speed' and 'value' columns/keys with wind speeds in m/s and
          the corresponding power curve value in W.

        Default: False.
    power_coefficient_curve : bool, str, :pandas:`pandas.DataFrame<frame>` or dict (optional)
        Specifies power coefficient curve of the wind turbine or where to
        retrieve it from. Possible options are:

        * bool
          If set to True power coefficient curve is retrieved from oedb turbine
          library. Additionally, the parameter `turbine_type` must be provided
          to specify which turbine to retrieve the power coefficient curve for.
          The default is False in which case no power coefficient curve is set.
        * str
          File name of self-provided csv file the power coefficient curve is
          retrieved from. Additionally, the path pointing to the files
          directory must be provided through the parameter `path`. See
          `example_power_coefficient_curves.csv` in example/data directory for
          the required format of the csv file.
        * :pandas:`pandas.DataFrame<frame>` or dict
          Directly sets the power coefficient curve. DataFrame/dictionary must
          have 'wind_speed' and 'value' columns/keys with wind speeds in m/s
          and the corresponding power coefficient curve value.

        Default: False.
    turbine_type : str (optional)
        Name of the wind turbine type. Must be provided if power (coefficient)
        curve is retrieved from oedb turbine library or self provided file.
        Use :py:func:`~.get_turbine_types` to see a table of all wind turbines
        for which power (coefficient) curve data is provided. Default: None.
    rotor_diameter : float (optional)
        Diameter of the rotor in m. Only needs to be provided if power output
        is calculated using the power coefficient curve. Default: None.
    nominal_power : float (optional)
        The nominal output of the wind turbine in W. Default: None.
        ToDo: Expand docstring once it is decided how nominal power is set in
        case it is not directly provided.
    path : str (optional)
        In case :py:attr:`power_curve`, :py:attr:`power_coefficient_curve`, or
        :py:attr:`nominal_power` needs to be retrieved from self provided csv
        files, `path` specifies the path to the directory the csv files
        are located in.

    Attributes
    ----------
    turbine_type : str
        Name of the wind turbine.
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
   
    Notes
    ------
    Your wind turbine object needs to have a power coefficient or power curve.
    If you set the parameters `power_curve`, `power_coefficient_curve` and/or
    `nominal_power` to True the respective data is automatically fetched from
    the oedb turbine library (a dataset provided in the OpenEnergy Database).
    You can also provide your own csv files with power coefficient and power
    curves. See `example_power_curves.csv',
    `example_power_coefficient_curves.csv` and `example_nominal_power.csv`
    in example/data for the required form of such csv files.

    Examples
    --------
    >>> from windpowerlib import wind_turbine
    >>> enerconE126 = {
    ...    'hub_height': 135,
    ...    'rotor_diameter': 127,
    ...    'turbine_type': 'E-126/4200',
    ...    'power_curve':True}
    >>> e126 = wind_turbine.WindTurbine(**enerconE126)
    >>> print(e126.nominal_power)
    4200000.0

    """

    def __init__(self, hub_height, power_curve=False,
                 power_coefficient_curve=False,
                 turbine_type=None, rotor_diameter=None,
                 nominal_power=None, path=None, **kwargs):

        self.hub_height = hub_height
        self.turbine_type = turbine_type
        self.rotor_diameter = rotor_diameter
        # ToDo Check and transparently document where nominal_power is gotten
        # from (input parameter, csv file or maximum of power curve).
        self.nominal_power = nominal_power

        if power_curve:
            # if True get power curve from oedb turbine library
            if power_curve is True:
                self.power_curve = get_oedb_turbine_data(
                    self.turbine_type, fetch_data='power_curve')
            # if string try to retrieve power curve from file
            elif isinstance(power_curve, str):
                self.power_curve = get_turbine_data_from_file(
                    self.turbine_type, os.path.join(path, power_curve))
            # if dict or pd.DataFrame use it directly
            elif isinstance(power_curve, dict) or \
                    isinstance(power_curve, pd.DataFrame):
                self.power_curve = power_curve
            else:
                raise TypeError("Unknown type for parameter 'power_curve'.")
        else:
            self.power_curve = None

        if power_coefficient_curve:
            # if True get power coefficient curve from oedb turbine library
            if power_coefficient_curve is True:
                self.power_coefficient_curve = get_oedb_turbine_data(
                    self.turbine_type,
                    fetch_data='power_coefficient_curve')
            # if a string try to retrieve power coefficient curve from file
            elif isinstance(power_coefficient_curve, str):
                self.power_coefficient_curve = get_turbine_data_from_file(
                    self.turbine_type,
                    os.path.join(path, power_coefficient_curve))
            # if dict or pd.DataFrame use it directly
            elif isinstance(power_coefficient_curve, dict) or \
                    isinstance(power_coefficient_curve, pd.DataFrame):
                self.power_coefficient_curve = power_coefficient_curve
            else:
                raise TypeError("Unknown type for parameter "
                                "'power_coefficient_curve'.")
        else:
            self.power_coefficient_curve = None

        # test if either power curve or power coefficient curve is assigned
        if not power_curve and not power_coefficient_curve:
            raise AttributeError("Wind turbine must either have a power curve "
                                 "or power coefficient curve.")

    def __repr__(self):
        info = []
        if self.nominal_power is not None:
            info.append('nominal power={} W'.format(self.nominal_power))
        if self.hub_height is not None:
            info.append('hub height={} m'.format(self.hub_height))
        if self.rotor_diameter is not None:
            info.append('rotor diameter={} m'.format(self.rotor_diameter))

        if self.turbine_type is not None:
            repr = 'Wind turbine: {name} {info}'.format(
                name=self.turbine_type, info=info)
        else:
            repr = 'Wind turbine: {info}'.format(info=info)

        return repr


def get_turbine_data_from_file(turbine_type, file_):
    r"""
    Fetches turbine data from a csv file.

    See `example_power_curves.csv', `example_power_coefficient_curves.csv` and
    `example_nominal_power_data.csv` in example/data for the required format of
    a csv file. Make sure to provide wind speeds in m/s and power in W or
    convert units after loading the data.

    Parameters
    ----------
    turbine_type : str
        Specifies the turbine type data is fetched for.
    file_ : str
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
    >>> source = os.path.join(os.path.dirname(__file__), '../example/data',
    ...                       'example_power_curves.csv')
    >>> p_nom_source = os.path.join(os.path.dirname(__file__),
    ...                             '../example/data',
    ...                             'example_nominal_power.csv')
    >>> example_turbine = {
    ...    'hub_height': 100,
    ...    'rotor_diameter': 70,
    ...    'name': 'DUMMY 3',
    ...    'power_curve': source,
    ...    'power_coefficient_curve': None,
    ...    'nominal_power': p_nom_source}
    >>> e_t_1 = wind_turbine.WindTurbine(**example_turbine)
    >>> print(e_t_1.power_curve['value'][7])
    18000.0
    >>> print(e_t_1.nominal_power)
    150000.0

    """

    try:
        df = pd.read_csv(file_, index_col=0)
    except FileNotFoundError:
        raise FileNotFoundError("The file '{}' was not found.".format(file_))
    wpp_df = df[df.index == turbine_type]
    # if turbine not in data file
    if wpp_df.shape[0] == 0:
        pd.set_option('display.max_rows', len(df))
        logging.info('Possible types: \n{0}'.format(pd.DataFrame(df.index)))
        pd.reset_option('display.max_rows')
        raise KeyError("Wind converter type {0} not provided.".format(
            turbine_type))
    # if turbine in data file change the format
    if 'nominal_power' in file_:
        return float(wpp_df['nominal_power'].values[0])
    else:
        wpp_df.dropna(axis=1, inplace=True)
        wpp_df = wpp_df.transpose().reset_index()
        wpp_df.columns = ['wind_speed', 'value']
        # transform wind speeds to floats
        wpp_df['wind_speed'] = wpp_df['wind_speed'].apply(lambda x: float(x))
        return wpp_df


def get_oedb_turbine_data(turbine_type, fetch_data):
    r"""
    Retrieves wind turbine data from the oedb turbine library.

    The oedb turbine library is provided along with the windpowerlib and
    provides power curves, power coefficient curves and nominal power for a
    large number of wind turbines. The latest oedb turbine library can be
    fetched by executing :py:func:`~.load_turbine_data_from_oedb`.

    Parameters
    ----------
    turbine_type : str
        Specifies the wind turbine the data is fetched for.
        Use :py:func:`~.get_turbine_types` to see a table of all wind turbines
        in the oedb turbine library and information about whether power
        (coefficient) curve data is provided.
    fetch_data : str
        Parameter to specify what data to retrieve. Valid options are
        'power_curve', 'power_coefficient_curve' and 'nominal_power'.

    Returns
    -------
    :pandas:`pandas.DataFrame<frame>` or float
        Power curve or power coefficient curve (pandas.DataFrame) or nominal
        power in W (float) of specified wind turbine type. Power (coefficient)
        curve DataFrame contains power coefficient curve values (dimensionless)
        or power curve values in W in column 'values' with the corresponding
        wind speeds in m/s in column 'wind_speed'.

    """
    if fetch_data == 'nominal_power':
        filename = os.path.join(os.path.dirname(__file__), 'data',
                                'oedb_{}.csv'.format(fetch_data))
    else:
        filename = os.path.join(os.path.dirname(__file__), 'data',
                                'oedb_{}s.csv'.format(fetch_data))

    data = get_turbine_data_from_file(turbine_type=turbine_type,
                                      file_=filename)

    # nominal power and power curve values in W
    if fetch_data == 'nominal_power':
        data = data * 1000
    elif fetch_data == 'power_curve':
        # power in W
        data['value'] = data['value'] * 1000
    return data


def load_turbine_data_from_oedb():
    r"""
    Loads turbine library from the OpenEnergy database (oedb).

    Turbine data is saved to csv files ('oedb_power_curves.csv',
    'oedb_power_coefficient_curves.csv' and 'oedb_nominal_power') for offline
    usage of the windpowerlib. If the files already exist they are overwritten.

    Returns
    -------
    :pandas:`pandas.DataFrame<frame>`
        Turbine data of different turbines such as 'manufacturer',
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
        curves_df.to_csv(filename.format('{}s'.format(curve_type)))

    # get nominal power of all wind turbine types and save to file
    nominal_power_df = turbine_data[
        ['turbine_type', 'installed_capacity']].set_index(
        'turbine_type').rename(
        columns={'installed_capacity': 'nominal_power'})
    nominal_power_df.to_csv(filename.format('nominal_power'))
    return turbine_data


def get_turbine_types(print_out=True, filter_=True):
    r"""
    Get all wind turbine types provided in the oedb turbine library.

    By default only turbine types for which a power coefficient curve or power
    curve is provided are returned. Set `filter_=False` to see all turbine
    types for which any data (e.g. hub height, rotor diameter, ...) is
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
    # ToDo Use local csv files instead of querying the oedb
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
