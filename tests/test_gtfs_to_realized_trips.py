import sys
import pytest
import pandas as pd
import numpy as np
from pathlib import Path

sys.path.append("../")
import rgtfs
from rgtfs import io


def round_distance_and_average_speed(df):
    df["distance"] = df["distance"].apply(lambda x: np.round(x, decimals=1))
    df["average_speed"] = df["average_speed"].apply(lambda x: np.round(x, decimals=1))
    return df


@pytest.fixture
def sample_data(tmpdir_factory):
    return Path(__file__).parent / "sample_data"


@pytest.fixture
def sample_gtfs_path(sample_data):
    return sample_data / "sample_gtfs"


@pytest.fixture
def simple_realized_trips(sample_data):
    return sample_data / "simple_realized_trips.csv"


@pytest.fixture
def sample_realized_trips(sample_data):
    csv_path = sample_data / "simple_realized_trips.csv"
    with open(csv_path, "r") as f:
        rt = pd.read_csv(f, parse_dates=["arrival_datetime", "departure_datetime"])
    return rt


def test_simple_gtfs_to_realized(sample_gtfs_path, sample_realized_trips):
    rt = rgtfs.generate_realized_trips_from_gtfs(sample_gtfs_path)
    rt = round_distance_and_average_speed(rt)
    rt['arrival_id'] = rt['arrival_id'].astype(dtype="int64")
    rt['departure_id'] = rt['departure_id'].astype(dtype="int64")
    rt['trip_id'] = rt['trip_id'].astype(dtype="int64")
    assert rt.equals(sample_realized_trips)
