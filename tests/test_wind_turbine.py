"""
Testing the wind_turbine module.
"""

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"

import pytest
import os
from windpowerlib.tools import WindpowerlibUserWarning

from windpowerlib.wind_turbine import (get_turbine_data_from_file, WindTurbine,
                                       get_turbine_types,
                                       load_turbine_data_from_oedb)


class TestWindTurbine:

    def test_warning(self, recwarn):
        source = os.path.join(os.path.dirname(__file__), '../example/data')
        test_turbine_data = {'hub_height': 100,
                             'rotor_diameter': 80,
                             'turbine_type': 'turbine_not_in_file',
                             'path': source}
        assert(WindTurbine(**test_turbine_data).power_curve is None)
        assert recwarn.pop(WindpowerlibUserWarning)

    def test_get_turbine_data_from_file(self):
        # Raise FileNotFoundError due to missing
        with pytest.raises(FileNotFoundError):
            get_turbine_data_from_file(turbine_type='...',
                                       path='not_existent')

    def test_get_turbine_types(self, capsys):
        get_turbine_types()
        captured = capsys.readouterr()
        assert 'Enercon' in captured.out
        get_turbine_types('oedb', print_out=False, filter_=False)
        msg = "`turbine_library` is 'wrong' but must be 'local' or 'oedb'."
        with pytest.raises(ValueError, match=msg):
            get_turbine_types('wrong')

    def test_wrong_url_load_turbine_data(self):
        """Load turbine data from oedb."""
        with pytest.raises(ConnectionError,
                           match="Database connection not successful"):
            load_turbine_data_from_oedb('wrong_schema')

    @pytest.mark.filterwarnings("ignore:The WindTurbine")
    def test_string_representation_of_wind_turbine(self):
        assert "Wind turbine: ['hub height=120 m'" in repr(WindTurbine(120))

    def test_power_curve_is_of_wrong_type(self):
        """Error raising due to wrong type of WindTurbine.power_curve."""
        test_turbine_data = {'hub_height': 100,
                             'rotor_diameter': 80,
                             'turbine_type': 'test_type',
                             'power_curve': 'string'}
        with pytest.raises(TypeError):
            WindTurbine(**test_turbine_data)

    def test_power_coefficient_curve_is_of_wrong_type(self):
        """Error raising due to wrong type of
        WindTurbine.power_coefficient_curve."""
        test_turbine_data = {'hub_height': 100,
                             'rotor_diameter': 80,
                             'turbine_type': 'test_type',
                             'power_coefficient_curve': 'string'}
        with pytest.raises(TypeError):
            WindTurbine(**test_turbine_data)