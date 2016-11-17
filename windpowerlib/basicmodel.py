import os
import sys
import logging
import numpy as np
import pandas as pd
import requests


class SimpleWindTurbine:
    r"""Model to determine the output of a wind turbine

    Parameters
    ----------
    wind_conv_type : string
        Name of the wind converter type. Use get_wind_pp_types() to see a list
        of all possible wind converters.
    h_hub : float
        Height of the hub of the wind turbine.
    d_rotor : float
        Diameter of the rotor.
    cp_values : pandas.DataFrame
        The index should be the wind speed and a column should be named 'cp'.
    nominal_power : float
        The nominal output of the wind power plant.

    Attributes
    ----------
    wind_conv_type : string
        Name of the wind converter type. Use get_wind_pp_types() to see a list
        of all possible wind converters.
    h_hub : float
        Height of the hub of the wind turbine.
    d_rotor : float
        Diameter of the rotor.
    cp_values : pandas.DataFrame
        The index should be the wind speed and a column should be named 'cp'.
    nominal_power : float
        The nominal output of the wind power plant.


    Examples
    --------
    >>> from windpowerlib import basicmodel
    >>> enerconE126 = {
    ...    'h_hub': 135,
    ...    'd_rotor': 127,
    ...    'wind_conv_type': 'ENERCON E 126 7500'}
    >>> e126 = basicmodel.SimpleWindTurbine(**enerconE126)
    >>> print(e126.d_rotor)
    127
    """

    def __init__(self, wind_conv_type=None, h_hub=None, d_rotor=None,
                 cp_values=None, nominal_power=None):
        self.h_hub = h_hub
        self.d_rotor = d_rotor
        self.wind_conv_type = wind_conv_type
        self.cp_values = cp_values
        self.nominal_power = nominal_power

        if cp_values is None or nominal_power is None:
            wpp_data = self.fetch_wpp_data()
            if cp_values is None:
                self.cp_values = wpp_data[0]
            if nominal_power is None:
                self.nominal_power = wpp_data[1]

    def rho_hub(self, weather, data_height):
        r"""
        Calculates the density of air in kg/m³ at hub height.
            (temperature in K, height in m, pressure in Pa)

        Parameters
        ----------
        weather : DataFrame or Dictionary
            Containing columns or keys with the timeseries for Temperature
            (temp_air) and pressure (pressure).
        data_height : DataFrame or Dictionary
            Containing columns or keys with the height of the measurement or
            model data for temperature (temp_air) and pressure (pressure).

        Returns
        -------
        float
            density of air in kg/m³ at hub height

        Notes
        -----
        Assumptions:
          * Temperature gradient of -6.5 K/km
          * Pressure gradient of -1/8 hPa/m

        The following equations are used [22]_:

        .. math:: T_{hub}=T_{air, data}-0.0065\cdot\left(h_{hub}-h_{T,data}
            \right)
        .. math:: p_{hub}=\left(p_{data}/100-\left(h_{hub}-h_{p,data}\right)
            *\frac{1}{8}\right)/\left(2.8706\cdot T_{hub}\right)

        with T: temperature [K], h: height [m], p: pressure [Pa]

        ToDo: Check the equation and add references.

        References
        ----------
        .. [22] ICAO-Standardatmosphäre (ISA).
            http://www.deutscher-wetterdienst.de/lexikon/download.php?file=Standardatmosphaere.pdf

        See Also
        --------
        v_wind_hub
        """
        h_temperature_data = data_height['temp_air']
        h_pressure_data = data_height['pressure']
        temperature_hub = weather.temp_air - 0.0065 * (
            self.h_hub - h_temperature_data)
        return (
            weather.pressure / 100 -
            (self.h_hub - h_pressure_data) * 1 / 8
            ) / (2.8706 * temperature_hub)

    def v_wind_hub(self, weather, data_height):
        r"""
        Calculates the wind speed in m/s at hub height.

        Parameters
        ----------
        weather : DataFrame or Dictionary
            Containing columns or keys with the timeseries for wind speed
            (v_wind) and roughness length (z0).
        data_height : DataFrame or Dictionary
            Containing columns or keys with the height of the measurement or
            model data for temperature (temp_air) and pressure (pressure).

        Returns
        -------
        float
            wind speed [m/s] at hub height

        Notes
        -----
        The following equation is used for the logarithmic wind profile [20]_:

        .. math:: v_{wind,hub}=v_{wind,data}\cdot\frac{\ln\left(\frac{h_{hub}}
            {z_{0}}\right)}{\ln\left(\frac{h_{data}}{z_{0}}\right)}

        with:
            v: wind speed [m/s], h: height [m], z0: roughness length [m]

        :math:`h_{data}` is the height in which the wind velocity is measured.
        (height in m, velocity in m/s)

        ToDo: Check the equation and add references.

        References
        ----------
        .. [20] Gasch R., Twele J.: "Windkraftanlagen". 6. Auflage, Wiesbaden,
                Vieweg + Teubner, 2010, page 129

        See Also
        --------
        rho_hub
        """
        return (weather.v_wind * np.log(self.h_hub / weather.z0) /
                np.log(data_height['v_wind'] / weather.z0))

    def fetch_wpp_data(self, **kwargs):
        r"""
        Fetch data of the requested wind converter.

        Returns
        -------
        tuple with pandas.DataFrame and float
            cp values and the nominal power of the requested wind converter

        Examples
        --------
        >>> from windpowerlib import basicmodel
        >>> e126 = basicmodel.SimpleWindTurbine('ENERCON E 126 7500')
        >>> print(e126.cp_values.cp[5.0])
        0.423
        >>> print(e126.nominal_power)
        7500000.0
        """
        df = read_wpp_data(**kwargs)
        wpp_df = df[df.rli_anlagen_id == self.wind_conv_type]
        if wpp_df.shape[0] == 0:
            pd.set_option('display.max_rows', len(df))
            logging.info('Possible types: \n{0}'.format(df.rli_anlagen_id))
            pd.reset_option('display.max_rows')
            sys.exit('Cannot find the wind converter typ: {0}'.format(
                self.wind_conv_type))
        ncols = ['rli_anlagen_id', 'p_nenn', 'source', 'modificationtimestamp']
        cp_data = np.array([0, 0])
        for col in wpp_df.keys():
            if col not in ncols:
                if wpp_df[col].iloc[0] is not None and not np.isnan(
                        float(wpp_df[col].iloc[0])):
                    cp_data = np.vstack((cp_data, np.array(
                        [float(col), float(wpp_df[col])])))
        cp_data = np.delete(cp_data, 0, 0)
        cp_df = pd.DataFrame(cp_data, columns=['v_wind', 'cp'])
        cp_df.set_index('v_wind', drop=True, inplace=True)
        nominal_power = wpp_df['p_nenn'].iloc[0] * 1000
        return cp_df, nominal_power

    def cp_series(self, v_wind):
        r"""
        Interpolates the cp value as a function of the wind velocity between
        data obtained from the power curve of the specified wind turbine type.

        Parameters
        ----------
        v_wind : pandas.Series or numpy.array
            Wind speed at hub height [m/s]

        Returns
        -------
        numpy.array
            cp values, wind converter type, installed capacity

        >>> import numpy
        >>> from windpowerlib import basicmodel
        >>> e126 = basicmodel.SimpleWindTurbine('ENERCON E 126 7500')
        >>> v_wind = numpy.array([1,2,3,4,5,6,7,8])
        >>> print(e126.cp_series(v_wind))
        [ 0.     0.     0.191  0.352  0.423  0.453  0.47   0.478]
        """
        v_max = self.cp_values.index.max()
        v_wind[v_wind > v_max] = v_max
        return np.interp(v_wind, self.cp_values.index, self.cp_values.cp)

    def turbine_power_output(self, weather, data_height):
        r"""
        Calculates the power output in W of one wind turbine.

        Parameters
        ----------
        weather : feedinlib.weather.FeedinWeather object
            Instance of the feedinlib weather object (see class
            :py:class:`FeedinWeather<feedinlib.weather.FeedinWeather>` for more
            details)
        data_height : dictionary
            Containing the heights of the weather measurements or weather
            model in meters with the keys of the data parameter

        # TODO Move the following parameters to a better place :-)

        Returns
        -------
        pandas.Series
            Electrical power of the wind turbine

        Notes
        -----
        The following equation is used for the power output :math:`P_{wpp}`
        [21]_:

        .. math:: P_{wpp}=\frac{1}{8}\cdot\rho_{air,hub}\cdot d_{rotor}^{2}
            \cdot\pi\cdot v_{wind}^{3}\cdot cp\left(v_{wind}\right)

        with:
            v: wind speed [m/s], d: diameter [m], :math:`\rho`: density [kg/m³]

        ToDo: Check the equation and add references.

        References
        ----------
        .. [21] Gasch R., Twele J.: "Windkraftanlagen". 6. Auflage, Wiesbaden,
                Vieweg + Teubner, 2010, pages 35ff, 208
        """
        if self.h_hub is None:
            logging.error("Attribute h_hub (hub height) is missing.")
            exit(0)
        if self.d_rotor is None:
            logging.error("Attribute d_rotor (diameter of rotor) is missing.")
            exit(0)
        p_wpp = (
            (self.rho_hub(weather, data_height) / 2) *
            (((self.d_rotor / 2) ** 2) * np.pi) *
            np.power(self.v_wind_hub(weather, data_height), 3) *
            self.cp_series(self.v_wind_hub(weather, data_height)))

        p_wpp_series = pd.Series(data=p_wpp,
                                 index=weather.index,
                                 name='feedin_wind_pp')
        p_wpp_series.index.names = ['']

        return p_wpp_series.clip(upper=(float(self.nominal_power)))


