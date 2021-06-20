import gtfs_kit as gk
import pandas as pd
import pymove as pm


def read_gtfs(gtfs_path, dist_units="km"):

    return gk.read_feed(gtfs_path, dist_units=dist_units)


def read_gps(gps_path):
    """Read GPS feed in CSV.

    Expects GPS structured as:

        vehicle_id: str
            Internal system identification of the vehicle.
            Should be unique per vehicle, and is used for tracking the
            vehicle as it proceeds through the system.
        route_id: str
            The route_id from the GTFS feed that this selector refers to
        datetime: datetime
            Moment at which the vehicle's position was measured
        latitude: float
            Degrees North, in the WGS-84 coordinate system.
        longitude: float
            Degrees East, in the WGS-84 coordinate system.

    Parameters
    ----------
    gps_path : [type]
        [description]

    Returns
    -------
    pm.MoveDataFrame
        GPS data as a MoveDataFrame
    """

    return pm.MoveDataFrame(
        data=pd.read_csv(gps_path),
        latitude="latitude",
        longitude="longitude",
        datetime="datetime",
        traj_id="vehicle_id",
    )