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
    object_name : string
        Name of the wind farm.
    wind_turbine_fleet : list of dictionaries
        Wind turbines of wind farm. Dictionaries must have 'wind_turbine'
        (contains a :class:`~.wind_turbine.WindTurbine` object) and
        'number_of_turbines' (number of turbine type in wind farm) as keys.
    coordinates : list or None
        List of coordinates [lat, lon] of location for loading data.
        Default: None.
    efficiency : Float or pd.DataFrame or Dictionary
        Efficiency of the wind farm. Either constant (float) or wind efficiency
        curve (pd.DataFrame or Dictionary) containing 'wind_speed' and
        'efficiency' columns/keys with wind speeds in m/s and the
        corresponding dimensionless wind farm efficiency. Default: None.

    Attributes
    ----------
    object_name : string
        Name of the wind farm.
    wind_turbine_fleet : list of dictionaries
        Wind turbines of wind farm. Dictionaries must have 'wind_turbine'
        (contains a :class:`~.wind_turbine.WindTurbine` object) and
        'number_of_turbines' (number of turbine type in wind farm) as keys.
    coordinates : list or None
        List of coordinates [lat, lon] of location for loading data.
        Default: None.
    efficiency : Float or pd.DataFrame or Dictionary
        Efficiency of the wind farm. Either constant (float) or wind efficiency
        curve (pd.DataFrame or Dictionary) containing 'wind_speed' and
        'efficiency' columns/keys with wind speeds in m/s and the
        corresponding dimensionless wind farm efficiency. Default: None.
    hub_height : float
        The calculated average hub height of the wind farm.
    installed_power : float
        Installed power of the wind farm.
    power_curve : pandas.DataFrame or None
        The calculated power curve of the wind farm.
    power_output : pandas.Series
        The calculated power output of the wind farm.
    """
    def __init__(self, object_name, wind_turbine_fleet, coordinates=None,
                 efficiency=None):

        self.object_name = object_name
        self.wind_turbine_fleet = wind_turbine_fleet
        self.coordinates = coordinates
        self.efficiency = efficiency

        self.hub_height = None
        self.installed_power = None
        self.power_curve = None
        self.power_output = None

    def mean_hub_height(self):
        r"""
        Calculates the mean power weighted hub height of a wind farm.

        Assigns the hub height to the wind farm object.

        Returns
        -------
        self

        Notes
        -----
        The following equation is used [1]_:
        .. math:: h_{WF} = e^{\sum\limits_{k}{ln(h_{WT,k})}
                           \frac{P_{N,k}}{\sum\limits_{k}{P_{N,k}}}}

        with:
            :math:`h_{WF}`: mean hub height of wind farm,
            :math:`h_{WT,k}`: hub height of the k-th wind turbine of a wind
            farm, :math:`P_{N,k}`: nominal power of the k-th wind turbine

        References
        ----------
        .. [1]  Knorr, K.: "Modellierung von raum-zeitlichen Eigenschaften der
                 Windenergieeinspeisung für wetterdatenbasierte
                 Windleistungssimulationen". Universität Kassel, Diss., 2016,
                 p. 35

        """
        self.hub_height = np.exp(
            sum(np.log(wind_dict['wind_turbine'].hub_height) *
                wind_dict['wind_turbine'].nominal_power *
                wind_dict['number_of_turbines']
                for wind_dict in self.wind_turbine_fleet) /
            self.get_installed_power())
        return self

    def get_installed_power(self):
        r"""
        Calculates the installed power of a wind farm.

        Returns
        -------
        float
            Installed power of the wind farm.

        """
        return sum(
            wind_dict['wind_turbine'].nominal_power *
            wind_dict['number_of_turbines']
            for wind_dict in self.wind_turbine_fleet)
