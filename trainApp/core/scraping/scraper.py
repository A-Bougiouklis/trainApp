'''

    With this class we can scrap informaion from a wikipedia table to create 2 dictionaries:

    1) {station_name : station_object}
    2) { line_name : [station_1, ..., station_n]}

    And then save the results.

'''
from core.models.station import Station
from core.models.line import Line
from core.constants.constants import DB_PATH
from bs4 import BeautifulSoup
import requests, pickle, os

class Scraper:

    def __init__(self, url, stations = dict(), lines = dict()):
        self.url = url
        self.stations = stations
        self.lines = lines

    def _save_the_results(self):

        if not os.path.exists(DB_PATH):
            raise Exception('The DB path is not valid')

        with open(os.path.join(DB_PATH, 'Station_dict'), 'wb') as outfile:
            pickle.dump(self.stations, outfile)

        with open(os.path.join(DB_PATH, 'Line_dict'), 'wb') as outfile:
            pickle.dump(self.lines, outfile)

    #Return a list with the read table elemets
    def _read_table_elements(self, elements):

        final_lst = list()
        links = elements.findAll('a')
       
        for link in links:
            # We want to skip any endnote of the table
            if link.get('href')[0] != '#':
                final_lst.append(link.text)

        return final_lst

    #Add the station in the self.lines dictionary
    def _update_lines_dict(self, station):

        for train_line in station.lines:
            #If the train_line exist in the self.lines -> update the key
            if self.lines.get(train_line):
                line_obj = self.lines[train_line]
                line_obj.add_station(station.name)
                line_obj.add_line_lst(station.lines)
                self.lines[train_line] = line_obj
            #Else create a new key
            else:
                line_obj = Line(train_line, station.name, station.lines)
                self.lines[train_line] = line_obj

    #Scrape the data from the given url and convert them to BeautifulSoup
    def _scarpe_url(self, url):
        #Get the data from the given url.
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception('The request was not successful, the server did not responded with the requested data.')

        #Extract the information from the response
        soup = BeautifulSoup(response.text,'lxml')

        return soup
    
    #This function scrape a new line table from a given url and updates the already existed tables
    def scrape_new_train_line(self, url, new_line_name):

        soup = self._scarpe_url(url)

        #From every row of the table read the station name
        for row in soup.find('table', class_='wikitable').find_all('tr')[1::1]:

            try:    
                elements = row.find('td')
                station_name = elements.text.rstrip() #remove end of line
                
                #If this station already exists in the dictionary, update the element
                if self.stations.get(station_name):
                    station_obj = self.stations[station_name]
                    
                    #if the new line does not exist already add it
                    if new_line_name not in station_obj.lines:
                        station_obj.lines.append(new_line_name)

                #Else if it does not exist create a new element to the dict
                else:
                    #Create a station object to add all the information to it
                    station_obj = Station(station_name)

                    station_obj.lines = [new_line_name]
                    self._update_lines_dict(station_obj)

                    zones = elements.find_next_sibling().find_next_sibling()
                    station_obj.zones = self._read_table_elements(zones)

                    usage = zones.find_next_sibling().find_next_sibling().find_next_sibling().find_next_sibling()
                    station_obj.usage = float(usage.find('span').text)

                    #Update the dictionary with the new station
                    self.stations[station_name] = station_obj

            except:
                raise Exception('An unexpected exception was raised while the train table was parsed')
    
        #Save the station dictionary
        self._save_the_results()

    def scrape_train_stations(self):

        soup = self._scarpe_url(self.url)

        #From every row of the table read the station name, the used trains lines, the zone where it is located
        #and the station usage and add them to the dictionary.
        for row in soup.find('table', class_='wikitable').find_all('tr')[1::1]:
            
            try:
                header = row.find('th')
                elements = row.find('td')

                station_name = header.a.text
                
                #Create a station object to add all the information to it
                station_obj = Station(station_name)

                train_lines = elements.find_next_sibling()
                station_obj.lines = self._read_table_elements(train_lines)
                self._update_lines_dict(station_obj)

                zones = train_lines.find_next_sibling().find_next_sibling()
                station_obj.zones = self._read_table_elements(zones)

                usage = zones.find_next_sibling().find_next_sibling().find_next_sibling().find_next_sibling()
                station_obj.usage = float(usage.find('span').text)

                #Update the dictionary with the new station
                self.stations[station_name] = station_obj

            except:
                raise Exception('An unexpected exception was raised while the train table was parsed')
    
        #Save the station dictionary
        self._save_the_results()
