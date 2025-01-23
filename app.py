import dash
from dash import dcc
from dash import html
import psycopg2
import pandas as pd
import plotly.express as px
import json
from shapely import wkb
from geoalchemy2 import WKTElement
from shapely.geometry import mapping
import plotly.express as px
import pandas as pd
from db_connect.connect import connect 
from shapely import wkb
import geopandas as gpd
import geojson
import plotly.graph_objects as go
import json
import matplotlib.pyplot as plt
from shapely.geometry import shape
import folium
from folium import GeoJson, Choropleth
from folium.features import DivIcon


# QUERIES  ----------------------------------------------------------------------------------------------------
# select data from PostgreSQL database  

query_pois_berlin = """
SELECT 
    id, 
    fclass,
    ST_AsGeoJSON(geom) AS geojson
FROM 
    berlin_osm_pois
WHERE 
    fclass IN ('kindergarten', 'school', 'college');
"""


# connect to DB
raw_data_pois_berlin = connect(query_pois_berlin)

# convert to df 
df_pois_berlin = {
    "id":[],
    "fclass": [],
    "geojson": [],
}

if raw_data_pois_berlin[1]:
    for tup in raw_data_pois_berlin[0]:
        df_pois_berlin ["id"].append(tup[0])
        df_pois_berlin ["fclass"].append(tup[1])
        df_pois_berlin ["geojson"].append(tup[2])
  

df_pois_berlin["geometry"] = [shape(json.loads(geojson)) for geojson in df_pois_berlin["geojson"]]
gdf_pois_berlin = gpd.GeoDataFrame(df_pois_berlin, geometry="geometry") 


# BERLIN district geometry merged with district information
query_berlin = """
SELECT 
    bd.id, 
    bd.district_name, 
    ST_AsGeoJSON(bd.geom) AS geojson, 
    bdd.population,
    bdd.population_age_under_18_count,
    bdd.population_age_under_18_percentage,
    bdd.population_age_65_count,
    bdd.population_age_65_percentage,
    bdd.unemployment_percentage,
    bdd.youth_unemployment_percentage,
    bdd.communities_of_need_percentage,
    bdd.communities_of_need_under_15_percentage,
    bdd.grundsicherung_65_percentage,
    bdd.population_migration_background_count,
    bdd.population_migration_background_percentage,
    -- Count kindergartens, schools, and colleges
    COUNT(CASE WHEN p.fclass = 'kindergarten' THEN 1 END) AS kindergartens,
    COUNT(CASE WHEN p.fclass = 'school' THEN 1 END) AS schools,
    COUNT(CASE WHEN p.fclass = 'college' THEN 1 END) AS colleges
FROM 
    berlin_districts bd
JOIN 
    berlin_districts_data bdd ON bd.district_name = bdd.district_name
LEFT JOIN 
    berlin_osm_pois p ON ST_Within(p.geom, bd.geom)  -- Check if POI is inside district
GROUP BY 
    bd.id, bd.district_name, bdd.population, 
    bdd.population_age_under_18_count, bdd.population_age_under_18_percentage,
    bdd.population_age_65_count, bdd.population_age_65_percentage,
    bdd.unemployment_percentage, bdd.youth_unemployment_percentage,
    bdd.communities_of_need_percentage, bdd.communities_of_need_under_15_percentage,
    bdd.grundsicherung_65_percentage, bdd.population_migration_background_count,
    bdd.population_migration_background_percentage;
"""


raw_data_berlin = connect(query_berlin)

df_berlin = {
    "id": [],
    "district_name": [],
    "geojson": [],
    "population": [],
    "population_age_under_18_count": [],
    "population_age_under_18_percentage": [],
    "population_age_65_plus_count": [],
    "population_age_65_plus_percentage": [],
    "unemployment": [],
    "youth_unemployment_percentage": [],
    "communities_of_need_percentage": [],
    "communities_of_need_under_15_percentage": [],
    "grundsicherung_65_plus_percentage": [],
    "population_migration_background_count": [],
    "population_migration_background_percentage": [],
    "kindergartens": [],
    "schools": [],
    "colleges": []
}

