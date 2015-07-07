class Place:
    def __init__(self, uid, lat, lon, name, num, stands, bike_numbers=None):
        self.uid = uid
        self.lat = lat
        self.lon = lon
        self.name = name
        self.num = num
        self.stands = stands
        self.bike_numbers = []

    def __str__(self):
        return "#" + str(self.uid) + ": " + str(self.num) + "," + self.name + " with " + str(self.stands) + " stands. $lat$" + str(self.lat) + " $lon$" + str(self.lon) + " $bike_numbers$" + str(len(self.bike_numbers))

class City:
    def __init__(self, uid, name, places=None):
        self.uid = uid
        self.name = name
        self.places = []

    def __str__(self):
        return "#" + str(self.uid) + " @" + self.name + " with " + str(len(self.places)) + " places."

class Country:
    def __init__(self, name, country, cities=None):
        self.name = name
        self.country = country
        self.cities = []

    def __str__(self):
        return "$" + self.name + " @" + self.country + " with " + str(len(self.cities)) + " cities."
