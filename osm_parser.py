class osmParser:

    def __init__(self, nodes=None, ways=None):
        import xml.etree.ElementTree as XML
        import osm_class as OC

        plik = XML.parse("export.osm")
        root = plik.getroot()

        nodes_list = []
        ways_list = []

        for child in root:
            if child.tag == "note" or child.tag == "meta":
                pass
            elif child.tag == "node":
                iD = child.attrib["id"]
                lat = child.attrib["lat"]
                lon = child.attrib["lon"]
                tags = {}
                for tag in child:
                    if tag.attrib["k"] == "amenity":
                        pass
                    elif tag.attrib["k"] in ["capacity", "name", "network", "operator", "ref", "website", "source"]:
                        k = tag.attrib["k"]
                        v = tag.attrib["v"]
                        tags[k] = v

                c = OC.Node(iD, lat, lon, tags)
                nodes_list.append(c)
            elif child.tag == "way":
                iD = child.attrib["id"]
                nodes = []
                tags = {}
                for instance in child:
                    if instance.tag == "nd":
                        nodes.append(instance.attrib["ref"])
                    else:
                         if instance.attrib["k"] == "amenity":
                             pass
                         elif instance.attrib["k"] in ["capacity", "name", "network", "operator", "ref", "website", "source"]:
                             k = instance.attrib["k"]
                             v = instance.attrib["v"]
                             tags[k] = v

                w = OC.Way(iD, nodes, tags)
                ways_list.append(w)

        self.nodes = nodes_list
        self.ways = ways_list

    def __str__(self):
        return "Found " + str(len(self.nodes)) + " nodes and " + str(len(self.ways)) + " ways."

    def find_node(self, iD):
        '''Returns data from iD searched'''
        for i in self.nodes:
            if i.iD == iD:
                return i

    def fill_ways(self):
        '''Can be done in OSM processing class?'''
        temp = []
        for way in self.ways:
            for node in way.nodes:
                print(node)
                p = self.find_node(node)
                print(p)

                node = (p.lat, p.lon)
                print(node)
            print(way)

    def fake_all(self):
        '''Run fake_it for all ways in Class'''
        for way in self.ways:
            way.fake_it()

    def dumb_nodes(self):
        print("DUMBING ALL NODES:................")
        for i in self.nodes:
            print(i)
            print("ID:   " + i.iD + ";LAT:   " + i.lat + ";LON:   " + i.lon)# + ";TAGS:   " + print(key, value) for key, value in i.tags.items())
        print("DUMBED NODES#")

    def dumb_ways(self):
        print("DUMBING ALL WAYS:................")
        for i in self.ways:
            print(i)
        print("DUMBED WAYS#")
