"""
The ``wind_farm`` module contains the class WindFarm that implements
a wind farm in the windpowerlib and functions needed for the modelling of a
wind farm.

"""

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"

from windpowerlib import tools, power_curves
import numpy as np
import pandas as pd
import os

try:
    from matplotlib import pyplot as plt
except ImportError:
    plt = None


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
        curve or power efficiency curve (pd.DataFrame) containing
        'wind_speed' and 'efficiency' columns/keys with wind speeds in m/s and
        the corresponding dimensionless wind farm efficiency. Default: None.

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

    def assign_power_curve(self, wake_losses_method='wind_efficiency_curve',
                           smoothing=True, block_width=0.5,
                           standard_deviation_method='turbulence_intensity',
                           smoothing_order='wind_farm_power_curves',
                           turbulence_intensity=None, **kwargs):
        r"""
        Calculates the power curve of a wind farm.

        The wind farm power curve is calculated by aggregating the wind turbine
        power curves of the wind farm.
        Depending on the parameters the wind turbine power curves are smoothed
        before or after the summation and/or a wind farm efficiency is applied
        after the summation. TODO: check entry

        Parameters
        ----------
        wake_losses_method : String
            Defines the method for talking wake losses within the farm into
            consideration. Options: 'wind_efficiency_curve',
            'constant_efficiency' or None. Default: 'wind_efficiency_curve'.
        smoothing : Boolean
            If True the power curves will be smoothed before the summation.
            Default: True.
        block_width : Float, optional
            Width of the moving block.
            Default in :py:func:`~.power_curves.smooth_power_curve`: 0.5.
        standard_deviation_method : String, optional
            Method for calculating the standard deviation for the gaussian
            distribution. Options: 'turbulence_intensity',
            'Staffell_Pfenninger'.
            Default in :py:func:`~.power_curves.smooth_power_curve`:
            'turbulence_intensity'.
        smoothing_order : String
        Defines when the smoothing takes place if `smoothing` is True. Options:
        'turbine_power_curves' (to the single turbine power curves),
        'wind_farm_power_curves'. Default: 'wind_farm_power_curves'.
        turbulence_intensity : Float
            Turbulence intensity. Default: None.

        Other Parameters
        ----------------
        roughness_length : Float, optional.
            Roughness length.

        Returns
        -------
        self

        """
        # Check if all wind turbines have a power curve as attribute
        for item in self.wind_turbine_fleet:
            if item['wind_turbine'].power_curve is None:
                raise ValueError("For an aggregated wind farm power curve " +
                                 "each wind turbine needs a power curve " +
                                 "but `power_curve` of wind turbine " +
                                 "{} is {}.".format(
                                     item['wind_turbine'].object_name,
                                     item['wind_turbine'].power_curve))
        # Initialize data frame for power curve values
        df = pd.DataFrame()
        for turbine_type_dict in self.wind_turbine_fleet:
            # Check if all needed parameters are available
            if smoothing:
                if (standard_deviation_method == 'turbulence_intensity' and
                        turbulence_intensity is None):
                    if 'roughness_length' in kwargs:
                        # Calculate turbulence intensity and write to kwargs
                        turbulence_intensity = (
                            tools.estimate_turbulence_intensity(
                                turbine_type_dict['wind_turbine'].hub_height,
                                kwargs['roughness_length']))
                        kwargs['turbulence_intensity'] = turbulence_intensity
                    else:
                        raise ValueError(
                            "`roughness_length` must be defined for using " +
                            "'turbulence_intensity' as " +
                            "`standard_deviation_method` if " +
                            "`turbulence_intensity` is not given")
            if wake_losses_method is not None:
                if self.efficiency is None:
                    raise KeyError(
                        "wind_farm_efficiency is needed if " +
                        "`wake_losses_method´ is '{0}', but ".format(
                            wake_losses_method) +
                        " `wind_farm_efficiency` of {0} is {1}.".format(
                            self.object_name, self.efficiency))
            # Get original power curve
            power_curve = pd.DataFrame(
                turbine_type_dict['wind_turbine'].power_curve)
            # Editions to power curve before the summation
            if smoothing and smoothing_order == 'turbine_power_curves':
                power_curve = power_curves.smooth_power_curve(
                    power_curve['wind_speed'], power_curve['power'],
                    standard_deviation_method=standard_deviation_method,
                    block_width=block_width, **kwargs)
            # Add power curves of all turbine types to data frame
            # (multiplied by turbine amount)
            df = pd.concat(
                    [df, pd.DataFrame(
                        power_curve.set_index(['wind_speed']) *
                        turbine_type_dict['number_of_turbines'])], axis=1)
        # Sum up all power curves
        summarized_power_curve = pd.DataFrame(
            df.interpolate(method='index').sum(axis=1))
        summarized_power_curve.columns = ['power']
        # Return wind speed (index) to a column of the data frame
        summarized_power_curve_df = pd.DataFrame(
            data=[list(summarized_power_curve.index),
                  list(summarized_power_curve['power'].values)]).transpose()
        summarized_power_curve_df.columns = ['wind_speed', 'power']
        # Editions to power curve after the summation
        if smoothing and smoothing_order == 'wind_farm_power_curves':
            summarized_power_curve_df = power_curves.smooth_power_curve(
                summarized_power_curve_df['wind_speed'],
                summarized_power_curve_df['power'],
                standard_deviation_method=standard_deviation_method,
                block_width=block_width, **kwargs)
        if (wake_losses_method == 'constant_efficiency' or
                wake_losses_method == 'wind_efficiency_curve'):
            summarized_power_curve_df = (
                power_curves.wake_losses_to_power_curve(
                    summarized_power_curve_df['wind_speed'].values,
                    summarized_power_curve_df['power'].values,
                    wake_losses_method=wake_losses_method,
                    wind_farm_efficiency=self.efficiency))
        self.power_curve = summarized_power_curve_df
        return self
    # TODO: rename to wind_farm_power_curve
