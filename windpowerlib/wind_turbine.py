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
          to specify which turbine to retrieve the power curve for. The
          default is False in which case no power curve is set.
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
                self.power_curve, self.nominal_power = get_oedb_turbine_data(
                    self.turbine_type, fetch_curve='power_curve')
            # if power_curve is a string try to retrieve power curve from file
            elif isinstance(power_curve, str):
                self.power_curve, self.nominal_power = \
                    get_turbine_data_from_file(self.turbine_type,
                                               os.path.join(path, power_curve))
            # if power_curve is dict or pd.DataFrame use it directly
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
                self.power_coefficient_curve, self.nominal_power = \
                    get_oedb_turbine_data(
                        self.turbine_type,
                        fetch_curve='power_coefficient_curve')
            # if power_coefficient_curve is a string try to retrieve power
            # coefficient curve from file
            elif isinstance(power_coefficient_curve, str):
                self.power_coefficient_curve, self.nominal_power = \
                    get_turbine_data_from_file(
                        self.turbine_type,
                        os.path.join(path, power_coefficient_curve))
            # if power_coefficient_curve is dict or pd.DataFrame use it
            # directly
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
    # note: this try except statement will be removed in 0.2.0 and only
    # the exception will stay. The example power (coefficient) curve files
    # will then be adapted
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
    # note: this try except statement will be removed in 0.2.0 and only
    # the exception will stay. The example power (coefficient) curve files
    # will then be adapted
    try:
        nominal_power = wpp_df['p_nom'].iloc[0]
    except KeyError:
        nominal_power = float(wpp_df['nominal_power'].iloc[0])
    return df, nominal_power


def get_oedb_turbine_data(turbine_type, fetch_curve):
    r"""
    Retrieves wind turbine data from the oedb turbine library.

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
