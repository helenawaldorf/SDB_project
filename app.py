import geopandas as gpd
import numpy as np
import json
from shapely.geometry import shape
from db_connect.connect import connect 
import folium
from folium import GeoJson
from folium.features import DivIcon



# BERLIN ------------------------------------------------------------------------------------------------------
# QUERIES  ----------------------------------------------------------------------------------------------------
# select data from PostgreSQL database  

# data: access to education 
query_pois_berlin = """
SELECT 
    id, 
    fclass,
    ST_AsGeoJSON(geom) AS geojson,
    name 
FROM 
    berlin_osm_pois
WHERE 
    fclass IN ('kindergarten', 'school', 'college');
"""

# connect to DB
raw_data_pois_berlin = connect(query_pois_berlin)

df_pois_berlin = {
    "id":[],
    "fclass": [],
    "geojson": [],
    "name": []
}

if raw_data_pois_berlin[1]:
    for tup in raw_data_pois_berlin[0]:
        df_pois_berlin ["id"].append(tup[0])
        df_pois_berlin ["fclass"].append(tup[1])
        df_pois_berlin ["geojson"].append(tup[2])
        df_pois_berlin ["name"].append(tup[3])
  

df_pois_berlin["geometry"] = [shape(json.loads(geojson)) for geojson in df_pois_berlin["geojson"]]
gdf_pois_berlin = gpd.GeoDataFrame(df_pois_berlin, geometry="geometry") 
gdf_pois_berlin = gdf_pois_berlin.set_crs("EPSG:4326")
gdf_pois_berlin.to_file("query_geojson/gdf_pois_berlin.geojson", driver="GeoJSON")

# data: district geometry merged with district information and count of education access within district 
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

    COUNT(CASE WHEN p.fclass = 'kindergarten' THEN 1 END) AS kindergartens,
    COUNT(CASE WHEN p.fclass = 'school' THEN 1 END) AS schools,
    COUNT(CASE WHEN p.fclass = 'college' THEN 1 END) AS colleges
FROM 
    berlin_districts bd
JOIN 
    berlin_districts_data bdd ON bd.district_name = bdd.district_name
LEFT JOIN 
    berlin_osm_pois p ON ST_Within(p.geom, bd.geom)  
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
gdf_berlin = gpd.GeoDataFrame(df_berlin, geometry="geometry") # create a GeoDataFrame 
gdf_berlin = gdf_berlin.set_crs("EPSG:4326")
gdf_berlin.to_file("query_geojson/gdf_berlin.geojson", driver="GeoJSON")

# VISUALIZATION  ----------------------------------------------------------------------------------------------------

# interactive map with folium
m_berlin = folium.Map(location = [52.520008, 13.404954], zoom_start = 10, # map centered on Berlin
                tiles = "CartoDB positron")

geojson_berlin = gdf_berlin.to_json() # convert GeoDataFrame to GeoJSON format

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
    data = gdf_berlin,
    columns = ['district_name', 'population'],
    key_on = 'feature.properties.district_name',
    fill_color = 'Purples',  
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
    data=gdf_berlin,
    columns=['district_name', 'unemployment'],
    key_on='feature.properties.district_name',
    fill_color='YlGnBu',  
    fill_opacity=0.7,
    line_opacity=0.2,
    bins=unemployment_rate_bins,
    legend_name=None,  
    show_legend = False  
    
).add_to(m_berlin)

for child in unemployment_choropleth_berlin._children:
        if child.startswith("color_map"):
            del unemployment_choropleth_berlin._children[child]


population_under_18_rate_bins = np.linspace(13.8, 18.8, 7) 

# choropleth for population under 18 
population_under_18_chloropleth = folium.Choropleth(
    geo_data=geojson_berlin,
    show=False,
    name='Population % (< 18 years)',
    data=gdf_berlin,
    columns=['district_name', 'population_age_under_18_percentage'],
    key_on='feature.properties.district_name',
    bins = population_under_18_rate_bins,
    fill_color='YlOrRd',  
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name=None,  
    show_legend = False 
).add_to(m_berlin)

