"""
The ``turbine_cluster_modelchain`` module contains functions and classes of the
windpowerlib. TODO: adapt

"""

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"

from . import modelchain, power_output, tools, wind_farm, wind_turbine_cluster
import pandas as pd


class TurbineClusterModelChain(object):
    r"""
    Model to determine the output of a wind farm or wind turbine cluster.

    Parameters
    ----------
    wind_object : WindFarm or WindTurbineCluster
        A :class:`~.wind_farm.WindFarm` object representing the wind farm or
        a :class:`~.wind_turbine_cluster.WindTurbineCluster` object
        representing the wind turbine cluster.
    density_correction : Boolean
        If True a density correction will be applied to the power curves
        before the summation. Default: False.
    wake_losses_method : String
        Defines the method for talking wake losses within the farm into
        consideration. Default: 'constant_efficiency'.
    smoothing : Boolean
        If True the power curves will be smoothed before the summation.
        Default: True.
    block_width : Float, optional
        Width of the moving block.
        Default in :py:func:`~.power_output.smooth_power_curve`: 0.5.
    standard_deviation_method : String, optional
        Method for calculating the standard deviation for the gaussian
        distribution. Options: 'turbulence_intensity', 'Norgaard', 'Staffell'.
        Default in :py:func:`~.power_output.smooth_power_curve`:
        'turbulence_intensity'.

    Attributes
    ----------
    wind_object : WindFarm or WindTurbineCluster
        A :class:`~.wind_farm.WindFarm` object representing the wind farm or
        a :class:`~.wind_turbine_cluster.WindTurbineCluster` object
        representing the wind turbine cluster.
    density_correction : Boolean
        If True a density correction will be applied to the power curves
        before the summation. Default: False.
    wake_losses_method : String
        Defines the method for talking wake losses within the farm into
        consideration. Default: 'constant_efficiency'.
    smoothing : Boolean
        If True the power curves will be smoothed before the summation.
        Default: True.
    block_width : Float, optional
        Width of the moving block.
        Default in :py:func:`~.power_output.smooth_power_curve`: 0.5.
    standard_deviation_method : String, optional
        Method for calculating the standard deviation for the gaussian
        distribution. Options: 'turbulence_intensity', 'Norgaard', 'Staffell'.
        Default in :py:func:`~.power_output.smooth_power_curve`:
        'turbulence_intensity'.
    power_output : pandas.Series
        Electrical power output of the wind turbine in W.

    """
    def __init__(self, wind_object, density_correction=False,  #TODO: parameter cluster_or_farm boolean ?
                 wake_losses_method='constant_efficiency', smoothing=True,
                 block_width=0.5,
                 standard_deviation_method='turbulence_intensity',
                 density_correction_order='wind_farm_power_curves', # TODO add to docstring
                 smoothing_order='wind_farm_power_curves'):
# 'turbine_power_curves' 'wind_farm_power_curves' 'cluster_power_curve'
        self.wind_object = wind_object
        self.density_correction = density_correction
        self.wake_losses_method = wake_losses_method
        self.smoothing = smoothing
        self.block_width = block_width
        self.standard_deviation_method = standard_deviation_method
        self.density_correction_order = density_correction_order
        self.smoothing_order = smoothing_order

        self.power_output = None

