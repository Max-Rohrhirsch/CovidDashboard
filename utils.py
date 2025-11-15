from typing import Hashable
import pandas as pd
from pandas import DataFrame

_df = pd.read_csv("file.csv")
# laender = pd.read_csv("countryLoc.csv")


def get_dataframe() -> dict[Hashable, DataFrame]:
    # Daily für cases berechnen wenn NaN
    _df["daily_new_cases"] = _df.groupby("country")["cumulative_total_cases"] \
        .diff() \
        .fillna(_df["daily_new_cases"]) \
        .fillna(0)

    # Daily für deaths berechnen wenn NaN
    _df["daily_new_deaths"] = _df.groupby("country")["cumulative_total_deaths"] \
        .diff() \
        .fillna(_df["daily_new_deaths"]) \
        .fillna(0)

    countries = {
        country: subdf.drop(columns=["country"]).reset_index(drop=True)
        for country, subdf in _df.groupby("country")
    }

    return countries


def get_latest_data():
    df = get_full_dataframe()

    coords = pd.read_csv("countriLoc.csv")

    df_latest = (
        df.sort_values("date")
          .groupby("country", as_index=False)
          .tail(1)
    )

    df_latest = df_latest.merge(
        coords[["name", "latitude", "longitude"]],
        left_on="country",
        right_on="name",
        how="left"
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


def normalize_country_csv(file_name: str, columnName: str):
    df = pd.read_csv(file_name)

    df[columnName] = df[columnName].str.lower()

    df.to_csv(file_name, index=False)

# normalize_country_csv("countriLoc.csv", "name")
# normalize_country_csv("file.csv", "country")
