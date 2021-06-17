import basedosdados as bd
import pymove as pm
import gtfs_kit as gk
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import numpy as np
from copy import deepcopy

from rgtfs import utils, io
from pymove.utils import log as pymove_log

pymove_log.set_verbosity("ERROR")


def add_buffer_around_stops(df, gtfs, radius=100):

    stops = gtfs.stops[gtfs.stops["stop_id"].isin(df["stop_id"].unique())][
        ["stop_id", "stop_lat", "stop_lon"]
    ]

    stops["stop_buffer"] = stops.apply(
        lambda r: utils.buffer_in_meters(r["stop_lon"], r["stop_lat"], radius), 1
    )

    return pd.merge(stops, df, on="stop_id")


def get_first_last_stops(gtfs):

    # Get last stops
    last_stops = gtfs.stop_times.iloc[
        gtfs.stop_times.groupby("trip_id")["stop_sequence"].idxmax()
    ][["trip_id", "stop_id"]]
    last_stops["stop_label"] = "last"

    # Get first stops
    first_stops = gtfs.stop_times.query("stop_sequence == 1")[["trip_id", "stop_id"]]
    first_stops["stop_label"] = "first"

    # Aggerate stops and add ids
    first_last_stops = pd.merge(
        pd.concat([first_stops, last_stops]),
        gtfs.trips[["route_id", "service_id", "direction_id", "trip_id"]],
        on="trip_id",
    )

    return first_last_stops


def clean_gps(gps):

    gps = pm.filters.clean_gps_nearby_points_by_distances(gps, radius_area=10)

    gps["point"] = gps.apply(lambda x: Point(x["lon"], x["lat"]), 1)

    return gpd.GeoDataFrame(gps, geometry="point").rename(columns={"id": "vehicle_id"})


def get_departure_arrival(df):

    new_df = pd.DataFrame(
        [
            {
                "vehicle_id": df["vehicle_id"].unique()[0],
                "route_id": df["route_id"].unique()[0],
                "direction_id": df["direction_id"].unique()[0],
                "departure_datetime": df[df["stop_label"] == "first"][
                    "datetime"
                ].values[0],
                "arrival_datetime": df[df["stop_label"] == "last"]["datetime"].values[
                    0
                ],
            }
        ]
    )

    return new_df


def get_realized_trips_simple(_df):

    _df = _df.sort_values(
        by=[
            "vehicle_id",
            "direction_id",
            "datetime",
        ]
    ).reset_index(drop=True)

    pattern = ["first", "last"]

    final = pd.DataFrame()

    for i in range(len(_df)):

        if i == 0:
            continue

        if (
            pattern == [_df.loc[i - 1]["stop_label"], _df.loc[i]["stop_label"]]
            and _df.loc[i - 1]["direction_id"] == _df.loc[i]["direction_id"]
        ):
            final = pd.concat([final, get_departure_arrival(_df.loc[[i - 1, i]])])

    return final


def match_gps_and_stops(
    stops,
    gps,
):

    return gpd.sjoin(stops, gps, lsuffix="stops", rsuffix="gps")[
        [
            "vehicle_id",
            "datetime",
            "route_id_stops",
            "route_id_gps",
            "trip_id",
            "direction_id",
            "stop_id",
            "stop_label",
            "stop_buffer",
        ]
    ]


def match_linha_route_id(gps_path, gtfs, unplanned_path="unplanned.csv"):

    gps = pd.read_csv(gps_path)
    routes = gtfs.routes

    routes["linha"] = routes["route_short_name"].apply(lambda x: x.replace("BRT_", ""))

    merged = gps.merge(routes[["linha", "route_id"]], on="linha", how="left")

    merged["dia"] = pd.to_datetime(merged.datetime).dt.date

    mask = merged["route_id"].isna()

    grouped = merged[mask].groupby("linha")

    unplanned = grouped.count().datetime.rename("n_registros").reset_index()
    unplanned["dia"] = grouped.dia.unique().reset_index(drop=True)
    unplanned["dia"] = unplanned["dia"].apply(lambda x: x[0])

    merged.to_csv(gps_path, index=False)
    unplanned.to_csv(unplanned_path, index=False)

    return merged, unplanned


def treat_calendar(gtfs):

    calendar = deepcopy(gtfs.calendar)
    calendar["start_date"] = calendar["start_date"].apply(pd.Timestamp)
    calendar["end_date"] = calendar["end_date"].apply(pd.Timestamp)
    return calendar.rename(
        columns={
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6,
        }
    )


def get_service_id(dt, calendar):

    calendar = calendar[(calendar["start_date"] < dt) & (calendar["end_date"] > dt)]

    return calendar[calendar[dt.dayofweek] == 1]["service_id"].values[0]


def get_realized_trips(stops, gps, gtfs, ignore_vehicles_with_wrong_route_id):

    if ignore_vehicles_with_wrong_route_id:

        matched = match_gps_and_stops(stops, gps)

        realized_trips = (
            matched[
                matched["route_id_stops"].astype("string")
                == matched["route_id_gps"].astype("string")
            ]
            .rename(columns={"route_id_gps": "route_id"})
            .groupby("vehicle_id")
            .apply(get_realized_trips_simple)
            .reset_index(drop=True)
        )
        # Adds service id
        calendar = treat_calendar(gtfs)
        realized_trips["service_id"] = realized_trips["departure_datetime"].apply(
            lambda r: get_service_id(r, calendar)
        )
        # Adds trip id
        realized_trips = pd.merge(
            realized_trips,
            gtfs.trips[["route_id", "direction_id", "service_id", "trip_id"]],
            on=["route_id", "direction_id", "service_id"],
        )

    return realized_trips[
        [
            "vehicle_id",
            "route_id",
            "direction_id",
            "service_id",
            "trip_id",
            "departure_datetime",
            "arrival_datetime",
        ]
    ]


def realized_trips_to_gtfs(_realized_trips, _gtfs):

    times = pd.DatetimeIndex(_realized_trips["departure_datetime"])
    t = _realized_trips.groupby(["trip_id", times.hour]).count()["vehicle_id"]
    t = (
        (3600 / t)
        .to_frame()
        .reset_index()
        .rename(columns={"vehicle_id": "headway_secs"})
    )
    t["start_time"] = t["departure_datetime"].apply(lambda x: f"{x:02}:00:00")
    t["end_time"] = t["departure_datetime"].apply(lambda x: f"{x+1:02}:00:00")
    t["exact_times"] = np.nan

    _gtfs.frequencies = t[
        ["trip_id", "start_time", "end_time", "headway_secs", "exact_times"]
    ]

    return _gtfs


def main(
    gtfs_path,
    gps_path,
    rgtfs_path,
    dist_units="km",
    stop_buffer_radius=100,
    ignore_vehicles_with_wrong_route_id=True,
):
    gtfs = io.read_gtfs(gtfs_path, "km")

    gps_pre, unplanned = match_linha_route_id(gps_path, gtfs)

    gps = io.read_gps(gps_path)
    gps = clean_gps(gps)

    first_last_stops = get_first_last_stops(gtfs)
    first_last_stops = add_buffer_around_stops(
        first_last_stops, gtfs, stop_buffer_radius
    )
    first_last_stops = gpd.GeoDataFrame(first_last_stops, geometry="stop_buffer")

    realized_trips = get_realized_trips(
        first_last_stops, gps, gtfs, ignore_vehicles_with_wrong_route_id
    )

    rgtfs = realized_trips_to_gtfs(realized_trips, gtfs)
    rgtfs.write(rgtfs_path)

    return realized_trips, unplanned


if __name__ == "__main__":

    main()
