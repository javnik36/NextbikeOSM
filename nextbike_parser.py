import xml.etree.ElementTree as XML
import nextbike_class as NC

plik = XML.parse("nextbike.xml")
root = plik.getroot()

for country in root:
    for city in country:
        place_list = []
        for place in city:
            try:
                uid = place.attrib["uid"]
                lat = place.attrib["lat"]
                lon = place.attrib["lng"]
                name = place.attrib["name"]
                try:
                    num = place.attrib["number"]
                except:
                    num = 9999 
                try:
                    bike_stands = place.get["bike_racks"]
                except:
                    bike_stands = "!"
                try:
                    bike_nrs = place.attrib["bike_numbers"]
                    n = NC.Place(uid, lat, lon, name, num, bike_stands, bike_nrs)
                except:
                    n = NC.Place(uid, lat, lon, name, num, bike_stands)

            except Exception as e:
                print(e)
                print(str(uid))

            place_list.append(n)
