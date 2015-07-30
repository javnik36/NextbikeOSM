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
        dist_m = round((dist * 1000), 2)  # WORKS!
        return dist_m

    def via_id(self, place):
        '''Return osm feature by ref matching'''
        # input: next_place (nextbike Place)
        nextb_ref = place.num
        for i in self.osm_data.nodes:
            for k, v in i.tags.items():
                if k == "ref":
                    if v == nextb_ref:
                        return i
                    else:
                        pass
        return None

    def via_distance(self, place):
        '''Return osm feature by distance matching'''
        dist = 10000000
        nearest = 0
        for i in self.osm_data.nodes:
            meas = self.measure(place, i)
            if meas < dist:
                dist = meas
                nearest = i
            elif meas > dist:
                continue
        return [nearest, dist]

    def pair(self, next_places):
        '''Makes pair of OSM and Nexbike features by they's distance.'''
        # input: list of next_places from city & osm
        dane = []
        for i in next_places:
            id_match = self.via_id(i)
            if id_match != None:
                meas = self.measure(i, id_match)

                fway = self.osm_data.find(id_match.iD, 'w')
                if fway != None:
                    d1 = (meas, i, fway, 'w', 'id')
                else:
                    d1 = (meas, i, id_match, 'n', 'id')
                dane.append(d1)
            else:
                data = self.via_distance(i)
                obj = data[0]
                meas = data[1]

                fway = self.osm_data.find(obj.iD, 'w')
                if fway != None:
                    d1 = (meas, i, fway, 'w', 'di')
                else:
                    d1 = (meas, i, obj, 'n', 'di')
                dane.append(d1)

        self.pair_bank = dane

    def html_it(self):
        '''Produces html with processing data.'''
        import difflib as SC
        from time import localtime, strftime
        timek = strftime("%a, %d %b @ %H:%M:%S", localtime())
        self.html = '''<html>\n<head>
        <link rel="icon" type="image/png" href="../favs/db-32x32.png" sizes="32x32">
        <link rel="icon" type="image/png" href="../favs/db-194x194.png" sizes="194x194">
        <link rel="icon" type="image/png" href="../favs/db-96x96.png" sizes="96x96">
        <link rel="icon" type="image/png" href="../favs/db-16x16.png" sizes="16x16">
        <meta charset="UTF-8">\n<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>\n<script type="text/javascript" src="./jquery.floatThead.min.js"></script>\n</head>
        <body>
        <script>
        $(function() {
            $('table').floatThead({
                useAbsolutePositioning: true
            });
        });
        </script>
        <style>
            table, td, tr, th{
                border: 1px solid black;
                border-collapse: collapse;
            }
            thead{
                background-color: white;
                /*border: 1px solid black;*/
            }
            .fill{
                background-color: #D4D4D4;
            }
            .red{
                background-color: #FF8080;
            }
            </style>'''
        self.html += "<i>Updated: " + timek + "</i>"
        self.html += '''
        <table>
            <thead>
            <tr>
                <th rowspan="2">NextBike<br>uid</th>
                <th rowspan="2">OSM id<br>(closest match)</th>
                <th rowspan="2">Distance<br>(in meters)</th>
                <th colspan="2">Name</th>
                <th colspan="2">Ref</th>
                <th colspan="2">Stands</th>
                <th rowspan="2">Network</th>
                <th rowspan="2">Operator</th>
            </tr>
            <tr>
                <th>nextbike</th>
                <th>osm</th>
                <th>nextbike</th>
                <th>osm</th>
                <th>nextbike</th>
                <th>osm</th>
            </tr>
            </thead>
            <tbody>
            '''
        counter = 1
        for i in self.pair_bank:
            dist = i[0]
            nextb = i[1]
            osm = i[2]
            if i[-2] == 'w':
                mapa1 = '<a href="http://www.openstreetmap.org/way/{uid}">{uid}</a>'
            else:
                mapa1 = '<a href="http://www.openstreetmap.org/node/{uid}">{uid}</a>'
            mapa2 = '<a href="http://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=19/{lat}/{lon}">{uid}</a>'
            josm = '<a href="http://localhost:8111/load_and_zoom?left={minlon}&right={maxlon}&top={maxlat}&bottom={minlat}">josm</a>'
            stry = "<td class='red'>"
            offset = 0.0009

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
                mapa2.format(lat=nextb.lat, lon=nextb.lon, uid=nextb.uid) + '\n' + josm.format(minlon=str((float(nextb.lon) - offset)),
                                                                                               maxlon=str((float(nextb.lon) + offset)), minlat=str((float(nextb.lat) - offset)), maxlat=str((float(nextb.lat) + offset))) + en
            self.html += st + mapa1.format(uid=osm.iD) + en
            if dist > 50 and i[-1] == 'id':
                self.html += stry + '<b>' + str(dist) + '</b>' + en
            elif dist > 50:
                self.html += stry + str(dist) + en
            elif i[-1] == 'id':
                self.html += st + '<b>' + str(dist) + '</b>' + en
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
        self.html += '''</tbody></table>\n</body>\n</html>'''

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

    def is_whatever(self, path):
        from time import localtime, strftime
        timek = strftime("%a, %d %b @ %H:%M:%S", localtime())

        if self.osm_data.nodes == [] and self.osm_data.ways == []:
            self.html = '''<html>\n<head><meta charset="UTF-8"></head>\n<body>\n<h2>Received empty dataset...sorry :(</h2><br>Add some data in this vicinity, then look here later.<br><br><i>Last checked: {last}</i></body>\n</html>'''.format(
                last=timek)
            self.save_it(path)
            raise ValueError("OSM Data not found!")

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
            c.is_whatever(html)
            c.pair(d)
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
            c.is_whatever(html)
            c.pair(d)
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
            c.pair(d)
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
        pass
