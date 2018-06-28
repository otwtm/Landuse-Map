import pandas as pd
import numpy as np
import math
import functions as fn
import os

from bokeh.models import (
    ColumnDataSource,
    HoverTool,
    TapTool,
    LogColorMapper,
    Patches
)
#from bokeh.palettes import Viridis6 as palette
from bokeh.palettes import RdYlGn10 as palette

from bokeh.plotting import figure

from map_classes import Country
from map_classes import Coordinates
from map_classes import Product
from bokeh.models.widgets import Slider
from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox
from bokeh.models.glyphs import Text
from bokeh.io import output_file, show
from bokeh.layouts import widgetbox
from bokeh.models.widgets import CheckboxButtonGroup
from bokeh.models.markers import Circle
from bokeh.models import CustomJS
from bokeh.models.selections import Selection

print(palette)

# Event handlers
def my_tap_handler(attr,old,new):
    global selected_country
    global slider_vegetarians
    global source

    indices = source.selected.indices
    print("indices: ", indices)
    print(len(indices))
    #if len(indices)>0:
    country_name = source.data["name"][indices[0]]

    new_indicies = list(df.loc[df['name'] == country_name].index)
    print("country_name: ", country_name)
    print("new_indices: ", new_indicies)

    #country_indices = df['id'][df['group'] == group_name]

    if len(indices)==1 and len(new_indicies)>1:
        source.selected = Selection(indices=new_indicies)

    selected_country = [country for country in countries if country.get_name()==country_name][0]
    selected_country.set_veges(slider_vegetarians.value)
    update_circle()
    update_slider_title(selected_country)

def update_slider_title(country):
    global slider_vegetarians
    slider_vegetarians.title = "Vegetarians in " +country.get_name()+ " in percent"

def button_handler(new):
    print('button option ' + str(new) + ' selected.')

def update_data(attrname, old, new):
    global selected_country
    print(selected_country)
    selected_country.set_veges(new)
    update_circle()

def update_circle():
    global selected_country
    global source_circle
    x = [selected_country.get_center().lon()]
    y = [selected_country.get_center().lat()]
    r = [fn.radius_deg(selected_country, beef)]
    source_circle.data = dict(x=x,y=y,r=r)

palette.reverse()


# initialize countries
countries = []


import fiona
shape_file = fiona.open("natural_earth/ne_110m_admin_0_countries.shp")
country_data = pd.read_csv("country_data_test.csv")


print(country_data.iloc[0]['key'])

for shape in shape_file:
    #print(shape["properties"])
    coordinates = shape["geometry"]["coordinates"]
    coord = []
    if shape["geometry"]["type"] == "Polygon":
        for unit in coordinates:
            #print(unit)
            lon = pd.Series([idx[0] for idx in unit])
            lat = pd.Series([idx[1] for idx in unit])
            coord.append(Coordinates(lon, lat))
    elif shape["geometry"]["type"] == "MultiPolygon":
        for unit in coordinates:

            lon = pd.Series([idx[0] for idx in unit[0]])
            lat = pd.Series([idx[1] for idx in unit[0]])
            coord.append(Coordinates(lon, lat))
    country_name = shape["properties"]["ADMIN"]
    country_code = shape["properties"]["ADM0_A3"]
    country = Country(country_name, country_code, 350, population=80, coordinate_list=coord)
    countries.append(country)



for country in countries:
    country.set_meat_cons_pc(100)
    country.set_veges(0)
    i = country_data.index[country_data['key'] == country.get_key()]
    country.set_population(country_data.iloc[i]['population'].tolist()[0])
    country.set_area(country_data.iloc[i]['landarea'].tolist()[0])
    if not math.isnan(country_data.iloc[i]['vegetarian'].tolist()[0]):
        country.set_veges(country_data.iloc[i]['vegetarian'].tolist()[0])
    print(country)



selected_country = countries[0]

# initialize products
beef = Product(name="beef", type="animal")
beef.set_lifetime(1.5)
beef.set_landuse_per_kg(20)


temp_list = [[unit.lon() for unit in country.get_coordinate_list()] for country in countries]
country_xs = [item for sublist in temp_list for item in sublist]
temp_list = [[unit.lat() for unit in country.get_coordinate_list()] for country in countries]
country_ys = [item for sublist in temp_list for item in sublist]
temp_list = [[country.get_name() for unit in country.get_coordinate_list()] for country in countries]
country_names = [item for sublist in temp_list for item in sublist]
temp_list = [[country.get_area() for unit in country.get_coordinate_list()] for country in countries]
country_areas = [item for sublist in temp_list for item in sublist]
temp_list = [[country.get_key() for unit in country.get_coordinate_list()] for country in countries]
country_keys = [item for sublist in temp_list for item in sublist]
temp_list = [[country.get_veges() for unit in country.get_coordinate_list()] for country in countries]
country_veges = [item for sublist in temp_list for item in sublist]

df = pd.DataFrame(data=dict(
    x=country_xs,
    y=country_ys,
    name=country_names,
    area=country_areas,
    key=country_keys,
    veges=country_veges
))
print(df.tail())


source = ColumnDataSource(df)



color_mapper = LogColorMapper(palette=palette)
print("col_map: ", color_mapper)
print("palette: ", palette)

TOOLS = "pan,wheel_zoom,reset,hover,save,tap"
p = figure(
    title="First Test Map ", tools=TOOLS,
    x_axis_location=None, y_axis_location=None,
    plot_width=1600, plot_height=800
)
p.grid.grid_line_color = None
p.background_fill_color = "#33b5ff"
p.background_fill_alpha = 0.2


renderer = p.patches('x', 'y', source=source,
          fill_color={'field': 'veges', 'transform': color_mapper},
          selection_line_color="blue",
          fill_alpha=0.7, line_color="white", line_width=0.5)



selected_patches = Patches(fill_color={'field': 'veges', 'transform': color_mapper},fill_alpha=0.7, line_color="white", line_width=2)
nonselected_patches = Patches(fill_color={'field': 'veges', 'transform': color_mapper},fill_alpha=0.3, line_color="white", line_width=0.5)

renderer.selection_glyph = selected_patches
renderer.nonselection_glyph = nonselected_patches

hover = p.select_one(HoverTool)
hover.point_policy = "follow_mouse"
hover.tooltips = [
    ("name", "@name"),
    ("area", "@area"),
    ("vegetarians", "@veges"),
    ("(long, lat)", "($x, $y)"),
]

r = [fn.radius_deg(selected_country, beef)]
x = [selected_country.get_center().lon()]
y = [selected_country.get_center().lat()]

source_circle = ColumnDataSource(data=dict(x=x,y=y,r=r))
glyph = Circle(x="x", y="y", radius="r", line_color="#3288bd", fill_color="white", line_width=3)
p.add_glyph(source_circle, glyph)



# widgets
slider_vegetarians = Slider(title="Vegetarians in "+selected_country.get_name()+" in percent", value=selected_country.get_veges(), start=0.0, end=100.0, step=0.1)


checkbox_button_group = CheckboxButtonGroup(
        labels=["Option 1", "Option 2", "Option 3"], active=[0, 1])


# Events
slider_vegetarians.on_change('value', update_data)

renderer.data_source.on_change("selected", my_tap_handler)

checkbox_button_group.on_click(button_handler)



#######################################

# Set up layouts and add to document
inputs = widgetbox(slider_vegetarians, checkbox_button_group)

curdoc().add_root(row(inputs, p, width=800))
curdoc().title = "Vege Map"