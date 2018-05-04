"""
functions used in the land use map
"""
import math

def calc_area(country, product):
    """
    calculate landuse area for a product in a country
    """

    area = (1.0-0.01*country.get_veges())*country.get_population() * country.get_meat_cons_pc() * product.landuse_per_kg() * product.lifetime()  # [km2]
    return area

def km2deg(km):
    """
    converts km to degree (simplified)
    """
    return km / 111.111

def radius_deg(country, product):
    area = calc_area(country=country, product=product)
    radius = math.sqrt(area / math.pi)  # [km]
    r_deg = km2deg(radius)  # [deg]
    return(r_deg)

def country_center(country):
    """
    return the center (median) of a country's coordinates
    """
    lat = country.get_coordinates().lat().median()
    lon = country.get_coordinates().lon().median()
    return [lat, lon]
