import pandas as pd
import geopandas as gpd
import numpy as np
import geojson
import json
from shapely import wkb
from shapely.geometry import mapping
from shapely.geometry import shape
from db_connect.connect import connect 
import matplotlib.pyplot as plt
import folium
from folium import GeoJson, Choropleth
from folium.features import DivIcon
from folium import CircleMarker
from folium import FeatureGroup
from folium.plugins import MarkerCluster
from folium.map import LayerControl
from folium import LinearColormap
import branca.colormap as cm

# VISUALIZATION  ----------------------------------------------------------------------------------------------------

# interactive map with folium
m_berlin = folium.Map(location = [52.520008, 13.404954], zoom_start = 10, # map centered on Berlin
                tiles = "CartoDB positron")

geojson_berlin = gpd.read_file("gdf_berlin.geojson")
# style function for the districts: no fill
def style_function_district(feature):
    return {
        'fillColor': 'transparent',  
        'color': 'black',  
        'weight': 0.5,  
        'opacity': 1
    }


# districts with data information
folium.GeoJson(
    geojson_berlin, 
    name='Berlin Districts',
    style_function=style_function_district,
    tooltip=folium.GeoJsonTooltip(
        fields=[
            'district_name', 
            'population', 
            'population_age_under_18_count', 
            'population_age_under_18_percentage',
            'population_age_65_plus_count', 
            'population_age_65_plus_percentage', 
            'population_migration_background_count', 
            'population_migration_background_percentage',
            'unemployment', 
            'youth_unemployment_percentage',
            'communities_of_need_percentage',
            'communities_of_need_under_15_percentage', 
            'grundsicherung_65_plus_percentage',
            'kindergartens',  
            'schools',        
            'colleges'],
        aliases=[
            'District:', 
            'Total Population:', 
            'Population (<18 years):', 
            'Population % (<18 years):', 
            'Population (>65 years):', 
            'Population % (>65 years):', 
            'Population with migration background:', 
            'Population with migration background %:',
            'Unemployment rate % (15-65 years) (SGB II/SGB III):', 
            'Unemployment rate % (15-25 years) (SGB II/SGB III):', 
            'Persons in SGB II-communities of need % (>65 years):', 
            'Persons in SGB II-communities of need % (>15 years)', 
            'Recipients of basic income support % (SGB XII) (> 65 years):',
            'Kindergartens:',   
            'Schools:',         
            'Colleges:'],
        style="""
        background-color: #F0EFEF;
        border: 2px solid black;
        border-radius: 3px;
        box-shadow: 3px;  """,
        localize=True,
    )
).add_to(m_berlin)


# choropleth map by population 
population_choropleth = folium.Choropleth(
    geo_data = geojson_berlin,
    show=False,
    name = 'Population',
    data = geojson_berlin,
    columns = ['district_name', 'population'],
    key_on = 'feature.properties.district_name',
    fill_color = 'YlOrRd',  
    fill_opacity = 0.5,
    line_opacity = 0.2,
    legend_name = 'Population'
).add_to(m_berlin)

unemployment_rate_bins = np.linspace(2.5, 8.2, 9) 

# choropleth map by unemployment rate 
unemployment_choropleth_berlin = folium.Choropleth(
    geo_data=geojson_berlin,
    show=False,
    name='Unemployment rate % (15-65 years)',
    data=geojson_berlin,
    columns=['district_name', 'unemployment'],
    key_on='feature.properties.district_name',
    fill_color='YlGnBu',  
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Unemployment rate % (15-65 years)',
    bins=unemployment_rate_bins,
    reset=True
).add_to(m_berlin)


# choropleth for population under 18 
population_under_18_chrpleth = folium.Choropleth(
    geo_data=geojson_berlin,
    show=False,
    name='Population % (< 18 years)',
    data=geojson_berlin,
    columns=['district_name', 'population_age_under_18_percentage'],
    key_on='feature.properties.district_name',
    fill_color='YlGnBu',  #
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name = 'Population % (< 18 years)'
).add_to(m_berlin)

