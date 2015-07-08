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
