"""
SPDX-FileCopyrightText: 2019 oemof developer group <contact@oemof.org>
SPDX-License-Identifier: MIT
"""

import os
import time
from datetime import datetime
from shutil import copyfile

import pandas as pd
import pytest

from windpowerlib.data import (
    check_data_integrity, check_imported_data, get_turbine_types,
    store_turbine_data_from_oedb)


class TestDataCheck:
    @classmethod
    def setup_class(cls):
        cls.path = os.path.join(os.path.dirname(__file__), "oedb")
        cls.filename = os.path.join(cls.path, "{0}.csv")
        cls.df = pd.read_csv(cls.filename.format("turbine_data"), index_col=0)
        cls.time_stamp = datetime.now().strftime("%Y%m%d%H%M%S")
        cls.broken_fn = os.path.join(cls.path, "power_curves_broken.csv")
        cls.backup_fn = os.path.join(cls.path, "power_curves_backup.csv")
        cls.orig_path = os.path.join(
            os.path.dirname(__file__), os.pardir, "windpowerlib", "oedb"
        )
        cls.orig_fn = os.path.join(cls.orig_path, "power_curves.csv")

    @classmethod
    def teardown_class(cls):
        cls.path = os.path.join(os.path.dirname(__file__), "oedb")
        cls.backup_fn = os.path.join(cls.path, "power_curves_backup.csv")
        orig_path = os.path.join(
            os.path.dirname(__file__), os.pardir, "windpowerlib", "oedb"
        )
        cls.orig_fn = os.path.join(orig_path, "power_curves.csv")
        copyfile(cls.backup_fn, cls.orig_fn)
        for f in os.listdir(cls.path):
            if "error" in f:
                os.remove(os.path.join(cls.path, f))

    def test_normal_data_check(self):
        copyfile(
            self.filename.format("turbine_data"),
            self.filename.format("turbine_data_{0}".format(self.time_stamp)),
        )
        for curve_type in ["power_curve", "power_coefficient_curve"]:
            copyfile(
                self.filename.format("{}s".format(curve_type)),
                self.filename.format(
                    "{0}s_{1}".format(curve_type, self.time_stamp)
                ),
            )
        check_imported_data(self.df, self.filename, self.time_stamp)

    def test_data_check_logging_warnings(self, caplog):
        self.df.loc["GE158/4800", "has_power_curve"] = True
        self.df.loc["GE100/2750", "has_cp_curve"] = True
        check_data_integrity(self.df, min_pc_length=26)
        assert "E48/800: power_curve is to short (25 values)" in caplog.text
        assert "GE158/4800: No power curve" in caplog.text
        assert "GE100/2750: No cp-curve but has_cp_curve" in caplog.text

    def test_global_error(self):
        msg = "Must have equal len keys"
        with pytest.raises(ValueError, match=msg):
            self.df.loc["GE158/4800", "has_cp_curve"] = [5, 3]
            check_imported_data(self.df, self.filename, self.time_stamp)

    def test_broken_pwr_curve(self):
        copyfile(self.orig_fn, self.backup_fn)
        copyfile(self.broken_fn, self.orig_fn)
        msg = "could not convert string to float"
        with pytest.raises(ValueError, match=msg):
            check_imported_data(self.df, self.filename, self.time_stamp)

    def test_get_turbine_types(self, capsys):
        get_turbine_types()
        captured = capsys.readouterr()
        assert "Enercon" in captured.out
        get_turbine_types("oedb", print_out=False, filter_=False)
        msg = "`turbine_library` is 'wrong' but must be 'local' or 'oedb'."
        with pytest.raises(ValueError, match=msg):
            get_turbine_types("wrong")

    def test_store_turbine_data_from_oedb(self):
        store_turbine_data_from_oedb()

    def test_wrong_url_load_turbine_data(self):
        """Load turbine data from oedb."""
        with pytest.raises(
            ConnectionError, match="Database connection not successful"
        ):
            store_turbine_data_from_oedb("wrong_schema")
