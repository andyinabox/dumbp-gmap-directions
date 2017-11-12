import googlemaps
import pystache
import os, json, codecs, urllib, uuid, base64
from datetime import datetime

# set constants
API_KEY = os.environ['DUMBP_GMAPS_API_KEY']
HOME_ADDRESS = os.environ['DUMBP_HOME_ADDRESS']
SAVE_DIR = os.environ['DUMBP_SAVE_DIR']
IMAGE_URL_TEMPLATE = "https://maps.googleapis.com/maps/api/staticmap?size=%dx%d&path=enc:%s&key=" + API_KEY
IMAGE_SIZE = (230, 230)
TPL_FILE_NAME = 'directions.mustache'

output_file_name = "directions.html"

def get_map_base64(encoded_polyline):
  url = IMAGE_URL_TEMPLATE % (IMAGE_SIZE[0], IMAGE_SIZE[1], encoded_polyline)
  img_data = urllib.urlopen(url)
  return base64.b64encode(img_data.read())

def get_image_data(route):

  route['overview_polyline']['base64'] = get_map_base64(route['overview_polyline']['points'])

  for step in route['legs'][0]['steps']:
    step['polyline']['base64'] = get_map_base64(step['polyline']['points'])

def process_directions_data(route):
  get_image_data(route)
  return route

def get_directions(origin, destination, travel_mode, filename, save_dir):
  # template for html file
  tpl_file = codecs.open('directions.mustache', 'r', 'utf-8')
  tpl = pystache.parse(tpl_file.read())

  # access google maps api
  gmaps = googlemaps.Client(key=API_KEY)
  response = gmaps.directions(origin, destination, mode=travel_mode, departure_time=datetime.now())

  if len(response < 1):
    print "No results found! Try again with more specific places..."
    exit()

  # make modifications to json data
  route = process_directions_data(response[0])

  # render html template
  html = pystache.render(tpl, route)

  output_file_path = os.path.join(save_dir, filename)
  output = open(output_file_path, 'w')
  output.write(html)

  return output_file_path


# prompt user for input
print "Let's get started. Where are you coming from? (%s)" % (HOME_ADDRESS)
origin = raw_input("-> ")
print "Ok, now where are you going? (%s)" % (HOME_ADDRESS)
destination = raw_input("-> ")
print "Select from: transit, walking, bicycling, driving (driving)"
travel_mode = raw_input("-> ")
print "Name for directions file (%s)" % (output_file_name)
filename = raw_input("-> ")
filename = output_file_name if filename is None else filename
print "Where to save file? (%s)" % (SAVE_DIR)
save_dir = raw_input("-> ")
save_dir = SAVE_DIR if save_dir is None else save_dir

print "Getting results from Google..."
output = get_directions(origin, destination, travel_mode, filename, save_dir)
print "Directions saved to %s" % (output)