# Process the data from the raw query results
if raw_data_berlin[1]:
    for tup in raw_data_berlin[0]:
        df_berlin["id"].append(tup[0])
        df_berlin["district_name"].append(tup[1])
        df_berlin["geojson"].append(tup[2])
        df_berlin["population"].append(tup[3]) 
        df_berlin["population_age_under_18_count"].append(tup[4])
        df_berlin["population_age_under_18_percentage"].append(tup[5])
        df_berlin["population_age_65_plus_count"].append(tup[6])
        df_berlin["population_age_65_plus_percentage"].append(tup[7])
        df_berlin["unemployment"].append(tup[8]) 
        df_berlin["youth_unemployment_percentage"].append(tup[9])
        df_berlin["communities_of_need_percentage"].append(tup[10])
        df_berlin["communities_of_need_under_15_percentage"].append(tup[11])
        df_berlin["grundsicherung_65_plus_percentage"].append(tup[12])
        df_berlin["population_migration_background_count"].append(tup[13])
        df_berlin["population_migration_background_percentage"].append(tup[14])
        df_berlin["kindergartens"].append(tup[15])
        df_berlin["schools"].append(tup[16])
        df_berlin["colleges"].append(tup[17])


df_berlin["geometry"] = [shape(json.loads(geojson)) for geojson in df_berlin["geojson"]]
gdf_berlin = gpd.GeoDataFrame(df_berlin, geometry="geometry") # create a GeoDataFrame from df3


# VISUALIZATION  ----------------------------------------------------------------------------------------------------

# interactive map with folium
m_berlin = folium.Map(location=[52.520008, 13.404954], zoom_start=11,
                tiles="CartoDB positron")
# map centered on Berlin

# convert GeoDataFrame to GeoJSON format
geojson_berlin = gdf_berlin.to_json()

# Style function for the districts: no borders, no fill
def style_function(feature):
    return {
        'fillColor': 'transparent',  
        'color': 'transparent',  
        'weight': 0,  
        'opacity':  0 
    }



population_choropleth = folium.Choropleth(
    geo_data=geojson_berlin,
    name='Population',
    data=gdf_berlin,
    columns=['district_name', 'population'],
    key_on='feature.properties.district_name',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Population',
).add_to(m_berlin)


unemployment_choropleth = folium.Choropleth(
    geo_data=geojson_berlin,
    name='Unemployment',
    data=gdf_berlin,
    columns=['district_name', 'unemployment'],
    key_on='feature.properties.district_name',
    fill_color='YlOrRd',  # color scale for Unemployment
    fill_opacity=0.5,
    line_opacity=0.5,
    legend_name='Unemployment Percentage'
).add_to(m_berlin)

# Choropleth for Population under 18 percentage
population_under_18_choropleth = folium.Choropleth(
    geo_data=geojson_berlin,
    name='Population Under 18 Percentage',
    data=gdf_berlin,
    columns=['district_name', 'population_age_under_18_percentage'],
    key_on='feature.properties.district_name',
    fill_color='YlGnBu',  # color scale for Population under 18 Percentage
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Population Under 18 Percentage'
).add_to(m_berlin)

# Choropleth for Population 65+ percentage
population_65plus_choropleth = folium.Choropleth(
    geo_data=geojson_berlin,
    name='Population 65+ Percentage',
    data=gdf_berlin,
    columns=['district_name', 'population_age_65_plus_percentage'],
    key_on='feature.properties.district_name',
    fill_color='YlOrRd',  # color scale for Population 65+ Percentage
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Population 65+ Percentage'
).add_to(m_berlin)

# Choropleth for Unemployment Percentage
unemployment_choropleth = folium.Choropleth(
    geo_data=geojson_berlin,
    name='Youth Unemployment Percentage',
    data=gdf_berlin,
    columns=['district_name', 'youth_unemployment_percentage'],
    key_on='feature.properties.district_name',
    fill_color='YlOrRd',  # color scale for Unemployment
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Youth Unemployment Percentage'
).add_to(m_berlin)

# Add GeoJSON layer for the districts with colorful borders and updated tooltip
# Assuming gdf_berlin is already correctly created from the DataFrame

GeoJson(
    geojson_berlin,  # This will be your geojson data (make sure it's the right one, could also be gdf_berlin['geometry'])
    name='Berlin Districts',
    style_function=style_function,
    tooltip=folium.GeoJsonTooltip(
        fields=[
            'district_name', 
            'population', 
            'unemployment',  # Make sure this matches your column names in gdf_berlin
            'population_age_under_18_percentage', 
            'population_age_65_plus_percentage', 
            'population_age_under_18_count', 
            'population_age_65_plus_count', 
            'population_migration_background_percentage',  # Make sure column name matches
            'youth_unemployment_percentage', 
            'communities_of_need_percentage', 
            'communities_of_need_under_15_percentage', 
            'grundsicherung_65_plus_percentage',
            'kindergartens',  # Kindergarten count
            'schools',        # School count
            'colleges'        # College count
        ],
        aliases=[
            'District:', 
            'Population:', 
            'Unemployment Percentage:', 
            'Under 18 Population Percentage:', 
            '65+ Population Percentage:', 
            'Under 18 Population Count:', 
            '65+ Population Count:', 
            'Migration Background Percentage:', 
            'Youth Unemployment Percentage:', 
            'Communities of Need Percentage:', 
            'Communities of Need Under 15 Percentage:', 
            'Grundsicherung 65+ Percentage:',
            'Kindergartens:',   # Kindergarten label
            'Schools:',         # School label
            'Colleges:'         # College label
        ],
        localize=True
    )
).add_to(m_berlin)


