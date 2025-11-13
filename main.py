import folium
import pandas as pd
from shiny import App, ui, render, reactive
import plotly.express as px
from shinywidgets import output_widget, render_widget

from utils import get_latest_data, get_full_dataframe

df = get_full_dataframe()
df_daily = (
    df.groupby("date", as_index=False)
        .agg({
          "daily_new_cases": "sum",
          "daily_new_deaths": "sum",
          "cumulative_total_cases": "sum",
          "cumulative_total_deaths": "sum",
        })
        .sort_values("date")
        .dropna()
)
df_latest = get_latest_data()
print(df_latest.head(10).to_string())
print(df_latest.head(-10).to_string())

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
            ui.row(
                ui.column(
                    6,
                    ui.input_select(
                        "metric_type",
                        "Metric type",
                        {"new": "New", "cumulative": "Cumulative"},
                        selected="new"
                    ),
                ),
                ui.column(
                    6,
                    ui.input_select(
                        "measure",
                        "Measure",
                        {"cases": "Cases", "deaths": "Deaths"},
                        selected="cases"
                    ),
                ),
            ),
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
    # ----------- Filters -----------
    @reactive.Calc
    def metric_column():
        metric_type = input.metric_type()
        measure = input.measure()

        if metric_type == "new" and measure == "cases":
            return "daily_new_cases"
        if metric_type == "new" and measure == "deaths":
            return "daily_new_deaths"
        if metric_type == "cumulative" and measure == "cases":
            return "cumulative_total_cases"
        if metric_type == "cumulative" and measure == "deaths":
            return "cumulative_total_deaths"

    # ----------- LEFT SIDE -----------
    @render_widget
    def plot_top():
        col = metric_column()
        fig = px.bar(
            df_daily,
            x="date",
            y=col,
            title=f"Global {input.metric_type().capitalize()} {input.measure().capitalize()} per Day",
            labels={col: input.measure().capitalize(), "date": "Date"},
            color_discrete_sequence=["#00B4FF"]
        )
        fig.update_layout(
            margin=dict(l=20, r=20, t=40, b=30)
        )
        return fig

    @render_widget
    def plot_bottom():
        col = metric_column()
        fig = px.bar(
            df_daily,
            x="date",
            y=col,
            title=f"{input.metric_type().capitalize()} {input.measure().capitalize()} Over Time",
            labels={col: input.measure().capitalize(), "date": "Date"},
            color_discrete_sequence=["orange"]
        )
        fig.update_layout(
            margin=dict(l=20, r=20, t=40, b=30)
        )
        return fig

    # ---------- MAP ----------

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


            value = row[metric_column()]

            if pd.isna(value):
                continue

            radius = (int(value) ** 0.5) * 10000
            if "cumulative" in metric_column():
                radius /= 50

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
                radius=radius,
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
        col = metric_column()

        data = (
            df_latest.sort_values(col, ascending=False)
            .head(20)
        )

        fig = px.bar(
            data,
            x=col,
            y="country",
            orientation="h",
            title=f"Top 20 Countries by {input.metric_type().capitalize()} {input.measure().capitalize()}",
            labels={col: input.measure().capitalize(), "country": ""},
            color_discrete_sequence=["#00B4FF"]
        )

        fig.update_yaxes(autorange="reversed")
        fig.update_layout(height=700, margin=dict(l=50, r=20, t=60, b=40))
        return fig


if __name__ == "__main__":
    app = App(app_ui, server)
    app.run()

