# import dash
# import dash_core_components as dcc
# import dash_html_components as html
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

# select data from PostgreSQL database 
query1 = "SELECT id, fclass, geom FROM berlin_osm_green_areas;"
query2 = "SELECT id, district_name, ST_AsGeoJSON(geom) as geojson FROM berlin_districts;"


# establish connection and fetch queries
raw_data = connect(query2)
#first figure bar --------------------------------------------------
df2 = {"id": [],"district_name" : [], "geojson" : []}
# transform data
if raw_data[1]:
    for tup in raw_data[0]:
        df2["id"].append(tup[0])
        df2["district_name"].append(tup[1])
        df2["geojson"].append(tup[2])
    

else:
    print("Error")

df_2 = pd.DataFrame(df2)
df_2['geojson'] = df_2['geojson'].apply(json.loads)
df_2['geometry'] = df_2['geojson'].apply(lambda x: shape(x))  # Convert geojson into Shapely geometries

# Now create a GeoDataFrame from df_2
gdf = gpd.GeoDataFrame(df_2, geometry='geometry')

# Ensure the GeoDataFrame is in a valid CRS (use EPSG 4326 for lat/lon)
gdf = gdf.set_crs("EPSG:4326", allow_override=True)

# Plot the geometries
ax = gdf.plot(
    figsize=(10, 10),  # Set the figure size
    edgecolor='black',  # Outline color for polygons
    color='lightblue',  # Fill color for polygons
    legend=True  # Show legend (if necessary)
)

# Optionally, add title and labels
ax.set_title("Multipolygon Data")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
plt.show()