# choropleth for population 65+
population_65plus_choropleth = folium.Choropleth(
    geo_data=geojson_berlin,
    show=False,
    name='Population % (> 65 years)',
    data=geojson_berlin,
    columns=['district_name', 'population_age_65_plus_percentage'],
    key_on='feature.properties.district_name',
    fill_color='YlOrRd',  
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Population % (> 65 years)'
).add_to(m_berlin)

# choropleth for youth unemployment rate
youth_unemployment_choropleth = folium.Choropleth(
    geo_data=geojson_berlin,
    show=False,
    name='Unemployment rate % (15-25 years)',
    data=geojson_berlin,
    columns=['district_name', 'youth_unemployment_percentage'],
    key_on='feature.properties.district_name',
    fill_color='YlOrRd',  
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name = 'Unemployment rate % (15-25 years)'
).add_to(m_berlin)


# add education points 
 # convert POI GeoDataFrame to GeoJSON
geojson_pois_berlin = gpd.read_file("gdf_pois_berlin.geojson")
# color mapping for `fclass` 
fclass_color_map = {
    'college': '#CBE896',
    'school': '#F37A0F',
    'kindergarten': '#8ACEF5'
}



def get_poi_color(fclass):
    return fclass_color_map.get(fclass, 'gray')  # default to gray if not found

# for each POI category: layer 
poi_layers = {}
for _, poi in geojson_pois_berlin.iterrows():
    lat, lon = poi.geometry.y, poi.geometry.x  # latitude and longitude of the POI
    color = get_poi_color(poi['fclass'])  # color based on the `fclass`
    # DivIcon for each POI (colored dot)
    poi_icon = DivIcon(
        icon_size=(5, 5),  
        icon_anchor=(5, 5),  
        html=f'<div style="background-color: {color}; width: 10px; height: 10px; border-radius: 50%;border: 0.5px solid black;"></div>'   # colored dot
    )
    
    # marker with a DivIcon
    marker = folium.Marker(
        location=[lat, lon],
        icon=poi_icon #,
       #tooltip=folium.Tooltip(f'{poi["fclass"]} POI')  # Tooltip with POI type
    )
    
    if poi['fclass'] not in poi_layers:
        poi_layers[poi['fclass']] = folium.FeatureGroup(name=poi['fclass'], show=False) 
    poi_layers[poi['fclass']].add_child(marker)

for layer in poi_layers.values():
    layer.add_to(m_berlin)

# Layer Control: toggling layers
folium.LayerControl().add_to(m_berlin)

m_berlin.save('berlin_population_unemployment_map.html')



# VISUALIZATION  ----------------------------------------------------------------------------------------------------

m_hamburg = folium.Map(location=[53.5511, 9.9937], zoom_start=10, 
               tiles="CartoDB positron") # map centered on hamburg

geojson_hamburg = gpd.read_file("gdf_hamburg.geojson")


# districts with data information
GeoJson(
    geojson_hamburg,  
    name='hamburg Districts',
    style_function=style_function_district,
    tooltip=folium.GeoJsonTooltip(
        fields=[
            'district_name', 
            'population', 
            'population_age_under_18_count', 
            'population_age_under_18_percentage',
            'population_age_65_plus_count', 
            'population_age_65_plus_percentage', 
            'population_migration_background_count', 
            'population_migration_background_percentage',
            'unemployment', 
            'youth_unemployment_percentage',
            'communities_of_need_percentage',
            'communities_of_need_under_15_percentage', 
            'grundsicherung_65_plus_percentage',
            'kindergartens',  
            'schools',        
            'colleges'],
        aliases=[
            'District:', 
            'Total Population:', 
            'Population (<18 years):', 
            'Population % (<18 years):', 
            'Population (>65 years):', 
            'Population % (>65 years):', 
            'Population with migration background:', 
            'Population with migration background %:',
            'Unemployment rate % (15-65 years) (SGB II/SGB III):', 
            'Unemployment rate % (15-25 years) (SGB II/SGB III):', 
            'Persons in SGB II-communities of need % (>65 years):', 
            'Persons in SGB II-communities of need % (>15 years)', 
            'Recipients of basic income support % (SGB XII) (> 65 years):',
            'Kindergartens:',   
            'Schools:',         
            'Colleges:'],
        style="""
        background-color: #F0EFEF;
        border: 2px solid black;
        border-radius: 3px;
        box-shadow: 3px;  """,
        localize=True,
    )
).add_to(m_hamburg)