# TODO: if a wind turbine of wind farm does not have power curve but cp curve:
    # calculate power curve from cp curve

    def wind_farm_power_curve(self, **kwargs):
        r"""
        Caluclates the power curve of the wind farm.

        Depending on the parameters of the class the power cuvers are smoothed
        and/or density corrected before or after the summation and/or a wind
        farm efficiency is applied after the summation. TODO: check entry

        Other Parameters
        ----------------
        roughness_length : Float, optional.
            Roughness length.
        turbulence_intensity : Float, optional.
            Turbulence intensity.

        Returns
        -------
        self

        """
        # Initialize data frame for power curve values
        df = pd.DataFrame()
        for turbine_type_dict in self.wind_object.wind_turbine_fleet:
            # Check if all needed parameters are available
            if self.smoothing:
                if (self.standard_deviation_method == 'turbulence_intensity'
                        and 'turbulence_intensity' not in kwargs):
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
                            "`standard_deviation_method`")
            if self. density_correction:
                pass # TODO: any restrictions? density needed
            if self.wake_losses_method is not None:
                if self.wind_object.efficiency is None: # TODO if not...
                    raise KeyError(
                        "wind_farm_efficiency is needed if " +
                        "`wake_losses_method´ is '{0}', but ".format(
                            self.wake_losses_method) +
                        " `wind_farm_efficiency` of {0} is {1}.".format(
                            self.wind_object.object_name,
                            self.wind_object.efficiency))
            # Get original power curve
            power_curve = pd.DataFrame(
                turbine_type_dict['wind_turbine'].power_curve)
            # Editions to power curve before the summation
            if (self.density_correction and
                    self.density_correction_order == 'turbine_power_curves'):
                pass # TODO: add density correction
            if (self.smoothing and
                    self.smoothing_order == 'turbine_power_curves'):
                power_curve = power_output.smooth_power_curve(
                    power_curve['wind_speed'], power_curve['power'], **kwargs)
            # Add power curves of all turbines of same type to data frame after
            # renaming columns
            power_curve.columns = ['wind_speed', turbine_type_dict[
                'wind_turbine'].object_name]
            df = pd.concat([df, pd.DataFrame(
                power_curve.set_index(['wind_speed']) *
                turbine_type_dict['number_of_turbines'])], axis=1)
            # Rename back TODO: copy()
            power_curve.columns = ['wind_speed', 'power']
        # Sum up power curves of all turbine types
        summarized_power_curve = pd.DataFrame(
            sum(df[item].interpolate(method='index') for item in list(df)))
        summarized_power_curve.columns = ['power']
        # Return wind speed (index) to a column of the data frame
        summarized_power_curve_df = pd.DataFrame(
            data=[list(summarized_power_curve.index),
                  list(summarized_power_curve['power'].values)]).transpose()
        summarized_power_curve_df.columns = ['wind_speed', 'power']
        # Editions to power curve after the summation
        if (self.density_correction and
                self.density_correction_order == 'wind_farm_power_curves'):
            pass # TODO: add density correction
        if (self.smoothing and
                self.smoothing_order == 'wind_farm_power_curves'):
            summarized_power_curve_df = power_output.smooth_power_curve(
                summarized_power_curve_df['wind_speed'],
                summarized_power_curve_df['power'], **kwargs)
        if (self.wake_losses_method == 'constant_efficiency' or
                self.wake_losses_method == 'wind_efficiency_curve'):
            summarized_power_curve_df = (
                power_output.wake_losses_to_power_curve(
                    summarized_power_curve_df['wind_speed'].values,
                    summarized_power_curve_df['power'].values,
                    wake_losses_method=self.wake_losses_method,
                    wind_farm_efficiency=self.wind_object.efficiency))
        self.wind_object.power_curve = summarized_power_curve_df
        return self

    def get_modelchain_data(self, **kwargs):
        modelchain_data = {}
        if 'wind_speed_model' in kwargs:
            modelchain_data['wind_speed_model'] = kwargs[
                'wind_speed_model']
        if 'temperature_model' in kwargs:
            modelchain_data['temperature_model'] = kwargs[
                'temperature_model']
        if 'density_model' in kwargs:
            modelchain_data['density_model'] = kwargs[
                'density_model']
        if 'power_output_model' in kwargs:
            modelchain_data['power_output_model'] = kwargs[
                'power_output_model']
        if 'density_correction' in kwargs:
            modelchain_data['density_correction'] = kwargs[
                'density_correction']
        if 'obstacle_height' in kwargs:
            modelchain_data['obstacle_height'] = kwargs[
                'obstacle_height']
        if 'hellman_exp' in kwargs:
            modelchain_data['hellman_exp'] = kwargs[
                'hellman_exp']
        return modelchain_data

    def run_model(self, weather_df, **kwargs):
        r"""
        Runs the model.

        Parameters
        ----------
        weather_df : pandas.DataFrame
            DataFrame with time series for wind speed `wind_speed` in m/s, and
            roughness length `roughness_length` in m, as well as optionally
            temperature `temperature` in K, pressure `pressure` in Pa and
            density `density` in kg/m³ depending on `power_output_model` and
            `density_model chosen`.
            The columns of the DataFrame are a MultiIndex where the first level
            contains the variable name (e.g. wind_speed) and the second level
            contains the height at which it applies (e.g. 10, if it was
            measured at a height of 10 m). See below for an example on how to
            create the weather_df DataFrame.

        Other Parameters
        ----------------
        wind_speed_model : string
            Parameter to define which model to use to calculate the wind speed
            at hub height. Valid options are 'logarithmic', 'hellman' and
            'interpolation_extrapolation'.
        temperature_model : string
            Parameter to define which model to use to calculate the temperature
            of air at hub height. Valid options are 'linear_gradient' and
            'interpolation_extrapolation'.
        density_model : string
            Parameter to define which model to use to calculate the density of
            air at hub height. Valid options are 'barometric', 'ideal_gas' and
            'interpolation_extrapolation'.
        power_output_model : string
            Parameter to define which model to use to calculate the turbine
            power output. Valid options are 'power_curve' and
            'power_coefficient_curve'.
        density_correction : boolean
            If the parameter is True the density corrected power curve is used
            for the calculation of the turbine power output.
        obstacle_height : float
            Height of obstacles in the surrounding area of the wind turbine in
            m. Set `obstacle_height` to zero for wide spread obstacles.
        hellman_exp : float
            The Hellman exponent, which combines the increase in wind speed due
            to stability of atmospheric conditions and surface roughness into
            one constant.
        roughness_length : Float, optional.
            Roughness length.
        turbulence_intensity : Float, optional.
            Turbulence intensity.

        Returns
        -------
        self

        Examples
        ---------
        >>> import numpy as np
        >>> import pandas as pd
        >>> weather_df = pd.DataFrame(np.random.rand(2,6),
        ...                           index=pd.date_range('1/1/2012',
        ...                                               periods=2,
        ...                                               freq='H'),
        ...                           columns=[np.array(['wind_speed',
        ...                                              'wind_speed',
        ...                                              'temperature',
        ...                                              'temperature',
        ...                                              'pressure',
        ...                                              'roughness_length']),
        ...                                    np.array([10, 80, 10, 80,
        ...                                             10, 0])])
        >>> weather_df.columns.get_level_values(0)[0]
        'wind_speed'

        """
        if isinstance(self.wind_object, wind_farm.WindFarm):
            # Assign mean hub height to wind farm
            self.wind_object.mean_hub_height()
            # Assign wind farm power curve to wind farm
            self.wind_farm_power_curve(**kwargs)
        if isinstance(self.wind_object,
                      wind_turbine_cluster.WindTurbineCluster):
            pass
        # Get modelchain parameters
        modelchain_data = self.get_modelchain_data(**kwargs)
        # Run modelchain
        mc = modelchain.ModelChain(
            self.wind_object, **modelchain_data).run_model(weather_df)
        self.power_output = mc.power_output
        return self
