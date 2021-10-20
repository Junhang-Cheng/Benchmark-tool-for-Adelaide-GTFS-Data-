import pandas as pd
import time
import sys

### Class for graph construction
class Edge:
    def __init__(self, value, adj_id, trip_id):
        self.value = value
        self.adj = adj_id
        self.trip = trip_id
        
class Stop:
    def __init__(self, sid, name):
        self.sid = sid
        self.name = name
#         self.arrival = pd.to_datetime("00:00:00")
        self.edges_list = []
        
    def add_edge(self, x):
        self.edges_list.append(x)

class Digraph:
    def __init__(self):
        self.num_vertices = 0
        self.num_edges = 0
        self.stop_dict = {}

    def count_vertices(self):
        return self.num_vertices

    def count_edges(self):
        return self.num_edges

    def add_stop(self, x):
        self.stop_dict[x.sid]=x
        self.num_vertices += 1
        
    def add_edge(self, x, y, value, trip_id):
        new_edge = Edge(value, y, trip_id)
        self.stop_dict[x].add_edge(new_edge)
        self.num_edges += 1
        
### Read Dataset
def readDataset():
    stops = pd.read_csv('stops.txt')
    stop_times = pd.read_csv('stop_times.txt')
    trips = pd.read_csv('trips.txt')
    return stops, stop_times, trips

### Initialize Graph
def initialGraph():
    graph = Digraph() 
    return graph

### Initialize Stop Nodes
def initialNode(graph, stops):
    stop_id_name = stops[["stop_id", "stop_name"]].sort_values(by="stop_id")
    row, col = stop_id_name.shape
       
    for i in range(0, row):
        sid, name = stop_id_name.iloc[i]
        graph.add_stop(Stop(sid, name))

### Initialize Edges
def initialEdge(graph, stops, stop_times, trips):    
    trips.drop_duplicates(subset = ["route_id"],keep="first",inplace=True)
    trips_id = trips["trip_id"]
    new_stop_times = pd.merge(stop_times, trips_id, on=['trip_id'], how='inner')
    row, _ = new_stop_times.shape
    
    for id in trips_id:
        trip = new_stop_times[new_stop_times["trip_id"]==id]
        trip = trip.sort_values(by="stop_sequence", ascending=True)

        for i in range(1, trip.shape[0]):
            x = trip["stop_id"].iloc[i-1]
            y = trip["stop_id"].iloc[i]
            t1 = trip["arrival_time"].iloc[i-1]
            t2 = trip["arrival_time"].iloc[i]

            try:
                t1_date = pd.to_datetime(t1)
                t2_date = pd.to_datetime(t2)
                value = t2_date - t1_date
            except Exception as e:
                t1_list = t1.split(":")
                t2_list = t2.split(":")
                if(int(t1_list[0])>23): 
                    t1_list[0] = str(int(t1_list[0])-24)
                    t2_list[0] = str(int(t2_list[0])-24)
                    t1 = t1_list[0] + ":" + t1_list[1] + ":" + t1_list[2]
                    t2 = t2_list[0] + ":" + t2_list[1] + ":" + t2_list[2]
                    value = pd.to_datetime(t2) - pd.to_datetime(t1)
                else:
                    if(int(t2_list[0])>23): 
                        temp = "23:59:59"
                        before = pd.to_datetime(temp) - t1_date
                        t2_list[0] = str(int(t2_list[0])-24)
                        t2 = t2_list[0] + ":" + t2_list[1] + ":" + t2_list[2]
                        value = before + \
                              (pd.to_datetime(t2) - pd.to_datetime("00:00:00")) + \
                              (pd.to_datetime("00:00:01") - pd.to_datetime("00:00:00"))
                    else:
                        value = pd.to_datetime(t2) - pd.to_datetime(t1)

            graph.add_edge(x, y, value, id)

