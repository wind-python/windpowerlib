.. currentmodule:: windpowerlib


Classes
=========

.. autosummary::
   :toctree: temp/

   wind_turbine.WindTurbine
   modelchain.Modelchain


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

   wind_turbine.WindTurbine.fetch_wpp_data
   wind_turbine.get_wind_pp_types
   wind_turbine.read_wpp_data


Power output
==============

Functions for calculating power output of a wind turbine.

.. autosummary::
   :toctree: temp/

   power_output.cp_curve
   power_output.cp_curve_density_corr
   power_output.p_curve
   power_output.p_curve_density_corr


Modelchain
==============

Creating a Modelchain object.

.. autosummary::
   :toctree: temp/

   modelchain.Modelchain

Running the modelchain.

.. autosummary::
   :toctree: temp/

   modelchain.Modelchain.run_model

Methods of the Modelchain object.

.. autosummary::
   :toctree: temp/

   modelchain.Modelchain.rho_hub
   modelchain.Modelchain.v_wind_hub
   modelchain.Modelchain.turbine_power_output
   modelchain.Modelchain.read_weather_data