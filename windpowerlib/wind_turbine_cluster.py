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
    wind_farms : list
        ...
    object_name : string or None
        Name of the wind turbine cluster. Default: None.
    coordinates : list or None
        List of coordinates [lat, lon] of location for loading data.
        Default: None.

    Attributes
    ----------

    """
    def __init__(self, wind_farms, object_name=None, coordinates=None):

        self.object_name = object_name
        self.wind_farms = wind_farms
        self.coordinates = coordinates
