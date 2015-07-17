import osm_parser as OP
import nextbike_parser as NP


class NextbikeValidator:

    '''Analyzer class'''

    def __init__(self, next_data, osm_data, pair_bank=None, html=None):
        self.next_data = next_data
        self.osm_data = osm_data
        self.pair_bank = []
        self.html = html

    def measure(self, point_next, point_osm):
        '''Measures distance between 2 points with Haversine formula.'''
        import math as m
        lat_next = float(point_next.lat)
        lon_next = float(point_next.lon)
        lat_osm = float(point_osm.lat)
        lon_osm = float(point_osm.lon)

        R = 6378.41
        # Haversine formula
        dist = 2 * R * m.asin(m.sqrt((m.sin(m.radians(0.5 * (lat_next - lat_osm))))**2 + m.cos(m.radians(
            lat_osm)) * m.cos(m.radians(lat_next)) * (m.sin(m.radians(0.5 * (lon_next - lon_osm))))**2))  # in KM
        dist_m = dist * 1000  # WORKS!
        return dist_m

    def pair_it(self, next_places):
        '''Makes pair of OSM and Nexbike features by they's distance.'''
        # input: list of next_places from city & osm
        dane = []
        for i in next_places:
            dist = 10000000
            nearest = 0
            for t in self.osm_data.nodes:
                meas = self.measure(i, t)
                if meas < dist:
                    dist = meas
                    nearest = t
                elif meas > dist:
                    continue

            fway = self.osm_data.find(nearest.iD, 'w')
            if fway != None:
                d1 = (dist, i, fway, 'w')
            else:
                d1 = (dist, i, nearest)
            dane.append(d1)

        self.pair_bank = dane
        # return dane

    def html_it(self):
        '''Produces html with processing data.'''
        import difflib as SC
        self.html = '''<html>\n<head><meta charset="UTF-8"></head>\n
        <body>\n
        <style>
            table{
                border: 1px solid black;
                border-collapse: collapse;
            }
            th{
                text-align: center;
                vertical-align: center;
                border: 1px solid black;
            }
            td, tr{
                border: 1px solid black;
            }
            .fill{
                background-color: #D4D4D4;
            }
            .red{
                background-color: #FF8080;
            }
            </style>
        <table>\n
            <tr>\n
                <th rowspan="2">NextBike<br>uid</th>\n
                <th rowspan="2">OSM id<br>(closest match)</th>\n
                <th rowspan="2">Distance<br>(in meters)</th>\n
                <th colspan="2">Name</th>\n
                <th colspan="2">Ref</th>\n
                <th colspan="2">Stands</th>\n
                <th rowspan="2">Network</th>\n
                <th rowspan="2">Operator</th>\n
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
        counter = 1
        for i in self.pair_bank:
            dist = i[0]
            nextb = i[1]
            osm = i[2]
            if i[-1] == 'w':
                mapa1 = '<a href="http://www.openstreetmap.org/way/{uid}">{uid}</a>'
            else:
                mapa1 = '<a href="http://www.openstreetmap.org/node/{uid}">{uid}</a>'
            mapa2 = '<a href="http://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=19/{lat}/{lon}">{uid}</a>'
            stry = "<td class='red'>"

            if counter % 2 != 0:
                P = "<tr>\n"
                K = "</tr>\n"
                st = "<td class='fill'>\n"
                en = "</td>\n"
            else:
                P = "<tr>\n"
                K = "</tr>\n"
                st = "<td>\n"
                en = "</td>\n"

            counter += 1
            self.html += P
            self.html += st + \
                mapa2.format(lat=nextb.lat, lon=nextb.lon, uid=nextb.uid) + en
            self.html += st + mapa1.format(uid=osm.iD) + en
            if dist > 50:
                self.html += stry + str(dist) + en
            else:
                self.html += st + str(dist) + en
            self.html += st + nextb.name + en
            try:
                prob = SC.SequenceMatcher(
                    None, nextb.name, osm.tags.get("name")).ratio()
                if prob <= 0.8:
                    self.html += stry + osm.tags.get("name") + en
                else:
                    self.html += st + osm.tags.get("name") + en
            except:
                self.html += stry + "NONE" + en
            self.html += st + str(nextb.num) + en
            try:
                if int(nextb.num) == int(osm.tags.get("ref")):
                    self.html += st + osm.tags.get("ref") + en
                else:
                    self.html += stry + osm.tags.get("ref") + en
            except:
                self.html += stry + "NONE" + en
            self.html += st + nextb.stands + en
            try:
                if int(osm.tags.get("capacity")) == int(nextb.stands):
                    self.html += st + osm.tags.get("capacity") + en
                else:
                    self.html += stry + osm.tags.get("capacity") + en
            except:
                self.html += stry + "NONE" + en
            try:
                self.html += st + osm.tags.get("network") + en
            except:
                self.html += stry + "NONE" + en
            try:
                self.html += st + osm.tags.get("operator") + en + K
            except:
                self.html += stry + "NONE" + en + K
        self.html += '''</table>\n</body>\n</html>'''

    def save_it(self, nazwa="nextbikeOSM_results.html"):
        '''Saves html from self.html to file'''
        plik = open(nazwa, 'w', encoding="utf-8")
        save = plik.write(self.html)
        plik.close()

        # NEXT vs osm
        # uid  !=     iD
        # lat         lat
        # lon         lon
        # name        name {tags}
        # num         ref {tags}
        # stands      capacity {tags}++

if __name__ == "__main__":
    import sys
    try:
        if sys.argv[1] == "-a" and sys.argv[2] == "-u":
            place = sys.argv[3]
            path_osm = sys.argv[4]
            html = sys.argv[5]

            a = OP.osmParser(path_osm)
            a.fill_ways()
            a.clear_nodes()
            a.fake_all()
            NP.NextbikeParser.update()
            b = NP.NextbikeParser()
            b.get_uids()
            c = NextbikeValidator(b, a)
            if place.isnumeric():
                d = b.find_city(place)
            else:
                d = b.find_network(place)
            c.pair_it(d)
            c.html_it()
            c.save_it(html)
        elif sys.argv[1] == "-a":
            place = sys.argv[2]
            path_osm = sys.argv[3]
            html = sys.argv[4]

            a = OP.osmParser(path_osm)
            a.fill_ways()
            a.clear_nodes()
            a.fake_all()
            b = NP.NextbikeParser()
            b.get_uids()
            c = NextbikeValidator(b, a)
            if place.isnumeric():
                d = b.find_city(place)
            else:
                d = b.find_network(place)
            c.pair_it(d)
            c.html_it()
            c.save_it(html)
        elif sys.argv[1] == "-d":
            a = OP.osmParser()
            a.fill_ways()
            a.clear_nodes()
            a.fake_all()
            b = NP.NextbikeParser()
            b.get_uids()
            c = NextbikeValidator(b, a)
            d = b.find_network("VETURILO Poland")
            c.pair_it(d)
            c.html_it()
            c.save_it("RESUME.html")
        elif sys.argv[1] == "-u":
            NP.NextbikeParser.update()
        elif sys.argv[1] == "help":
            print(
                "python nextbike_valid.py -a (-u) network_name osm_path html_path")
            print("python nextbike_valid.py : guide for anyone")
            print("python nextbike_valid.py -d : default for debugging")
            print("python nextbike_valid.py -u : updates xml manually")
    except:
        path_osm = input("Write path to osm file:\n")
        a = OP.osmParser(path_osm)
        a.fill_ways()
        a.clear_nodes()
        a.fake_all()
        b = NP.NextbikeParser()
        b.get_uids()
        place = input(
            "______________\nWhat kind of network\city should I process?\n>If you want particular city please write it's uid number from nextbike_uids.txt\n>>For whole network write it's name(within ''), also from nextbike_uids.txt\n")
        c = NextbikeValidator(b, a)
        if place.isnumeric():
            d = b.find_city(place)
        else:
            d = b.find_network(place)
        c.pair_it(d)
        c.html_it()
        html = input("______________\nHTML name?\n")
        c.save_it(html)
        print("______________\nAll done...thanks!")
