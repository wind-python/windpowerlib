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


Density
==============

Functions for calculating air density at hub height.

.. autosummary::
   :toctree: temp/

   density.temperature_gradient
   density.temperature_interpol
   density.rho_barometric
   density.rho_ideal_gas
   

Wind speed
==============

Functions for calculating wind speed at hub height.

.. autosummary::
   :toctree: temp/

   wind_speed.logarithmic_wind_profile
   wind_speed.v_wind_hellman
   

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

   power_output.cp_curve
   power_output.cp_curve_density_corr
   power_output.p_curve
   power_output.p_curve_density_corr


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

   modelchain.ModelChain.rho_hub
   modelchain.ModelChain.v_wind_hub
   modelchain.ModelChain.turbine_power_output


Tools
==============

Additional functions used in the windpowerlib.

.. autosummary::
   :toctree: temp/

   tools.smallest_difference


Example
==============

The basic example consists of the following functions.

.. include:: example.rst
