import osm_parser as OP
import nextbike_parser as NP

class NextbikeValidator:
    def __init__(self, next_data, osm_data, pair_bank=None, html=None):
        self.next_data = next_data
        self.osm_data = osm_data
        self.pair_bank = []
        self.html = html

    def measure(self, point_next, point_osm):
        import math as m
        lat_next = float(point_next.lat)
        lon_next = float(point_next.lon)
        lat_osm = float(point_osm.lat)
        lon_osm = float(point_osm.lon)

        #test field
        # lat_next = float(52.28584837775539)
        # lon_next = float(20.940569043159485)
        # lat_osm = float(52.2858671)
        # lon_osm = float(20.9405856)

        R = 6378.41
        #Haversine formula
        dist = 2*R* m.asin( m.sqrt( (m.sin(m.radians(0.5*(lat_next-lat_osm))))**2 + m.cos(m.radians(lat_osm))*m.cos(m.radians(lat_next))*(m.sin(m.radians(0.5*(lon_next-lon_osm))))**2 )) #in KM
        dist_m = dist * 1000 #WORKS!
        return dist_m

    def pair_it(self, next_places):
        #input: list of next_places from city & osm
        dane = []
        for i in next_places:
            dist = 10000000
            nearest = 0
            for t in self.osm_data.nodes:
                meas = self.measure(i,t)
                if meas < dist:
                    dist = meas
                    nearest = t
                elif meas > dist:
                    continue

            d1 = (dist, i, nearest)
            dane.append(d1)

        self.pair_bank = dane
        # return dane

    def html_it(self):
        self.html = '''<html>\n
        <body>\n
        <table>\n
            <tr>\n
                <th rowspan="2">NextBike uid</th>\n
                <th rowspan="2">OSM id(closed match)</th>\n
                <th rowspan="2">Distance(in meters)</th>\n
                <th colspan="2">Name</th>\n
                <th colspan="2">Ref</th>\n
                <th colspan="2">Stands</th>\n
            </tr>\n
            <tr>\n
                <th>nextbike</th>\n
                <th>osm</th>\n
                <th>nextbike</th>\n
                <th>osm</th>\n
                <th>nextbike</th>\n
                <th>osm</th>\n
            </tr>\n
            '''
        for i in self.pair_bank:
            P = "<tr>\n"
            K = "</tr>\n"
            st = "<td>\n"
            en = "</td>\n"
            mapa1 = '<a href="http://www.openstreetmap.org/node/{uid}">{uid}</a>'
            mapa2 = '<a href="http://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=19/{lat}/{lon}">{uid}</a>'
            dist = i[0]
            nextb = i[1]
            osm = i[2]
            self.html += P + st
            self.html += mapa2.format(lat=nextb.lat, lon=nextb.lon, uid=nextb.uid) + en + st
            self.html += mapa1.format(uid=osm.iD) + en + st
            self.html += str(dist) + en + st
            self.html += nextb.name + en + st
            try:
                self.html += osm.tags.get("name") + en + st
            except:
                self.html += "BRAK" + en + st
            self.html += nextb.num + en + st
            try:
                self.html += osm.tags.get("ref") + en + st
            except:
                self.html += "BRAK" + en + st
            self.html += nextb.stands + en + st
            try:
                self.html += osm.tags.get("capacity") + en + K
            except:
                self.html += "BRAK" + en + K
        self.html += '''</table>\n</body>\n</html>'''

    def save_it(self, nazwa):
        plik = open(nazwa, 'w')
        save = plik.write(self.html)
        plik.close()




    # def tagging(self):
            # def
            ##NEXT vs osm
            # uid  !=     iD
            # lat         lat
            # lon         lon
            # name        name {tags}
            # num         ref {tags}
            # stands      capacity {tags}++


a = OP.osmParser()
b = NP.NextbikeParser()
c = NextbikeValidator(b,a)
d = b.find("VETURILO Poland")
c.pair_it(d)
c.html_it()
c.save_it("RESUME.html")
