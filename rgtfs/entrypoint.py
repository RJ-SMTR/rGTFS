import pandas as pd
import datetime
import numpy as np
from copy import deepcopy

from rgtfs import io, tables


def calculate_exits(row, calendar_dates_by_trip_id):

    dow = {
        0: "monday",
        1: "tuesday",
        2: "wednesday",
        3: "thursday",
        4: "friday",
        5: "saturday",
        6: "sunday",
    }
    _df = []

    calendar = calendar_dates_by_trip_id.query(f'trip_id == "{row["trip_id"]}"').iloc[0]

    current_date = pd.Timestamp(str(calendar["start_date"]))
    end_date = pd.Timestamp(str(calendar["end_date"]))

    # Loop through all dates in calendar
    while current_date <= end_date:

        # Has to be match day of the week
        if not calendar[dow[current_date.weekday()]]:
            current_date = current_date + datetime.timedelta(days=1)

        current_time = pd.Timestamp(str(current_date.date()) + " " + row["start_time"])
        end_time = pd.Timestamp(str(current_date.date()) + " " + row["end_time"])

        while current_time < end_time:

            _df.append(current_time)
            current_time = current_time + datetime.timedelta(
                seconds=row["headway_secs"]
            )

        current_date = current_date + datetime.timedelta(days=1)

    _df = pd.DataFrame({"departure_datetime": _df})
    _df["trip_id"] = row["trip_id"]
    return _df


def generate_realized_trips_from_gtfs(gtfs_path):
    """Transforms a GTFS feed to realized_trips format (see README for specification).

    It can either read a feed zip file or a folder.

    Parameters
    ----------
    gtfs_path : str
        GTFS feed zip file or folder path

    Returns
    -------
    pd.DataFrame
        realized_trips data structure (see README for specification)
    """

    gtfs = io.read_gtfs(gtfs_path, "km")

    # Generates all exits
    calendar_dates_by_trip_id = (
        pd.merge(
            gtfs.trips[["service_id", "trip_id"]], gtfs.calendar, on=["service_id"]
        )
    ).drop_duplicates(subset=["service_id", "trip_id"])

    realized_trips = []
    for i, row in gtfs.frequencies.iterrows():

        realized_trips.append(calculate_exits(row, calendar_dates_by_trip_id))

    realized_trips = pd.concat(realized_trips)

    # Adds statistics
    realized_trips = pd.merge(
        realized_trips,
        gtfs.compute_trip_stats()[
            ["trip_id", "duration", "distance", "speed", "start_stop_id", "end_stop_id"]
        ],
        on="trip_id",
    ).rename(
        columns={
            "duration": "elapsed_time",
            "speed": "average_speed",
            "start_stop_id": "departure_id",
            "end_stop_id": "arrival_id",
        }
    )

    # Adds arrival time
    realized_trips["arrival_datetime"] = realized_trips.apply(
        lambda row: row["departure_datetime"]
        + datetime.timedelta(hours=row["elapsed_time"]),
        1,
    )

    # Adds trajectory type
    realized_trips["trajectory_type"] = "complete_trip"

    # creates missing columns
    for c in tables.realized_trips_cols:
        if c not in realized_trips.columns:
            realized_trips[c] = np.nan

    return realized_trips[tables.realized_trips_cols]
