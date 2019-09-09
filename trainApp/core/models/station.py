'''
    This class represents a train station from a specific line.
   
'''

class Station:

    def __init__(self, name):

        self.name = name
        self.lines = list()
        self.zones = list()
        self.usage = float()