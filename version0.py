import pandas as pd
import math
from bokeh.io import show
from bokeh.models import (
    ColumnDataSource,
    HoverTool,
    TapTool,
    LogColorMapper,
    Patches,
    OpenURL
)
from bokeh.palettes import Viridis6 as palette
from bokeh.plotting import figure

from map_classes import Country
from map_classes import Coordinates
from map_classes import Product
from bokeh.models.widgets import Slider
from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox
from bokeh.models.glyphs import Text

import functions as fn

data = pd.read_csv("coordinates.csv")

palette.reverse()

# initialize countries
ger = Country('Germany',350,0,80,[])
usa = Country('USA',9147,0,325,[])
usa.set_meat_cons_pc(120)
usa.set_veges(5)
print(str(ger))
countries=[ger,usa]
for country in countries:
    lat = data[data['key'] == country.get_key()]['lat']
    lon = data[data['key'] == country.get_key()]['lon']
    country.set_coordinates(Coordinates(lat,lon))

# initialize products
beef = Product(name="beef", type="animal")
beef.set_lifetime(1.5)
beef.set_landuse_per_kg(20)

country_xs = [country.get_coordinates().lon() for country in countries]
country_ys = [country.get_coordinates().lat() for country in countries]

country_names = [country.get_name() for country in countries]
country_areas = [country.get_area() for country in countries]

color_mapper = LogColorMapper(palette=palette)


source = ColumnDataSource(data=dict(
    x=country_xs,
    y=country_ys,
    name=country_names,
    area=country_areas,
))

TOOLS = "pan,wheel_zoom,reset,hover,save,tap"


p = figure(
    title="First Test Map ", tools=TOOLS,
    x_axis_location=None, y_axis_location=None,
    plot_width=1600, plot_height=800
)
p.grid.grid_line_color = None

renderer = p.patches('x', 'y', source=source,
          fill_color={'field': 'area', 'transform': color_mapper},
          fill_alpha=0.7, line_color="white", line_width=0.5)



selected_patches = Patches(fill_color="#a6cee3")
nonselected_patches = Patches(fill_color="#ffcee3")

renderer.selection_glyph = selected_patches
renderer.nonselection_glyph = nonselected_patches


hover = p.select_one(HoverTool)
hover.point_policy = "follow_mouse"
hover.tooltips = [
    ("name", "@name"),
    ("area", "@area"),
    ("(long, lat)", "($x, $y)"),
]



usa_center_lat = usa.get_coordinates().lat().median()
usa_center_lon = usa.get_coordinates().lon().median()


area = fn.calc_area(country=usa, product=beef)
radius = math.sqrt(area / math.pi)  # [km]
radius_deg = fn.km2deg(radius)
z = [radius_deg]


source_z = ColumnDataSource(data=dict(z=z))
p.circle(usa_center_lon,usa_center_lat,radius='z', source=source_z)

slider_vegetarians = Slider(title="vegetarians [percent]", value=usa.get_veges(), start=0.0, end=100.0, step=0.1)

area = fn.calc_area(country=usa, product=beef)
print("area:", area)

def update_data(attrname, old, new):

    # update value
    #land_use_per_kg = 20
    #animal_lifetime = 1.5 # [y]
    # area = share of canivores x population[mil] x cons_per_capita x landuse per kg meat x animal_lifetime
    #area = (1.0-0.01*slider_vegetarians.value)*usa.get_population() * usa.get_meat_cons_pc() * land_use_per_kg * animal_lifetime # [km2]

    usa.set_veges(slider_vegetarians.value)
    area = fn.calc_area(country=usa, product=beef)

    print("area:", area)
    radius = math.sqrt(area/math.pi) # [km]
    #radius_deg = radius/ 111.111 # [deg]
    radius_deg = fn.km2deg(radius)
    z = [radius_deg]
    source_z.data = dict(z=z)

slider_vegetarians.on_change('value', update_data)

###############
from bokeh.io import output_file, show
from bokeh.layouts import widgetbox
from bokeh.models.widgets import CheckboxButtonGroup

output_file("checkbox_button_group.html")

checkbox_button_group = CheckboxButtonGroup(
        labels=["Option 1", "Option 2", "Option 3"], active=[0, 1])

#show(widgetbox(checkbox_button_group))


def my_radio_handler(new):
    print('Radio button option ' + str(new) + ' selected.')


checkbox_button_group.on_click(my_radio_handler)
#######################################

# Set up layouts and add to document
inputs = widgetbox(slider_vegetarians, checkbox_button_group)

curdoc().add_root(row(inputs, p, width=800))
curdoc().title = "Vege Map"

url = "http://www.colors.com"
def my_tap_handler(attr,old,new):
    #print('hi there')
    #p.text(x=0,y=0,text="@name")
    patch_name =  source.data['name'][new['1d']['indices'][0]]
    print("TapTool callback executed on Patch {}".format(patch_name))

renderer.data_source.on_change("selected", my_tap_handler)
#taptool = p.select(type=TapTool)
#taptool.callback = my_tap_handler()

