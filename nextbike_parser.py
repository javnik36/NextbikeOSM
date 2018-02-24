import logging

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

    def __init__(self, uid, name, bounds, places=None):
        self.uid = uid
        self.name = name
        self.bounds = bounds
        self.places = []

    def __str__(self):
        return "#" + str(self.uid) + " @" + self.name + " with " + str(len(self.places)) + " places."

    def get(self, nr):
        if self.uid == nr:
            return self.places

    def get_uid(self):
        return self.uid

    def get_data(self):
        import overpass

        api = overpass.API(timeout=600)
        logging.debug(str(self.bounds))

        dane = api.Get('''node["amenity"="bicycle_rental"]{0};way["amenity"="bicycle_rental"]{0};'''.format(str(self.bounds)),verbosity="body;>;out skel qt",responseformat="xml")
        #dane = api.Get('''node["amenity"="bicycle_rental"]{0};way["amenity"="bicycle_rental"]{0}'''.format(str(self.bounds),str(self.bounds)),responseformat="xml")
        return dane


class Country:

    def __init__(self, name, country, cities=None):
        self.name = name
        self.country = country
        self.cities = []

    def __str__(self):
        return "$" + self.name + " @" + self.country + " with " + str(len(self.cities)) + " cities."


class NextbikeParser:

    '''Aggregates Nextbike country Classes'''

    def __init__(self, countrys=None):
        import xml.etree.ElementTree as XML
        import nosm_utils

        nosm_utils.refresh_nxtb()
        plik = XML.parse("nextbike.xml")
        root = plik.getroot()

        C_list = []

        for country in root:
            cities_list = []

            name = country.attrib["name"]
            coun = country.attrib["country"]

            C = Country(name, coun)
            for city in country:
                place_list = []

                uid = city.attrib["uid"]
                name = city.attrib["name"]
                bounds = city.attrib["bounds"]
                w_bounds = nosm_utils.get_bounds(bounds)
                logging.debug("Zapisuje współrzędne {0}".format(str(w_bounds)))
                c = City(uid, name, bounds=w_bounds)

                for place in city:
                    try:
                        uid = place.attrib["uid"]
                        lat = place.attrib["lat"]
                        lon = place.attrib["lng"]
                        name = place.attrib["name"]
                        try:
                            num = place.attrib["number"]
                        except:
                            num = 0000
                        try:
                            bike_stands = place.attrib["bike_racks"]
                        except:
                            bike_stands = "None"
                        try:
                            bike_nrs = place.attrib["bike_numbers"]
                            n = Place(
                                uid, lat, lon, name, num, bike_stands, bike_nrs)
                        except:
                            n = Place(uid, lat, lon, name, num, bike_stands)

                    except Exception as e:
                        print(e)
                        print(str(uid))

                    place_list.append(n)

                c.places = place_list
                cities_list.append(c)

            C.cities = cities_list
            C_list.append(C)
        self.countrys = C_list
        # self.countrys = []

    def __str__(self):
        for i in self.countrys:
            return i.name

    def find_network(self, name):
        '''Returns data for whole network'''
        db = []
        for i in self.countrys:
            if i.name == name:
                for city in i.cities:
                    e = city.places
                    db += e
        return db

    def find_city(self, name):
        '''Returns data for city only'''
        for i in self.countrys:
            for city in i.cities:
                if city.uid == str(name):
                    #e = city.places
                    e = city
                    return e

    def check_uids(self, new_uids):
        old_uids = []
        with open("uids.set", 'r') as f:
            for line in f.readlines():
                line = line.rstrip()
                old_uids.append(line)

        def diff(a, b):
            b = set(b)
            difr = [aa for aa in a if aa not in b]
            return difr

        removed = diff(old_uids, new_uids)
        new = diff(new_uids, old_uids)

        if removed != []:
            print("REMOVED UIDS FOUND! {0}".format(str(removed)))
        if new != []:
            print("NEW UIDS FOUND! {0}".format(str(new)))

    def get_uids(self, cons="n"):
        '''Makes file with all uids from xml-file. If cons='y' it's print it to console too.'''
        temp = []
        uids = []
        for c in self.countrys:
            p = c.name
            temp.append("_______________")
            temp.append(p)
            for ci in c.cities:
                a = ci.get_uid()
                b = str(ci.name)
                c = a + ' ' + b
                temp.append(c)
                uids.append(a)

        plik = open("nextbike_uids.txt", 'w', encoding="utf-8")
        plik.write("Network\nuid<<>>city name\n")
        for i in temp:
            if cons == "y":
                print(str(i))
            plik.write(str(i) + '\n')
        plik.close()

        self.check_uids(uids)

        with open("uids.set", 'w') as f:
            for i in uids:
                f.write("{0}\n".format(i))

    @staticmethod
    def update():
        '''Updates xml manually'''
        import urllib.request as urllib
        path = "https://nextbike.net/maps/nextbike-live.xml"
        urllib.urlretrieve(path, "nextbike.xml")
