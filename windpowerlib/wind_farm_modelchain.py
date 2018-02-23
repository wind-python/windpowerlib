"""
The ``wind_farm_modelchain`` module contains functions and classes of the
windpowerlib. This module makes it easy to get started with the windpowerlib
and demonstrates standard ways to use the library. TODO: adapt

"""

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"

from . import modelchain, power_output


class WindFarmModelChain(object):
    r"""
    Model to determine the output of a wind farm or wind turbine cluster.

    Parameters
    ----------
    wind_farm :
        TODO: add to docstring
    cluster : Boolean

    density_correction : Boolean
        If True a density correction will be applied to the power curves
        before the summation. Default: False.
    wake_losses : Boolean
        If True wake losses within the farm are taken into consideration.
        Default: False.
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

    """
    def __init__(self, wind_farm, cluster=False, density_correction=False,
                 wake_losses=False, smoothing=True, block_width=0.5,
                 standard_deviation_method='turbulence_intensity'):

        self.wind_farm = wind_farm
        self.cluster = cluster
        self.density_correction = density_correction
        self.wake_losses = wake_losses
        self.smoothing = smoothing
        self.block_width = block_width
        self.standard_deviation_method = standard_deviation_method

        self.power_output = None

    def wind_farm_power_curve(self, **kwargs):
        r"""
        Caluclates the power curve of the wind farm.

        Other Parameters
        ----------------
        weather_df : pd.DataFrame
            TODO: add to docstring

        Returns
        -------
        self

        """
        # Create kwargs
        try:
            kwargs['turbulence_intensity'] = (
                kwargs['weather_df']['turbulence_intensity'][
                    self.wind_farm.hub_height])
        except Exception:
            pass # TODO other solution (weather[] is..)
        try:
            kwargs['roughness_length'] = (
                kwargs['weather_df']['roughness_length']).mean()[0]
        except Exception:
            pass # TODO other solution
        # Calculate power curve
        self.wind_farm.power_curve = power_output.summarized_power_curve(
            self.wind_farm.wind_turbine_fleet, smoothing=self.smoothing,
            density_correction=self.density_correction,
            wake_losses=self.wake_losses, block_width=self.block_width,
            standard_deviation_method=self.standard_deviation_method, **kwargs)
        return self

    def run_model(self, weather_df):
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
        # Assign mean hub height of wind farm
        self.wind_farm.mean_hub_height()
        # Assign wind farm power curve to wind farm
        self.wind_farm_power_curve(weather_df=weather_df)
        # Run modelchain
        mc = modelchain.ModelChain(self.wind_farm).run_model(weather_df)
        self.power_output = mc.power_output
        return self
