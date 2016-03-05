import sqlite3 as sql
__DB__ = 'feeds.db'


class Feed:

    def __init__(self, objname, nodes, ways, places):
        from jinja2 import PackageLoader, Environment
        self.objname = objname
        self.nodes = nodes
        self.ways = ways
        self.places = places
        self.features = self.nodes + self.ways
        self.envir = Environment(
            loader=PackageLoader('feed_gen', 'templates'))
        self.osm_new = []
        self.osm_rem = []
        self.osm_changes = []
        self.nxtb_new = []
        self.nxtb_rem = []
        self.nxtb_changes = []

    def new_db(self):
        import os

        connection = sql.connect(__DB__)
        c = connection.cursor()
        db_tables = c.execute('''SELECT * FROM sqlite_master''').fetchall()
        tables = []
        for i in db_tables:
            i = i[1]
            tables.append(i)
        if '{0}_OSM'.format(self.objname) not in tables:
            c.execute(
                '''CREATE TABLE {0}_OSM (id INT, version INT)'''.format(self.objname))
        if '{0}_NXTB'.format(self.objname) not in tables:
            c.execute(
                '''CREATE TABLE {0}_NXTB (id INT, name TEXT)'''.format(self.objname))
        if '{0}_FEED'.format(self.objname) not in tables:
            c.execute(
                '''CREATE TABLE {0}_FEED (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, data TEXT, content TEXT)'''.format(self.objname))
        connection.commit()
        connection.close()

    def detuple(self, lista):
        new_list = []
        for i in lista:
            new_list.append(i[0])
        return new_list

    def check_db(self):
        connection = sql.connect(__DB__)
        c = connection.cursor()
        sel = '''SELECT * FROM {0}_OSM WHERE id={1}'''
        new = '''INSERT INTO {0}_OSM VALUES ({1}, {2})'''
        upd = '''UPDATE {0}_OSM SET version={1} WHERE id={2}'''

        dbaza = c.execute(
            '''SELECT id FROM {0}_OSM'''.format(self.objname)).fetchall()
        baza = self.detuple(dbaza)

        for i in self.features:
            osm_hist = c.execute(
                sel.format(self.objname, str(i.iD))).fetchone()

            if osm_hist == None:
                self.osm_new.append(i)
                c.execute(new.format(self.objname, i.iD, i.version))
            else:
                if osm_hist[1] == i.version:
                    baza.remove(int(i.iD))
                else:
                    self.osm_changes.append(i)
                    c.execute(upd.format(self.objname, i.version, i.iD))
                    baza.remove(int(i.iD))

        if baza != []:
            for i in baza:
                DEL = '''DELETE FROM {0}_OSM WHERE id={1}'''
                c.execute(DEL.format(self.objname, i))
                self.osm_rem.append(i)

        connection.commit()

        sel = '''SELECT * FROM {0}_NXTB WHERE id={1}'''
        new = '''INSERT INTO {0}_NXTB VALUES ({1}, '{2}')'''
        upd = '''UPDATE {0}_NXTB SET name='{1}' WHERE id={2}'''

        dbaza = c.execute(
            '''SELECT id FROM {0}_NXTB'''.format(self.objname)).fetchall()
        baza = self.detuple(dbaza)
        for i in self.places:
            nxtb_hist = c.execute(sel.format(self.objname, i.num)).fetchone()

            if nxtb_hist == None:
                self.nxtb_new.append(i)
                c.execute(new.format(self.objname, i.num, i.name))
            else:
                if nxtb_hist[1] == i.name:
                    baza.remove(int(i.num))
                else:
                    self.nxtb_changes += [nxtb_hist, i]
                    c.execute(upd.format(self.objname, i.name, i.num))
                    baza.remove(int(i.num))

        if baza != []:
            for i in baza:
                DEL = '''DELETE FROM {0}_NXTB WHERE id={1}'''
                c.execute(DEL.format(self.objname, i))
                self.nxtb_rem.append(i)

        connection.commit()
        connection.close()

    def make_feeds(self):
        from time import localtime, strftime
        #osm_changes, osm_rem, osm_new
        #nxtb_changes, nxtb_rem, nxtb_new
        connection = sql.connect(__DB__)
        c = connection.cursor()

        ins = '''INSERT INTO {0}_FEED VALUES (NULL, '{1}', '{2}', '{3}')'''

        template = self.envir.get_template("osm_new.html")
        for i in self.osm_new:
            fill_template = template.render({'i': i, 'name': self.objname})

            title = 'New bicycle rental in osm found!'
            timek = strftime("%Y-%m-%dT%H:%M:%S+01:00", localtime())
            c.execute(
                ins.format(self.objname, title, timek, fill_template))
        template = self.envir.get_template("osm_rem.html")
        for i in self.osm_rem:
            fill_template = template.render({'i': i, 'name': self.objname})

            title = 'Removed bicycle rental in osm found!'
            timek = strftime("%Y-%m-%dT%H:%M:%S+01:00", localtime())
            c.execute(
                ins.format(self.objname, title, timek, fill_template))
        template = self.envir.get_template("osm_changes.html")
        for i in self.osm_changes:
            fill_template = template.render({'i': i, 'name': self.objname})

            title = 'Changed bicycle rental in osm found!'
            timek = strftime("%Y-%m-%dT%H:%M:%S+01:00", localtime())
            c.execute(
                ins.format(self.objname, title, timek, fill_template))

        template = self.envir.get_template("nxtb_new.html")
        for i in self.nxtb_new:
            fill_template = template.render({'i': i, 'name': self.objname})

            title = 'New Nextbike bicycle rental found!'
            timek = strftime("%Y-%m-%dT%H:%M:%S+01:00", localtime())
            c.execute(
                ins.format(self.objname, title, timek, fill_template))
        template = self.envir.get_template("nxtb_rem.html")
        for i in self.nxtb_rem:
            fill_template = template.render({'i': i, 'name': self.objname})

            title = 'Removed Nextbike bicycle rental found!'
            timek = strftime("%Y-%m-%dT%H:%M:%S+01:00", localtime())
            c.execute(
                ins.format(self.objname, title, timek, fill_template))
        template = self.envir.get_template("nxtb_changes.html")
        for i in self.nxtb_changes:
            now = i[1]
            old = i[0]
            fill_template = template.render(
                {'i': i[1], 'old': i[0].name, 'name': self.objname})

            title = 'Changed Nextbike bicycle rental name found!'
            timek = strftime("%Y-%m-%dT%H:%M:%S+01:00", localtime())
            c.execute(
                ins.format(self.objname, title, timek, fill_template))

        connection.commit()
        connection.close()

    def create_feed(self):
        from time import localtime, strftime
        connection = sql.connect(__DB__)
        c = connection.cursor()

        feeds = c.execute(
            '''SELECT * FROM {0}_FEED'''.format(self.objname)).fetchall()
        connection.close()

        template = self.envir.get_template("atom.xml")

        articles = []
        for i in feeds:
            new_entry = {'title': i[
                1], 'id': "{0}:{1}".format(self.objname, str(i[0])), 'updated': i[2], 'content': i[3]}
            articles.append(new_entry)

        timek = strftime("%Y-%m-%dT%H:%M:%S+01:00", localtime())
        fill_template = template.render({'title': "Atom feed for {0}".format(
            self.objname), 'name': 'http://javnik.tk/NextbikeOSM/{0}_atom.xml'.format(self.objname), 'update': timek, 'articles': articles})

        with open('{0}_atom.xml'.format(self.objname), 'w', encoding='utf-8') as f:
            f.write(fill_template)
