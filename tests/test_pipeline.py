import numpy as np
import pandas as pd
import pytest

from src.data import load_clean
from src.demo import make_demo
from src.features import make_features, make_target, source_apportionment


@pytest.fixture(scope="module")
def df(tmp_path_factory):
    p = tmp_path_factory.mktemp("d") / "demo.csv"
    make_demo(str(p), years=0.5, seed=1)
    d, _ = load_clean(str(p))
    return d


def test_grid_is_regular(df):
    assert (df.index.to_series().diff().dropna() == pd.Timedelta("15min")).all()


def test_no_future_leakage_in_features(df):
    """Altering BC6 after time t0 must not change any feature at or before t0."""
    t0 = df.index[len(df) // 2]
    a = make_features(df, use_bc_history=True)
    d2 = df.copy()
    d2.loc[d2.index > t0, ["BC6", "CO", "PM25"]] *= 3.0
    b = make_features(d2, use_bc_history=True)
    pd.testing.assert_frame_equal(a.loc[:t0], b.loc[:t0])


def test_virtual_sensor_has_no_bc_features(df):
    X = make_features(df, use_bc_history=False)
    assert not [c for c in X.columns if c.startswith("BC")]


def test_target_is_shifted_forward(df):
    y = make_target(df, 4)
    i = 100
    assert y.iloc[i] == df["BC6"].iloc[i + 4] or (np.isnan(y.iloc[i]) and np.isnan(df["BC6"].iloc[i + 4]))


def test_apportionment_bounds(df):
    ap = source_apportionment(df)
    assert ap is not None
    f = ap["bb_fraction"].dropna()
    assert f.between(0, 1).all() and 0.2 < f.mean() < 0.8
