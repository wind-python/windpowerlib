"""
The ``wind_turbine_cluster`` module is under development and is not working yet.

"""
# TODO: desciption

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"


import numpy as np


class WindTurbineCluster(object):
    r"""

    Parameters
    ----------
    object_name : string
        Name of the wind turbine cluster.
    wind_farms : list
        Contains objects of the :class:`~.wind_farm.WindFarm`.
    coordinates : list or None
        List of coordinates [lat, lon] of location for loading data.
        Default: None.

     Attributes
    ----------
    object_name : string
        Name of the wind turbine cluster.
    wind_farms : list
        Contains objects of the :class:`~.wind_farm.WindFarm`.
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

    def mean_hub_height(self):
        r"""
        Calculates the mean power weighted hub height of the turbine cluster.

        Assigns the hub height to the wind turbine cluster object.

        Returns
        -------
        self

        Notes
        -----
        The following equation is used [1]_:
        .. math:: h_{WTC} = e^{\sum\limits_{k}{ln(h_{WF,k})}
                           \frac{P_{N,k}}{\sum\limits_{k}{P_{N,k}}}}

        with:
            :math:`h_{WTC}`: mean hub height of wind turbine cluster,
            :math:`h_{WF,k}`: hub height of the k-th wind farm of the cluster,
            :math:`P_{N,k}`: nominal power of the k-th wind farm

        References
        ----------
        .. [1]  Knorr, K.: "Modellierung von raum-zeitlichen Eigenschaften der
                 Windenergieeinspeisung für wetterdatenbasierte
                 Windleistungssimulationen". Universität Kassel, Diss., 2016,
                 p. 35

        """
        self.hub_height = np.exp(
            sum(np.log(wind_farm.hub_height) * wind_farm.installed_power for
                wind_farm in self.wind_farms) / self.get_installed_power())
        return self

    def get_installed_power(self):
        r"""
        Calculates the installed power of a wind turbine cluster.

        Returns
        -------
        float
            Installed power of the wind turbine cluster.

        """
        return sum(wind_farm.installed_power for wind_farm in self.wind_farms)
