import folium
import matplotlib.pyplot as plt
import numpy as np
from click import style
from shiny import App, ui, render

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
            ui.output_plot("plot_top", height="300px"),
            ui.output_plot("plot_bottom", height="300px"),

            style="padding:20px; background:#f5f5f5; border-radius:8px;",
        ),

        ui.div(
            ui.tags.h3("New Positive Cases (Map)"),
            ui.output_ui("covid_map"),
            full_screen=True,
            height="1400px",
            style="border: 1px solid red"
        ),

        ui.card(
            ui.tags.h3("New Positive Cases (Top 20)"),
            ui.output_plot("cases_plot", height="700px"),

            full_screen=True
        ),

        col_widths=(3, 5, 3)
    )
)


# ================== SERVER ==================

def server(input, output, session):

    # ----------- LEFT SIDE -----------
    @output
    @render.plot
    def plot_top():
        fig, ax = plt.subplots(figsize=(7, 4))

        ax.bar(
            df_daily["date"],
            df_daily["daily_new_cases"],
            color="#00B4FF"
        )

        ax.set_title("Global New Positive Cases per Day")
        ax.set_ylabel("Cases")
        ax.set_xlabel("Date")
        fig.autofmt_xdate()  # rotate dates cleanly
        return fig

    @output
    @render.plot
    def plot_bottom():
        fig, ax = plt.subplots(figsize=(7, 4))

        ax.bar(
            df_daily["date"],
            df_daily["daily_new_deaths"],
            color="orange"
        )

        ax.set_title("Global New Deaths per Day")
        ax.set_ylabel("Deaths")
        ax.set_xlabel("Date")
        fig.autofmt_xdate()
        return fig

    # ---------- MAP (Folium) ----------

    @output
    @render.ui
    def covid_map():
        m = folium.Map(
            location=[30, 0],
            zoom_start=2,
            tiles="CartoDB positron",
        )

        for _, row in df_latest.iterrows():
            try:
                folium.Circle(
                    location=[row["latitude"], row["longitude"]],
                    radius=row["daily_new_cases"] * 20,
                    color="blue",
                    fill=True,
                    tooltip=f"Country: {row["country"]}\n Cases: {row['daily_new_cases']}",
                    fill_opacity=0.5
                ).add_to(m)
            except Exception as e:
                pass
                # print(row["country"])
        return ui.HTML(m._repr_html_())

    # ---------- BAR CHART RIGHT ----------

    @output
    @render.plot
    def cases_plot():
        data = (
            df_latest.sort_values("daily_new_cases", ascending=False)
            .head(20)
        )

        fig, ax = plt.subplots(figsize=(5, 10))
        ax.barh(
            y=data["country"],
            width=data["daily_new_cases"],
            color="#00B4FF"
        )

        ax.invert_yaxis()
        ax.set_xlabel("New cases")
        ax.set_ylabel("")
        ax.set_title("Top 20 countries by new cases")

        fig.tight_layout()
        return fig


if __name__ == "__main__":
    app = App(app_ui, server)
    app.run()