for child in population_under_18_chloropleth._children:
       if child.startswith("color_map"):
           del population_under_18_chloropleth._children[child]

# choropleth for population 65+
# population_65plus_choropleth = folium.Choropleth(
#     geo_data=geojson_berlin,
#     show=False,
#     name='Population % (> 65 years)',
#     data=gdf_berlin,
#     columns=['district_name', 'population_age_65_plus_percentage'],
#     key_on='feature.properties.district_name',
#     fill_color='YlOrRd',  
#     fill_opacity=0.7,
#     line_opacity=0.2,
#     legend_name='Population % (> 65 years)'
# ).add_to(m_berlin)

youth_unemployment_rate_bins_rate_bins = np.linspace(1.1, 4.9, 8) 

# choropleth for youth unemployment rate
youth_unemployment_choropleth = folium.Choropleth(
    geo_data=geojson_berlin,
    show=False,
    name='Unemployment rate % (15-25 years)',
    data=gdf_berlin,
    columns=['district_name', 'youth_unemployment_percentage'],
    key_on='feature.properties.district_name',
    fill_color='PuRd',  
    fill_opacity=0.7,
    line_opacity=0.2,
    bins = youth_unemployment_rate_bins_rate_bins, 
    legend_name = 'Unemployment rate % (15-25 years)'
).add_to(m_berlin)

for child in youth_unemployment_choropleth._children:
       if child.startswith("color_map"):
           del youth_unemployment_choropleth._children[child]


# add education points 
geojson_pois_berlin = gdf_pois_berlin.to_json()  # convert POI GeoDataFrame to GeoJSON

# color mapping for `fclass` 
fclass_color_map = {
    'college': '#CBE896',
    'school': '#F37A0F',
    'kindergarten': '#8ACEF5'
}



def get_poi_color(fclass):
    return fclass_color_map.get(fclass, 'gray')  

# for each POI category: layer 
poi_layers = {}
for _, poi in gdf_pois_berlin.iterrows():
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
        icon=poi_icon 
    )
    
    if poi['fclass'] not in poi_layers:
        poi_layers[poi['fclass']] = folium.FeatureGroup(name=poi['fclass'], show=False) 
    poi_layers[poi['fclass']].add_child(marker)

for layer in poi_layers.values():
    layer.add_to(m_berlin)

# Layer Control: toggling layers
folium.LayerControl().add_to(m_berlin)

m_berlin.save('web_application/berlin_population_unemployment_map.html')





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
gdf_pois_hamburg = gdf_pois_hamburg.set_crs("EPSG:4326")
gdf_pois_hamburg.to_file("query_geojson/gdf_pois_hamburg.geojson", driver="GeoJSON")

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
    
    COUNT(CASE WHEN p.fclass = 'kindergarten' THEN 1 END) AS kindergartens,
    COUNT(CASE WHEN p.fclass = 'school' THEN 1 END) AS schools,
    COUNT(CASE WHEN p.fclass = 'college' THEN 1 END) AS colleges

FROM 
    hamburg_districts bd
JOIN 
    hamburg_districts_data bdd ON bd.district_name = bdd.district_name
LEFT JOIN 
    hamburg_osm_pois p ON ST_Within(p.geom, ST_Transform(bd.geom, 4326)) 
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
gdf_hamburg = gpd.GeoDataFrame(df_hamburg, geometry="geometry") 

gdf_hamburg = gdf_hamburg.set_crs("EPSG:4326")
gdf_hamburg.to_file("query_geojson/gdf_hamburg.geojson", driver="GeoJSON")


# VISUALIZATION  ----------------------------------------------------------------------------------------------------

m_hamburg = folium.Map(location=[53.5511, 9.9937], zoom_start=10, 
               tiles="CartoDB positron") # map centered on hamburg

