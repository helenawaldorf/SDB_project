import psycopg2
import pandas as pd
from shapely import wkb
import geojson
import plotly.express as px

# database connection parameters
host = "localhost"  
database = "sdb_project"
user = "waldo"
password = ""

# Connection string
conn = psycopg2.connect(
    host=host,
    database=database,
    user=user,
    password=password
)

# Create a cursor object
cursor = conn.cursor()

# Define the SQL query to extract data from your spatial table
sql_query = """
SELECT 
    id, 
    fclass, 
    geom
FROM 
    hamburg_osm_water_a_free_1;
"""

# Execute the SQL query
cursor.execute(sql_query)
# Fetch the data
data = cursor.fetchall()

# Convert the data to a DataFrame
columns = ['id', 'fclass', 'geom']
df = pd.DataFrame(data, columns=columns)

# Convert the WKB geometries to GeoJSON with explicit 'id' and 'fclass'
def wkb_to_geojson(wkb_geom, id_value, fclass_value):
    geom = wkb.loads(wkb_geom)  # Load WKB into Shapely geometry
    return geojson.Feature(geometry=geom, properties={'id': id_value, 'fclass': fclass_value})

# Apply the conversion to each row
df['geojson'] = df.apply(
    lambda row: wkb_to_geojson(row['geom'], row['id'], row['fclass']),
    axis=1
)

# Now, extract the geometries and plot them using Plotly
features = [feature for feature in df['geojson']]

# Create a GeoJSON FeatureCollection
geojson_data = geojson.FeatureCollection(features)

# Plot the data using Plotly
fig = px.choropleth_mapbox(
    geojson=geojson_data,
    locations=[f['properties']['id'] for f in features],  # Use the 'id' for locations
    color=[f['properties']['fclass'] for f in features],  # Use 'fclass' as color
    hover_name=[f['properties']['fclass'] for f in features],
    color_continuous_scale="Viridis",  # You can change the color scale
    title="Water Features in Hamburg (OSM Data)",
    height=600
)

# Update layout for better map appearance
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(mapbox_style="carto-positron", mapbox_zoom=12, mapbox_center={"lat": 53.5511, "lon": 9.9937})  # Center the map on Hamburg

fig.show()

# Close the database connection
cursor.close()
conn.close()