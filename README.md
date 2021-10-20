# Benchmark-tool-for-Adelaide-GTFS-Data-

This resposity is a master research project for the University of Adelaide 

# Time_Expend Dijkstra
The Dijkstra.py is written in Python3, only three GTFS files are required:  stop_time.txt,stops.txt and trips.txt

The reference for GTFS data can be found here: https://developers.google.com/transit/gtfs/reference#stopstxt

# Example
The program can search the shorest bus distance from one stop to another stop by following the start stop id and end stop id with start time. 

`python3 diskstra.py` and select 1 to start search (Initialize graph may take sometimes). 

This is a sample screeshot from stop 77 Curtis Rd - North East side(id:22) to stop 80M Warooka Dr - North East side(id:88)
![example](https://github.com/c321474/Benchmark-tool-for-Adelaide-GTFS-Data-/blob/main/Resources/example.png)
