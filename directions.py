import googlemaps
import pystache
import os, json, codecs
from datetime import datetime

# get api key from environment
API_KEY = os.environ['GMAPS_API_KEY']

# set up mustache template
tpl_file = codecs.open('directions.mustache', 'r', 'utf-8')
tpl = pystache.parse(tpl_file.read())

# Gather user data
print "Let's get started. Where are you coming from?"
origin = raw_input("-> ")
print "Ok, now where are you going?"
destination = raw_input("-> ")
print "How are you planning to get there? (transit, walking, bicycling, blank for driving)"
travel_mode = raw_input("-> ")


# get results
print "Ok, getting results from Google..."
gmaps = googlemaps.Client(key=API_KEY)
now = datetime.now()
directions_result = gmaps.directions(origin, destination, mode=travel_mode, departure_time=now)

# # get first result
# # @todo handle multiple options
directions = directions_result[0]

# summary = directions["summary"]

# # sticking to just one leg for now
# route = directions["legs"][0]
# start_address = route["start_address"]
# end_address = route["end_address"]
# total_distance = route["distance"]["text"]
# total_duration = route["duration"]["text"]

# # actual driving steps
# steps = route["steps"]

json = json.dumps(directions_result, sort_keys=True, indent=2)
html = pystache.render(tpl, directions)

print json
print html

json_file = open('directions.json', 'w')
json_file.write(json)
html_file = open('directions.html', 'w')
html_file.write(html)

# print start_address + " to " + end_address
# print summary + " (" + total_distance + "/" + total_duration + ")"


# for step in steps:
  # print step["html_instructions"]
