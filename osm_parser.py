class Node:

    def __init__(self, iD, lat, lon, tags):
        self.iD = iD
        self.lat = lat
        self.lon = lon
        self.tags = tags  # []

    def __str__(self):
        return str(self.iD) + " @lat: " + str(self.lat) + " @lon: " + str(self.lon) + " $tags " + str(len(self.tags))


class Way:

    def __init__(self, iD, nodes, tags, fake_node=None):
        self.iD = iD
        self.nodes = nodes  # []
        self.tags = tags  # {}
        self.fake_node = None

    def __str__(self):
        return str(self.iD) + " $points " + str(len(self.nodes)) + " $tags " + str(len(self.tags))

    def fake_it(self):
        #nodes = [  (y,x)  ]
        count = 0
        y_count = 0
        x_count = 0
        for i in self.nodes:
            y_count += float(i[0])
            x_count += float(i[1])
            count += 1

        y_s = y_count / count
        x_s = x_count / count
        self.fake_node = (y_s, x_s)
        return y_s, x_s

    def fake_instance(self):
        return Node(self.iD, self.fake_node[0], self.fake_node[1], self.tags)


class osmParser:

    def __init__(self, path="export.osm", nodes=None, ways=None):
        self.path = path
        import xml.etree.ElementTree as XML

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
                        if tag.attrib["v"] == "bicycle_rental":
                            tags["is_rental"] = "yes"
                    elif tag.attrib["k"] in ["capacity", "name", "network", "operator", "ref", "website", "source"]:
                        k = tag.attrib["k"]
                        v = tag.attrib["v"]
                        tags[k] = v
                c = Node(iD, lat, lon, tags)
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
                            if tag.attrib["v"] == "bicycle_rental":
                                tags["is_rental"] = "yes"
                        elif instance.attrib["k"] in ["capacity", "name", "network", "operator", "ref", "website", "source"]:
                            k = instance.attrib["k"]
                            v = instance.attrib["v"]
                            tags[k] = v

                w = Way(iD, nodes, tags)
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
            # + ";TAGS:   " + print(key, value) for key, value in i.tags.items())
            print("ID:   " + i.iD + ";LAT:   " + i.lat + ";LON:   " + i.lon)
        print("DUMBED NODES#")

    def dumb_ways(self):
        print("DUMBING ALL WAYS:................")
        for i in self.ways:
            print(i)
        print("DUMBED WAYS#")
