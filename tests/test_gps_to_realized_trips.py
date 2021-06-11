from dask.dataframe.methods import sample
import pytest
import sys
import pandas as pd
from pathlib import Path

sys.path.append("../")
from rgtfs import io, simple


@pytest.fixture
def sample_data_path():
    return Path(__file__).parent / "sample_data"


@pytest.fixture
def sample_gps_path(sample_data_path):
    return sample_data_path /"simple_csv"/ "simple_gps.csv"


@pytest.fixture
def sample_gtfs_path(sample_data_path):
    return sample_data_path / "sample_gtfs"


@pytest.fixture
def rgtfs_path(sample_data_path):
    return sample_data_path / "rgtfs"


@pytest.fixture
def simple_rt_from_gps(sample_data_path):
    csv_path = sample_data_path /"simple_csv" /"simple_rt_from_gps.csv"
    with open(csv_path, "r") as f:
        df = pd.read_csv(f, parse_dates=["arrival_datetime", "departure_datetime"])
    return df


def test_gps_to_realized_trips(
    sample_gps_path, sample_gtfs_path, rgtfs_path, simple_rt_from_gps
):
    rt = simple.main(sample_gtfs_path, sample_gps_path, rgtfs_path)

    assert rt.equals(simple_rt_from_gps)
