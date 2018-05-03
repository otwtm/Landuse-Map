"""
functions used in the land use map
"""

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
