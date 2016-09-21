import sqlite3 as sql
import dataset
DB = 'sqlite:///feeds.db'


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
        c = dataset.connect(DB)
        base = "{0}_FEED"

        db_tables = c.query('''SELECT name FROM sqlite_master''')#.fetchall()
        tables = []
        for i in db_tables:
            i = i['name']
            tables.append(i)
        if '{0}_OSM'.format(self.objname) not in tables:
            c.query(
                '''CREATE TABLE {0}_OSM (id INT, version INT)'''.format(self.objname))
        if '{0}_NXTB'.format(self.objname) not in tables:
            c.query(
                '''CREATE TABLE {0}_NXTB (id INT, name TEXT)'''.format(self.objname))
        if '{0}_FEED'.format(self.objname) not in tables:
            c.query(
                '''CREATE TABLE {0}_FEED (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, data TEXT, content TEXT)'''.format(self.objname))
        c.commit()

    def detuple(self, lista):
        new_list = []
        for i in lista:
            new_list.append(i['id'])
        return new_list

    def check_db(self):
        c = dataset.connect(DB)
        ctab = c.load_table("{0}_OSM".format(self.objname))
        dbaza = ctab.all()
        baza = self.detuple(dbaza)

        for i in self.features:
            osm_hist = ctab.find_one(id=str(i.iD))

            if osm_hist == None:
                self.osm_new.append(i)
                ctab.insert(dict(id=i.iD, version=i.version))
            else:
                if osm_hist["version"] == i.version:
                    baza.remove(int(i.iD))
                else:
                    self.osm_changes.append(i)
                    ctab.update(dict(id=i.iD, version=i.version), ['id'])
                    baza.remove(int(i.iD))

        if baza != []:
            for i in baza:
                ctab.delete(id=i)
                self.osm_rem.append(i)

        c.commit()

        ctab = c.load_table("{0}_NXTB".format(self.objname))
        dbaza = ctab.all()
        baza = self.detuple(dbaza)

        for i in self.places:
            nxtb_hist = ctab.find_one(id=i.num)

            if nxtb_hist == None:
                self.nxtb_new.append(i)
                ctab.insert(dict(id=i.num, name=i.name))
            else:
                if i.num == 0 or i.name.startswith('.') or i.name.startswith('@') or i.name == '':
                    pass
                elif nxtb_hist["name"] == i.name:
                    baza.remove(int(i.num))
                else:
                    self.nxtb_changes += [nxtb_hist, i]
                    ctab.update(dict(id=i.num, name=i.name), ['id'])
                    try:
                        baza.remove(int(i.num))
                    except:
                        pass
                        #add debug info here

        if baza != []:
            for i in baza:
                ctab.delete(id=i)
                self.nxtb_rem.append(i)

        c.commit()

    def make_feeds(self):
        from time import localtime, strftime
        #osm_changes, osm_rem, osm_new
        #nxtb_changes, nxtb_rem, nxtb_new
        c = dataset.connect(DB)
        base = "{0}_FEED"

        template = self.envir.get_template("osm_new.html")
        for i in self.osm_new:
            fill_template = template.render({'i': i, 'name': self.objname})

            title = 'New bicycle rental in osm found!'
            timek = strftime("%Y-%m-%dT%H:%M:%S+01:00", localtime())
            ins_data = dict(id=None, title=title, data=timek, content=fill_template)
            c[self.objname + "_FEED"].insert(ins_data)
        template = self.envir.get_template("osm_rem.html")
        for i in self.osm_rem:
            fill_template = template.render({'i': i, 'name': self.objname})

            title = 'Removed bicycle rental in osm found!'
            timek = strftime("%Y-%m-%dT%H:%M:%S+01:00", localtime())
            ins_data = dict(id=None, title=title, data=timek, content=fill_template)
            c[self.objname + "_FEED"].insert(ins_data)
        template = self.envir.get_template("osm_changes.html")
        for i in self.osm_changes:
            fill_template = template.render({'i': i, 'name': self.objname})

            title = 'Changed bicycle rental in osm found!'
            timek = strftime("%Y-%m-%dT%H:%M:%S+01:00", localtime())
            ins_data = dict(id=None, title=title, data=timek, content=fill_template)
            c[self.objname + "_FEED"].insert(ins_data)
        template = self.envir.get_template("nxtb_new.html")
        for i in self.nxtb_new:
            fill_template = template.render({'i': i, 'name': self.objname})

            title = 'New Nextbike bicycle rental found!'
            timek = strftime("%Y-%m-%dT%H:%M:%S+01:00", localtime())
            ins_data = dict(id=None, title=title, data=timek, content=fill_template)
            c[self.objname + "_FEED"].insert(ins_data)
        template = self.envir.get_template("nxtb_rem.html")
        for i in self.nxtb_rem:
            fill_template = template.render({'i': i, 'name': self.objname})

            title = 'Removed Nextbike bicycle rental found!'
            timek = strftime("%Y-%m-%dT%H:%M:%S+01:00", localtime())
            ins_data = dict(id=None, title=title, data=timek, content=fill_template)
            c[self.objname + "_FEED"].insert(ins_data)
        template = self.envir.get_template("nxtb_changes.html")
        for i in self.nxtb_changes:
            now = i[1]
            old = i[0]
            fill_template = template.render(
                {'i': i[1], 'old': i[0].name, 'name': self.objname})

            title = 'Changed Nextbike bicycle rental name found!'
            timek = strftime("%Y-%m-%dT%H:%M:%S+01:00", localtime())
            ins_data = dict(id=None, title=title, data=timek, content=fill_template)
            c[self.objname + "_FEED"].insert(ins_data)

        c.commit()

    def create_feed(self):
        from time import localtime, strftime
        c = dataset.connect(DB)
        ctab = c.load_table("{0}_FEED".format(self.objname))
        feeds = ctab.all()

        template = self.envir.get_template("atom.xml")

        articles = []
        for i in feeds:
            new_entry = {'title': i[
                "title"], 'id': "{0}:{1}".format(self.objname, str(i["id"])), 'updated': i["data"], 'content': i["content"]}
            articles.append(new_entry)

        timek = strftime("%Y-%m-%dT%H:%M:%S+01:00", localtime())
        fill_template = template.render({'title': "Atom feed for {0}".format(
            self.objname), 'name': 'http://javnik.tk/NextbikeOSM/{0}_atom.xml'.format(self.objname), 'update': timek, 'articles': articles})

        with open('{0}_atom.xml'.format(self.objname), 'w', encoding='utf-8') as f:
            f.write(fill_template)
