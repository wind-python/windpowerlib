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
import warnings


class WindFarm(object):
    r"""
    Defines a standard set of wind farm attributes.

    Parameters
    ----------
    wind_turbine_fleet : list(dict)
        Wind turbines of wind farm. Dictionaries must have 'wind_turbine'
        (contains a :class:`~.wind_turbine.WindTurbine` object) and
        'number_of_turbines' (number of wind turbines of the same turbine type
        in the wind farm) as keys.
    efficiency : float or :pandas:`pandas.DataFrame<frame>` or None (optional)
        Efficiency of the wind farm. Provide as either constant (float) or
        power efficiency curve (pd.DataFrame) containing 'wind_speed' and
        'efficiency' columns with wind speeds in m/s and the corresponding
        dimensionless wind farm efficiency. Default: None.
    name : str (optional)
        Can be used as an identifier of the wind farm. Default: ''.

    Attributes
    ----------
    wind_turbine_fleet : list(dict)
        Wind turbines of wind farm. Dictionaries must have 'wind_turbine'
        (contains a :class:`~.wind_turbine.WindTurbine` object) and
        'number_of_turbines' (number of wind turbines of the same turbine type
        in the wind farm) as keys.
    efficiency : float or :pandas:`pandas.DataFrame<frame>` or None
        Efficiency of the wind farm. Either constant (float) power efficiency
        curve (pd.DataFrame) containing 'wind_speed' and 'efficiency'
        columns with wind speeds in m/s and the corresponding
        dimensionless wind farm efficiency. Default: None.
    name : str
        If set this is used as an identifier of the wind farm.
    hub_height : float
        The calculated mean hub height of the wind farm. See
        :py:func:`mean_hub_height` for more information.
    nominal_power : float
        The nominal power is the sum of the nominal power of all turbines in
        the wind farm in W.
    power_curve : :pandas:`pandas.DataFrame<frame>` or None
        The calculated power curve of the wind farm. See
        :py:func:`assign_power_curve` for more information.
    power_output : :pandas:`pandas.Series<series>`
        The calculated power output of the wind farm.

    Examples
    --------
    >>> from windpowerlib import wind_farm
    >>> from windpowerlib import wind_turbine
    >>> enerconE126 = {
    ...    'hub_height': 135,
    ...    'rotor_diameter': 127,
    ...    'name': 'E-126/4200',
    ...    'fetch_curve': 'power_curve',
    ...    'data_source': 'oedb'}
    >>> e126 = wind_turbine.WindTurbine(**enerconE126)
    >>> example_farm_data = {
    ...    'name': 'example_farm',
    ...    'wind_turbine_fleet': [{'wind_turbine': e126,
    ...                            'number_of_turbines': 6}]}
    >>> example_farm = wind_farm.WindFarm(**example_farm_data)
    >>> print(example_farm.nominal_power)
    25200000.0

    """

    def __init__(self, wind_turbine_fleet, efficiency=None, name='', **kwargs):

        self.wind_turbine_fleet = wind_turbine_fleet
        self.efficiency = efficiency
        self.name = name

        self.hub_height = None
        self._nominal_power = None
        self.power_curve = None

    def __repr__(self):
        #ToDo implement nice nice string representation
        return self.name

    @property
    def nominal_power(self):
        r"""
        The nominal power of the wind farm.

        See :attr:`~.wind_farm.WindFarm.nominal_power` for further information.

        Parameters
        -----------
        nominal_power : float
            Nominal power of the wind farm in W.

        Returns
        -------
        float
            Nominal power of the wind farm in W.

        """
        if not self._nominal_power:
            self.nominal_power = self.get_installed_power()
        return self._nominal_power

    @nominal_power.setter
    def nominal_power(self, nominal_power):
        self._nominal_power = nominal_power

    def mean_hub_height(self):
        r"""
        Calculates the mean hub height of the wind farm.

        The mean hub height of a wind farm is necessary for power output
        calculations with an aggregated wind farm power curve containing wind
        turbines with different hub heights. Hub heights of wind turbines with
        higher nominal power weigh more than others.
        After the calculations the mean hub height is assigned to the attribute
        :py:attr:`~hub_height`.

        Returns
        -------
        :class:`~.wind_farm.WindFarm`
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
        Calculates :py:attr:`~nominal_power` of the wind farm.

        Returns
        -------
        float
            Nominal power of the wind farm in W. See :py:attr:`~nominal_power`
            for further information.

        """
        return sum(
            wind_dict['wind_turbine'].nominal_power *
            wind_dict['number_of_turbines']
            for wind_dict in self.wind_turbine_fleet)

    def assign_power_curve(self, wake_losses_model='power_efficiency_curve',
                           smoothing=False, block_width=0.5,
                           standard_deviation_method='turbulence_intensity',
                           smoothing_order='wind_farm_power_curves',
                           turbulence_intensity=None, **kwargs):
        r"""
        Calculates the power curve of a wind farm.

        The wind farm power curve is calculated by aggregating the power curves
        of all wind turbines in the wind farm. Depending on the parameters the
        power curves are smoothed (before or after the aggregation) and/or a
        wind farm efficiency (power efficiency curve or constant efficiency) is
        applied after the aggregation.
        After the calculations the power curve is assigned to the attribute
        :py:attr:`~power_curve`.

        Parameters
        ----------
        wake_losses_model : str
            Defines the method for taking wake losses within the farm into
            consideration. Options: 'wind_farm_efficiency' or None.
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
            Turbulence intensity at hub height of the wind farm for power curve
            smoothing with 'turbulence_intensity' method. Can be calculated
            from `roughness_length` instead. Default: None.
        roughness_length : float (optional)
            Roughness length. If `standard_deviation_method` is
            'turbulence_intensity' and `turbulence_intensity` is not given
            the turbulence intensity is calculated via the roughness length.

        Returns
        -------
        :class:`~.wind_farm.WindFarm`
            self

        """
        # Check if all wind turbines have a power curve as attribute
        for item in self.wind_turbine_fleet:
            if item['wind_turbine'].power_curve is None:
                raise ValueError("For an aggregated wind farm power curve " +
                                 "each wind turbine needs a power curve " +
                                 "but `power_curve` of '{}' is None.".format(
                                     item['wind_turbine']))
        # Initialize data frame for power curve values
        df = pd.DataFrame()
        for turbine_type_dict in self.wind_turbine_fleet:
            # Check if needed parameters are available and/or assign them
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
            # Get original power curve
            power_curve = pd.DataFrame(
                turbine_type_dict['wind_turbine'].power_curve)
            # Editions to the power curves before the summation
            if smoothing and smoothing_order == 'turbine_power_curves':
                power_curve = power_curves.smooth_power_curve(
                    power_curve['wind_speed'], power_curve['value'],
                    standard_deviation_method=standard_deviation_method,
                    block_width=block_width, **kwargs)
            else:
                # Add value zero to start and end of curve as otherwise
                # problems can occur during the aggregation
                if power_curve.iloc[0]['wind_speed'] != 0.0:
                    power_curve = pd.concat(
                        [pd.DataFrame(data={
                            'value': [0.0], 'wind_speed': [0.0]}),
                         power_curve], sort=True)
                if power_curve.iloc[-1]['value'] != 0.0:
                    power_curve = pd.concat(
                        [power_curve, pd.DataFrame(data={
                            'value': [0.0], 'wind_speed': [
                                power_curve['wind_speed'].loc[
                                    power_curve.index[-1]] + 0.5]})],
                        sort=True)
            # Add power curves of all turbine types to data frame
            # (multiplied by turbine amount)
            df = pd.concat(
                [df, pd.DataFrame(power_curve.set_index(['wind_speed']) *
                 turbine_type_dict['number_of_turbines'])], axis=1)
        # Aggregate all power curves
        wind_farm_power_curve = pd.DataFrame(
            df.interpolate(method='index').sum(axis=1))
        wind_farm_power_curve.columns = ['value']
        wind_farm_power_curve.reset_index('wind_speed', inplace=True)
        # Apply power curve smoothing and consideration of wake losses
        # after the summation
        if smoothing and smoothing_order == 'wind_farm_power_curves':
            wind_farm_power_curve = power_curves.smooth_power_curve(
                wind_farm_power_curve['wind_speed'],
                wind_farm_power_curve['value'],
                standard_deviation_method=standard_deviation_method,
                block_width=block_width, **kwargs)
        if (wake_losses_model == 'constant_efficiency' or
                wake_losses_model == 'power_efficiency_curve'):
            if self.efficiency is not None:
                wind_farm_power_curve = (
                    power_curves.wake_losses_to_power_curve(
                        wind_farm_power_curve['wind_speed'].values,
                        wind_farm_power_curve['value'].values,
                        wind_farm_efficiency=self.efficiency))
            else:
                logging.info("`wake_losses_model` is {} but wind farm ".format(
                    wake_losses_model) + "efficiency is NOT taken into "
                                         "account as it is None.")
        self.power_curve = wind_farm_power_curve
        return self
