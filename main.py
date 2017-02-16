#!/usr/bin/env python
from base import base

data = None
client = base(data)

location = {'lat': '47.6049811', 'lng': '-122.3342493'}

client.send_location(location)