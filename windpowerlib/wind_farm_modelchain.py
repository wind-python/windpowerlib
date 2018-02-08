"""
The ``wind_farm_modelchain`` module contains functions and classes of the
windpowerlib. This module makes it easy to get started with the windpowerlib
and demonstrates standard ways to use the library. TODO: adapt

"""

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"

import logging
from . import modelchain, power_output, tools


class WindFarmModelChain(object):
    r"""
    Model to determine the output of a wind farm or wind turbine cluster.

    Parameters
    ----------

    Attributes
    ----------

    """
    def __init__(self, wind_farm, cluster=False, density_correction=False,
                 wake_losses=False, smoothing=True, block_width=0.5,
                 standard_deviation_method='turbulence_intensity',
                 turbulence_intensity=None, roughness_length=None):

        self.wind_farm = wind_farm
        self.cluster = cluster
        self.density_correction = density_correction
        self.wake_losses = wake_losses
        self.smoothing = smoothing
        self.block_width = block_width
        self.standard_deviation_method = standard_deviation_method
        self.turbulence_intensity = turbulence_intensity
        self.roughness_length = roughness_length

    def give_name():
        r"""


        """
        

    def run_model(weather_df):
        r"""
        Runs the model.

        """
