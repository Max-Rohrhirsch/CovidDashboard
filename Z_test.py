# import folium
#
# # Center the map at a location (e.g., Levi, Finland)
# m = folium.Map(location=[67.805, 24.802], zoom_start=10)
#
# # Save as HTML
# m.save("map.html")

# test_app.py


# test_app.py
import pandas as pd
import plotly.graph_objects as go
from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_widget

# --- Example Data ---
df = pd.DataFrame({
    "country": ["germany", "finland", "france"],
    "lat":     [51.1657, 61.9241, 46.2276],
    "lon":     [10.4515, 25.7482, 2.2137],
    "value":   [12000000, 3000000, 8000000],
})


# --- UI ---
app_ui = ui.page_fluid(
    ui.h2("Clickable Plotly Map with Borders"),
    output_widget("map", height="600px"),
    ui.tags.hr(),
    ui.output_text_verbatim("clicked_country")
)


# --- SERVER ---
def server(input, output, session):
    selected_country = reactive.value(None)

    @render_widget
    def map():
        fig = go.FigureWidget(
            data=[
                go.Scattergeo(
                    lat=df["lat"],
                    lon=df["lon"],
                    text=df["country"],
                    customdata=df["country"],
                    mode="markers",
                    marker=dict(
                        size=df["value"] / 3000,   # <-- scale sizes
                        sizemode="area",
                        sizeref=2,
                        color="blue",
                        opacity=0.7
                    ),
                )
            ]
        )

        # CLICK HANDLER
        def on_click(trace, points, state):
            if not points.point_inds:
                return
            idx = points.point_inds[0]
            country = trace.customdata[idx]
            print("Clicked:", country)
            selected_country.set(country)

        fig.data[0].on_click(on_click)

        # MAP STYLING (with borders)
        fig.update_geos(
            projection_type="natural earth",
            showcountries=True,
            countrycolor="black",
            showsubunits=True,
            subunitcolor="gray",
            showcoastlines=True,
            coastlinecolor="black",
            showland=True,
            landcolor="#f0f0f0",
        )

        fig.update_layout(
            width=1400,  # deutlich breiter als Default 700
            height=800,
            margin=dict(l=10, r=10, t=40, b=10),
            title="Click a marker — Borders enabled",
        )

        return fig

    @output
    @render.text
    def clicked_country():
        c = selected_country.get()
        return f"Selected: {c if c else '-'}"


app = App(app_ui, server)

if __name__ == "__main__":
    app.run()
