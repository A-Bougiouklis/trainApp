'''
    This is the file to deploy in order to run the application and make rest requests
'''


from flask import Flask, jsonify, request
from core.constants.constants import *
from core.scraping.scraper import Scraper
from core.queries.route_planning import Route_planning
import pickle
app = Flask(__name__)

#Global dictionaries which will hosth the scraped data
station_dict = dict()
line_dict = dict()

#load the scraped data into the global variables
def load_dictionaries():
    global station_dict
    global line_dict

    with open(STATION_DICT_PATH, 'rb') as input_file:
        station_dict = pickle.load(input_file)

    with open(LINE_DICT_PATH, 'rb') as input_file:
        line_dict = pickle.load(input_file)

    return station_dict, line_dict

@app.route('/scrape/wikipedia/stations', methods=['POST'])
def scrape_train_stations():
    #Scrape the train station table from wikipedia
    try:
        body = request.json
        scraper = Scraper(body["url"])
        scraper.scrape_train_stations()
        return jsonify({'result': 'Scraping Completed'})
    except:
        return jsonify({'ERROR': 'Scraping Failed'})

@app.route('/scrape/wikipedia/new_line', methods=['POST'])
def scrape_new_train_line():
    #Scrape the train station table from wikipedia
    try:
        body = request.json
        scraper = Scraper("", station_dict, line_dict)
        scraper.scrape_new_train_line(body["url"], body["line name"])
        return jsonify({'result': 'Scraping of new line {} Completed'.format(body["line name"])})
    except:
        return jsonify({'ERROR': 'Scraping of new line {} Failed'.format(body["line name"])})

@app.route('/load/scraped/data', methods=['GET'])
def load_scraped_data():
    try:
        load_dictionaries()
        return jsonify({'result': 'Load Completed'})
    except:
        return jsonify({'ERROR': 'Load Failed, verify that the requested files have been scraped'})

@app.route('/station/<station_name>', methods=['GET'])
def station_info(station_name):
    try:
        station_obj = station_dict[station_name]
        return jsonify({'Staion_Name': station_obj.name, \
                        'Interchanges': station_obj.lines, \
                        'Zone': station_obj.zones, \
                        'Usage_In_Millions': station_obj.usage})
    except:
        return jsonify({'ERROR': \
            'Cannot retrive the station information for the station {}, verrify that you have loaded the scraped data'\
                .format(station_name)})

@app.route('/station/<station_name>/<attribute>', methods=['GET'])
def station_attribute(station_name, attribute):
    try:
        station_obj = station_dict[station_name]
        return jsonify({attribute: getattr(station_obj, attribute)})
    except:
        return jsonify({'ERROR': \
            'Cannot retrive the station information for the station {}, verrify that you have loaded the scraped data'\
                .format(station_name),
                'Accepted Attributes': ['name' , 'lines', 'zones', 'usage']})

@app.route('/line/<line_name>', methods=['GET'])
def line_info(line_name):
    try:
        line_obj = line_dict[line_name]
        return jsonify({'Line_Name': line_obj.name, \
                'Stations': line_obj.stations, \
                'Connected_lines': line_obj.connected_lines})
    except:
        return jsonify({'ERROR': \
            'Cannot retrive the line information for the line {}, verrify that you have loaded the scraped data'\
                .format(line_name)})

@app.route('/line/<line_name>/<attribute>', methods=['GET'])
def line_attribute(line_name, attribute):
    try:
        line_obj = line_dict[line_name]
        return jsonify({attribute: getattr(line_obj, attribute)})
    except:
        return jsonify({'ERROR': \
            'Cannot retrive the station information for the station {}, verrify that you have loaded the scraped data'\
                .format(line_name),
                'Accepted Attributes': ['name' , 'stations', 'connected_lines']})

@app.route('/route/<origin>/<destination>', methods=['GET'])
def route_calculation(origin, destination):
    try:
        route_plenner = Route_planning(station_dict[origin], station_dict[destination])
        return jsonify({'Calculated_Route': route_plenner.find_the_best_route()})
    except:
        return jsonify({'ERROR': 'Cannot calculate a route between {} and {}'\
                .format(origin, destination)})

@app.route('/longest_line', methods=['GET'])
def longest_line():
    try:
        longest_line = None
        max_number_of_stations = 0

        for line_name, line_obj in line_dict.items(): 
            if len(line_obj.stations) > max_number_of_stations:
                longest_line = line_name
                max_number_of_stations = len(line_obj.stations)

        return jsonify({'Longest_Line': longest_line, \
                        'Number_Of_Staions': max_number_of_stations,
                        'Stations': line_dict[longest_line].stations})
    except:
        return jsonify({'ERROR': \
            'Cannot culculate the longest line, verrify that you have loaded the scraped data'})

@app.route('/most_interchanges', methods=['GET'])
def station_with_the_most_interchanges():
    try:
        station_most_interchanges = None
        num_most_interchanges = 0

        for station_name, station_obj in station_dict.items(): 
            if len(station_obj.lines) > num_most_interchanges:
                station_most_interchanges = station_name
                num_most_interchanges = len(station_obj.lines)

        return jsonify({'Station_With_The_Most_Interchanges': station_most_interchanges, \
                        'Number_Of_Interchanges': num_most_interchanges,
                        'Interchanges': station_dict[station_most_interchanges].lines})
    except:
        return jsonify({'ERROR': \
            'Cannot culculate the station with the most interchanges, verrify that you have loaded the scraped data'})


if __name__=='__main__':
    app.run(debug=True)