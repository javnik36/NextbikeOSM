class NextbikeParser:
    '''Aggregates Nextbike country Classes'''

    def __init__(self, countrys=None):
        import xml.etree.ElementTree as XML
        import nextbike_class as NC

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
                            n = NC.Place(uid, lat, lon, name, num, bike_stands, bike_nrs)
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
        #self.countrys = []

    def find(self, name):
        for i in self.countrys:
            if i.name == name:
                d = i.cities[0]
                e = d.places
                return e
