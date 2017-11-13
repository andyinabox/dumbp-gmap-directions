import googlemaps
import pystache
import os, json, codecs, urllib, base64, time, tempfile
from datetime import datetime
import parsedatetime

# set constants
API_KEY = os.environ['DUMBP_GMAPS_API_KEY']
HOME_ADDRESS = os.environ['DUMBP_HOME_ADDRESS']
IMAGE_URL_TEMPLATE = "https://maps.googleapis.com/maps/api/staticmap?size=%dx%d&path=enc:%s&key=" + API_KEY
IMAGE_SIZE = (230, 230)
INPUT_PROMPT = "-> "
TPL_FILE_NAME = 'tpl/directions.mustache'

output_file_name = str(time.time())

# utility function to take input with default value
def input_default(prompt, default_value):
    value = raw_input(prompt)
    value = default_value if not value else value
    return value

def get_map_base64(encoded_polyline):
  url = IMAGE_URL_TEMPLATE % (IMAGE_SIZE[0], IMAGE_SIZE[1], encoded_polyline)
  img_data = urllib.urlopen(url)
  return base64.b64encode(img_data.read())

def get_image_data(route):

  route['overview_polyline']['base64'] = get_map_base64(route['overview_polyline']['points'])

  for step in route['legs'][0]['steps']:
    step['polyline']['base64'] = get_map_base64(step['polyline']['points'])

def set_transit_flags(route, travel_mode):
  route["is_transit"] = travel_mode is "transit"
  route["travel_mode"] = travel_mode

  # for step in route['legs'][0]['steps']:
    # step['is_transit'] = True if step['travel_mode'].lower() is "transit" else False


def get_directions(origin, destination, travel_mode, departure_time, add_info=True):
  # access google maps api
  gmaps = googlemaps.Client(key=API_KEY)
  response = gmaps.directions(origin, destination, mode=travel_mode, departure_time=departure_time)

  if len(response) < 1:
    print "No results found! Try again with more specific places..."
    exit()

  route = response[0]

  if add_info:
    route["origin_name"] = "Home" if origin is HOME_ADDRESS else origin
    route["destination_name"] = "Home" if destination is HOME_ADDRESS else destination
    route["travel_mode"] = travel_mode

  # make modifications to json data
  return route



def render_template(route, tpl, include_details=True):

  # process data
  route["include_details"] = include_details

  # rename sub-steps to be more mustache-friendly
  for step in route['legs'][0]['steps']:
    if 'steps' in step:
      step['sub_steps'] = step['steps']
      del step['steps']

  # get maps
  get_image_data(route)
  return pystache.render(tpl, route)

# open in Bluetooth File Exchange
# http://hints.macworld.com/article.php?story=20040413031046870
def open_in_bluetooth_file_exchange(file_path):
  os.system("/usr/bin/open -a /Applications/Utilities/Bluetooth\ File\ Exchange.app %s" % file_path)

def os_open(file_path):
  os.system("/usr/bin/open %s" % file_path)


# # prompt user for input
print "Let's get started. Where are you coming from? (%s)" % (HOME_ADDRESS)
origin = input_default("->", HOME_ADDRESS)

print "Ok, now where are you going? (%s)" % (HOME_ADDRESS)
destination = input_default(INPUT_PROMPT, HOME_ADDRESS)

print "Select from: transit, walking, bicycling, driving (driving)"
travel_mode = raw_input(INPUT_PROMPT)

print "What time will you leave (now)"
departure_time = raw_input(INPUT_PROMPT)
if departure_time:
  cal = parsedatetime.Calendar()
  time_struct, parse_status = cal.parse(departure_time)
  if parse_status:
    departure_time = datetime(*time_struct[:6])
  else:
    print "I didn't understand that. Setting departure time to now."
    departure_time = datetime.now()
else:
  departure_time = datetime.now()


print "Name for directions file (extension will be added) (%s.html)" % (output_file_name)
filename = input_default(INPUT_PROMPT, output_file_name) + ".html"

print "Include detailed directions? (Yn)"
include_details = raw_input(INPUT_PROMPT)
include_details = False if include_details.lower() == "n" else True

print "Automatically send via bluetooth? (Yn)"
bluetooth = raw_input(INPUT_PROMPT)
bluetooth = False if bluetooth.lower() == "n" else True


print "Getting results from Google..."
route = get_directions(origin, destination, travel_mode, departure_time)

print "Rendering HTML..."
# template for html file
tpl_file = codecs.open('tpl/directions.mustache', 'r', 'utf-8')
tpl = pystache.parse(tpl_file.read())
html = render_template(route, tpl, include_details)

# save file
output_file_path = os.path.join(tempfile.gettempdir(), filename)
output_file = open(output_file_path, 'w')
output_file.write(html)

# either send to bluetooth or open
if bluetooth:
  print "Sending file to Bluetooth File Exchange"
  open_in_bluetooth_file_exchange(output_file_path)
else:
  print "Opening file in browser"
  os_open(output_file_path)

print "Press any key to delete file at %s and exit" % (output_file_path)
done = raw_input("")

os.remove(output_file_path)