def read_wpp_data(**kwargs):
    r"""
    Fetch cp values from a file or download it from a server.

    The files are located in the ~/.oemof folder.

    Returns
    -------
    pandas.DataFrame
        cp values, wind converter type, installed capacity or the full
        table if the given wind converter cannot be found in the table.

    Other Parameters
    ----------------
    cp_path : string, optional
        Path where the cp file is stored. Default: $HOME/.windpower
    filename : string, optional
        Filename of the cp file without suffix. The suffix of the file should be
        csv or hf5.
    url : string, optional
        URL from where the cp file is loaded if not present

    Notes
    -----
    The files can be downloaded from
    http://vernetzen.uni-flensburg.de/~git/
    """
    default_cp_path = os.path.join(os.path.expanduser("~"), '.windpower')
    cp_path = kwargs.get('cp_path', default_cp_path)
    filename = kwargs.get('filename', 'cp_values')
    filepath = os.path.join(cp_path, filename)
    url = kwargs.get(
        'url', 'http://vernetzen.uni-flensburg.de/~git/cp_values')
    suffix = '.hf5'
    if not os.path.exists(cp_path):
        os.makedirs(cp_path)
    if not os.path.isfile(filepath + suffix):
        req = requests.get(url + suffix)
        with open(filepath + suffix, 'wb') as fout:
            fout.write(req.content)
        logging.info('Copying cp_values from {0} to {1}'.format(
            url, filepath + suffix))
    logging.debug('Retrieving cp values from {0}'.format(
        filename + suffix))
    try:
        df = pd.read_hdf(filepath + suffix, 'cp')
    except ValueError:
        suffix = '.csv'
        logging.info('Failed loading cp values from hdf file, trying csv.')
        logging.debug('Retrieving cp values from {0}'.format(
            filename + suffix))
        if not os.path.isfile(filename + suffix):
            req = requests.get(url + suffix)
            with open(filename + suffix, 'wb') as fout:
                fout.write(req.content)
            logging.info('Copying cp_values from {0} to {1}'.format(
                url, filename + suffix))
        df = pd.read_csv(filename + suffix, index_col=0)
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
    >>> from windpowerlib import basicmodel
    >>> valid_types_df = basicmodel.get_wind_pp_types(print_out=False)
    >>> valid_types_df.shape
    (91, 2)
    >>> print(valid_types_df.iloc[5])
    rli_anlagen_id    DEWIND D8 2000
    p_nenn                    2000.0
    Name: 5, dtype: object
    """
    df = read_wpp_data()

    if print_out:
        pd.set_option('display.max_rows', len(df))
        print(df[['rli_anlagen_id', 'p_nenn']])
        pd.reset_option('display.max_rows')
    return df[['rli_anlagen_id', 'p_nenn']]


if __name__ == "__main__":
    import doctest
    doctest.testmod()
