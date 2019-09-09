'''
    In this class the best route for a trip is being calculated.

    This question has 2 parts because we do not have an exact representation of the train map.
    We know only the line interconnections and the stations locations represented by zones.

    1) In the first step we culculate the lines that we have to take to travel to our destination,
    with the least possible interconnections.
    2) In the second step we find the best possible stations that we have to take and the best
    combination of lines. We culculate the cost from the zones and I have used a greedy approach to 
    solve the problem.

    Class attributes:
        self.origin = station object
        self.destination = station object
        self.station_dict = the wikipedia scraped station_dict
        self.line_dict =the wikipedia scraped line_dict
        self.lines_already_checked = lines that we have checked in our search
'''
from core.constants.constants import STATION_DICT_PATH, LINE_DICT_PATH
from core.models.graph_node import Node
import pickle, os, math

class Route_planning():

    def __init__(self, station_origin, station_destination):
        self.origin = station_origin
        self.destination = station_destination
        self.station_dict = self._load_dict(STATION_DICT_PATH)
        self.line_dict = self._load_dict(LINE_DICT_PATH)
        self.lines_already_checked = list()
        self.final_node = None

    def _load_dict(self, filepath):
        if not os.path.exists(filepath):
            raise Exception('The file path is not valid')

        with open(filepath, 'rb') as input_file:
            station_dict = pickle.load(input_file)
        return station_dict

    def _is_connected_with_dest(self, line):
        return line in self.destination.lines

    #Returns the level lines connected with the destination
    def _level_check(self, level_lines):
        possible_lines = list()
        for line in level_lines:
            if (self._is_connected_with_dest(line)) and (line not in possible_lines):
                possible_lines.append(line)

        return possible_lines

    #This function checks all train lines recursively and returns a list of lists 
    #with the possible conections to the destination.
    #For example if we want to travel from Farringdon to Canary Wharf the result would be:
    #[['Metropolitan', 'Circle', 'Hammersmith & City'], ['Jubilee']]
    #Because we can go to Jubilee from every line of the first list
    def _identify_line_connections(self, level_lines):

        #If there are no level lines it means that there are no possible connections
        if not level_lines:
            return [[]]

        #Check if there are lines connected to the destination
        connections_to_dst = self._level_check(level_lines)
        #If not check the children of the level_lines
        if not connections_to_dst:
            #Keep track the already checked lines to prune all the back brances
            self.lines_already_checked.extend(level_lines)

            #The lines of the next level are the children of the level_lines
            #which have not been visited yet.
            next_level_lines = [next_level_line 
                                for line_name in level_lines
                                for next_level_line in self.line_dict[line_name].connected_lines
                                if next_level_line not in self.lines_already_checked]
            
            lines_to_dst = self._identify_line_connections(next_level_lines)

            #the parents are the lines which can be connected with the lines_to_dst
            #from this level
            add_parents = []
            children_lines = lines_to_dst[0]
            for children_line in children_lines:
                for parent in level_lines:
                    if children_line in self.line_dict[parent].connected_lines and parent not in add_parents:
                        add_parents.append(parent)

            #return the complite list of possible connections
            return( [add_parents] + lines_to_dst )

        #if we have found a possible connection return it
        #a 2dimentional list is being used because there could be a lot 
        #of different ways to reach the final destination
        else:
            return [connections_to_dst]

    #Returns the common stations between line1 and line2
    def _stations_with_lines(self, line1, line2):
        station_lst = list()
        for _, station in self.station_dict.items():
            if line1 in station.lines and line2 in station.lines:
                station_lst.append(station)
        
        return(station_lst)

    #Select the station closer to the destination to make a interchange
    def _select_best_station_to_change(self, stations):
        
        #Initialize the distance between a station and the destination
        min_distance_from_dst = 100 
        selected_station = ""

        for station in stations:
            
            for zone_dst in self.destination.zones:
                for zone_src in station.zones:
                    distance_from_dst = math.fabs( int(zone_dst) - int(zone_src) )
                    
                    #if the destination and the interchange are in the same zone 
                    #there is no point on continuing the search
                    if distance_from_dst == 0: 
                        return station, 0
                    if min_distance_from_dst > distance_from_dst:
                        min_distance_from_dst = distance_from_dst
                        selected_station = station
        
        return selected_station, min_distance_from_dst

    #Create a graph level and select the station to make a interchange
    def _create_level_nodes(self, src_lines, dst_lines, parent):
        
        level_nodes = list()

        for src_line in src_lines:
            for dst_line in dst_lines:
                common_stations = self._stations_with_lines(src_line, dst_line)
                selected_station, distance_from_dst = self._select_best_station_to_change(common_stations)

                #create a node
                level_node = Node(selected_station, distance_from_dst, parent, src_line, dst_line)
                level_nodes.append(level_node)
        
        #sort the list according to the culculated distance
        return sorted(level_nodes, key=lambda x: x.distance_from_dst, reverse=True)
    
    #This function selects the best stations to change and the best lines to take to arrive to the destination.
    def _select_interconnections(self, connections, parrent):     
        
        interchanges_to_dst = len(connections)

        #if there are no more interchanges return the final node - destination node
        if interchanges_to_dst == 1:

            #if we travel directly select a random line to go. They have the same cost
            if parrent.station == self.origin:
                parrent.line_after = parrent.station.lines[0]

            final_node = Node(self.destination, 0, parrent, parrent.line_after)
            self.final_node = final_node
            return True

        #if there are interchanges analise the graph
        else:
            src_lines = connections[0]
            dst_lines = connections[1]
            sorted_level_nodes = self._create_level_nodes(src_lines, dst_lines, parrent)

            for node in sorted_level_nodes:
                finished = self._select_interconnections(connections[1:], node)
                if finished: return

    def _generate_path(self):

        path = str()
        current_node = self.final_node
        while current_node.station != self.origin:
            path =  "travel to {} via {} next {}".format(current_node.station.name,current_node.line_before,path) 
            current_node = current_node.previous_vertex
        
        path =  "Originated from {} {}".format(current_node.station.name, path)
        return path[:-5] #remove the last next

    def find_the_best_route(self):

        try:
            #Identify the possible lines that can be used to reach the destination.
            queue = self.origin.lines #The initial lines that can be used.
            possible_connections = self._identify_line_connections(queue)

            #Compare the selected lines and the best stations to make the interconnections.
            origin_node = Node(self.origin)
            self._select_interconnections(possible_connections, origin_node)

            #generate the path from the final node
            return self._generate_path()
        except:
            raise Exception("While the route from {} to {} was calculated an unexcpected error occurred" \
                .format(self.origin.name, self.destination.name))
