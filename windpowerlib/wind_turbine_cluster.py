"""
The ``wind_turbine_cluster`` module contains the class WindTurbineCluster that
implements a wind turbine cluster in the windpowerlib and provides functions
needed for modelling a wind turbine cluster.
A wind turbine cluster comprises wind farms and wind turbines belonging to the
same weather data point.

SPDX-FileCopyrightText: 2019 oemof developer group <contact@oemof.org>
SPDX-License-Identifier: MIT
"""
import numpy as np
import pandas as pd


class WindTurbineCluster(object):
    r"""
    Defines a standard set of wind turbine cluster attributes.

    Parameters
    ----------
    wind_farms : list(:class:`~.wind_farm.WindFarm`)
        List of wind farms in cluster.
    name : str (optional)
        Can be used as an identifier of the wind turbine cluster. Default: ''.

    Attributes
    ----------
    wind_farms : list(:class:`~.wind_farm.WindFarm`)
        List of wind farms in cluster.
    name : str
        If set this is used as an identifier of the wind turbine cluster.
    hub_height : float
        The calculated average hub height of the wind turbine cluster. See
        :py:func:`mean_hub_height` for more information.
    power_curve : :pandas:`pandas.DataFrame<frame>` or None
        The calculated power curve of the wind turbine cluster. See
        :py:func:`assign_power_curve` for more information.

    """

    def __init__(self, wind_farms, name="", **kwargs):

        self.wind_farms = wind_farms
        self.name = name

        self.hub_height = None
        self._nominal_power = None
        self.power_curve = None

    def __repr__(self):
        if self.name != "":
            wf_repr = "Wind turbine cluster: {name}".format(name=self.name)
        else:
            info = []
            for wind_farm in self.wind_farms:
                info.append(wind_farm)
            wf_repr = r"Wind turbine cluster with: {info}".format(info=info)
        return wf_repr

    @property
    def nominal_power(self):
        r"""
        The nominal power is the sum of the nominal power of all turbines in
        the wind turbine cluster.

        Returns
        -------
        float
            Nominal power of the wind turbine cluster in W.

        """
        if not self._nominal_power:
            self.nominal_power = sum(
                wind_farm.nominal_power for wind_farm in self.wind_farms
            )
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

        .. math:: h_{WTC}=e^{\sum\limits_{k}{ln(h_{WF,k})}
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
        self.hub_height = np.exp(
            sum(
                np.log(wind_farm.hub_height) * wind_farm.nominal_power
                for wind_farm in self.wind_farms
            )
            / self.nominal_power
        )
        return self

    def assign_power_curve(
        self,
        wake_losses_model="wind_farm_efficiency",
        smoothing=False,
        block_width=0.5,
        standard_deviation_method="turbulence_intensity",
        smoothing_order="wind_farm_power_curves",
        turbulence_intensity=None,
        **kwargs,
    ):
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
            Defines the method for taking wake losses within the wind farms of
            the  cluster into consideration. Options: 'wind_farm_efficiency'
            or None. If 'wind_farm_efficiency' is chosen the `efficiency`
            attribute of the WindFarms must be set.
            Default: 'wind_farm_efficiency'.
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
                smoothing=smoothing,
                block_width=block_width,
                standard_deviation_method=standard_deviation_method,
                smoothing_order=smoothing_order,
                turbulence_intensity=turbulence_intensity,
                **kwargs,
            )
        # Create data frame from power curves of all wind farms
        df = pd.concat(
            [
                farm.power_curve.set_index(["wind_speed"]).rename(
                    columns={"value": i}
                )
                for farm, i in zip(
                    self.wind_farms, list(range(len(self.wind_farms)))
                )
            ],
            axis=1,
            sort=True
        )
        # Sum up power curves
        cluster_power_curve = pd.DataFrame(
            df.interpolate(method="index").sum(axis=1)
        )
        cluster_power_curve.columns = ["value"]
        # Return wind speed (index) to a column of the data frame
        cluster_power_curve.reset_index(inplace=True)
        self.power_curve = cluster_power_curve
        return self
