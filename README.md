# rGTFS

Tool to compare planned GTFS with real GTFS (rGTFS) extracted from GPS data.

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