geojson_hamburg = gdf_hamburg.to_json()


# districts with data information
GeoJson(
    geojson_hamburg,  
    name='Hamburg Districts',
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
    data=gdf_hamburg,
    columns=['district_name', 'population'],
    key_on='feature.properties.district_name',
    fill_color='Purples',  
    fill_opacity=0.5,
    line_opacity=0.5,
    legend_name='Population',
).add_to(m_hamburg)

# choropleth map by unemployment rate 
unemployment_choropleth = folium.Choropleth(
    geo_data=geojson_hamburg,
    show=False,
    name='Unemployment rate % (15-65 years)',
    data=gdf_hamburg,
    columns=['district_name', 'unemployment'],
    key_on='feature.properties.district_name',
    bins=unemployment_rate_bins,
    fill_color='YlGnBu',  
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name=None,  
    show_legend = False  
).add_to(m_hamburg)

for child in unemployment_choropleth._children:
        if child.startswith("color_map"):
            del unemployment_choropleth._children[child]


# choropleth for population under 18 
population_under_18_chloropleth = folium.Choropleth(
    geo_data=geojson_hamburg,
    show=False,
    name='Population % (< 18 years)',
    data=gdf_hamburg,
    columns=['district_name', 'population_age_under_18_percentage'],
    key_on='feature.properties.district_name',
    fill_color='YlOrRd', 
    bins = population_under_18_rate_bins,
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name = None,  
    show_legend = False 
).add_to(m_hamburg)

for child in population_under_18_chloropleth._children:
       if child.startswith("color_map"):
           del population_under_18_chloropleth._children[child]

# choropleth for population 65+ 
# population_65plus_choropleth = folium.Choropleth(
#     geo_data=geojson_hamburg,
#     show=False,
#     name='Population % (> 65 years)',
#     data=gdf_hamburg,
#     columns=['district_name', 'population_age_65_plus_percentage'],
#     key_on='feature.properties.district_name',
#     fill_color='YlOrRd',  
#     fill_opacity=0.7,
#     line_opacity=0.2,
#     legend_name='Population % (> 65 years)'
# ).add_to(m_hamburg)

# choropleth for youth unemployment rate
youth_unemployment_choropleth = folium.Choropleth(
    geo_data=geojson_hamburg,
    show=False,
    name='Unemployment rate % (15-25 years)',
    data=gdf_hamburg,
    columns=['district_name', 'youth_unemployment_percentage'],
    key_on='feature.properties.district_name',
    fill_color='PuRd',  
    fill_opacity=0.7,
    line_opacity=0.2,
    bins = youth_unemployment_rate_bins_rate_bins, 
    legend_name = 'Unemployment rate % (15-25 years)'
).add_to(m_hamburg)

for child in youth_unemployment_choropleth._children:
       if child.startswith("color_map"):
           del youth_unemployment_choropleth._children[child]


# add education points 
geojson_pois_hamburg = gdf_pois_hamburg.to_json()  



poi_layers = {}
for _, poi in gdf_pois_hamburg.iterrows():
    lat, lon = poi.geometry.y, poi.geometry.x  
    color = get_poi_color(poi['fclass'])  

    poi_icon = DivIcon(
        icon_size=(5, 5),  
        icon_anchor=(5, 5),  
        html=f'<div style="background-color: {color}; width: 10px; height: 10px; border-radius: 50%;border: 0.5px solid black;"></div>'   # colored dot
    )
    marker = folium.Marker(
        location=[lat, lon],
        icon=poi_icon 
    )

    if poi['fclass'] not in poi_layers:
        poi_layers[poi['fclass']] = folium.FeatureGroup(name=poi['fclass'], show=False) 
    
    poi_layers[poi['fclass']].add_child(marker)


for layer in poi_layers.values():
    layer.add_to(m_hamburg)

folium.LayerControl().add_to(m_hamburg)

m_hamburg.save('web_application/hamburg_population_unemployment_map.html')