geojson_pois_berlin = gdf_pois_berlin.to_json()  # Convert POI GeoDataFrame to GeoJSON

# Define a color mapping for the POIs based on their `fclass` (type)
fclass_color_map = {
    'college': 'red',
    'school': 'orange',
    'kindergarten': 'yellow'
}

def get_poi_color(fclass):
    return fclass_color_map.get(fclass, 'gray')  # default to gray if not found

# Create Layer Groups for each POI category
poi_layers = {}

# Loop through POIs and add them to layer groups based on `fclass`
for _, poi in gdf_pois_berlin.iterrows():
    lat, lon = poi.geometry.y, poi.geometry.x  # Get latitude and longitude of the POI
    color = get_poi_color(poi['fclass'])  # Get color based on the `fclass`
    
    # Create a DivIcon for each POI (colored dot)
    poi_icon = DivIcon(
        icon_size=(10, 10),  # Small size for the dot
        icon_anchor=(5, 5),  # Center the dot
        html=f'<div style="background-color: {color}; width: 10px; height: 10px; border-radius: 50%;"></div>'  # Colored dot
    )
    
    # Create a Marker with a DivIcon
    marker = folium.Marker(
        location=[lat, lon],
        icon=poi_icon #,
       #tooltip=folium.Tooltip(f'{poi["fclass"]} POI')  # Tooltip with POI type
    )
    
    # Add the marker to a LayerGroup for the specific `fclass`
    if poi['fclass'] not in poi_layers:
        poi_layers[poi['fclass']] = folium.FeatureGroup(name=poi['fclass'])
    
    poi_layers[poi['fclass']].add_child(marker)

# Add all POI layers to the map
for layer in poi_layers.values():
    layer.add_to(m_berlin)

# Add Layer Control for toggling POI layers and other layers
folium.LayerControl(collapsed=False).add_to(m_berlin)


m_berlin.save('berlin_population_unemployment_map.html')





# Hamburg district geometry merged with district information

query_pois_hamburg = """
SELECT 
    id, 
    fclass,
    ST_AsGeoJSON(geom) AS geojson
    
FROM 
    hamburg_osm_pois
WHERE 
    fclass IN ('kindergarten', 'school', 'college');
"""

# connect to DB
raw_data_pois_hamburg = connect(query_pois_hamburg)

# convert to df 
df_pois_hamburg = {
    "id":[],
    "fclass": [],
    "geojson": [],
}

if raw_data_pois_hamburg[1]:
    for tup in raw_data_pois_hamburg[0]:
        df_pois_hamburg ["id"].append(tup[0])
        df_pois_hamburg ["fclass"].append(tup[1])
        df_pois_hamburg ["geojson"].append(tup[2])
  

df_pois_hamburg["geometry"] = [shape(json.loads(geojson)) for geojson in df_pois_hamburg["geojson"]]
gdf_pois_hamburg = gpd.GeoDataFrame(df_pois_hamburg, geometry="geometry") 



query_hamburg = """
SELECT 
    bd.id, 
    bd.district_name, 
    ST_AsGeoJSON(ST_Transform(bd.geom, 4326)) AS geojson,
    bdd.population,
    bdd.population_age_under_18_count,
    bdd.population_age_under_18_percentage,
    bdd.population_age_65_count,
    bdd.population_age_65_percentage,
    bdd.unemployment_percentage,
    bdd.youth_unemployment_percentage,
    bdd.communities_of_need_percentage,
    bdd.communities_of_need_under_15_percentage,
    bdd.grundsicherung_65_percentage,
    bdd.population_migration_background_count,
    bdd.population_migration_background_percentage,
    -- Count kindergartens, schools, and colleges
    COUNT(CASE WHEN p.fclass = 'kindergarten' THEN 1 END) AS kindergartens,
    COUNT(CASE WHEN p.fclass = 'school' THEN 1 END) AS schools,
    COUNT(CASE WHEN p.fclass = 'college' THEN 1 END) AS colleges

FROM 
    hamburg_districts bd
JOIN 
    hamburg_districts_data bdd ON bd.district_name = bdd.district_name
LEFT JOIN 
    hamburg_osm_pois p ON ST_Within(p.geom, ST_Transform(bd.geom, 4326)) -- Check if POI is inside district
GROUP BY 
    bd.id, bd.district_name, bdd.population, 
    bdd.population_age_under_18_count, bdd.population_age_under_18_percentage,
    bdd.population_age_65_count, bdd.population_age_65_percentage,
    bdd.unemployment_percentage, bdd.youth_unemployment_percentage,
    bdd.communities_of_need_percentage, bdd.communities_of_need_under_15_percentage,
    bdd.grundsicherung_65_percentage, bdd.population_migration_background_count,
    bdd.population_migration_background_percentage;
"""


