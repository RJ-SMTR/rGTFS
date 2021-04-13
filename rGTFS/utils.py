import pyproj
from functools import partial
from shapely.ops import transform
from shapely.geometry import Point


def buffer_in_meters(lng, lat, radius):
    proj_meters = pyproj.Proj(init="epsg:3857")
    proj_latlng = pyproj.Proj(init="epsg:4326")

    project_to_meters = partial(pyproj.transform, proj_latlng, proj_meters)
    project_to_latlng = partial(pyproj.transform, proj_meters, proj_latlng)

    pt_latlng = Point(lng, lat)
    pt_meters = transform(project_to_meters, pt_latlng)

    buffer_meters = pt_meters.buffer(radius)
    buffer_latlng = transform(project_to_latlng, buffer_meters)
    return buffer_latlng
