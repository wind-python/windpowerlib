.. currentmodule:: windpowerlib

#############
API
#############

Classes
=========

.. autosummary::
   :toctree: temp/

   wind_turbine.WindTurbine
   wind_farm.WindFarm
   wind_turbine_cluster.WindTurbineCluster
   modelchain.ModelChain
   turbine_cluster_modelchain.TurbineClusterModelChain


Temperature
==============

Function for calculating air temperature at hub height.

.. autosummary::
   :toctree: temp/

   temperature.linear_gradient

Density
==============

Functions for calculating air density at hub height.

.. autosummary::
   :toctree: temp/

   density.barometric
   density.ideal_gas
  

Wind speed
==============

Functions for calculating wind speed at hub height.

.. autosummary::
   :toctree: temp/

   wind_speed.logarithmic_profile
   wind_speed.hellman
   

Wind turbine data
====================

Functions and methods to obtain the nominal power as well as 
power curve or power coefficient curve needed by the :py:class:`~wind_turbine.WindTurbine` class.


.. autosummary::
   :toctree: temp/

   wind_turbine.WindTurbine.fetch_turbine_data
   wind_turbine.get_turbine_types
   wind_turbine.read_turbine_data


Power output
==============

Functions for calculating power output of a wind turbine.

.. autosummary::
   :toctree: temp/

   power_output.power_coefficient_curve
   power_output.power_curve
   power_output.power_curve_density_correction


Alteration of power curves
==============

Functions for smoothing power curves or applying wake losses.

.. autosummary::
   :toctree: temp/

   power_curves.smooth_power_curve
   power_curves.wake_losses_to_power_curve


ModelChain
==============

Creating a ModelChain object.

.. autosummary::
   :toctree: temp/

   modelchain.ModelChain

Running the ModelChain.

.. autosummary::
   :toctree: temp/

   modelchain.ModelChain.run_model

Methods of the ModelChain object.

.. autosummary::
   :toctree: temp/

   modelchain.ModelChain.temperature_hub
   modelchain.ModelChain.density_hub
   modelchain.ModelChain.wind_speed_hub
   modelchain.ModelChain.turbine_power_output


TurbineClusterModelChain
==============
The TurbineClusterModelChain inherits all functions from the ModelChain.

Creating a TurbineClusterModelChain object.

.. autosummary::
   :toctree: temp/

   turbine_cluster_modelchain.TurbineClusterModelChain

Running the TurbineClusterModelChain.

.. autosummary::
   :toctree: temp/

   turbine_cluster_modelchain.TurbineClusterModelChain.run_model

Methods of the TurbineClusterModelChain object.

.. autosummary::
   :toctree: temp/

   turbine_cluster_modelchain.TurbineClusterModelChain.temperature_hub
   turbine_cluster_modelchain.TurbineClusterModelChain.density_hub
   turbine_cluster_modelchain.TurbineClusterModelChain.wind_speed_hub
   turbine_cluster_modelchain.TurbineClusterModelChain.turbine_power_output


Tools
==============

Additional functions used in the windpowerlib.

.. autosummary::
   :toctree: temp/

   tools.linear_interpolation_extrapolation
   tools.logarithmic_interpolation_extrapolation
   tools.gauss_distribution
   tools.estimate_turbulence_intensity


Example
==============

The basic example consists of the following functions.

.. include:: example.rst
