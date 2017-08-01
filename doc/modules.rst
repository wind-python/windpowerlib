.. currentmodule:: windpowerlib

#############
API
#############

Classes
=========

.. autosummary::
   :toctree: temp/

   wind_turbine.WindTurbine
   modelchain.ModelChain


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


Tools
==============

Additional functions used in the windpowerlib.

.. autosummary::
   :toctree: temp/

   tools.linear_interpolation_extrapolation


Example
==============

The basic example consists of the following functions.

.. include:: example.rst
