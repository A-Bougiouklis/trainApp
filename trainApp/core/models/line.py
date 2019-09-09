'''
    This class represent a train line with all the stations and the lines 
    that is connected with.
'''

class Line:

    def __init__(self, line_name, initial_station, connected_lines):

        self.name = line_name
        self.stations = list(initial_station)
        self.connected_lines = self._remove_self_name_from_lst(connected_lines)

    def add_station(self, station_name):
        self.stations.append(station_name)
    
    #It removes the self.name from the connected lines list
    def _remove_self_name_from_lst(self, train_lines):

        final_lst = [line
                    for line in train_lines
                    if line !=self.name]
        return final_lst
    
    #Add only the lines that do not exist already
    def add_line_lst(self, train_lines):

        new_train_lines = self._remove_self_name_from_lst(train_lines)

        #To avoid duplications
        list_to_append =[line 
                        for line in new_train_lines
                        if line not in self.connected_lines]
        
        self.connected_lines.extend(list_to_append)
