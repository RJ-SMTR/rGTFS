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
    return sample_data_path / "simple_csv" / "simple_gps.csv"


@pytest.fixture
def sample_gtfs_path(sample_data_path):
    return sample_data_path / "sample_gtfs"


@pytest.fixture
def rgtfs_path(sample_data_path):
    return sample_data_path / "rgtfs"


@pytest.fixture
def simple_rt_from_gps(sample_data_path):
    csv_path = sample_data_path / "simple_csv" / "simple_rt_from_gps.csv"
    with open(csv_path, "r") as f:
        df = pd.read_csv(f, parse_dates=["arrival_datetime", "departure_datetime"])
    df["route_id"] = df["route_id"].astype("string")
    df["trip_id"] = df["trip_id"].astype("string")
    df["service_id"] = df["service_id"].astype("string")
    return df


def test_gps_to_realized_trips(
    sample_gps_path, sample_gtfs_path, rgtfs_path, simple_rt_from_gps
):
    rt = simple.main(sample_gtfs_path, sample_gps_path, rgtfs_path)
    rt["route_id"] = rt["route_id"].astype("string")
    rt["trip_id"] = rt["trip_id"].astype("string")
    rt["service_id"] = rt["service_id"].astype("string")
    assert rt.equals(simple_rt_from_gps)
