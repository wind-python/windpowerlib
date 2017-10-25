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
        List of coordinates [lat, lon] of location for loading data.
    power_curve : pandas.DataFrame or None
        Power curve of the wind turbine. DataFrame has 'wind_speed' and
        'values' columns with wind speeds in m/s and the corresponding power
        curve value in W.
    power_output : pandas.Series
        The calculated power output of the wind turbine.

    """
    def __init__(self, wind_farm_name, wind_turbine_fleet, coordinates):

        self.wind_farm_name = wind_farm_name
        self.wind_turbine_fleet = wind_turbine_fleet
        self.coordinates = coordinates

        self.power_curve = None
        self.power_output = None

#    def wind_park_p_curve(self):
#        p_curve = np.sum([self.wind_turbines[i].power_curve
#                          for i in range(len(self.wind_turbines))], axis=0)
#        return p_curve
