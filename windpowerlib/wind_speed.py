# -*- coding: utf-8 -*-
"""
Created on Mon Jan  2 11:07:52 2017

@author: RL-INSTITUT\sabine.haas
"""

"""
The ``wind_speed`` module contains methods
to calculate the wind_speed at hub height of a wind turbine.
"""

import numpy as np


def logarithmic_wind_profile(h_hub, weather, data_height):
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
        h_hub : float
            hub height of wind turbine in m

        Returns
        -------
        pandas.Series
            wind speed [m/s] at hub height as time series

        Notes
        -----
        The following equation is used for the logarithmic wind profile [20],
        [25]_:

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
        .. [25] Hau, E. Windkraftanlagen - Grundlagen, Technik, Einsatz,
                Wirtschaftlichkeit Springer-Verlag, 2008, p. 515

        """
        return (weather.v_wind * np.log(h_hub / weather.z0) /
                np.log(data_height['v_wind'] / weather.z0))
