"""
The ``turbine_cluster_modelchain_example`` module shows how to calculate the
power output of wind farms and wind turbine clusters with the windpowerlib.
A cluster can be useful if you want to calculate the feed-in of a region for
which you want to use one single weather data point.

Functions that are used in the ``modelchain_example``, like the initialization
of wind turbines, are imported and used without further explanations.

"""

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"

try:
    from matplotlib import pyplot as plt
except ImportError:
    plt = None

from example import modelchain_example as mc_e
from windpowerlib import WindFarm
from windpowerlib import WindTurbineCluster
from windpowerlib import TurbineClusterModelChain

# You can use the logging package to get logging messages from the windpowerlib
# Change the logging level if you want more or less messages
import logging
logging.getLogger().setLevel(logging.DEBUG)


def initialize_wind_farms(my_turbine, e126):
    r"""
    Initializes two :class:`~.wind_farm.WindFarm` objects.

    This function shows how to initialize a WindFarm object. You need to
    provide at least a name and a the wind farm's wind turbine fleet as done
    below for 'example_farm'. Optionally you can provide a wind farm efficiency
    (which can be constant or dependent on the wind speed) and coordinates as
    done for 'example_farm_2'. In this example the coordinates are not being
    used as just a single weather data set is provided as example data.

    Parameters
    ----------
    my_turbine : WindTurbine
        WindTurbine object with self provided power curve.
    e126 : WindTurbine
        WindTurbine object with power curve from data file provided by the
        windpowerlib.

    Returns
    -------
    Tuple (WindFarm, WindFarm)

    """

    # specification of wind farm data
    example_farm_data = {
        'name': 'example_farm',
        'wind_turbine_fleet': [{'wind_turbine': my_turbine,
                                'number_of_turbines': 6},
                               {'wind_turbine': e126,
                                'number_of_turbines': 3}
                               ]}

    # initialize WindFarm object
    example_farm = WindFarm(**example_farm_data)

    # specification of wind farm data (2) containing a wind farm efficiency
    # and coordinates
    example_farm_2_data = {
        'name': 'example_farm_2',
        'wind_turbine_fleet': [{'wind_turbine': my_turbine,
                                'number_of_turbines': 6},
                               {'wind_turbine': e126,
                                'number_of_turbines': 3}],
        'efficiency': 0.9,
        'coordinates': [52.2, 13.1]}

    # initialize WindFarm object
    example_farm_2 = WindFarm(**example_farm_2_data)

    return example_farm, example_farm_2


def initialize_wind_turbine_cluster(example_farm, example_farm_2):
    r"""
    Initializes a :class:`~.wind_turbine_cluster.WindTurbineCluster` object.

    Function shows how to initialize a WindTurbineCluster object. In this case
    the cluster only contains two wind farms.

    Parameters
    ----------
    example_farm : WindFarm
        WindFarm object.
    example_farm_2 : WindFarm
        WindFarm object constant wind farm efficiency and coordinates.

    Returns
    -------
    WindTurbineCluster

    """

    # specification of cluster data
    example_cluster_data = {
        'name': 'example_cluster',
        'wind_farms': [example_farm, example_farm_2]}

    # initialize WindTurbineCluster object
    example_cluster = WindTurbineCluster(**example_cluster_data)

    return example_cluster


def calculate_power_output(weather, example_farm, example_cluster):
    r"""
    Calculates power output of wind farms and clusters using the
    :class:`~.turbine_cluster_modelchain.TurbineClusterModelChain`.

    The :class:`~.turbine_cluster_modelchain.TurbineClusterModelChain` is a
    class that provides all necessary steps to calculate the power output of a
    wind farm or cluster. You can either use the default methods for the
    calculation steps, as done for 'example_farm', or choose different methods,
    as done for 'example_cluster'.

    Parameters
    ----------
    weather : pd.DataFrame
        Contains weather data time series.
    example_farm : WindFarm
        WindFarm object.
    example_farm_2 : WindFarm
        WindFarm object constant wind farm efficiency and coordinates.

    """

    # set efficiency of example_farm to apply wake losses
    example_farm.efficiency = 0.9
    # power output calculation for example_farm
    # initialize TurbineClusterModelChain with default parameters and use
    # run_model method to calculate power output
    mc_example_farm = TurbineClusterModelChain(example_farm).run_model(weather)
    # write power output time series to WindFarm object
    example_farm.power_output = mc_example_farm.power_output

    # power output calculation for turbine_cluster
    # own specifications for TurbineClusterModelChain setup
    modelchain_data = {
        'wake_losses_model': 'constant_efficiency',  #
                                           # 'dena_mean' (default), None,
                                           # 'power_efficiency_curve',
                                           # 'constant_efficiency' or name of
                                           #  a wind efficiency curve
                #  see :py:func:`~.wake_losses.display_wind_efficiency_curves`
        'smoothing': True,  # False (default) or True
        'block_width': 0.5,  # default: 0.5
        'standard_deviation_method': 'Staffell_Pfenninger',  #
                                            # 'turbulence_intensity' (default)
                                            # or 'Staffell_Pfenninger'
        'smoothing_order': 'wind_farm_power_curves',  #
                                        # 'wind_farm_power_curves' (default) or
                                        # 'turbine_power_curves'
        'wind_speed_model': 'logarithmic',  # 'logarithmic' (default),
                                            # 'hellman' or
                                            # 'interpolation_extrapolation'
        'density_model': 'ideal_gas',  # 'barometric' (default), 'ideal_gas' or
                                       # 'interpolation_extrapolation'
        'temperature_model': 'linear_gradient',  # 'linear_gradient' (def.) or
                                                 # 'interpolation_extrapolation'
        'power_output_model': 'power_curve',  # 'power_curve' (default) or
                                              # 'power_coefficient_curve'
        'density_correction': True,  # False (default) or True
        'obstacle_height': 0,  # default: 0
        'hellman_exp': None}  # None (default) or None
    # initialize TurbineClusterModelChain with own specifications and use
    # run_model method to calculate power output
    mc_example_cluster = TurbineClusterModelChain(
            example_cluster, **modelchain_data).run_model(weather)
    # write power output time series to WindTurbineCluster object
    example_cluster.power_output = mc_example_cluster.power_output

    return


def plot_or_print(example_farm, example_cluster):
    r"""
    Plots or prints power output and power (coefficient) curves.

    Parameters
    ----------
    example_farm : WindFarm
        WindFarm object.
    example_farm_2 : WindFarm
        WindFarm object constant wind farm efficiency and coordinates.

    """

    # plot or print power output
    if plt:
        example_cluster.power_output.plot(legend=True, label='example cluster')
        example_farm.power_output.plot(legend=True, label='example farm')
        plt.show()
    else:
        print(example_cluster.power_output)
        print(example_farm.power_output)


def run_example():
    r"""
    Run the example.

    """
    weather = mc_e.get_weather_data('weather.csv')
    my_turbine, e126 = mc_e.initialize_wind_turbines()
    example_farm, example_farm_2 = initialize_wind_farms(my_turbine, e126)
    example_cluster = initialize_wind_turbine_cluster(example_farm,
                                                      example_farm_2)
    calculate_power_output(weather, example_farm, example_cluster)
    plot_or_print(example_farm, example_cluster)


if __name__ == "__main__":
    run_example()
