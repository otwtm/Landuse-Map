import pandas as pd
import math
import functions as fn


from bokeh.models import (
    ColumnDataSource,
    HoverTool,
    TapTool,
    LogColorMapper,
    Patches
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
from bokeh.io import output_file, show
from bokeh.layouts import widgetbox
from bokeh.models.widgets import CheckboxButtonGroup
from bokeh.models.markers import Circle
from bokeh.models import CustomJS


# Event handlers
def my_tap_handler(attr,old,new):
    global selected_country
    global slider_vegetarians
    patch_name = source.data['key'][new['1d']['indices'][0]]
    print("patch_name: ", patch_name)
    selected_country = [country for country in countries if country.get_key()==patch_name][0]
    selected_country.set_veges(slider_vegetarians.value)
    print(selected_country)
    update_circle()
    update_slider_title(selected_country)

def update_slider_title(country):
    global slider_vegetarians
    slider_vegetarians.title = "Vegetarians in "+country.get_name()+" in percent"

def button_handler(new):
    print('button option ' + str(new) + ' selected.')

def update_data(attrname, old, new):
    global selected_country
    selected_country.set_veges(new)
    update_circle()

def update_circle():
    global selected_country
    global source_circle
    x = [selected_country.get_center().lon()]
    y = [selected_country.get_center().lat()]
    r = [fn.radius_deg(selected_country, beef)]
    source_circle.data = dict(x=x,y=y,r=r)


data = pd.read_csv("coordinates.csv")

palette.reverse()

# initialize countries
lat = data[data['key'] == 'ger']['lat']
lon = data[data['key'] == 'ger']['lon']
ger = Country('Germany',350,80,Coordinates(lat,lon))
lat = data[data['key'] == 'usa']['lat']
lon = data[data['key'] == 'usa']['lon']
usa = Country('USA',9147,325,Coordinates(lat,lon))
usa.set_meat_cons_pc(120)
ger.set_meat_cons_pc(100)
usa.set_veges(5)
ger.set_veges(5)
countries = [ger,usa]


selected_country = ger

# initialize products
beef = Product(name="beef", type="animal")
beef.set_lifetime(1.5)
beef.set_landuse_per_kg(20)

# plotting data
country_xs = [country.get_coordinates().lon() for country in countries]
country_ys = [country.get_coordinates().lat() for country in countries]
country_names = [country.get_name() for country in countries]
country_areas = [country.get_area() for country in countries]
country_keys = [country.get_key() for country in countries]

color_mapper = LogColorMapper(palette=palette)

source = ColumnDataSource(data=dict(
    x=country_xs,
    y=country_ys,
    name=country_names,
    area=country_areas,
    key = country_keys
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

r = [fn.radius_deg(selected_country, beef)]
x = [selected_country.get_center().lon()]
y = [selected_country.get_center().lat()]

source_circle = ColumnDataSource(data=dict(x=x,y=y,r=r))
glyph = Circle(x="x", y="y", radius="r", line_color="#3288bd", fill_color="white", line_width=3)
p.add_glyph(source_circle,glyph)


callback = CustomJS(args=dict(source_circle=source_circle), code="""
    var data = source_circle.data;
    x = data['x']
    y = data['y']
    r = data['r']
    var new = cb_obj.value
    z = [fn.radius_deg(selected_country, beef)]
    x = [fn.country_center(selected_country)[1]]
    data['r'] = [fn.country_center(selected_country)[0]]
    print(data['r'])
    source_circle.change.emit();
    source_circle.data = dict(x=x,y=y,z=z)
""")


# widgets
slider_vegetarians = Slider(title="Vegetarians in "+selected_country.get_name()+" in percent", value=selected_country.get_veges(), start=0.0, end=100.0, step=0.1)
# slider_vegetarians = Slider(start=0.0, end=100, value=1, step=.1, title="power", callback=callback)

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