### Dijkstra
def findShortestPath(source, dest, graph):
    inf = pd.Timedelta("999 days 00:00:00")
    parent_dict = {}
    tripid_dict = {}
    dist_dict = {}
    visited_dict = {}
    
    for key in graph.stop_dict:
        parent_dict[key] = ""
        tripid_dict[key] = ""
        dist_dict[key] = inf
        visited_dict[key] = 0
        
    parent_dict[source] = -1
    dist_dict[source] = pd.Timedelta("0 days 00:00:00")
    
    while(visited_dict[dest]==0):
        ### Find minimum in dist_dict
        mini = dest
        for key in dist_dict:
            if(visited_dict[key] == 0):
                if(dist_dict[key]<dist_dict[mini]):
                    mini = key
            
        ### Visit its edges
        for edge in graph.stop_dict[mini].edges_list:
            if(visited_dict[edge.adj]==0):
                if(dist_dict[mini] + edge.value < dist_dict[edge.adj]):
                    dist_dict[edge.adj] = dist_dict[mini] + edge.value
                    parent_dict[edge.adj] = mini
                    tripid_dict[edge.adj] = edge.trip
        visited_dict[mini] = 1

    path = []
    path_name = []
    trip_id = []
    node = dest
    while(node!=-1 and parent_dict[node] ):
        path.append(node)
        trip_id.append(tripid_dict[node])
        path_name.append(graph.stop_dict[node].name)        
        node = parent_dict[node]  
    
    path.reverse()
    path_name.reverse()
    trip_id.reverse()
    trip_id[0] = trip_id[1]
    
    return path, path_name, trip_id, dist_dict

def checkInput(graph, source, dest, start_time):
    try:
        source = int(source)
        _ = graph.stop_dict[source]
    except Exception as e:
        print("Start Point Not Found") 
        return 0
    try:
        dest = int(dest)
        _ = graph.stop_dict[dest]
    except Exception as e:
        print("End Point Not Found") 
        return 0
    try:
        start_time = pd.to_datetime(start_time)
    except Exception as e:
        print("Invalid Start Time")
        return 0
    return 1

def printResult(graph, source, dest, start_time, path, path_name,trip_id, dist_dict, comp_time):
    print("Start Point: " + graph.stop_dict[source].name)
    print("End Point: " + graph.stop_dict[dest].name)
  
    for i in range(1,len(path)+1):
        print("Step {}: Start from {}, {} take the NO.{} bus" \
             .format(i, path_name[i-1],start_time + dist_dict[path[i-1]], trip_id[i-1]))

    print("Time for Trip:", end=" ")
    print(dist_dict[dest])
    print("Computation Time:", end=" ")
    print(comp_time, end="")
    print("s")

if __name__ == "__main__":
    init_time = time.time()
    print("Initialize Graph...")
    ### Read Dataset
    stops, stop_times, trips = readDataset()
    ### Initialize Graph
    graph = initialGraph()
    initialNode(graph, stops)
    initialEdge(graph, stops, stop_times, trips )
    init_time = time.time() - init_time
    print("Initialization Time: " + str(init_time), end="")
    print("s")
          
    ### Prompting Loop
    while(True):
        command = input("Enter 1 to Search or Other to Exit:")
        if(command!="1"):
            break
            
        ### Get Input    
        source = input("Enter Start Point ID:")
        dest = input("Enter End Point ID:")
        start_time = input("Enter Start Time (e.g.12:00:00):")
        if(checkInput(graph, source, dest, start_time)==0):
            print()
            continue
            
        source = int(source)
        dest = int(dest)
        start_time = pd.to_datetime(start_time)
        ### Get Shortest Path
        comp_time = time.time()
        path, path_name, trip_id, dist_dict = findShortestPath(source, dest, graph)
        comp_time = time.time() - comp_time
    
        ### Print Result
        printResult(graph, source, dest, start_time, path, path_name, trip_id, dist_dict, comp_time)
        print()
    