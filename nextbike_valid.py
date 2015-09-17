import osm_parser as OP
import nextbike_parser as NP

__VERSION__ = '2.0.0'


class NextbikeValidator:

    '''Analyzer class'''

    def __init__(self, next_data, osm_data, pair_bank=None, html=None):
        from jinja2 import PackageLoader, Environment
        self.next_data = next_data
        self.osm_data = osm_data
        self.pair_bank = []
        self.html = html
        self.envir = Environment(
            loader=PackageLoader('nextbike_valid', 'templates'))

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

    def html_it(self, nazwa="nextbikeOSM_results.html", feed=False):
        '''Produces html with processing data.'''
        import difflib as SC
        from time import localtime, strftime
        timek = strftime("%a, %d %b @ %H:%M:%S", localtime())

        template = self.envir.get_template("base.html")

        dane = []
        timestamp = 'Updated: {0}'.format(timek)
        copyright = "Created using NextbikeOSM.py v.{0} by Javnik".format(
            __VERSION__)
        feed_info = '<a href="./{0}_atom.xml"><img src="../imgs/feed-icon-14x14.png"></a> '.format(
            nazwa.rstrip('.html'))

        for i in self.pair_bank:
            i_dict = {}
            i_dict['distance'] = i[0]
            i_dict['nxtb'] = i[1]
            i_dict['osm'] = i[2]
            i_dict['type'] = i[3]
            i_dict['match'] = i[4]

            nextb = i[1]
            osm = i[2]
            try:
                prob = SC.SequenceMatcher(
                    None, nextb.name, osm.tags.get("name")).ratio()
            except:
                prob = 0

            i_dict['prob'] = prob

            dane.append(i_dict)

        if feed:
            c = feed_info + copyright
            fill_template = template.render(
                {'items': dane, 'timek': timestamp, 'copy': c})
        else:
            fill_template = template.render(
                {'items': dane, 'timek': timestamp, 'copy': copyright})

        with open(nazwa, 'w', encoding="utf-8") as f:
            f.write(fill_template)

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
            template = self.envir.get_template("empty.html")
            fill_template = template.render({'last': timek})

            with open(path, 'w', encoding="utf-8") as f:
                f.write(fill_template)

            raise ValueError("OSM Data not found!")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--auto', action='store', nargs=3, metavar=('NETWORK', 'OSM_PATH', 'HTML_PATH'),
                        help='NETWORK is uid or name to be found in nextbike_uids.txt')
    parser.add_argument(
        '-i', '--interactive', action='store_true', help='runs interactive guide')
    parser.add_argument(
        '-u', '--update', action='store_true', help='updates manually nextbike .xml file and .set file with uids')
    parser.add_argument(
        '-f', '--feed', action='store_true', help='runs feed creation (only with -a!)')
    args = parser.parse_args()

    if args.update:
        NP.NextbikeParser.update()
        a = NP.NextbikeParser()
        a.get_uids()
    if args.auto:
        a = OP.osmParser(args.auto[1])
        a.fill_ways()
        a.clear_nodes()
        a.fake_all()
        b = NP.NextbikeParser()
        c = NextbikeValidator(b, a)
        if args.auto[0].isnumeric():
            d = b.find_city(args.auto[0])
        else:
            d = b.find_network(args.auto[0])
        c.is_whatever(args.auto[2])
        c.pair(d)
        if args.feed:
            import feed_gen as FG
            c.html_it(args.auto[2], feed=True)
            a.remove_fakes()
            f = FG.Feed(args.auto[2].rstrip('.html'), a.nodes, a.ways, d)
            f.new_db()
            f.check_db()
            f.make_feeds()
            f.create_feed()
        else:
            c.html_it(args.auto[2])

    if args.interactive:
        path_osm = input("Write path to osm file:\n")
        a = OP.osmParser(path_osm)
        a.fill_ways()
        a.clear_nodes()
        a.fake_all()
        b = NP.NextbikeParser()
        place = input(
            "______________\nWhat kind of network\city should I process?\n>If you want particular city please write it's uid number from nextbike_uids.txt\n>>For whole network write it's name(within ''), also from nextbike_uids.txt\n")
        c = NextbikeValidator(b, a)
        if place.isnumeric():
            d = b.find_city(place)
        else:
            d = b.find_network(place)
        c.pair(d)
        html = input("______________\nHTML name?\n")
        c.is_whatever(html)
        c.html_it(html)
        print("______________\nAll done...thanks!")
