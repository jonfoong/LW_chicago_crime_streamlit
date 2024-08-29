# import streamlit as st
# import pydeck as pdk
# import geopandas as gpd
# import json
# from shapely.geometry import shape

# # General Settings
# st.set_page_config(page_title="Chicago Crime Map Overview", page_icon="🗺️", layout="wide")

# # Sidebar
# st.sidebar.header('Settings')

# # Map Style
# map_style_options = {
#     "Dark Mode": "mapbox://styles/mapbox/dark-v11",
#     "Satellite View": "mapbox://styles/mapbox/satellite-v9",
#     "Satellite with Streets": "mapbox://styles/mapbox/satellite-streets-v12",
#     "Navigation Day": "mapbox://styles/mapbox/navigation-day-v1",
#     "Navigation Night": "mapbox://styles/mapbox/navigation-night-v1"
# }
# selected_style_name = st.sidebar.selectbox(
#     "Select your map style:",
#     list(map_style_options.keys())
# )
# chicago_map_style = map_style_options[selected_style_name]

# # Page content
# st.title('Chicago Crime Map')

# @st.cache_data
# def load_districts_data():
#     # Pfad zur lokalen JSON-Datei
#     file_path = 'data/geodata.json'
    
#     # Daten aus der lokalen Datei lesen
#     with open(file_path, 'r', encoding='utf-8') as file:
#         districts_json = json.load(file)
    
#     # Capitalize the community names in the JSON data
#     for district in districts_json:
#         if 'community' in district:
#             district['community'] = district['community'].title()
    
#     # Create GeoDataFrame
#     districts = gpd.GeoDataFrame.from_features([{
#         'geometry': shape(district['the_geom']),
#         'properties': district
#     } for district in districts_json])
    
#     # Change GeoDataFrame in GeoJSON-Format
#     districts_geojson = json.loads(districts.to_json())
#     return districts_geojson

# # Settings: Main page
# col1, col2, col3 = st.columns(3, vertical_alignment='bottom')

# with col1:
#     days_to_predict = st.number_input("Days to predict:", value=7)
# with col2:
#     districts_geojson = load_districts_data()  # Ensure data is loaded here
#     communities = [feature['properties']['community'] for feature in districts_geojson['features']]
#     district_selected = st.selectbox(
#         "Which district do you want to look at?",
#         list(set(communities))  # Ensure unique values
#     )
# with col3:
#     submit = st.button("Get crime prediction", 'prediction')

# # Input warning
# if days_to_predict >= 30:
#     st.warning("Please bear in mind that long-term forecasts are becoming less accurate!", icon="⚠️")

# # Create the interactive map only if the button is pressed
# if submit:
#     st.pydeck_chart(pdk.Deck(
#         map_style=chicago_map_style,
#         initial_view_state=pdk.ViewState(
#             latitude=41.881832,
#             longitude=-87.623177,
#             zoom=10,
#             pitch=45,  # 45-degree pitch
#         ),
#         layers=[
#             pdk.Layer(
#                 'GeoJsonLayer',
#                 data=districts_geojson,
#                 pickable=True,
#                 stroked=True,
#                 filled=True,
#                 extruded=True,
#                 elevation_scale=50,
#                 elevation_range=[0, 1000],
#                 get_line_color=[0, 0, 139],  # Dark blue
#                 auto_highlight=True,
#                 get_fill_color=f"properties.community == '{district_selected}' ? [255, 99, 71, 200] : [200, 230, 250, 200]",  # Red for selected, light blue for others
#                 get_elevation=f"properties.community == '{district_selected}' ? 20 : 0",  # Elevation for selected
#             )
#         ],
#         tooltip={
#             "html": "<b>District(No.):</b> {community} ({area_numbe})",
#             "style": {"backgroundColor": "white", "color": "black"}
#         }
#     ), use_container_width=True)
