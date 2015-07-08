class Node:
    def __init__(self, iD, lat, lon, tags):
        self.iD = iD
        self.lat = lat
        self.lon = lon
        self.tags = tags #[]

    def __str__(self):
        return str(self.iD)+ " @lat: " + str(self.lat) + " @lon: " + str(self.lon) + " $tags " + str(len(self.tags))

class Way:
    def __init__(self, iD, nodes, tags, fake_node=None):
        self.iD = iD
        self.nodes = nodes #[]
        self.tags = tags #{}
        self.fake_node = None

    def __str__(self):
        return str(self.iD) + " $points " + str(len(self.nodes)) + " $tags " + str(len(self.tags))

    def fill(self, node_s):
        '''Can be done in OSM processing class?'''
        temp = []
        for point in self.nodes:
            for obj in node_s:
                if obj.iD == point:
                    temp.append( (obj.lat,obj.lon) )
        self.nodes = temp

    def fake_it(self):
        import statistics as s
        #nodes = [  (y,x)  ]
        y = []
        x = []
        for i in self.nodes:
            y.append(i[0])
            x.append(i[1])

        y_s = s.mean(max(y), min(y))
        x_s = s.mean(max(x), min(x))
        self.fake_node = (y_s, x_s)
        return y_s, x_s