raw_data_hamburg = connect(query_hamburg)

# Adjust the column names in the DataFrame as well to reflect the removed columns
df_hamburg = {
    "id": [],
    "district_name": [],
    "geojson": [],
    "population": [],
    "population_age_under_18_count": [],
    "population_age_under_18_percentage": [],
    "population_age_65_plus_count": [],
    "population_age_65_plus_percentage": [],
    "unemployment": [],
    "youth_unemployment_percentage": [],
    "communities_of_need_percentage": [],
    "communities_of_need_under_15_percentage": [],
    "grundsicherung_65_plus_percentage": [],
    "population_migration_background_count": [],
    "population_migration_background_percentage": [],
    "kindergartens": [],
    "schools": [],
    "colleges": []
}
# Processing the query result
if raw_data_hamburg[1]:
    for tup in raw_data_hamburg[0]:
        df_hamburg["id"].append(tup[0])
        df_hamburg["district_name"].append(tup[1])
        df_hamburg["geojson"].append(tup[2])
        df_hamburg["population"].append(tup[3]) 
        df_hamburg["population_age_under_18_count"].append(tup[4])
        df_hamburg["population_age_under_18_percentage"].append(tup[5])
        df_hamburg["population_age_65_plus_count"].append(tup[6])
        df_hamburg["population_age_65_plus_percentage"].append(tup[7])
        df_hamburg["unemployment"].append(tup[8]) 
        df_hamburg["youth_unemployment_percentage"].append(tup[9])
        df_hamburg["communities_of_need_percentage"].append(tup[10])
        df_hamburg["communities_of_need_under_15_percentage"].append(tup[11])
        df_hamburg["grundsicherung_65_plus_percentage"].append(tup[12])
        df_hamburg["population_migration_background_count"].append(tup[13])
        df_hamburg["population_migration_background_percentage"].append(tup[14])
        df_hamburg["kindergartens"].append(tup[15])
        df_hamburg["schools"].append(tup[16])
        df_hamburg["colleges"].append(tup[17])


df_hamburg["geometry"] = [shape(json.loads(geojson)) for geojson in df_hamburg["geojson"]]
gdf_hamburg = gpd.GeoDataFrame(df_hamburg, geometry="geometry") # create a GeoDataFrame from df3




# VISUALIZATION  ----------------------------------------------------------------------------------------------------

# interactive map with folium
m_hamburg = folium.Map(location=[53.5511, 9.9937], zoom_start=11, 
               tiles="CartoDB positron")
# map centered on hamburg

# convert GeoDataFrame to GeoJSON format
geojson_hamburg = gdf_hamburg.to_json()




population_choropleth = folium.Choropleth(
    geo_data=geojson_hamburg,
    name='Population',
    data=gdf_hamburg,
    columns=['district_name', 'population'],
    key_on='feature.properties.district_name',
    fill_color='YlGnBu',  # color scale for Population
    fill_opacity=0.5,
    line_opacity=0.5,
    legend_name='Population',
    show=False,
).add_to(m_hamburg)


unemployment_choropleth = folium.Choropleth(
    geo_data=geojson_hamburg,
    name='Unemployment',
    data=gdf_hamburg,
    columns=['district_name', 'unemployment'],
    key_on='feature.properties.district_name',
    fill_color='YlOrRd',  # color scale for Unemployment
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Unemployment Percentage'
).add_to(m_hamburg)

# Choropleth for Population under 18 percentage
population_under_18_choropleth = folium.Choropleth(
    geo_data=geojson_hamburg,
    name='Population Under 18 Percentage',
    data=gdf_hamburg,
    columns=['district_name', 'population_age_under_18_percentage'],
    key_on='feature.properties.district_name',
    fill_color='YlGnBu',  # color scale for Population under 18 Percentage
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Population Under 18 Percentage'
).add_to(m_hamburg)

