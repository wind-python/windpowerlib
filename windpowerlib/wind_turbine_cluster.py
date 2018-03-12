"""
The ``wind_turbine_cluster`` module is under development and is not working yet.

"""
# TODO: desciption

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"

import numpy as np
#from windpowerlib import wind_turbine


class WindTurbineCluster(object):
    r"""

    Parameters
    ----------
    object_name : string
        Name of the wind turbine cluster.
    wind_farms : list
        ...
    coordinates : list or None
        List of coordinates [lat, lon] of location for loading data.
        Default: None.

     Attributes
    ----------
    object_name : string
        Name of the wind turbine cluster.
    wind_farms : list
        ...
    coordinates : list or None
        List of coordinates [lat, lon] of location for loading data.
        Default: None.
    hub_height : float
        The calculated average hub height of the wind turbine cluster.
    installed_power : float
        The calculated installed power of the wind turbine cluster.
    power_curve : pandas.DataFrame or None
        The calculated power curve of the wind turbine cluster.
    power_output : pandas.Series
        The calculated power output of the wind turbine cluster.

    """
    def __init__(self, object_name, wind_farms, coordinates=None):

        self.object_name = object_name
        self.wind_farms = wind_farms
        self.coordinates = coordinates

        self.hub_height = None
        self.installed_power = None
        self.power_curve = None
        self.power_output = None
