"""
SPDX-FileCopyrightText: 2019 oemof developer group <contact@oemof.org>
SPDX-License-Identifier: MIT
"""

import filecmp
import os
from shutil import copyfile

import pandas as pd
import pytest
from windpowerlib.data import (
    check_data_integrity,
    check_turbine_data,
    get_turbine_types,
    restore_default_turbine_data,
    store_turbine_data_from_oedb,
)


class TestDataCheck:
    @classmethod
    def setup_class(cls):
        cls.path = os.path.join(os.path.dirname(__file__), "oedb")
        cls.filename = os.path.join(cls.path, "{0}.csv")
        cls.df = pd.read_csv(cls.filename.format("turbine_data"), index_col=0)
        cls.broken_fn = os.path.join(cls.path, "{0}_broken.csv")
        cls.backup_fn = os.path.join(cls.path, "{0}_backup.csv")
        cls.tmp_fn = os.path.join(cls.path, "{0}_tmp.csv")
        cls.orig_path = os.path.join(
            os.path.dirname(__file__), os.pardir, "windpowerlib", "oedb"
        )
        cls.orig_fn = os.path.join(cls.orig_path, "{0}.csv")

    @classmethod
    def teardown_class(cls):
        cls.path = os.path.join(os.path.dirname(__file__), "oedb")
        for f in os.listdir(cls.path):
            if "error" in f or "backup" in f or "tmp" in f:
                os.remove(os.path.join(cls.path, f))
        restore_default_turbine_data()

    def test_normal_data_check(self):
        check_turbine_data(self.filename.format("turbine_data"))

    def test_data_check_logging_warnings(self, caplog):
        self.df.loc["GE158/4800", "has_power_curve"] = True
        self.df.loc["GE100/2750", "has_cp_curve"] = True
        self.df.to_csv(self.tmp_fn.format("turbine_data"))
        check_data_integrity(self.tmp_fn, min_pc_length=26)
        assert "E48/800: power_curve is too short (25 values)" in caplog.text
        assert "GE158/4800: No power curve" in caplog.text
        assert "GE100/2750: No cp-curve but has_cp_curve" in caplog.text

    def test_global_error(self):
        msg = r"could not convert string to*"
        name = "turbine_data"
        copyfile(self.orig_fn.format(name), self.backup_fn.format(name))
        copyfile(self.broken_fn.format(name), self.orig_fn.format(name))
        with pytest.raises(ValueError, match=msg):
            check_turbine_data(self.orig_fn)
        copyfile(self.backup_fn.format(name), self.orig_fn.format(name))

    def test_broken_pwr_curve(self):
        name = "power_curves"
        copyfile(self.orig_fn.format(name), self.backup_fn.format(name))
        copyfile(self.broken_fn.format(name), self.orig_fn.format(name))
        msg = "could not convert string to float"
        with pytest.raises(ValueError, match=msg):
            check_turbine_data(self.orig_fn)
        copyfile(self.backup_fn.format(name), self.orig_fn.format(name))

    def test_get_turbine_types(self, capsys):
        get_turbine_types()
        captured = capsys.readouterr()
        assert "Enercon" in captured.out
        get_turbine_types("oedb", print_out=False, filter_=False)
        msg = "`turbine_library` is 'wrong' but must be 'local' or 'oedb'."
        with pytest.raises(ValueError, match=msg):
            get_turbine_types("wrong")

    def test_store_turbine_data_from_oedb(self):
        t = {}
        for fn in os.listdir(self.orig_path):
            t[fn] = os.path.getmtime(os.path.join(self.orig_path, fn))
        store_turbine_data_from_oedb()
        for fn in os.listdir(self.orig_path):
            assert t[fn] < os.path.getmtime(os.path.join(self.orig_path, fn))

    def test_wrong_url_load_turbine_data(self):
        """Load turbine data from oedb."""
        with pytest.raises(
            ConnectionError,
            match=r"Database \(oep\) connection not successful*",
        ):
            store_turbine_data_from_oedb("wrong_schema")

    def test_restore_default_data(self):
        names = ["turbine_data", "power_curves", "power_coefficient_curves"]
        default_path = os.path.join(
            self.orig_path, os.pardir, "data", "default_turbine_data"
        )
        for name in names:
            copyfile(self.broken_fn.format(name), self.orig_fn.format(name))
            file = self.orig_fn.format(name)
            default_file = os.path.join(
                default_path, os.path.basename(self.orig_fn.format(name))
            )
            assert not filecmp.cmp(file, default_file)
        restore_default_turbine_data()
        for name in names:
            file = self.orig_fn.format(name)
            default_file = os.path.join(
                default_path, os.path.basename(self.orig_fn.format(name))
            )
            assert filecmp.cmp(file, default_file)
