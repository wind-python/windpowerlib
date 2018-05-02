"""
The ``wind_turbine_cluster`` module is under development and is not working yet.

"""
# TODO: desciption

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"

from windpowerlib import power_curves

import numpy as np
import pandas as pd


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

    def assign_power_curve(self, wake_losses_method='wind_efficiency_curve',
                           smoothing=True, block_width=0.5,
                           standard_deviation_method='turbulence_intensity',
                           smoothing_order='wind_farm_power_curves', **kwargs):
        r"""
        Calculates the power curve of a wind turbine cluster.

        The turbine cluster power curve is calculated by aggregating the wind
        farm power curves of the turbine cluster.
        Depending on the parameters of the class the power curves are smoothed
        and/or density corrected after the summation of the wind farm power
        curves.

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

        Other Parameters
        ----------------
        roughness_length : Float, optional.
            Roughness length.
        turbulence_intensity : Float, optional.
            Turbulence intensity.

        Returns
        -------
        summarized_power_curve_df : pd.DataFrame
            Calculated power curve of the wind turbine cluster.

        """
        # Assign wind farm power curves to wind farms of wind turbine cluster
        for farm in self.wind_farms:
            farm.power_curve = farm.assign_power_curve(
                wake_losses_method=wake_losses_method,
                smoothing=smoothing, block_width=block_width,
                standard_deviation_method=standard_deviation_method,
                smoothing_order=smoothing_order, **kwargs)
        # Create data frame from power curves of all wind farms
        df = pd.concat([farm.power_curve.set_index(['wind_speed']).rename(
            columns={'power': farm.object_name}) for
            farm in self.wind_farms], axis=1)
        # Sum up power curves
        summarized_power_curve = pd.DataFrame(
            # TODO rename to aggregated_power_curve
            df.interpolate(method='index').sum(axis=1))
        summarized_power_curve.columns = ['power']
        # Return wind speed (index) to a column of the data frame
        summarized_power_curve.reset_index('wind_speed', inplace=True)
        return summarized_power_curve
