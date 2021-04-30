# rGTFS

Tool to compare planned GTFS with real GTFS (rGTFS) extracted from GPS data.
# Working API

```
import rgtfs

# Generage Realized Trips from GTFS
rgtfs.generate_realized_trips_from_gtfs(gtfs_path)

# Treat Rio de Janeiro BRT realized trips
rgtfs.helpers.treat_rj_brt_realized_trips(brt_raw_realized_trips_path)
```

# New Tables Documentation

##### Realized Trips

| Field Name | Type | Required | Description |
|-|-|-|-|
| vehicle_id | ID referencing vehicles.vehicle_id | Required | identifies vehicle |
| departure_datetime | Datetime | Required | Time at which the vehicle departs from the first stop |
| arrival_datetime | Datetime | Required | Time at which the vehicle departs from the stop |
| departure_id | ID referencing stops.stop_id or garages.garage.id | Required | Departure unique identifier. Can be a stop_id or a garage_id. |
| arrival_id | ID referencing stops.stop_id or garages.garage.id | Required | Arrival unique identifier. Can be a stop_id or a garage_id. Can be empty if trajectory_type is garage_to_stop. |
| distance | Float | Required | Distance travelled in the trajectory in seconds |
| elapsed_time | Integer | Required | Trajectory duration in seconds |
| average_speed | Float | Required | Trajectory average speed in km/h |
| trajectory_type | Enum | Required | One of the followin trajectory types: 1. complete_trip: A complete one-way trip. Departure stop and Arrival stop should map to the first and last stop of the trip respectively. 2. not_complete_trip: An incomplete one-way trip. Departure stop should map to the first stop of the trip, but the trip was sundelly aborted so it has no Arrival. 3. garage_to_stop: A trajectory between a garage and a stop or otherwise. One of the stops should map to a garage_id.  |
| trip_id | ID referencing trips.trip_id | Optional | Trip unique identier. Only applicable for trajectory_type: complete_trip and not_complete_trip |
| trip_short_name | Trip name | Optioanl | Public facing text used to identify the trip to riders, for instance, to identify train numbers for commuter rail trips. If riders do not commonly rely on trip names, leave this field empty. A trip_short_name value, if provided, should uniquely identify a trip within a service day; it should not be used for destination names or limited/express designations. It can be used if trip_id is not available. |


## How to go about it

##### Set standards of how the GPS data should look like. What are the accepted columns? How should the feed be structured? What is the best fit with GTFS?
##### What are the expected results?

- Retrospective GTFS, rGTFS, which is a GTFS of what actually happend on date YYYY-MM-DD
  - Fully dependend on GPS. It'd have to create the shapes, stops, lines, etc
  - Based on planned GTFS. It'd use the current GTFS shapes, stops and lines to support the algorithm

- Comparisson between GTFS and rGTFS
  - Difference in bus frequency/waiting times
  - Difference in the fleet. What are the lines larges fleet difference?
  - Ponctuality score. 

##### How the module should look like?

- io (read and write to GTFS)
- GTFS object
- rGTFS builder to GTFS object
- 


## Similar Projects

Related projects by other people:
* https://github.com/CUTR-at-USF/retro-gtfs/tree/GTFS-Realtime (a fork of this code extending it to GTFS-realtime data sources)
* https://github.com/WorldBank-Transport/Transitime

