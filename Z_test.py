import folium

# Center the map at a location (e.g., Levi, Finland)
m = folium.Map(location=[67.805, 24.802], zoom_start=10)

# Save as HTML
m.save("map.html")