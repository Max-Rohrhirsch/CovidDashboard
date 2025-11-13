from typing import Hashable
import pandas as pd
from pandas import DataFrame


def get_dataframe() -> dict[Hashable, DataFrame]:
    df = pd.read_csv("file.csv")

    # Daily für cases berechnen wenn NaN
    df["daily_new_cases"] = df.groupby("country")["cumulative_total_cases"] \
        .diff() \
        .fillna(df["daily_new_cases"]) \
        .fillna(0)

    # Daily für deaths berechnen wenn NaN
    df["daily_new_deaths"] = df.groupby("country")["cumulative_total_deaths"] \
        .diff() \
        .fillna(df["daily_new_deaths"]) \
        .fillna(0)

    countries = {
        country: subdf.drop(columns=["country"]).reset_index(drop=True)
        for country, subdf in df.groupby("country")
    }

    return countries


def get_latest_data() -> DataFrame:
    df = get_full_dataframe()

    df_latest = (
        df.sort_values("date")
          .groupby("country", as_index=False)
          .tail(1)
    )
    return df_latest


def get_full_dataframe() -> DataFrame:
    df = pd.read_csv("file.csv")
    df["date"] = pd.to_datetime(df["date"])

    # Calculate daily cases
    df["daily_new_cases"] = (
        df.groupby("country")["cumulative_total_cases"]
          .diff()
          .fillna(df["daily_new_cases"])
          .fillna(0)
    )

    # Calculate daily deaths
    df["daily_new_deaths"] = (
        df.groupby("country")["cumulative_total_deaths"]
          .diff()
          .fillna(df["daily_new_deaths"])
          .fillna(0)
    )

    return df
