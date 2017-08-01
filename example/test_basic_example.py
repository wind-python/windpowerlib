from example import basic_example as be
from numpy.testing import assert_allclose


class TestExamples:

    def test_basic_example_flh(self):
        # tests full load hours
        weather = be.get_weather_data('weather.csv')
        my_turbine, e126 = be.initialise_wind_turbines()
        be.calculate_power_output(weather, my_turbine, e126)

        assert_allclose(1766.6870, (e126.power_output.sum() /
                                    e126.nominal_power), 0.01)
        assert_allclose(1882.7567, (my_turbine.power_output.sum() /
                                        my_turbine.nominal_power), 0.01)