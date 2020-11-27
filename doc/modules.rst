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

.. _temperature_module_label:

Temperature
==============

Function for calculating air temperature at hub height.

.. autosummary::
   :toctree: temp/

   temperature.linear_gradient

.. _density_module_label:

Density
==============

Functions for calculating air density at hub height.

.. autosummary::
   :toctree: temp/

   density.barometric
   density.ideal_gas
  
.. _windspeedmodule-label:

Wind speed
==============

Functions for calculating wind speed at hub height.

.. autosummary::
   :toctree: temp/

   wind_speed.logarithmic_profile
   wind_speed.hellman
   
.. _wind_turbine_label:

Wind turbine data
====================

Functions and methods to obtain the nominal power as well as 
power curve or power coefficient curve needed by the :py:class:`~.wind_turbine.WindTurbine` class.

.. autosummary::
   :toctree: temp/

   wind_turbine.get_turbine_data_from_file
   data.store_turbine_data_from_oedb
   data.get_turbine_types

.. _create_input_types_label:

Data Container
=====================

Create data container to be used as an input in classes und functions.

.. autosummary::
   :toctree: temp/

   wind_turbine.WindTurbineGroup
   wind_turbine.WindTurbine.to_group

.. _wind_farm_label:

Wind farm calculations
======================

Functions and methods to calculate the mean hub height, installed power as well
as the aggregated power curve of a :py:class:`~.wind_farm.WindFarm` object.


.. autosummary::
   :toctree: temp/

   wind_farm.WindFarm.check_and_complete_wind_turbine_fleet
   wind_farm.WindFarm.nominal_power
   wind_farm.WindFarm.mean_hub_height
   wind_farm.WindFarm.assign_power_curve

.. _wind_turbine_cluster_label:

Wind turbine cluster calculations
=================================

Functions and methods to calculate the mean hub height, nominal power as well
as the aggregated power curve of a :py:class:`~.wind_turbine_cluster.WindTurbineCluster` object.
This is realized in a new module as the functions differ from the functions in
the :py:class:`~.wind_farm.WindFarm` class.

.. autosummary::
   :toctree: temp/

   wind_turbine_cluster.WindTurbineCluster.nominal_power
   wind_turbine_cluster.WindTurbineCluster.mean_hub_height
   wind_turbine_cluster.WindTurbineCluster.assign_power_curve

.. _poweroutput_module_label:

Power output
==============

Functions for calculating power output of a wind power plant.

.. autosummary::
   :toctree: temp/

   power_output.power_coefficient_curve
   power_output.power_curve
   power_output.power_curve_density_correction


Alteration of power curves
==========================

Functions for smoothing power curves or applying wake losses to a power curve.

.. autosummary::
   :toctree: temp/

   power_curves.smooth_power_curve
   power_curves.wake_losses_to_power_curve
   power_curves.create_power_curve


Wake losses
===========

Functions for applying wake losses to a wind speed time series.

.. autosummary::
   :toctree: temp/

   wake_losses.reduce_wind_speed
   wake_losses.get_wind_efficiency_curve

.. _modelchain_module_label:

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
   modelchain.ModelChain.calculate_power_output

.. _tc_modelchain_module_label:

TurbineClusterModelChain
========================
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

   turbine_cluster_modelchain.TurbineClusterModelChain.assign_power_curve
   turbine_cluster_modelchain.TurbineClusterModelChain.temperature_hub
   turbine_cluster_modelchain.TurbineClusterModelChain.density_hub
   turbine_cluster_modelchain.TurbineClusterModelChain.wind_speed_hub
   turbine_cluster_modelchain.TurbineClusterModelChain.calculate_power_output


.. _tools_module_label:

Tools
==============

Additional functions used in the windpowerlib.

.. autosummary::
   :toctree: temp/

   tools.linear_interpolation_extrapolation
   tools.logarithmic_interpolation_extrapolation
   tools.gauss_distribution
   tools.estimate_turbulence_intensity


ModelChain example
==================

The ``modelchain_example`` consists of the following functions.

.. include:: example.rst

TurbineClusterModelChain example
================================

The ``turbine_cluster_modelchain_example`` consists of the following functions
as well as it uses functions of the ``modelchain_example``.

.. include:: example_2.rst
