from shiny import App, ui, reactive
import plotly.express as px
import pandas as pd
from shinywidgets import output_widget, render_widget
import plotly.graph_objects as go
from plotly.callbacks import Points

from utils import get_latest_data, get_full_dataframe


#################### Change Data ####################
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

            # MAP
            output_widget("covid_map"),
            full_screen=True,
        ),

        # Right Chart
        ui.div(
            ui.tags.h3("New Positive Cases (Top 20)"),
            output_widget("cases_plot"),

            full_screen=True,
        ),

        col_widths=(3, 6, 3)
    )
)


#################### SERVER ####################

def server(input, output, session):

    # -------------- Country Filter ----------
    selected_country = reactive.Value(None)

    @reactive.Calc
    def filtered_daily():
        c = selected_country()
        if c is None:
            return df_daily
        return df[df["country"] == c].sort_values("date")

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
            filtered_daily(),
            x="date",
            y=col,
            title=f"Global {input.metric_type().capitalize()} {input.measure().capitalize()} per Day",
            labels={col: input.measure().capitalize(), "date": "Date"},
            color_discrete_sequence=["#00B4FF"]
        )
        fig.update_layout(
            margin=dict(l=20, r=20, t=40, b=30)
        )
        # fig.update_xaxes(type="date", tickformat="%Y-%m-%d", tickangle=-45)
        return fig

    @render_widget
    def plot_bottom():
        col = metric_column()
        fig = px.bar(
            filtered_daily(),
            x="date",
            y=col,
            title=f"{input.metric_type().capitalize()} {input.measure().capitalize()} Over Time",
            labels={col: input.measure().capitalize(), "date": "Date"},
            color_discrete_sequence=["orange"]
        )
        fig.update_layout(
            margin=dict(l=20, r=20, t=40, b=30)
        )
        # fig.update_xaxes(type="date", tickformat="%Y-%m-%d", tickangle=-45)
        return fig

    # ---------- MAP ----------

    @render_widget
    def covid_map():
        col = metric_column()
        data = df_latest.copy()

        # Size of dots
        values = data[col].fillna(0).clip(lower=0)
        size = (values ** 0.5) / 5
        if "cumulative" in col:
            size = size / 30
        if "deaths" in col:
            size = size * 30

        # Hover-Text
        cum_cases = data["cumulative_total_cases"].fillna(0).round().astype("int64").astype(str)
        daily_cases = data["daily_new_cases"].fillna(0).round().astype("int64").astype(str)
        cum_deaths = data["cumulative_total_deaths"].fillna(0).round().astype("int64").astype(str)
        daily_deaths = data["daily_new_deaths"].fillna(0).round().astype("int64").astype(str)

        hover_text = (
                "<b>" + data["country"] + "</b><br>"
                "Cumulative Cases: <b>" + cum_cases + "</b><br>"
                "Daily New Cases: <b>" + daily_cases + "</b><br><br>"
                "Cumulative Deaths: <b>" + cum_deaths + "</b><br>"
                "Daily New Deaths: <b>" + daily_deaths + "</b>"
        )

        fig = go.FigureWidget(
            data=[
                go.Scattergeo(
                    lat=data["latitude"],
                    lon=data["longitude"],
                    text=data["country"],
                    customdata=data["country"],
                    mode="markers",
                    hovertext=hover_text,
                    hoverinfo="text",
                    marker=dict(
                        size=size,
                        color="red",
                        opacity=0.5,
                    ),
                )
            ]
        )

        # MAP
        fig.update_geos(
            projection_type="natural earth",
            showcountries=True,
            countrycolor="black",
            showcoastlines=True,
            coastlinecolor="black",
            showland=True,
            landcolor="#f0f0f0",
            # fitbounds="locations",
        )

        fig.update_layout(
            width=900,
            height=700,
            title=f"{input.metric_type().capitalize()} {input.measure().capitalize()} by Country",
        )

        # Click Event
        def on_point_click(trace, points: Points, state):
            if not points.point_inds:
                return
            idx = points.point_inds[0]
            country = trace.customdata[idx]
            print("Clicked on map:", country)
            selected_country.set(country)

        fig.data[0].on_click(on_point_click)

        return fig

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
        fig.update_layout(margin=dict(l=50, r=20, t=60, b=40))

        # On Click
        w = go.FigureWidget(fig.data, fig.layout)

        def on_bar_click(trace, points: Points, state):
            if not points.point_inds:
                return
            idx = points.point_inds[0]

            country = trace.y[idx]
            print("Clicked country:", country)
            selected_country.set(country)

        # Attach click handler to first trace
        w.data[0].on_click(on_bar_click)

        return w


if __name__ == "__main__":
    app = App(app_ui, server)
    app.run()