# Choropleth for Population 65+ percentage
population_65plus_choropleth = folium.Choropleth(
    geo_data=geojson_hamburg,
    name='Population 65+ Percentage',
    data=gdf_hamburg,
    columns=['district_name', 'population_age_65_plus_percentage'],
    key_on='feature.properties.district_name',
    fill_color='YlOrRd',  # color scale for Population 65+ Percentage
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Population 65+ Percentage'
).add_to(m_hamburg)

# Choropleth for Unemployment Percentage
unemployment_choropleth = folium.Choropleth(
    geo_data=geojson_hamburg,
    name='Youth Unemployment Percentage',
    data=gdf_hamburg,
    columns=['district_name', 'youth_unemployment_percentage'],
    key_on='feature.properties.district_name',
    fill_color='YlOrRd',  # color scale for Unemployment
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Youth Unemployment Percentage'
).add_to(m_hamburg)

# Add GeoJSON layer for the districts with colorful borders and updated tooltip
# Assuming gdf_hamburg is already correctly created from the DataFrame

GeoJson(
    geojson_hamburg,  # This will be your geojson data (make sure it's the right one, could also be gdf_hamburg['geometry'])
    name='hamburg Districts',
    style_function=style_function,
    tooltip=folium.GeoJsonTooltip(
        fields=[
            'district_name', 
            'population', 
            'unemployment',  # Make sure this matches your column names in gdf_hamburg
            'population_age_under_18_percentage', 
            'population_age_65_plus_percentage', 
            'population_age_under_18_count', 
            'population_age_65_plus_count', 
            'population_migration_background_percentage',  # Make sure column name matches
            'youth_unemployment_percentage', 
            'communities_of_need_percentage', 
            'communities_of_need_under_15_percentage', 
            'grundsicherung_65_plus_percentage',
            'kindergartens',  # Kindergarten count
            'schools',        # School count
            'colleges'        # College count
        ],
        aliases=[
            'District:', 
            'Population:', 
            'Unemployment Percentage:', 
            'Under 18 Population Percentage:', 
            '65+ Population Percentage:', 
            'Under 18 Population Count:', 
            '65+ Population Count:', 
            'Migration Background Percentage:', 
            'Youth Unemployment Percentage:', 
            'Communities of Need Percentage:', 
            'Communities of Need Under 15 Percentage:', 
            'Grundsicherung 65+ Percentage:',
            'Kindergartens:',   # Kindergarten label
            'Schools:',         # School label
            'Colleges:'         # College label
        ],
        localize=True
    )
).add_to(m_hamburg)


geojson_pois_hamburg = gdf_pois_hamburg.to_json()  # Convert POI GeoDataFrame to GeoJSON

# Define a color mapping for the POIs based on their `fclass` (type)
fclass_color_map = {
    'college': 'red',
    'school': 'orange',
    'kindergarten': 'yellow',
    'dentist': 'cadetblue',
    'doctors': 'darkblue',
    'hospital': 'lightblue',
    'park': 'green',
  
}

def get_poi_color(fclass):
    return fclass_color_map.get(fclass, 'gray')  # default to gray if not found

# Create Layer Groups for each POI category
poi_layers = {}

# Loop through POIs and add them to layer groups based on `fclass`
for _, poi in gdf_pois_hamburg.iterrows():
    lat, lon = poi.geometry.y, poi.geometry.x  # Get latitude and longitude of the POI
    color = get_poi_color(poi['fclass'])  # Get color based on the `fclass`
    
    # Create a DivIcon for each POI (colored dot)
    poi_icon = DivIcon(
        icon_size=(10, 10),  # Small size for the dot
        icon_anchor=(5, 5),  # Center the dot
        html=f'<div style="background-color: {color}; width: 10px; height: 10px; border-radius: 50%;"></div>'  # Colored dot
    )
    
    # Create a Marker with a DivIcon
    marker = folium.Marker(
        location=[lat, lon],
        icon=poi_icon #,
       #tooltip=folium.Tooltip(f'{poi["fclass"]} POI')  # Tooltip with POI type
    )
    
    # Add the marker to a LayerGroup for the specific `fclass`
    if poi['fclass'] not in poi_layers:
        poi_layers[poi['fclass']] = folium.FeatureGroup(name=poi['fclass'])
    
    poi_layers[poi['fclass']].add_child(marker)

# Add all POI layers to the map
for layer in poi_layers.values():
    layer.add_to(m_hamburg)

# Add Layer Control for toggling POI layers and other layers
folium.LayerControl(collapsed=False).add_to(m_hamburg)


m_hamburg.save('hamburg_population_unemployment_map.html')










