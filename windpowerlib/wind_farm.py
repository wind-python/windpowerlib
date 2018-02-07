"""
The ``wind_farm`` module contains the class WindFarm that implements
a wind farm in the windpowerlib and functions needed for the modelling of a
wind farm.

"""

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"

import numpy as np


class WindFarm(object):
    r"""
    Defines a standard set of wind farm attributes.

    Parameters
    ----------
    wind_farm_name : string
        Name of the wind farm.
    wind_turbine_fleet : List of Dictionaries
        Wind turbines of wind farm. Dictionaries must have 'wind_turbine'
        (contains wind turbine object) and 'number_of_turbines' (number of
        turbine type in wind farm) as keys.
    coordinates : List
        List of coordinates [lat, lon] of location for loading data.

    Attributes
    ----------
    wind_farm_name : string
        Name of the wind farm.
    wind_turbine_fleet : List of Dictionaries
        Wind turbines of wind farm. Dictionaries must have 'wind_turbine'
        (contains wind turbine object) and 'number_of_turbines' (number of
        turbine type in wind farm) as keys.
    coordinates : List
        List of coordinates (floats) of location for loading data.
        Example: [lat, lon]
    power_curve : pandas.DataFrame or None
        Power curve of the wind turbine. DataFrame has 'wind_speed' and
        'values' columns with wind speeds in m/s and the corresponding power
        curve value in W.
    power_output : pandas.Series
        The calculated power output of the wind farm.
    annual_energy_output : float
        The calculated annual energy output of the wind farm.
    """
    def __init__(self, wind_farm_name, wind_turbine_fleet, coordinates):

        self.wind_farm_name = wind_farm_name
        self.wind_turbine_fleet = wind_turbine_fleet
        self.coordinates = coordinates

        self.average_hub_height = None
        # self.average_hub_height = self.average_hub_height()
        self.power_curve = None
        self.power_output = None
        self.annual_energy_output = None

    def average_hub_height(self):
        """

        Notes
        -----
        The following equation is used for the wind speed at site [1]_:
        .. math:: h_{WP} = e^{\sum\limits_{k}{ln(h_{WEA,k})}
                           \frac{P_{n,k}}{\sum\limits_{k}{P_{n,k}}}}

        with:


        References
        ----------
        .. [1]

        """
        return sum(np.log(wind_dict['wind_turbine'].hub_height ) *
                   wind_dict['wind_turbine'].nominal_power /
                   sum(wind_dict_2['wind_turbine'].nominal_power
                       for wind_dict_2 in self.wind_turbine_fleet)
                   for wind_dict in self.wind_turbine_fleet)
