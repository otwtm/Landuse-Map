class Country:
    def __init__(self, name, area, area_agri, population, coordinates):
        self._name = name
        self._key = name[:3].lower()
        self._population = population
        self._area = area
        self._area_agri = area_agri
        self._coordinates = coordinates

    def get_name(self):
        return self._name

    def get_key(self):
        return self._key

    def get_area(self):
        return self._area

    def get_area_agri(self):
        return self._area_agri

    def get_population(self):
        return self._population

    def get_coordinates(self):
        return self._coordinates

    def get_meat_cons_pc(self):
        return self._meat_cons_pc

    def get_veges(self):
        return self._veges

    def set_name(self, name):
        self._name = name

    def set_area(self, area):
        self._area = area

    def set_area_agri(self, area_agri):
        self._area_agri = area_agri

    def set_population(self, population):
        self._population = population

    def set_coordinates(self, coordinates):
        self._coordinates = coordinates

    def set_meat_cons_pc(self, meat_cons_pc):
        self._meat_cons_pc = meat_cons_pc

    def set_veges(self,veges):
        self._veges = veges

    def __str__(self):
        stri = "\nName: " + str(self._name) \
               + "\nKey: " + str(self._key) \
               + "\nPopulation: " + str(self._population) \
               + "\nArea: " + str(self._area) \
               + "\nCoordinates: " + str(self._coordinates) \
               + "\n"
        return stri

class Coordinates:
    def __init__(self,lat,lon):
        self._lat = lat
        self._lon = lon

    def lat(self):
        return self._lat

    def lon(self):
        return self._lon


class Product:
    def __init__(self, name, type):
        self._name = name
        self._key = name[:3].lower()
        self._type = type

    def __str__(self):
        stri = "\nName: " + str(self._name) \
               + "\nKey: " + str(self._key) \
               + "\nType: " + str(self._type) \
               + "\n"
        return stri

    def landuse_per_kg(self):
        return self._landuse_per_kg

    def lifetime(self):
        return self._lifetime

    def name(self):
        return self._name

    def key(self):
        return self._key

    def type(self):
        return self._type

    def set_lifetime(self, lifetime):
        self._lifetime = lifetime

    def set_landuse_per_kg(self,landuse_per_kg):
        self._landuse_per_kg = landuse_per_kg