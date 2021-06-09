import sys
import pytest
import pandas as pd
import numpy as np
from pathlib import Path

sys.path.append("../")
from rgtfs import io
import rgtfs


def round_distance_and_average_speed(df):
    df["distance"] = df["distance"].apply(lambda x: np.round(x, decimals=1))
    df["average_speed"] = df["average_speed"].aply(lambda x: np.round(x, decimals=1))
    return df


@pytest.fixture
def sample_data(tmpdir_factory):
    return Path("sample_data")


@pytest.fixture
def gtfs_path(sample_data):
    return sample_data / "sample_gtfs"


@pytest.fixture
def simple_realized_trips(sample_data):
    return sample_data / "sample_gtfs" / "simple_realized_trips.csv"


@pytest.fixture
def sample_realized_trips(simple_realized_trips):
    return pd.read_csv(simple_realized_trips)


def test_simple_gtfs_to_realized(sample_gtfs_path, sample_realized_trips):
    gtfs = io.read_gtfs(sample_gtfs_path, "km")
    realized_trips = rgtfs.generate_realized_trips_from_gtfs(gtfs)
    realized_trips = round_distance_and_average_speed(realized_trips)
    assert realized_trips == sample_realized_trips
