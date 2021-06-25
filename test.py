import googlemaps
import os
import configparser
from notion.client import NotionClient
from notion.block import ImageBlock, MapsBlock

class Place:
  """
  A class used to represent an place returned by the Google Places API.

  Attributes
  ----------
  name : str        name of the place
  address : str     address of the place
  type : list       list of types that describe the place
  photo : str       path
  """

  def __init__(self, record):
    self.name = record["name"]
    self.address = record["formatted_address"]
    self.type = self.get_type(record["types"])
    self.photo = self.save_photo(record)

  def get_type(self, types):
    filtered_types = ["point_of_interest",
                      "establishment"]
    lst = []
    for t in types:
      if t not in filtered_types:
        lst.append(t.replace("_"," ").title())

    return lst

  # Saves photo and returns path
  def save_photo(self, record):
    if "photos" not in record or len(record["photos"]) == 0:
      raise ValueError("No photo found")
    photo = record["photos"][0]
    places_photo = gmaps.places_photo(photo["photo_reference"], max_width=400)
    if not os.path.exists(query):
      os.mkdir(query)
    path = "/".join([query,self.name])
    if places_photo:
      f = open(path, 'wb')
      for chunk in places_photo:
        if chunk:
          f.write(chunk)
      f.close()
    return path

  def __str__(self):
    return "\n".join([self.name, self.address, str(self.type)])

def get_results(query):
  places = []
  response = gmaps.places(query)
  while (len(places) < num_results):
    for result in response["results"]:
      try:
        record = gmaps.place(result["place_id"])
        places.append(Place(record["result"]))
      except ValueError:
        continue
      if len(places) == num_results:
        return places
    response = gmaps.places(query, response["next_page_token"])
  return places

def add_places_to_database(places):
  cv = notion_client.get_collection_view(notion_url)
  collection = cv.collection
  for place in places:
    page = collection.add_row()
    page.name = place.name
    page.set_property("Address", place.address)
    page.set_property("Type", place.type)
    if place.photo:
      image = page.children.add_new(ImageBlock, width=400)
      image.upload_file(place.photo)

print("Reading config")
config = configparser.ConfigParser()
config.read('config.txt')
notion_client = NotionClient(token_v2=config['Notion']['token'])
notion_url = config['Notion']['database_url']
gmaps = googlemaps.Client(key=config['Maps']['key'])
query = config['Maps']['query']
num_results = int(config['Maps']['num_results'])

print("Finding results for", query)
places = get_results(query)

print("Found", len(places), "results.")

print("Adding places to database.")
add_places_to_database(places)

