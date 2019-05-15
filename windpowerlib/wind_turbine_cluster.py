"""
The ``wind_turbine_cluster`` module contains the class WindTurbineCluster that
implements a wind turbine cluster in the windpowerlib and provides functions
needed for modelling a wind turbine cluster.
A wind turbine cluster comprises wind farms and wind turbines belonging to the
same weather data point.

"""

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"


import numpy as np
import pandas as pd
import warnings


class WindTurbineCluster(object):
    r"""
    Defines a standard set of wind turbine cluster attributes.

    Parameters
    ----------
    name : str or None
        Name of the wind turbine cluster.
    wind_farms : list (:class:`~.wind_farm.WindFarm`)
        List of wind farms in cluster.
    coordinates : list(float) or None (optional)
        List with coordinates [lat, lon] of location. Default: None.

    Attributes
    ----------
    name : str or None
        Name of the wind turbine cluster.
    wind_farms : list (:class:`~.wind_farm.WindFarm`)
        List of wind farms in cluster.
    coordinates : list(float) or None
        List with coordinates [lat, lon] of location. Default: None.
    hub_height : float
        The calculated average hub height of the wind turbine cluster. See
        :py:func:`mean_hub_height` for more information.
    nominal_power : float
        The nominal power is the sum of the nominal power of all turbines in
        the wind turbine cluster in W.
    installed_power : float
        Installed nominal power of the wind turbine cluster in W. Deprecated!
        Use :attr:`~.wind_farm.WindFarm.nominal_power` instead.
    power_curve : :pandas:`pandas.DataFrame<frame>` or None
        The calculated power curve of the wind turbine cluster. See
        :py:func:`assign_power_curve` for more information.
    power_output : :pandas:`pandas.Series<series>`
        The calculated power output of the wind turbine cluster.

    """
    def __init__(self, name, wind_farms, coordinates=None, **kwargs):

        self.name = name
        self.wind_farms = wind_farms
        self.coordinates = coordinates

        self.hub_height = None
        self._nominal_power = None
        self._installed_power = None
        self.power_curve = None
        self.power_output = None

    @property
    def installed_power(self):
        r"""
        The installed nominal power of the wind turbine cluster. (Deprecated!)

        """
        warnings.warn(
            'installed_power is deprecated, use nominal_power instead.',
            FutureWarning)
        return self.nominal_power

    @installed_power.setter
    def installed_power(self, installed_power):
        self._installed_power = installed_power

    @property
    def nominal_power(self):
        r"""
        The nominal power of the wind turbine cluster.

        See :attr:`~.wind_turbine_cluster.WindTurbineCluster.nominal_power`
        for further information.

        Parameters
        -----------
        nominal_power : float
            Nominal power of the wind turbine cluster in w.

        Returns
        -------
        float
            Nominal power of the wind turbine cluster in w.

        """
        if not self._nominal_power:
            self.nominal_power = self.get_installed_power()
        return self._nominal_power

    @nominal_power.setter
    def nominal_power(self, nominal_power):
        self._nominal_power = nominal_power

    def mean_hub_height(self):
        r"""
        Calculates the mean hub height of the wind turbine cluster.

        The mean hub height of a wind turbine cluster is necessary for power
        output calculations with an aggregated wind turbine cluster power
        curve. Hub heights of wind farms with higher nominal power weigh more
        than others.
        After the calculations the mean hub height is assigned to the attribute
        :py:attr:`~hub_height`.

        Returns
        -------
        :class:`~.wind_turbine_cluster.WindTurbineCluster`
            self

        Notes
        -----
        The following equation is used [1]_:

        .. math:: h_{WTC} = e^{\sum\limits_{k}{ln(h_{WF,k})}
                           \frac{P_{N,k}}{\sum\limits_{k}{P_{N,k}}}}

        with:
            :math:`h_{WTC}`: mean hub height of wind turbine cluster,
            :math:`h_{WF,k}`: hub height of the k-th wind farm of the cluster,
            :math:`P_{N,k}`: installed power of the k-th wind farm

        References
        ----------
        .. [1]  Knorr, K.: "Modellierung von raum-zeitlichen Eigenschaften der
                 Windenergieeinspeisung für wetterdatenbasierte
                 Windleistungssimulationen". Universität Kassel, Diss., 2016,
                 p. 35

        """
        self.hub_height = np.exp(sum(
            np.log(wind_farm.hub_height) * wind_farm.get_installed_power() for
            wind_farm in self.wind_farms) / self.get_installed_power())
        return self

    def get_installed_power(self):
        r"""
        Calculates the :py:attr:`~nominal_power` of a wind turbine cluster.

        Returns
        -------
        float
            Nominal power of the wind farm in W. See :py:attr:`~nominal_power`
            for further information.

        """
        for wind_farm in self.wind_farms:
            wind_farm.nominal_power = wind_farm.get_installed_power()
        return sum(wind_farm.nominal_power for wind_farm in self.wind_farms)

    def assign_power_curve(self, wake_losses_model='power_efficiency_curve',
                           smoothing=False, block_width=0.5,
                           standard_deviation_method='turbulence_intensity',
                           smoothing_order='wind_farm_power_curves',
                           turbulence_intensity=None, **kwargs):
        r"""
        Calculates the power curve of a wind turbine cluster.

        The turbine cluster power curve is calculated by aggregating the wind
        farm power curves of wind farms within the turbine cluster. Depending
        on the parameters the power curves are smoothed (before or after the
        aggregation) and/or a wind farm efficiency is applied before the
        aggregation.
        After the calculations the power curve is assigned to the attribute
        :py:attr:`~power_curve`.

        Parameters
        ----------
        wake_losses_model : str
            Defines the method for taking wake losses within the farm into
            consideration. Options: 'power_efficiency_curve',
            'constant_efficiency' or None. Default: 'power_efficiency_curve'.
        smoothing : bool
            If True the power curves will be smoothed before or after the
            aggregation of power curves depending on `smoothing_order`.
            Default: False.
        block_width : float
            Width between the wind speeds in the sum of the equation in
            :py:func:`~.power_curves.smooth_power_curve`. Default: 0.5.
        standard_deviation_method : str
            Method for calculating the standard deviation for the Gauss
            distribution. Options: 'turbulence_intensity',
            'Staffell_Pfenninger'. Default: 'turbulence_intensity'.
        smoothing_order : str
            Defines when the smoothing takes place if `smoothing` is True.
            Options: 'turbine_power_curves' (to the single turbine power
            curves), 'wind_farm_power_curves'.
            Default: 'wind_farm_power_curves'.
        turbulence_intensity : float
            Turbulence intensity at hub height of the wind farm or
            wind turbine cluster for power curve smoothing with
            'turbulence_intensity' method. Can be calculated from
            `roughness_length` instead. Default: None.
        roughness_length : float (optional)
            Roughness length. If `standard_deviation_method` is
            'turbulence_intensity' and `turbulence_intensity` is not given
            the turbulence intensity is calculated via the roughness length.

        Returns
        -------
        :class:`~.wind_turbine_cluster.WindTurbineCluster`
            self

        """
        # Assign wind farm power curves to wind farms of wind turbine cluster
        for farm in self.wind_farms:
            # Assign hub heights (needed for power curve and later for
            # hub height of turbine cluster)
            farm.mean_hub_height()
            # Assign wind farm power curve
            farm.assign_power_curve(
                wake_losses_model=wake_losses_model,
                smoothing=smoothing, block_width=block_width,
                standard_deviation_method=standard_deviation_method,
                smoothing_order=smoothing_order,
                turbulence_intensity=turbulence_intensity, **kwargs)
        # Create data frame from power curves of all wind farms
        df = pd.concat([farm.power_curve.set_index(['wind_speed']).rename(
            columns={'value': farm.name}) for
            farm in self.wind_farms], axis=1)
        # Sum up power curves
        cluster_power_curve = pd.DataFrame(
            df.interpolate(method='index').sum(axis=1))
        cluster_power_curve.columns = ['value']
        # Return wind speed (index) to a column of the data frame
        cluster_power_curve.reset_index('wind_speed', inplace=True)
        self.power_curve = cluster_power_curve
        return self
