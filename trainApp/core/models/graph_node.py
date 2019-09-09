
class Node():

    def __init__(self, station, distance_from_dst = int(), previous_vertex = str(), \
                line_before = str(), line_after = str()):

        self.line_before = line_before
        self.line_after = line_after
        self.station = station
        self.distance_from_dst = distance_from_dst
        self.previous_vertex = previous_vertex