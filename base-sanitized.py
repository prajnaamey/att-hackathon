import urllib.parse
import json
import pprint
import os
import http.client
from googleplaces import GooglePlaces, types, lang

YOUR_API_KEY = 'key'
google_places = GooglePlaces(YOUR_API_KEY)


class base(object):
    """docstring for base"""

    def __init__(self, data):
        self.data = data
        self.conceptmap = {}
        self.location = None

    def parse_request(self):

        print("parsing request")
        pprint.pprint(self.data)

        concepts = self.data['concepts']

        for concept in concepts:
            name = concept
            value = concepts[concept][0]
            self.conceptmap[name] = value['literal']

        print(self.conceptmap)
        self.get_location()

    def get_location(self):
        query_result = google_places.nearby_search(
            location='47.6049811, -122.3342493', keyword=self.conceptmap['location'],
            radius=500, types=[types.TYPE_CAFE])

        total_res = len(query_result.places)

        self.location = query_result.places[total_res - 1]
        print(type(self.location))
        print(self.location)
        self.location = self.location.geo_location
        print(type(self.location))
        print(self.location)

        self.send_location()

    def send_location(self):

        conn = http.client.HTTPSConnection("api-m2x.att.com")
        headers = {
            'Content-type': 'application/json',
            'X-M2X-KEY': 'key'
        }

        location = str(self.location['lat']) + ',' + str(self.location['lng'])

        content = {
            "name": "GO",
            "data": {
                "location": location 
            },
            "targets": {"devices": ["client-dev-key"]}
        }

        json_content = json.dumps(content).encode('utf-8')

        print(json_content)

        conn.request("POST", "/v2/commands/", json_content, headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()

        if response.status != 200:
            print(response, data)
            return False
        else:
            return True
