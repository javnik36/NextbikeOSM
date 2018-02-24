import logging
#logging.basicConfig(filename="nosm_utils.log", level=logging.DEBUG, format="%(asctime)s:%(levelname)s:%(funcName)s: %(message)s")

# class Nutils:
#    '''Utilities for NextbikevsOSM'''
#
#    def __init__(self):
#        pass

def refresh_nxtb():
    import xml.etree.ElementTree as XML
    import urllib.request as urllib
    import os

    path="http://nextbike.net/maps/nextbike-official.xml"
    if "nextbike.xml" in os.listdir():
        logging.info("Znaleziono plik nextbike.xml")
    else:
        logging.info("Nie znaleziono pliku nextbike.xml, próbuję pobrać...")
        urllib.urlretrieve(path, "nextbike.xml")
        logging.info("Pobrano plik nextbike.xml")

    try:
        logging.info("Próbuję sparsować nextbike.xml")
        XML.parse("nextbike.xml")
    except:
        logging.warning("Parsowanie pliku nextbike.xml zakończone niepowodzeniem")
        logging.info("Pobieram plik nextbike.xml ponownie...")
        urllib.urlretrieve(path, "nextbike.xml")
        logging.info("Pobrano plik nextbike.xml")
        try:
            logging.info("Próbuję sparsować nextbike.xml")
            XML.parse("nextbike.xml")
        except:
            logging.error("Plik nextbike.xml niemozliwy do sparsowania!")
            raise SyntaxError("Feed input data bad formed...:/")

def get_bounds(bounds):
    import ast
    logging.debug(bounds)
    bounds = ast.literal_eval(bounds)
    dl = bounds["south_west"]
    gp = bounds["north_east"]
    d = dl["lat"]
    l = dl["lng"]
    g = gp["lat"]
    p = gp["lng"]
    logging.info("Skonwertowano współrzędne miasta")
    logging.debug("{0},{1},{2},{3}".format(str(d),str(l),str(g),str(p)))
    return (d,l,g,p)

