import pystache
import polyline
import os, json, codecs, urllib, base64

API_KEY = os.environ['GMAPS_API_KEY']

data_file = open('directions.json', 'r')
tpl_file = codecs.open('directions.mustache', 'r', 'utf-8')

data = json.loads(data_file.read())
tpl = pystache.parse(tpl_file.read())

data = data[0]

print data

html = pystache.render(tpl, data)

print html

html_file = open('directions.html', 'w')
html_file.write(html)

# points = polyline.decode("erlqGxbbxP{B?eA?")

# points_str = '|'.join(["%f,%f" % (x[0], x[1]) for x in points])

# print points
# print points_str

size = (250, 250)
path = "erlqGxbbxP{B?eA?"

map_url = "https://maps.googleapis.com/maps/api/staticmap?size=%dx%d&path=enc:%s&key=%s" % (size[0], size[1], path, API_KEY)

# urllib.urlretrieve(map_url, "images/map_test.png")

image_data = urllib.urlopen(map_url)

image_data_encoded = base64.b64encode(image_data.read())

encoded_image_src = "data:image/png;base64,%s" % (image_data_encoded)

print encoded_image_src