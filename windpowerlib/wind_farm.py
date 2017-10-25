"""
The ``wind_farm`` module contains the class WindFarm that implements
a wind farm in the windpowerlib and functions needed for the modelling of a
wind farm.

"""

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"

import numpy as np


class WindFarm(object):
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
