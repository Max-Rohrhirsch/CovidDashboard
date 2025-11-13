import folium
import pandas as pd
from shiny import App, ui, render
import plotly.express as px
from shinywidgets import output_widget, render_widget

from utils import get_latest_data, get_full_dataframe

df = get_full_dataframe()
df_daily = (
    df.groupby("date", as_index=False)
      .agg({
          "daily_new_cases": "sum",
          "daily_new_deaths": "sum"
      })
      .sort_values("date")
)
df_latest = get_latest_data()


#################### UI ####################
app_ui = ui.page_fluid(
    # HEADER
    ui.tags.div(
        "Global COVID-19 Dashboard",
        style=(
            "background-color:#1f2c3c;"
            "color:white;"
            "padding:20px;"
            "font-size:28px;"
            "font-weight:600;"
            "margin:0"
            "margin-bottom:15px;"
        ),
    ),

    # MAIN BODY
    ui.layout_columns(
        ui.div(
            output_widget("plot_top"),
            output_widget("plot_bottom"),
        ),

        ui.div(
            ui.tags.h3("New Positive Cases (Map)"),
            ui.output_ui("covid_map"),
            full_screen=True,
        ),

        ui.card(
            ui.tags.h3("New Positive Cases (Top 20)"),
            output_widget("cases_plot", height="700px"),

            full_screen=True,
        ),

        col_widths=(3, 6, 3)
    )
)


# ================== SERVER ==================

def server(input, output, session):

    # ----------- LEFT SIDE -----------
    # @output
    @render_widget
    def plot_top():
        fig = px.bar(
            df_daily,
            x="date",
            y="daily_new_cases",
            title="Global New Positive Cases per Day",
            labels={"daily_new_cases": "Cases", "date": "Date"},
            color_discrete_sequence=["#00B4FF"]
        )
        fig.update_layout(
            margin=dict(l=20, r=20, t=40, b=30)
        )
        return fig

    # @output
    @render_widget
    def plot_bottom():
        fig = px.bar(
            df_daily,
            x="date",
            y="daily_new_deaths",
            title="Global New Deaths per Day",
            labels={"daily_new_deaths": "Deaths", "date": "Date"},
            color_discrete_sequence=["orange"]
        )
        fig.update_layout(
            margin=dict(l=20, r=20, t=40, b=30)
        )
        return fig

    # ---------- MAP (Folium) ----------

    @output
    @render.ui
    def covid_map():
        m = folium.Map(
            location=[30, 0],
            zoom_start=2,
            height="100%",
            width="100%",
            tiles="CartoDB positron",
        )

        for _, row in df_latest.iterrows():
            if pd.isna(row["latitude"]) or pd.isna(row["longitude"]):
                continue

            html = f"""
                <b>{row["country"]}</b> 
                <br>
                Comulated Cases: <b>{row['cumulative_total_cases']}</b><br>
                Daily new Cases: <b>{row['daily_new_cases']}</b><br>
                <br>
                Comulated Deaths: <b>{row['cumulative_total_deaths']}</b><br>
                Daily new Deaths: <b>{row['daily_new_deaths']}</b><br>
                """

            folium.Circle(
                location=[row["latitude"], row["longitude"]],
                radius=(int(row["daily_new_cases"]) ** 0.5) * 10000,
                color="blue",
                fill=True,
                tooltip=html,
                fill_opacity=0.5
            ).add_to(m)
        map_html = m._repr_html_()

        map_html = map_html.replace("height:0;", "height:800px;")
        map_html = map_html.replace("padding-bottom:60%;", "padding-bottom:0;")
        return ui.HTML(f"<div style='height:900px; width:100%;'>{map_html}</div>")

    # ---------- BAR CHART RIGHT ----------

    @render_widget
    def cases_plot():
        data = (
            df_latest.sort_values("daily_new_cases", ascending=False)
            .head(20)
        )

        fig = px.bar(
            data,
            x="daily_new_cases",
            y="country",
            orientation="h",
            title="Top 20 Countries by New Positive Cases",
            labels={"daily_new_cases": "New Cases", "country": ""},
            color_discrete_sequence=["#00B4FF"]
        )

        # Make the largest at top (Plotly draws bars from bottom by default)
        fig.update_yaxes(autorange="reversed")

        fig.update_layout(
            height=700,
            margin=dict(l=50, r=20, t=60, b=40)
        )

        return fig


if __name__ == "__main__":
    app = App(app_ui, server)
    app.run()
