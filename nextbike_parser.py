class NextbikeParser:

    '''Aggregates Nextbike country Classes'''

    def __init__(self, countrys=None):
        import xml.etree.ElementTree as XML
        import nextbike_class as NC
        import urllib.request as urllib
        import os

        path = "https://nextbike.net/maps/nextbike-live.xml"
        if "nextbike.xml" in os.listdir():
            pass
        else:
            urllib.urlretrieve(path, "nextbike.xml")

        plik = XML.parse("nextbike.xml")
        root = plik.getroot()

        C_list = []

        for country in root:
            cities_list = []

            name = country.attrib["name"]
            coun = country.attrib["country"]

            C = NC.Country(name, coun)
            for city in country:
                place_list = []

                uid = city.attrib["uid"]
                name = city.attrib["name"]

                c = NC.City(uid, name)

                for place in city:
                    try:
                        uid = place.attrib["uid"]
                        lat = place.attrib["lat"]
                        lon = place.attrib["lng"]
                        name = place.attrib["name"]
                        try:
                            num = place.attrib["number"]
                        except:
                            num = 9999
                        try:
                            bike_stands = place.attrib["bike_racks"]
                        except:
                            bike_stands = "!"
                        try:
                            bike_nrs = place.attrib["bike_numbers"]
                            n = NC.Place(
                                uid, lat, lon, name, num, bike_stands, bike_nrs)
                        except:
                            n = NC.Place(uid, lat, lon, name, num, bike_stands)

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
                    e = city.places
                    return e

    def get_uids(self, cons="n"):
        '''Makes file with all uids from xml-file. If cons='y' it's print it to console too.'''
        temp = []
        for c in self.countrys:
            p = c.name
            temp.append("_______________")
            temp.append(p)
            for ci in c.cities:
                a = ci.get_uid()
                b = str(ci.name)
                c = a + ' ' + b
                temp.append(c)

        plik = open("nextbike_uids.txt", 'w', encoding="utf-8")
        plik.write("Network\nuid<<>>city name\n")
        for i in temp:
            if cons == "y":
                print(str(i))
            plik.write(str(i) + '\n')
        plik.close()

    @staticmethod
    def update():
        '''Updates xml manually'''
        import urllib.request as urllib
        path = "https://nextbike.net/maps/nextbike-live.xml"
        urllib.urlretrieve(path, "nextbike.xml")
