# trainApp

Table of context

    • Initial Description
    • Application description 
    • How to run the application
    • Results
    • Improvements


Initial Description

The main requirement for this task was to be able to scrape a Wikipedia table with train stations information 
and then build a REST API to query the scraped data. In addition the API has to be able to update the scraped data 
with new train lines.




Application Description

	The TrainApp scrapes data from a given Wikipedia link. In particular can scrape the train station names, 
  the station interchanges, the usage of the stations and the zones where the stations are located. 
  It uses these data to build a model and with a REST API makes queries to this model. 
  Finally the user can test the application with Postman.
	The first step of the application is the data scraping. 
  In order to scrape the needed data an analysis of the given Wikipedia page was done and then by using BeautifulSoup 
  the application parses the data. It creates two dictionaries which represent the stations and the lines in order to 
  gain instant access to any line and station needed. Also if the user provide a  Wikipedia page of any new train line 
  the application can add the new data to the  dictionaries.
	The next step is to query the scraped data. A big limitation of the Wikipedia table is that we do not know the exact 
  sequence of the stations on any train line and that is why to calculate the best routes between stations is a challenging task. However when a human makes this calculation he or she does not concern about the actual distance between the stations. The biggest waste of time when the train is used is during the waiting time between interchanges. That is why the used algorithm calculates the best route in two steps. In the first step it finds all the lines that can be used to reach the destination with the least interconnections. In the second step a greedy approach is taken to select the best stations to make the calculated  interchanges. In order to evaluate these changes we check the zones where the destination and the interchange are located and our goal is simply to move towards the final destination. The calculated route is presented to the user as a guide in the form of a string. The other type of queries requested have been performed via simple functions in the API level of the application.
	The last part of the application is the requested API. The flask python library has been used to deploy this API. 
  There are different types of functions that are implemented which perform all the requested queries. 
  In order to make it more user friendly I have used postman to interact and test the application. 
  In the given folder a postman collection has been added with all the possible calls and different tests.



How to run the application

	In order to run the application follow the next steps:

    1. Create a virtual environment with python 3.6
    2. Install the attached requirements: “pip3 install -r requirement.txt”
    3. Install postman
    4. Navigate to the folder trainApp and run the trainApi.py: 
 				“python3  trainApi.py”
    5. Open the attached postman collection and change the link in all the requests to your local host if necessary.
    6. Run the postman collection.


Results

	The application can successfully scrape the needed data from Wikipedia and then use an API to query them. 
  Also via Postman we can examine the functionality of the application and test ether every unit of it or end to end.


Improvements

The following could be added to the application as improvements:

    1. The current API was uploaded to a Google Cloud Server but I had issues connecting to it and that is why 
       I have not added it as an accomplished task. At this form the API can run in local ether via postman or
       directly from the command line.
    2. I have noticed some bugs in the system. For example in the previous pictures the first station is 
       divided into chars even though the station does exist in the model as the Postman test proves. 
       To further investigate more tests are necessary and of course python unit tests have to be created to ensure
       the correct behavior of the system.
    3. The routing algorithm is a little complicated, it can be optimized and the code could be simpler.
    4. An UI could improve massively the user experience.
    5. All the possible queries are hard coded into python functions, an SQL database could improve the model 
       and let the user make any kind of query.
    6. The usage of each station is captured during the scraping, these data can be used for statistical analysis.
