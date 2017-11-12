import googlemaps
import pystache
import os, json, codecs, urllib, uuid, base64
from datetime import datetime

# get api key from environment
API_KEY = os.environ['GMAPS_API_KEY']
URL_TEMPLATE = "https://maps.googleapis.com/maps/api/staticmap?size=%dx%d&path=enc:%s&key=" + API_KEY
IMAGE_SIZE = (230, 230)

def get_maps(route):
  for step in route['legs'][0]['steps']:
    step['uuid'] = uuid.uuid4().hex
    points = step['polyline']['points']
    url = URL_TEMPLATE % (400, 400, points)
    urllib.urlretrieve(url, "images/%s.png" % (step['uuid']))



def get_map_base64(encoded_polyline):
  url = URL_TEMPLATE % (IMAGE_SIZE[0], IMAGE_SIZE[1], encoded_polyline)
  img_data = urllib.urlopen(url)
  return base64.b64encode(img_data.read())

def get_image_data(route):

  route['overview_polyline']['base64'] = get_map_base64(route['overview_polyline']['points'])

  for step in route['legs'][0]['steps']:
    step['polyline']['base64'] = get_map_base64(step['polyline']['points'])



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
response = gmaps.directions(origin, destination, mode=travel_mode, departure_time=now)

if len(response) < 1:
  print "No results found! Try again with more specific places..."
  exit()
  
route = response[0]

print "Downloading maps..."

# get_maps(route)
get_image_data(route)

print "Saving directions..."

json_data = json.dumps(response, indent=2)
html = pystache.render(tpl, route)

print json_data
print html

json_file = open('directions.json', 'w')
json_file.write(json_data)
html_file = open('directions.html', 'w')
html_file.write(html)

# print start_address + " to " + end_address
# print summary + " (" + total_distance + "/" + total_duration + ")"


# for step in steps:
  # print step["html_instructions"]




