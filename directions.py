import googlemaps
import pystache
import os, json, codecs, urllib, base64, datetime, time, tempfile

# set constants
API_KEY = os.environ['DUMBP_GMAPS_API_KEY']
HOME_ADDRESS = os.environ['DUMBP_HOME_ADDRESS']
SAVE_DIR = os.environ['DUMBP_SAVE_DIR']
IMAGE_URL_TEMPLATE = "https://maps.googleapis.com/maps/api/staticmap?size=%dx%d&path=enc:%s&key=" + API_KEY
IMAGE_SIZE = (230, 230)
INPUT_PROMPT = "-> "
TPL_FILE_NAME = 'directions.mustache'

output_file_name = time.time()

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

def process_directions_data(route):
  get_image_data(route)
  return route

def get_directions(origin, destination, travel_mode):
  # template for html file
  tpl_file = codecs.open('directions.mustache', 'r', 'utf-8')
  tpl = pystache.parse(tpl_file.read())

  # access google maps api
  gmaps = googlemaps.Client(key=API_KEY)
  now = datetime.datetime.now()
  response = gmaps.directions(origin, destination, mode=travel_mode, departure_time=now)

  if len(response) < 1:
    print "No results found! Try again with more specific places..."
    exit()

  # make modifications to json data
  route = process_directions_data(response[0])

  # render html template
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
print "Name for directions file (extension will be added) (%d.html)" % (output_file_name)
filename = input_default(INPUT_PROMPT, output_file_name) + ".html"
print "Automatically send via bluetooth? (Yn)"
bluetooth = raw_input(INPUT_PROMPT)
bluetooth = False if bluetooth.lower() == "n" else True


# print "Where to save file? (%s)" % (SAVE_DIR)
# save_dir = input_default(INPUT_PROMPT, SAVE_DIR)

print "Getting results from Google..."
html = get_directions(origin, destination, travel_mode)

output_file_path = os.path.join(tempfile.gettempdir(), filename)
output_file = open(output_file_path, 'w')
output_file.write(html)

if bluetooth:
  print "Sending file to Bluetooth File Exchange"
  open_in_bluetooth_file_exchange(output_file_path)
else:
  print "Opening file in browser"
  os_open(output_file_path)

print "Press any key to delete file at %s and exit" % (output_file_path)
done = raw_input("")

os.remove(output_file_path)


