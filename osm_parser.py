class osmParser:

    def __init__(self, path="export.osm", nodes=None, ways=None):
        self.path = path
        import xml.etree.ElementTree as XML
        import osm_class as OC

        plik = XML.parse(self.path)
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

                # if len(list(child)) != 0:
                for tag in child:
                    if tag.attrib["k"] == "amenity":
                        pass
                    elif tag.attrib["k"] in ["capacity", "name", "network", "operator", "ref", "website", "source"]:
                        k = tag.attrib["k"]
                        v = tag.attrib["v"]
                        tags[k] = v
                c = OC.Node(iD, lat, lon, tags)
                nodes_list.append(c)
                # else:
                #     break

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

    def find(self, iD, mode='n'):
        '''Returns data from iD searched'''
        if mode == 'n':
            for i in self.nodes:
                if i.iD == iD:
                    return i
        elif mode == 'w':
            for i in self.ways:
                if i.iD == iD:
                    return i
        else:
            raise ValueError

    def clear_nodes(self):
        new_nodes = []
        for i in self.nodes:
            if len(i.tags) == 0:
                pass
            else:
                new_nodes.append(i)
        self.nodes = new_nodes

    def fill_ways(self):
        '''Fills up ways with data from nodes'''
        for way in self.ways:
            new_nodes = []
            for node in way.nodes:
                p = self.find(node)
                node = (p.lat, p.lon)
                new_nodes.append(node)
            way.nodes = new_nodes

    def fake_all(self):
        '''Run fake_it for all ways in Class'''
        for way in self.ways:
            way.fake_it()
            fi = way.fake_instance()
            self.nodes.append(fi)

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
