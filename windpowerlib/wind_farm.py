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
    def __init__(self, object_name, wind_turbine_fleet, coordinates):

        self.object_name = object_name
        self.wind_turbine_fleet = wind_turbine_fleet
        self.coordinates = coordinates

        self.average_hub_height = None
        # self.average_hub_height = self.mean_hub_height()
        self.power_curve = None
        self.power_output = None
        self.annual_energy_output = None

    def mean_hub_height(self):
        r"""
        Calculates the mean power weighted hub height of a wind farm.

        Returns
        -------
        Float
            Mean power weighted hub height.

        Notes
        -----
        The following equation is used for the wind speed at site [1]_:
        .. math:: h_{WF} = e^{\sum\limits_{k}{ln(h_{WT,k})}
                           \frac{P_{N,k}}{\sum\limits_{k}{P_{N,k}}}}

        with:
            :math:`h_{WF}`: mean hub height of wind farm,
            :math:`h_{WT,k}`: hub height of the k-th wind turbine of a wind
            farm, :math:`P_{N,k}`: nominal power of the k-th wind turbine,

        References
        ----------
        .. [1]  Knorr, K.: "Modellierung von raum-zeitlichen Eigenschaften der
                 Windenergieeinspeisung für wetterdatenbasierte
                 Windleistungssimulationen". Universität Kassel, Diss., 2016

        """
        total_nominal_power = sum(
            wind_dict_2['wind_turbine'].nominal_power *
            wind_dict_2['number_of_turbines']
            for wind_dict_2 in self.wind_turbine_fleet)
        return np.exp(sum(np.log(wind_dict['wind_turbine'].hub_height) *
                          wind_dict['wind_turbine'].nominal_power *
                          wind_dict['number_of_turbines']
                          for wind_dict in self.wind_turbine_fleet) /
                      total_nominal_power)