# choropleth map by population 
population_choropleth = folium.Choropleth(
    geo_data=geojson_hamburg,
    show=False,
    name='Population',
    data=geojson_hamburg,
    columns=['district_name', 'population'],
    key_on='feature.properties.district_name',
    fill_color='YlGnBu',  
    fill_opacity=0.5,
    line_opacity=0.5,
    legend_name='Population',
).add_to(m_hamburg)

# choropleth map by unemployment rate 
unemployment_choropleth = folium.Choropleth(
    geo_data=geojson_hamburg,
    show=False,
    name = 'Unemployment rate % (15-65 years)',
    data = geojson_hamburg,
    columns = ['district_name', 'unemployment'],
    key_on = 'feature.properties.district_name',
    bins = unemployment_rate_bins,
    fill_color='YlGnBu',  
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Unemployment rate % (15-65 years)',
).add_to(m_hamburg)


# choropleth for population under 18 
population_under_18_choropleth = folium.Choropleth(
    geo_data=geojson_hamburg,
    show=False,
    name='Population % (< 18 years)',
    data=geojson_hamburg,
    columns=['district_name', 'population_age_under_18_percentage'],
    key_on='feature.properties.district_name',
    fill_color='YlGnBu',  #
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name = 'Population % (< 18 years)'
).add_to(m_hamburg)

# choropleth for population 65+ 
population_65plus_choropleth = folium.Choropleth(
    geo_data=geojson_hamburg,
    show=False,
    name='Population % (> 65 years)',
    data=geojson_hamburg,
    columns=['district_name', 'population_age_65_plus_percentage'],
    key_on='feature.properties.district_name',
    fill_color='YlOrRd',  
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Population % (> 65 years)'
).add_to(m_hamburg)

# choropleth for youth unemployment rate
youth_unemployment_choropleth = folium.Choropleth(
    geo_data=geojson_hamburg,
    show=False,
    name='Unemployment rate % (15-25 years)',
    data=geojson_hamburg,
    columns=['district_name', 'youth_unemployment_percentage'],
    key_on='feature.properties.district_name',
    fill_color='YlOrRd',  
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name = 'Unemployment rate % (15-25 years)'
).add_to(m_hamburg)


# add education points 
geojson_pois_hamburg = gpd.read_file("gdf_pois_hamburg.geojson")


poi_layers = {}
for _, poi in geojson_pois_hamburg.iterrows():
    lat, lon = poi.geometry.y, poi.geometry.x  
    color = get_poi_color(poi['fclass'])  

    poi_icon = DivIcon(
        icon_size=(5, 5),  
        icon_anchor=(5, 5),  
        html=f'<div style="background-color: {color}; width: 10px; height: 10px; border-radius: 50%;border: 0.5px solid black;"></div>'   # colored dot
    )
    marker = folium.Marker(
        location=[lat, lon],
        icon=poi_icon #,
       #tooltip=folium.Tooltip(f'{poi["fclass"]} POI')  # Tooltip with POI type
    )

    if poi['fclass'] not in poi_layers:
        poi_layers[poi['fclass']] = folium.FeatureGroup(name=poi['fclass'], show=False) 
    
    poi_layers[poi['fclass']].add_child(marker)


for layer in poi_layers.values():
    layer.add_to(m_hamburg)

folium.LayerControl().add_to(m_hamburg)

m_hamburg.save('hamburg_population_unemployment_map.html')